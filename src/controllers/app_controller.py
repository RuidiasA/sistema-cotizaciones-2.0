from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from ..models.constants import DEFAULT_EXCEL_FOLDER, HOJAS_EXCLUIDAS, VARIACIONES_POR_CATEGORIA
from ..models.entities import FileScanReport, PriceStats
from ..services.excel_scan_service import ExcelScanService
from ..services.quote_service import QuoteService
from ..services.variation_service import VariationService
from ..views.main_view import MainView


class AppController:
    def __init__(self) -> None:
        self._variation_service = VariationService(VARIACIONES_POR_CATEGORIA)
        self._scan_service = ExcelScanService(HOJAS_EXCLUIDAS)
        self._quote_service = QuoteService()
        self._stats = PriceStats()
        self._matched_total = 0
        self._executor = ThreadPoolExecutor(max_workers=1)

        self._view = MainView(
            categories=self._variation_service.get_categories(),
            default_folder=DEFAULT_EXCEL_FOLDER,
            on_scan=self.handle_scan,
            on_quote=self.handle_quote,
        )

    def run(self) -> None:
        self._view.mainloop()

    def handle_scan(self, folder: str, categoria: str, keyword: str) -> None:
        self._view.set_status("Procesando...")
        self._view.clear_results()
        variations = self._variation_service.get_variations(categoria, keyword)
        if categoria and not variations:
            self._view.append_log("Categoria no reconocida. Revisa el nombre seleccionado.")
            self._view.set_status("Listo")
            return
        if keyword and not variations:
            self._view.append_log("No se encontraron variaciones para la palabra clave.")
            self._view.set_status("Listo")
            return
        future = self._executor.submit(self._scan_service.scan_folder, folder, variations)
        future.add_done_callback(lambda f: self._on_scan_done(f))

    def _on_scan_done(self, future) -> None:
        try:
            reports = future.result()
        except Exception as exc:
            self._view.after(0, lambda: self._view.append_log(f"Error: {exc}"))
            self._view.after(0, lambda: self._view.set_status("Error"))
            return

        def update_ui() -> None:
            self._stats = PriceStats()
            matched_total = 0
            if not reports:
                self._view.append_log("No se encontraron archivos Excel en la carpeta.")
                self._matched_total = 0
                self._view.set_stats_text(self._format_stats(0))
                self._view.set_status("Listo")
                return
            for report in reports:
                self._render_report(report)
                self._stats.merge(report.stats)
                matched_total += len(report.matched_rows)
            self._matched_total = matched_total
            self._view.set_stats_text(self._format_stats(matched_total))
            self._view.set_status("Listo")

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
