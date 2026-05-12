from __future__ import annotations

import os
import sys
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ..models.entities import FileScanReport, PriceStats, ScanRow
from .text_utils import limpiar_precio, limpiar_y_entero, normalizar_texto, recortar_detalle


class ExcelScanService:
    def __init__(self, hojas_excluidas: Sequence[str]) -> None:
        self._hojas_excluidas = [h.lower() for h in hojas_excluidas]

    def scan_folder(self, folder_path: str, variaciones: Sequence[str]) -> List[FileScanReport]:
        archivos = self._list_excel_files(folder_path)
        reports: List[FileScanReport] = []
        variaciones_norm = [normalizar_texto(v) for v in variaciones]
        for ruta in archivos:
            reports.append(self.scan_file(ruta, variaciones_norm))
        return reports

    def scan_file(self, file_path: str, variaciones_norm: Sequence[str]) -> FileScanReport:
        file_name = os.path.basename(file_path)
        report = FileScanReport(file_name=file_name)
        try:
            xls = pd.ExcelFile(file_path)
            best_df, best_sheet, col_map, max_matches = self._find_best_sheet(
                file_path, xls.sheet_names, variaciones_norm
            )
            if best_df is None or max_matches <= 0:
                report.error_message = "No se detecto una tabla valida."
                return report

            report.sheet_name = best_sheet
            self._process_rows(best_df, col_map, variaciones_norm, report)
            return report
        except Exception as exc:
            report.error_message = f"Error al leer archivo: {exc}"
            return report

    def _list_excel_files(self, folder_path: str) -> List[str]:
        if not folder_path or not os.path.isdir(folder_path):
            return []
        archivos = []
        for name in os.listdir(folder_path):
            if name.startswith("~$"):
                continue
            if name.lower().endswith((".xlsx", ".xls")):
                archivos.append(os.path.join(folder_path, name))
        return archivos

    def _find_best_sheet(
        self,
        file_path: str,
        sheet_names: Sequence[str],
        variaciones_norm: Sequence[str],
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
                    lambda row: self._cumple_busqueda_tokenizada(row, variaciones_norm),
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

    def _cumple_busqueda_tokenizada(self, fila: pd.Series, variaciones_norm: Sequence[str]) -> bool:
        import re
        from src.services.text_utils import normalizar_texto

        # --- FIX: Si la lista está vacía, no hay filtro, devolvemos True para ver TODO ---
        if not variaciones_norm:
            return True

        # Si hay variaciones, seguimos con la lógica estricta (el primer elemento es el keyword)
        termino_buscado = variaciones_norm[0]
        
        tokens_fila = [str(val) for val in fila.values if pd.notna(val)]
        contenido_fila = " ".join(tokens_fila)
        contenido_norm = normalizar_texto(contenido_fila)

        patron = rf'\b{re.escape(normalizar_texto(termino_buscado))}\b'
        return bool(re.search(patron, contenido_norm))
    
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
        variaciones_norm: Sequence[str],
        report: FileScanReport,
    ) -> None:
        import re
        from src.services.text_utils import normalizar_texto

        vistos = set()
        stats = PriceStats()
        
        # --- NUEVA LÓGICA DE FILTRADO ESTRICTO ---
        termino_buscado = variaciones_norm[0] if variaciones_norm else ""
        
        # Intentamos detectar si existe una columna de "Detalle" o similar en el col_map
        col_detalle = col_map.get("detalle") 

        for idx, fila in df.iterrows():
            # Primero validamos con el método de arriba
            if not self._cumple_busqueda_tokenizada(fila, variaciones_norm):
                continue
            
            # Validación extra: si tenemos la columna detalle, el término DEBE estar ahí
            if col_detalle and col_detalle in fila:
                texto_col = normalizar_texto(str(fila[col_detalle]))
                if not re.search(rf'\b{re.escape(termino_buscado)}\b', texto_col):
                    continue

            try:
                cantidad = limpiar_y_entero(fila[col_map["cant"]])
                if cantidad <= 0:
                    report.failed_rows.append(
                        ScanRow(
                            fila_id=int(idx),
                            articulo=recortar_detalle(
                                fila[col_map.get("detalle")] if col_map.get("detalle") else ""
                            ),
                            cantidad=cantidad,
                            precio_prov=0.0,
                            precio_cli=0.0,
                            margen=0.0,
                            motivo="cantidad",
                        )
                    )
                    continue

                v1 = 0.0
                for c in col_map["provs"]:
                    val = limpiar_precio(fila[c])
                    if val >= 0.2:
                        v1 = round(val, 2)
                        break

                v2 = self._buscar_precio_cliente(
                    fila,
                    col_map["finals"],
                    df.columns,
                    cantidad,
                    v1,
                )

                min_diff = 0.5 if v1 >= 5 else 0.1
                if v1 <= 0 or v2 <= 0 or (v2 - v1) < min_diff:
                    report.failed_rows.append(
                        ScanRow(
                            fila_id=int(idx),
                            articulo=recortar_detalle(
                                fila[col_map.get("detalle")] if col_map.get("detalle") else ""
                            ),
                            cantidad=cantidad,
                            precio_prov=v1,
                            precio_cli=v2,
                            margen=0.0,
                            motivo="precios",
                        )
                    )
                    continue

                huella = (cantidad, round(v1, 2), round(v2, 2))
                if huella in vistos:
                    report.failed_rows.append(
                        ScanRow(
                            fila_id=int(idx),
                            articulo=recortar_detalle(
                                fila[col_map.get("detalle")] if col_map.get("detalle") else ""
                            ),
                            cantidad=cantidad,
                            precio_prov=v1,
                            precio_cli=v2,
                            margen=0.0,
                            motivo="duplicado",
                        )
                    )
                    continue

                margen = ((v2 - v1) / v1) * 100 if v1 else 0.0
                if margen > 450:
                    report.failed_rows.append(
                        ScanRow(
                            fila_id=int(idx),
                            articulo=recortar_detalle(
                                fila[col_map.get("detalle")] if col_map.get("detalle") else ""
                            ),
                            cantidad=cantidad,
                            precio_prov=v1,
                            precio_cli=v2,
                            margen=margen,
                            motivo="margen",
                        )
                    )
                    continue

                vistos.add(huella)
                detalle_raw = (
                    fila[col_map.get("detalle")] if col_map.get("detalle") else ""
                )
                detalle = recortar_detalle(detalle_raw)
                margen = ((v2 - v1) / v1) * 100 if v1 else 0.0
                report.matched_rows.append(
                    ScanRow(
                        fila_id=int(idx),
                        articulo=detalle,
                        cantidad=cantidad,
                        precio_prov=v1,
                        precio_cli=v2,
                        margen=round(margen, 2),
                    )
                )
                stats.add_margin(cantidad, margen)
            except Exception:
                report.failed_rows.append(
                    ScanRow(
                        fila_id=int(idx),
                        articulo=recortar_detalle(
                            fila[col_map.get("detalle")] if col_map.get("detalle") else ""
                        ),
                        cantidad=0,
                        precio_prov=0.0,
                        precio_cli=0.0,
                        margen=0.0,
                        motivo="error",
                    )
                )

        report.stats = stats
