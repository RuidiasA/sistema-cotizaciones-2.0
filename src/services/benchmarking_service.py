from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import logging

from ..models.entities import ArchetypeData, BenchmarkingMatrix, ScanRow
from .text_utils import (
    es_servicio_o_logistica,
    extraer_material,
    extraer_segmento_calidad,
    normalizar_texto,
    remover_ruido_de_especificacion,
)


class BenchmarkingService:
    """Genera matrices de benchmarking por arquetipo de producto."""

    MARGEN_BASE = 35.0
    PESO_VIRTUAL = 3

    def __init__(self, umbral_confianza: int = 3) -> None:
        # Estado inmutable para mantener operaciones thread-safe.
        self._umbral_confianza = max(1, int(umbral_confianza))

    def extraer_arquetipo(self, fila_detalle: str, keyword: str = "") -> Optional[str]:
        if es_servicio_o_logistica(fila_detalle):
            return None

        limpio = remover_ruido_de_especificacion(fila_detalle)
        limpio_norm = normalizar_texto(limpio)
        if not limpio_norm:
            return None

        material = extraer_material(limpio)
        segmento = extraer_segmento_calidad(limpio)
        base = self._extraer_producto_base(limpio, material, segmento, keyword)

        if not base:
            return None

        partes = [base]
        if material and material not in partes:
            partes.append(material)
        if segmento and segmento not in partes:
            partes.append(segmento)

        return " ".join(partes).strip()

    def es_servicio_excluido(self, articulo: str) -> bool:
        return es_servicio_o_logistica(articulo)

    def generar_benchmarking(self, scan_rows: List[ScanRow], categoria: str, keyword: str = "") -> BenchmarkingMatrix:
        """Construye una matriz por arquetipos usando agregaciones de pandas."""
        fecha = datetime.now().isoformat(timespec="seconds")

        records: List[Dict[str, object]] = []
        for row in scan_rows:
            # Auditoría: registrar descartes por reglas de negocio
            if row.cantidad <= 0:
                logging.warning("Benchmarking: descartado por cantidad<=0 -> %s | cantidad=%s", row.articulo, row.cantidad)
                continue
            if row.margen <= 0:
                logging.warning("Benchmarking: descartado por margen<=0 -> %s | margen=%s", row.articulo, row.margen)
                continue

            arquetipo = self.extraer_arquetipo(row.articulo, keyword)
            if not arquetipo:
                logging.warning("Benchmarking: descartado por arquetipo vacío -> %s", row.articulo)
                continue

            records.append(
                {
                    "arquetipo": arquetipo,
                    "tier": self._tier_para_cantidad(row.cantidad),
                    "costo_prov": float(row.precio_prov),
                    "precio_cli": float(row.precio_cli),
                    "margen": float(row.margen),
                }
            )

        if not records:
            return BenchmarkingMatrix(
                categoria=categoria,
                arquetipos=[],
                fecha_generacion=fecha,
                total_registros_procesados=0,
            )

        df = pd.DataFrame(records)
        grouped = (
            df.groupby(["arquetipo", "tier"], as_index=False)
            .agg(
                costo_total=("costo_prov", "sum"),
                precio_total=("precio_cli", "sum"),
                costo_promedio=("costo_prov", "mean"),
                precio_promedio=("precio_cli", "mean"),
                casos=("precio_cli", "count"),
            )
            .sort_values(["arquetipo", "tier"])
        )

        bucket: Dict[str, Dict[str, Dict[str, float]]] = {}
        for row in grouped.itertuples(index=False):
            arquetipo = str(row.arquetipo)
            tier = str(row.tier)
            
            c_total = float(row.costo_total)
            p_total = float(row.precio_total)
            
            margen_consolidado = ((p_total - c_total) / c_total) * 100 if c_total > 0 else 0.0
            
            bucket.setdefault(arquetipo, {})[tier] = {
                "margen": round(margen_consolidado, 2),
                "costo": round(float(row.costo_promedio), 2),
                "precio": round(float(row.precio_promedio), 2),
                "casos": int(row.casos),
            }

        arquetipos: List[ArchetypeData] = []
        for nombre, tiers in sorted(bucket.items()):
            t100 = tiers.get("100", {"margen": 0.0, "costo": 0.0, "precio": 0.0, "casos": 0})
            t500 = tiers.get("500", {"margen": 0.0, "costo": 0.0, "precio": 0.0, "casos": 0})
            t1000 = tiers.get("1000", {"margen": 0.0, "costo": 0.0, "precio": 0.0, "casos": 0})

            c100 = int(t100["casos"])
            c500 = int(t500["casos"])
            c1000 = int(t1000["casos"])

            margen_100_obs = float(t100["margen"]) if c100 > 0 else None
            margen_500_obs = float(t500["margen"]) if c500 > 0 else None
            margen_1000_obs = float(t1000["margen"]) if c1000 > 0 else None

            margen_100, margen_500, margen_1000, c100, c500, c1000 = self._inferir_margenes(
                margen_100_obs,
                margen_500_obs,
                margen_1000_obs,
                c100,
                c500,
                c1000,
            )

            casos_totales = int(c100 + c500 + c1000)
            arquetipos.append(
                ArchetypeData(
                    nombre_arquetipo=nombre,
                    categoria=categoria,
                    margen_tier_100=round(margen_100, 2),
                    casos_tier_100=c100,
                    costo_avg_100=float(t100["costo"]),
                    precio_avg_100=float(t100["precio"]),
                    margen_tier_500=round(margen_500, 2),
                    casos_tier_500=c500,
                    costo_avg_500=float(t500["costo"]),
                    precio_avg_500=float(t500["precio"]),
                    margen_tier_1000=round(margen_1000, 2),
                    casos_tier_1000=c1000,
                    costo_avg_1000=float(t1000["costo"]),
                    precio_avg_1000=float(t1000["precio"]),
                    actualizado_en=fecha,
                    confianza_general=self.calcular_confianza(casos_totales),
                )
            )

        return BenchmarkingMatrix(
            categoria=categoria,
            arquetipos=arquetipos,
            fecha_generacion=fecha,
            total_registros_procesados=len(records),
        )

    def _weighted_avg(self, valor_a: float, peso_a: int, valor_b: float, peso_b: int) -> float:
        total_peso = max(1, peso_a + peso_b)
        return round(((valor_a * peso_a) + (valor_b * peso_b)) / total_peso, 2)

    def _inferir_margenes(
        self,
        margen_100_obs: Optional[float],
        margen_500_obs: Optional[float],
        margen_1000_obs: Optional[float],
        c100: int,
        c500: int,
        c1000: int,
    ) -> tuple[float, float, float, int, int, int]:
        """
        Calcula los márgenes faltantes asegurando que la data real sea el ancla
        y se respete la economía de escala (Piso Dinámico).
        """
        # 1. Inicialización limpia
        m100, m500, m1000 = margen_100_obs, margen_500_obs, margen_1000_obs

        # 2. ESCENARIOS DE INFERENCIA (Solo uno debe ejecutarse)
        
        # CASO A: No hay absolutamente nada de data -> Todo al base
        if m100 is None and m500 is None and m1000 is None:
            m100 = m500 = m1000 = self.MARGEN_BASE

        # CASO B: Solo existe M100 (El más común: pedidos pequeños)
        elif m100 is not None and m500 is None and m1000 is None:
            m1000 = self._weighted_avg(m100, c100, self.MARGEN_BASE, self.PESO_VIRTUAL)
            m500 = self._weighted_avg(m100, c100, m1000, self.PESO_VIRTUAL)

        # CASO C: Solo existe M1000 (Piso Dinámico Activado)
        elif m1000 is not None and m100 is None and m500 is None:
            piso = max(self.MARGEN_BASE, m1000)
            m100 = m500 = piso

        # CASO D: Solo existe M500 (El centro es el ancla)
        elif m500 is not None and m100 is None and m1000 is None:
            m100 = max(self.MARGEN_BASE, m500)
            m1000 = self._weighted_avg(m500, c500, self.MARGEN_BASE, self.PESO_VIRTUAL)

        # CASO E: Existen extremos (100 y 1000) pero falta el medio
        elif m100 is not None and m1000 is not None and m500 is None:
            m500 = self._weighted_avg(m100, c100, m1000, c1000)
        
        # CASO F: Cualquier otro hueco (relleno de seguridad)
        m100 = m100 if m100 is not None else self.MARGEN_BASE
        m1000 = m1000 if m1000 is not None else self.MARGEN_BASE
        m500 = m500 if m500 is not None else self._weighted_avg(m100, c100, m1000, c1000)

        # 3. RESTRICCIÓN DE MONOTONÍA
        # Creamos copias para que ninguna reasignación altere la evaluación de la siguiente línea
        m100_ant, m500_ant, m1000_ant = m100, m500, m1000

        # 500 no puede ser más barato que 1000 ni más caro que 100
        if m500_ant < m1000_ant: 
            m500 = m1000_ant
        if m500_ant > m100_ant:  
            m500 = m100_ant

        # 100 no puede ser más barato que 500
        if m100_ant < m500:      
            m100 = m500

        # 1000 no puede ser más caro que 500
        if m1000_ant > m500:     
            m1000 = m500

        return (
            round(m100, 2),
            round(m500, 2),
            round(m1000, 2),
            c100,
            c500,
            c1000,
        )

    def calcular_confianza(self, casos_totales: int) -> float:
        confianza = (float(casos_totales) / float(self._umbral_confianza)) * 100.0
        return round(min(100.0, max(0.0, confianza)), 2)

    def _tier_para_cantidad(self, cantidad: int) -> str:
        if cantidad >= 1000:
            return "1000"
        if cantidad >= 500:
            return "500"
        return "100"

    def _extraer_producto_base(
        self,
        texto: str,
        material: Optional[str],
        segmento: Optional[str],
        keyword: str = "",
    ) -> str:
        texto_norm = normalizar_texto(texto)
        if not texto_norm:
            return ""

        def singularizar(token: str) -> str:
            if token.endswith("ces") and len(token) > 3:
                return token[:-3] + "z"
            if token.endswith("es") and len(token) > 4:
                return token[:-2]
            if token.endswith("s") and len(token) > 3:
                return token[:-1]
            return token

        # If keyword is provided, try to find it in the text.
        if keyword:
            keyword_norm = normalizar_texto(keyword)
            tokens = texto_norm.split()
            for token in tokens:
                token_singular = singularizar(token)
                if keyword_norm in token_singular or token_singular in keyword_norm:
                    return token_singular.upper()

        tokens = texto_norm.split()
        descartes = {"de", "con", "para", "y", "en", "el", "la", "los", "las"}
        if material:
            descartes.add(normalizar_texto(material))
        if segmento:
            descartes.add(normalizar_texto(segmento))

        for token in tokens:
            if token not in descartes:
                return singularizar(token).upper()
        return ""
