from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
import threading
from typing import List, Optional

import pandas as pd

from ..models.constants import DEFAULT_EXCEL_FOLDER, HOJAS_EXCLUIDAS, VARIACIONES_POR_CATEGORIA
from ..models.entities import BenchmarkingMatrix, FileScanReport, PriceStats, ScanRow
from ..services.benchmarking_service import BenchmarkingService
from ..services.excel_scan_service import ExcelScanService
from ..services.quote_service import QuoteService
from ..services.variation_service import VariationService
from ..views.main_view import MainView


class AppController:
    def __init__(self) -> None:
        # Inicializamos los servicios y la vista. El VariationService se encarga de manejar las variaciones por categoría, el ExcelScanService se encarga de escanear los archivos Excel, y el QuoteService se encarga de generar cotizaciones basadas en los datos escaneados.
        self._variation_service = VariationService(VARIACIONES_POR_CATEGORIA)
        self._scan_service = ExcelScanService(HOJAS_EXCLUIDAS)
        self._quote_service = QuoteService()
        self._benchmarking_service = BenchmarkingService()
        self._stats = PriceStats()
        self._matched_total = 0
        self._last_scan_rows: List[ScanRow] = []
        self._current_benchmarking: Optional[BenchmarkingMatrix] = None
        self._stop_event = threading.Event()  
        self._executor = ThreadPoolExecutor(max_workers=1)

        # Configuramos la vista principal, pasando las categorías obtenidas del VariationService, el folder por defecto para los archivos Excel, y los handlers para las acciones de escaneo, cotización y cancelación.
        self._view = MainView(
            controller=self,
            categories=self._variation_service.get_categories(),
            default_folder=DEFAULT_EXCEL_FOLDER,
            on_quote=self.handle_quote,
            on_scan=self.handle_scan,
            on_cancel=self.handle_cancel,
        )

    def run(self) -> None:
        self._view.mainloop()

    def handle_scan(self, folder: str, categoria: str, keyword: str) -> None:
        self._stop_event.clear()
        self._view.set_scanning_state(True)
        self._view.enable_export(False)
        self._view.set_status("Procesando...")
        self._view.clear_results()
        search_pack = self._variation_service.get_variations(categoria, keyword)
        
        future = self._executor.submit(
            self._scan_service.scan_folder, folder, search_pack, self._stop_event
        )
        future.add_done_callback(lambda f: self._on_scan_done(f))
    
    def handle_cancel(self) -> None:
        """Activa la señal de parada"""
        self._stop_event.set()
        self._view.append_log("🛑 Cancelando escaneo... (esperando cierre de hilo)")
        self._view.set_status("Cancelando")

    # El callback se ejecuta en el hilo del executor, por lo que cualquier actualización a la UI debe hacerse usando self._view.after()
    def _on_scan_done(self, future) -> None:
        try:
            reports = future.result()
        except Exception as exc:
            def show_error() -> None:
                self._view.set_scanning_state(False)
                self._view.set_status(f"Error: {exc}")

            self._view.after(0, show_error)
            return

        def update_ui() -> None:
            self._stats = PriceStats()
            filas_globales = []
            
            for report in reports:
                if report.error_message:
                    self._view.append_log(f"⚠️ {report.file_name}: {report.error_message}")
                    continue
                
                self._view.append_log(f"✅ {report.file_name} ({report.sheet_name})")
                filas_globales.extend(report.matched_rows)
                self._stats.merge(report.stats)

            # ORDENAMIENTO GLOBAL A-Z
            filas_globales.sort(key=lambda x: str(x.articulo).strip().lower())

            # Renderizado único en la vista
            self._view.add_rows(filas_globales)
            self._last_scan_rows = list(filas_globales)
            
            self._matched_total = len(filas_globales)
            self._view.set_stats_text(self._format_stats(self._matched_total))
            if self._stop_event.is_set():
                self._view.set_status("Escaneo Cancelado")
            else:
                self._view.set_status("Listo")

            self._view.set_scanning_state(False)

        self._view.after(0, update_ui)

    def _format_stats(self, matched_total: int) -> str:
        if matched_total == 0:
            return (
                "Margen Promedio (>= 1000): 35.00% (0 casos) | "
                "Margen Promedio (>= 500): 35.00% (0 casos) | "
                "Margen Promedio (Resto): 35.00% (0 casos)"
            )
        avg_gt_1000 = self._stats.promedio_para_cantidad(1000)
        avg_gt_500 = self._stats.promedio_para_cantidad(500)
        avg_rest = self._stats.promedio_para_cantidad(1)
        return (
            "Margen Promedio (>= 1000): "
            f"{avg_gt_1000:.2f}% ({self._stats.count_gt_1000} casos) | "
            "Margen Promedio (>= 500): "
            f"{avg_gt_500:.2f}% ({self._stats.count_gt_500} casos) | "
            "Margen Promedio (Resto): "
            f"{avg_rest:.2f}% ({self._stats.count_rest} casos)"
        )

    def _render_report(self, report: FileScanReport) -> None:
        if report.error_message:
            self._view.append_log(f"{report.file_name}: {report.error_message}")
            return
        self._view.append_log(
            f"{report.file_name}: hoja '{report.sheet_name}', filas {len(report.matched_rows)}"
        )
        if report.failed_rows:
            self._view.append_log(f"  No devueltas: {len(report.failed_rows)}")
        self._view.add_rows(report.matched_rows)

    def handle_quote(self, product_name: str, cantidad: int, precio_prov: float) -> None:
        known = self._variation_service.is_known_product(product_name)
        stats = self._stats if self._matched_total > 0 else PriceStats()
        result = self._quote_service.create_quote(product_name, cantidad, precio_prov, stats)
        self._view.show_quote_result(result, known)

    def handle_benchmarking(self, categoria: str) -> None:
        if not self._last_scan_rows:
            self._view.after(0, lambda: self._view.set_status("Sin datos para benchmarking"))
            return

        self._view.after(0, lambda: self._view.set_benchmarking_state(True))
        self._view.after(0, lambda: self._view.enable_export(False))
        self._view.after(0, lambda: self._view.set_status("Generando Benchmarking..."))
        future = self._executor.submit(
            self._benchmarking_service.generar_benchmarking,
            list(self._last_scan_rows),
            categoria,
        )
        future.add_done_callback(lambda f: self._on_benchmarking_done(f))

    def _on_benchmarking_done(self, future) -> None:
        try:
            matrix: BenchmarkingMatrix = future.result()
        except Exception as exc:
            self._view.after(0, lambda: self._view.set_benchmarking_state(False))
            self._view.after(0, lambda: self._view.set_status(f"Error: {exc}"))
            return

        def update_ui() -> None:
            self._current_benchmarking = matrix
            benchmarking_rows = self._benchmarking_rows_from_matrix(matrix)
            total_arquetipos = len(matrix.arquetipos)
            self._view.clear_results()
            self._view.add_rows(benchmarking_rows)
            self._view.append_log(f"📊 Benchmarking generado: {total_arquetipos} arquetipos")
            self._view.set_status("Benchmarking Listo")
            self._view.set_benchmarking_state(False)
            self._view.enable_export(True)

        self._view.after(0, update_ui)

    def handle_export_benchmarking(self, folder_path: str) -> None:
        if self._current_benchmarking is None:
            self._view.after(0, lambda: self._view.set_status("Sin matriz de benchmarking"))
            return

        self._view.after(0, lambda: self._view.set_status("Exportando Benchmarking..."))
        matrix = self._current_benchmarking

        rows = []
        for item in matrix.arquetipos:
            rows.append(
                {
                    "Producto (Arquetipo)": item.nombre_arquetipo,
                    "Cantidad": 100,
                    "COSTO PROV.": round(float(item.costo_avg_100), 2),
                    "PRECIO CLI.": round(float(item.precio_avg_100), 2),
                    "Margen Promedio": round(float(item.margen_tier_100) if item.casos_tier_100 > 0 else 35.0, 2),
                    "Muestra (Casos)": item.casos_tier_100,
                }
            )
            rows.append(
                {
                    "Producto (Arquetipo)": item.nombre_arquetipo,
                    "Cantidad": 500,
                    "COSTO PROV.": round(float(item.costo_avg_500), 2),
                    "PRECIO CLI.": round(float(item.precio_avg_500), 2),
                    "Margen Promedio": round(float(item.margen_tier_500) if item.casos_tier_500 > 0 else 35.0, 2),
                    "Muestra (Casos)": item.casos_tier_500,
                }
            )
            rows.append(
                {
                    "Producto (Arquetipo)": item.nombre_arquetipo,
                    "Cantidad": 1000,
                    "COSTO PROV.": round(float(item.costo_avg_1000), 2),
                    "PRECIO CLI.": round(float(item.precio_avg_1000), 2),
                    "Margen Promedio": round(float(item.margen_tier_1000) if item.casos_tier_1000 > 0 else 35.0, 2),
                    "Muestra (Casos)": item.casos_tier_1000,
                }
            )

        df = pd.DataFrame(
            rows,
            columns=[
                "Producto (Arquetipo)",
                "Cantidad",
                "COSTO PROV.",
                "PRECIO CLI.",
                "Margen Promedio",
                "Muestra (Casos)",
            ],
        )

        categoria = (matrix.categoria or "General").strip() or "General"
        categoria_safe = "_".join(categoria.split())
        output_file = os.path.join(folder_path, f"Benchmarking_{categoria_safe}.xlsx")

        try:
            df.to_excel(output_file, index=False, engine="openpyxl")
        except Exception as exc:
            self._view.after(0, lambda: self._view.set_status(f"Error: {exc}"))
            return

        self._view.after(0, lambda: self._view.set_status("Benchmarking Exportado"))
        self._view.after(0, lambda: self._view.append_log(f"🗂️ Archivo: {output_file}"))

    def _benchmarking_rows_from_matrix(self, matrix: BenchmarkingMatrix) -> List[ScanRow]:
        rows: List[ScanRow] = []
        for item in matrix.arquetipos:
            margen_100 = round(float(item.margen_tier_100) if item.casos_tier_100 > 0 else 35.0, 2)
            margen_500 = round(float(item.margen_tier_500) if item.casos_tier_500 > 0 else 35.0, 2)
            margen_1000 = round(float(item.margen_tier_1000) if item.casos_tier_1000 > 0 else 35.0, 2)
            rows.append(
                ScanRow(
                    fila_id=int(item.casos_tier_100),
                    articulo=item.nombre_arquetipo,
                    cantidad=100,
                    precio_prov=round(float(item.costo_avg_100), 2),
                    precio_cli=round(float(item.precio_avg_100), 2),
                    margen=margen_100,
                )
            )
            rows.append(
                ScanRow(
                    fila_id=int(item.casos_tier_500),
                    articulo=item.nombre_arquetipo,
                    cantidad=500,
                    precio_prov=round(float(item.costo_avg_500), 2),
                    precio_cli=round(float(item.precio_avg_500), 2),
                    margen=margen_500,
                )
            )
            rows.append(
                ScanRow(
                    fila_id=int(item.casos_tier_1000),
                    articulo=item.nombre_arquetipo,
                    cantidad=1000,
                    precio_prov=round(float(item.costo_avg_1000), 2),
                    precio_cli=round(float(item.precio_avg_1000), 2),
                    margen=margen_1000,
                )
            )
        return rows
