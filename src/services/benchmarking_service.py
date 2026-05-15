from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

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
            if row.cantidad <= 0:
                continue
            if row.margen <= 0:
                continue

            arquetipo = self.extraer_arquetipo(row.articulo, keyword)
            if not arquetipo:
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
                margen_promedio=("margen", "mean"),
                costo_promedio=("costo_prov", "mean"),
                precio_promedio=("precio_cli", "mean"),
                casos=("margen", "count"),
            )
            .sort_values(["arquetipo", "tier"])
        )

        bucket: Dict[str, Dict[str, Dict[str, float]]] = {}
        for row in grouped.itertuples(index=False):
            arquetipo = str(row.arquetipo)
            tier = str(row.tier)
            bucket.setdefault(arquetipo, {})[tier] = {
                "margen": round(float(row.margen_promedio), 2),
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

            margen_100 = float(t100["margen"]) if c100 > 0 else 35.0
            margen_1000 = float(t1000["margen"]) if c1000 > 0 else 35.0

            if c500 > 0:
                margen_500 = float(t500["margen"])
            elif c100 == 0 and c1000 == 0:
                margen_500 = 35.0
            elif c100 == 0:
                margen_500 = margen_1000
            elif c1000 == 0:
                margen_500 = margen_100
            else:
                ancla = max(35.0, margen_1000)
                piso_virtual = float(self._umbral_confianza)
                margen_500 = (
                    (margen_100 * c100) + (margen_1000 * c1000) + (ancla * piso_virtual)
                ) / (c100 + c1000 + piso_virtual)

            if c1000 > 0:
                margen_500 = max(margen_500, margen_1000)
            if c100 > 0:
                margen_500 = min(margen_500, margen_100)

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
