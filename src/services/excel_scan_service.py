from __future__ import annotations

import os
import re
from pathlib import Path
import sys
import threading
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ..models.entities import FileScanReport, PriceStats, ScanRow
from .text_utils import limpiar_precio, limpiar_y_entero, normalizar_texto, recortar_detalle


class ExcelScanService:
    KEYWORDS_DESCARTAR = ["SERVICIO", "DELIVERY", "SUBTOTAL", "SUB TOTAL", "TOTAL", "IGV", "1RA"]
    
    def __init__(self, hojas_excluidas: Sequence[str]) -> None:
        self._hojas_excluidas = [h.lower() for h in hojas_excluidas]

    def scan_folder(self, folder_path: str, search_pack: dict, stop_event: threading.Event) -> List[FileScanReport]:
        archivos = self._list_excel_files(folder_path)
        reports: List[FileScanReport] = []
        if stop_event.is_set():
            return reports
        for ruta in archivos:
            # Verificamos SIEMPRE al inicio de cada archivo si se pidió cancelar
            if stop_event.is_set():
                break
            reports.append(self.scan_file(ruta, search_pack))
        return reports

    def scan_file(self, file_path: str, search_pack: dict) -> FileScanReport:
        file_name = os.path.basename(file_path)
        report = FileScanReport(file_name=file_name)
        try:
            # Tip: use_cols y engine ayudan a evitar algunos errores de memoria
            xls = pd.ExcelFile(file_path)

            # Iterar todas las hojas del workbook y procesar las que contengan datos válidos.
            sheets_processed: List[str] = []

            for sheet_name in xls.sheet_names:
                # Saltar hojas excluidas
                if any(ex in sheet_name.lower().strip() for ex in self._hojas_excluidas):
                    continue

                # Intentar detectar cabecera en las primeras filas
                try:
                    df_check = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=25)
                except Exception:
                    continue

                header_row = self._detect_header_row(df_check)
                if header_row is None:
                    continue

                # Leer la hoja completa con la cabecera detectada
                try:
                    df_temp = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
                except Exception:
                    continue

                df_temp.columns = [str(c).replace("\n", " ").strip() for c in df_temp.columns]

                # Detectar columnas claves
                c_cant = next(
                    (
                        c
                        for c in df_temp.columns
                        if any(kw in c.lower() for kw in ["cant. min.", "cant.", "cant", "cantidad"])
                    ),
                    None,
                )
                c_finals = [
                    c
                    for c in df_temp.columns
                    if any(kw in c.lower() for kw in ["unit", "uni.", "uni ", "no igv", "venta"]) 
                ]
                c_provs = [
                    c
                    for c in df_temp.columns
                    if any(kw in c.lower() for kw in ["costo s/.", "costo prov"]) and c not in c_finals and "total" not in c.lower()
                ]
                c_detalle = next((c for c in df_temp.columns if "detalle" in c.lower()), None)

                if c_cant and (c_provs or c_finals):
                    # Preparación mínima de la hoja
                    df_temp[c_cant] = df_temp[c_cant].ffill()
                    if c_detalle:
                        df_temp[c_detalle] = df_temp[c_detalle].ffill()
                    for c in (c_provs + c_finals):
                        df_temp[c] = df_temp[c].ffill()

                    # Comprobar si la hoja contiene matches
                    mask = df_temp.apply(
                        lambda row: self._cumple_busqueda_tokenizada(row, search_pack),
                        axis=1,
                    )
                    matches = int(mask.sum())
                    if matches > 0:
                        sheets_processed.append(sheet_name)
                        col_map = {
                            "cant": c_cant,
                            "provs": c_provs,
                            "finals": c_finals,
                            "detalle": c_detalle,
                        }
                        # Procesar filas de esta hoja y acumular en el report
                        self._process_rows(df_temp, col_map, search_pack, report)

            # Si no se encontraron filas válidas en ninguna hoja
            if not report.matched_rows and not report.failed_rows:
                report.error_message = "No se detectó una tabla válida."
                return report

            report.sheet_name = ", ".join(sheets_processed) if sheets_processed else None
            return report

        except PermissionError:
            report.error_message = "Archivo abierto por otro programa. Ciérralo."
        except Exception as exc:
            report.error_message = f"Error: {str(exc)}"
        return report
    
    def _list_excel_files(self, folder_path: str) -> List[str]:
        if not folder_path or not os.path.isdir(folder_path):
            return []
        archivos: List[str] = []
        root = Path(folder_path)
        # Buscar recursivamente ambos patrones y combinar resultados
        for pattern in ("*.xlsx", "*.xls"):
            for p in root.rglob(pattern):
                # Saltar archivos temporales de Excel (ej: ~$...)
                if p.name.startswith("~$"):
                    continue
                # Asegurarse de que sea un archivo regular
                if p.is_file():
                    archivos.append(str(p))
        return archivos

    def _find_best_sheet(
        self,
        file_path: str,
        sheet_names: Sequence[str],
        search_pack: dict,
    ) -> Tuple[Optional[pd.DataFrame], Optional[str], Dict[str, object], int]:
        best_df: Optional[pd.DataFrame] = None
        best_sheet: Optional[str] = None
        col_map: Dict[str, object] = {}
        max_matches = -1

        for sheet_name in sheet_names:
            if any(ex in sheet_name.lower() for ex in self._hojas_excluidas):
                continue
            
            df_check = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=25)
            header_row = self._detect_header_row(df_check)
            if header_row is None:
                continue
            df_temp = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            df_temp.columns = [str(c).replace("\n", " ").strip() for c in df_temp.columns]

            c_cant = next(
                (
                    c
                    for c in df_temp.columns
                    if any(kw in c.lower() for kw in ["cant. min.", "cant.", "cant", "cantidad"])
                ),
                None,
            )
            c_finals = [
                c
                for c in df_temp.columns
                if any(kw in c.lower() for kw in ["unit", "uni.", "uni ", "no igv", "venta"])
            ]
            c_provs = [
                c
                for c in df_temp.columns
                if any(kw in c.lower() for kw in ["costo s/.", "costo prov"])
                and c not in c_finals
                and "total" not in c.lower()
            ]
            c_detalle = next((c for c in df_temp.columns if "detalle" in c.lower()), None)

            if c_cant and (c_provs or c_finals):
                df_temp[c_cant] = df_temp[c_cant].ffill()
                if c_detalle:
                    df_temp[c_detalle] = df_temp[c_detalle].ffill()
                for c in (c_provs + c_finals):
                    df_temp[c] = df_temp[c].ffill()

                mask = df_temp.apply(
                    lambda row: self._cumple_busqueda_tokenizada(row, search_pack),
                    axis=1,
                )
                matches = int(mask.sum())
                if matches > max_matches:
                    max_matches = matches
                    best_df = df_temp
                    best_sheet = sheet_name
                    col_map = {
                        "cant": c_cant,
                        "provs": c_provs,
                        "finals": c_finals,
                        "detalle": c_detalle,
                    }

        return best_df, best_sheet, col_map, max_matches

    def _detect_header_row(self, df_check: pd.DataFrame) -> Optional[int]:
        for idx, fila in df_check.iterrows():
            linea = " ".join([str(x).lower() for x in fila.values])
            if ("cant" in linea or "cantidad" in linea) and (
                "costo" in linea or "s/." in linea or "uni" in linea
            ):
                return int(idx)
        return None

    def _cumple_busqueda_tokenizada(self, fila: pd.Series, search_pack: dict) -> bool:
        
        # Esta función evalúa si una fila cumple con los criterios de búsqueda definidos en search_pack.
        # Se basa en la presencia de "tags" (palabras clave) y "exclude" (palabras prohibidas) en el contenido de la fila.
        from src.services.text_utils import normalizar_texto

        tags = search_pack.get("tags", [])
        excludes = search_pack.get("exclude", [])
        
        all_excludes = list(set(excludes + self.KEYWORDS_DESCARTAR))
        
        # Limpieza de ruido y normalización
        tokens = [str(v).split("Presentación:")[0].strip() for v in fila.values if pd.notna(v)]
        contenido_norm = normalizar_texto(" ".join(tokens))
        
        # 1. EXCLUSIÓN (Si hay una prohibida, fuera)
        for exc in all_excludes:
            if re.search(rf'\b{re.escape(normalizar_texto(exc))}\b', contenido_norm):
                return False
            
        if not tags: return True
        # 2. INCLUSIÓN (Al menos un tag debe estar)
        for tag in tags:
            if re.search(rf'\b{re.escape(normalizar_texto(tag))}\b', contenido_norm):
                return True
        return False
    
    def _is_bolsos_search(self, variaciones_norm: Sequence[str]) -> bool:
        return any(
            kw in variaciones_norm
            for kw in ["bolso", "bolsos", "mochila", "mochilas", "morral", "morrales"]
        )

    def _convertir_total_a_unitario(self, col_nombre: str, valor: float, cantidad: int) -> float:
        if cantidad <= 0:
            return valor
        nombre = str(col_nombre).lower().strip()
        if "total producto" in nombre or "total.1" in nombre:
            return valor / cantidad if valor > 0 else valor
        if "total" in nombre and valor > cantidad:
            return valor / cantidad
        return valor

    def _buscar_precio_cliente(
        self,
        fila: pd.Series,
        cols_finals: Sequence[str],
        cols_all: Iterable[str],
        cantidad: int,
        v1: float,
    ) -> float:
        candidatos: List[float] = []
        for c in cols_finals:
            val = limpiar_precio(fila[c])
            if val > v1:
                candidatos.append(val)

        if not candidatos:
            fallback_cols = [
                c
                for c in cols_all
                if any(kw in str(c).lower() for kw in ["venta", "precio", "pvp", "no igv", "sin igv"])
            ]
            for c in fallback_cols:
                val = limpiar_precio(fila[c])
                val = self._convertir_total_a_unitario(c, val, cantidad)
                if val > v1:
                    candidatos.append(val)

        return round(min(candidatos), 2) if candidatos else 0.0

    def _process_rows(
        self,
        df: pd.DataFrame,
        col_map: Dict[str, object],
        search_pack: dict,
        report: FileScanReport,
    ) -> None:
        from src.services.text_utils import (
            normalizar_texto, 
            limpiar_y_entero, 
            limpiar_precio, 
            recortar_detalle
        )
        from ..models.entities import ScanRow, PriceStats

        vistos = set()
        stats = PriceStats()
        tags = search_pack.get("tags", [])
        col_detalle = col_map.get("detalle") 

        # --- [OPTIMIZACIÓN] Pre-calcular columnas prioritarias por niveles ---
        # Nivel 1: Columnas que explícitamente guardan el detalle extendido u observaciones
        cols_detalle_real = [
            c for c in df.columns
            if any(k in str(c).lower() for k in ["detalle", "descripcion", "descr", "observac", "obs", "especif"])
        ]
        
        # Nivel 2: Columnas de nombres cortos o ítems (solo como plan B si no hay Nivel 1)
        cols_producto_plan_b = [
            c for c in df.columns
            if any(k in str(c).lower() for k in ["articulo", "producto", "nombre", "item"])
            and c not in cols_detalle_real
        ]

        for idx, fila in df.iterrows():
            # 1. VALIDACIÓN SEMÁNTICA
            if not self._cumple_busqueda_tokenizada(fila, search_pack):
                continue
            
            # 2. FILTRADO ESTRICTO EN COLUMNA DETALLE
            if tags and col_detalle and col_detalle in fila:
                texto_col = normalizar_texto(str(fila[col_detalle]))
                match_detalle = any(
                    re.search(rf'\b{re.escape(normalizar_texto(t))}\b', texto_col) 
                    for t in tags
                )
                if not match_detalle:
                    continue

            # 3. PROCESAMIENTO DE DATOS Y PRECIOS
            try:
                cantidad = limpiar_y_entero(fila[col_map["cant"]])
                
                # Función ultra robusta para detectar números y códigos de barra/SKUs cortos (ej: CAN-NAV-01)
                def es_identificador_o_numero(v):
                    s = str(v).strip()
                    if not s:
                        return True
                    # Detectar números enteros o decimales
                    try:
                        float(s)
                        return True
                    except ValueError:
                        pass
                    # Detectar códigos/SKUs: textos cortos (menos de 20 caracteres) que no llevan espacios
                    if len(s) < 20 and " " not in s:
                        return True
                    return False

                # Intentar obtener el candidato inicial de la columna mapeada originalmente
                detalle_raw = ""
                if col_detalle and col_detalle in fila:
                    detalle_raw = fila[col_detalle]

                # Si lo mapeado está vacío o es un código/número, aplicamos la cascada inteligente
                if pd.isna(detalle_raw) or str(detalle_raw).strip() == "" or es_identificador_o_numero(detalle_raw):
                    encontrado = False
                    
                    # Paso A: Buscar primero en las columnas de descripción reales (Detalle, Observaciones, etc.)
                    for c in cols_detalle_real:
                        val = fila.get(c)
                        if pd.notna(val) and str(val).strip() and not es_identificador_o_numero(val):
                            detalle_raw = val
                            encontrado = True
                            break
                    
                    # Paso B: Si no funcionó, buscar en columnas de nombre de producto (Artículo, Producto)
                    if not encontrado:
                        for c in cols_producto_plan_b:
                            val = fila.get(c)
                            if pd.notna(val) and str(val).strip() and not es_identificador_o_numero(val):
                                detalle_raw = val
                                encontrado = True
                                break
                                
                    # Paso C (Heurística de Rescate Extremo): Si los encabezados son raros, buscar el texto MÁS LARGO de la fila
                    if not encontrado:
                        candidatos = []
                        for c in df.columns:
                            if c == col_map.get("cant") or any(k in str(c).lower() for k in ["codigo", "code", "id", "num", "nro", "precio", "costo"]):
                                continue
                            val = fila.get(c)
                            if pd.notna(val):
                                s_val = str(val).strip()
                                if s_val and not es_identificador_o_numero(s_val):
                                    candidatos.append(s_val)
                        
                        if candidatos:
                            # Nos quedamos con el string más largo de la fila (las descripciones siempre ganan en longitud)
                            detalle_raw = max(candidatos, key=len)
                            encontrado = True

                    # Paso D (Último recurso total): Si la fila entera son puros números/códigos, dejamos lo que haya
                    if not encontrado and (pd.isna(detalle_raw) or str(detalle_raw).strip() == ""):
                        for c in df.columns:
                            if c == col_map.get("cant"):
                                continue
                            val = fila.get(c)
                            if pd.notna(val) and str(val).strip():
                                detalle_raw = val
                                break

                    if cantidad <= 0:
                        report.failed_rows.append(
                            ScanRow(
                                fila_id=int(idx),
                                articulo=recortar_detalle(detalle_raw),
                                cantidad=cantidad,
                                precio_prov=0.0,
                                precio_cli=0.0,
                                margen=0.0,
                                motivo="cantidad",
                            )
                        )
                        continue

                # Extraer Precio Proveedor (v1)
                v1 = 0.0
                for c in col_map["provs"]:
                    val = limpiar_precio(fila[c])
                    if val >= 0.2:
                        v1 = round(val, 2)
                        break

                # Buscar Precio Cliente (v2)
                v2 = self._buscar_precio_cliente(
                    fila,
                    col_map["finals"],
                    df.columns,
                    cantidad,
                    v1,
                )

                # Validar coherencia de precios
                min_diff = 0.5 if v1 >= 5 else 0.1
                if v1 <= 0 or v2 <= 0 or (v2 - v1) < min_diff:
                    report.failed_rows.append(
                        ScanRow(
                            fila_id=int(idx),
                            articulo=recortar_detalle(detalle_raw),
                            cantidad=cantidad,
                            precio_prov=v1,
                            precio_cli=v2,
                            margen=0.0,
                            motivo="precios",
                        )
                    )
                    continue

                # Detección de Duplicados
                huella = (cantidad, round(v1, 2), round(v2, 2))
                if huella in vistos:
                    report.failed_rows.append(
                        ScanRow(
                            fila_id=int(idx),
                            articulo=recortar_detalle(detalle_raw),
                            cantidad=cantidad,
                            precio_prov=v1,
                            precio_cli=v2,
                            margen=0.0,
                            motivo="duplicado",
                        )
                    )
                    continue

                # Calcular Margen y Validar Límites
                margen_val = ((v2 - v1) / v1) * 100 if v1 else 0.0
                if margen_val > 450:
                    report.failed_rows.append(
                        ScanRow(
                            fila_id=int(idx),
                            articulo=recortar_detalle(detalle_raw),
                            cantidad=cantidad,
                            precio_prov=v1,
                            precio_cli=v2,
                            margen=round(margen_val, 2),
                            motivo="margen",
                        )
                    )
                    continue

                # ÉXITO: Agregar fila válida
                vistos.add(huella)
                report.matched_rows.append(
                    ScanRow(
                        fila_id=int(idx),
                        articulo=recortar_detalle(detalle_raw),
                        cantidad=cantidad,
                        precio_prov=v1,
                        precio_cli=v2,
                        margen=round(margen_val, 2),
                    )
                )
                stats.add_margin(cantidad, margen_val)

            except Exception:
                report.failed_rows.append(
                    ScanRow(
                        fila_id=int(idx),
                        articulo=recortar_detalle(detalle_raw if ( 'detalle_raw' in locals() and detalle_raw) else (fila[col_detalle] if col_detalle else "")),
                        cantidad=0,
                        precio_prov=0.0,
                        precio_cli=0.0,
                        margen=0.0,
                        motivo="error",
                    )
                )

        # 4. ORDENAMIENTO PARCIAL Y ACUMULACIÓN DE ESTADÍSTICAS
        report.matched_rows.sort(
            key=lambda row: (str(row.articulo).strip().lower() if row.articulo else "")
        )
        # Merge stats (no sobrescribir estadísticas previas del report)
        try:
            report.stats.merge(stats)
        except Exception:
            report.stats = stats