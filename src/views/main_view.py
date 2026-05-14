from typing import Callable, Dict, List
import customtkinter as ctk

from .quote_view import QuoteView
from .results_view import ResultsView
from .scan_controls import ScanControls
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

class MainView(ctk.CTk):
    def __init__(
        self,
        controller,
        categories: List[str],
        default_folder: str,
        on_scan: Callable[[str, str, str], None],
        on_quote: Callable[[str, int, float], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__()
        
        self.title("Gestión de Cotizaciones")
        self.geometry("1400x900")
        self.configure(fg_color="#cccccc")

        # Configuración de Grid: Columna 0 (Sidebar), Columna 1 (Contenido)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR LATERAL ---
        self._sidebar = ctk.CTkFrame(self, width=300, fg_color="#d9d9d9", corner_radius=0)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)

        # Controles de Búsqueda
        self._controls = ScanControls(
            self._sidebar,
            categories,
            default_folder,
            controller,
            on_scan,
            on_cancel,
        )
        self._controls.pack(fill="x", padx=15, pady=10)

        # Calculadora Rápida
        self._quote = QuoteView(self._sidebar, on_quote)
        self._quote.pack(fill="x", padx=15, pady=10)

        # --- ÁREA DE CONTENIDO (Resultados) ---
        self._results = ResultsView(self)
        self._results.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

    # Métodos de comunicación
    def set_scanning_state(self, is_scanning: bool): 
        """Propaga el estado a los controles para habilitar/deshabilitar botones"""
        self._controls.set_scanning_state(is_scanning)

    def set_benchmarking_state(self, is_benchmarking: bool):
        self._controls.set_benchmarking_state(is_benchmarking)

    def enable_export(self, enabled: bool):
        self._controls.enable_export(enabled)
        
    def set_status(self, text): self._controls.set_status(text)
    def clear_results(self): self._results.clear()
    def append_log(self, text): self._results.append_log(text)
    def add_rows(self, rows): self._results.add_rows(rows)
    def set_stats_text(self, text): self._results.set_stats_text(text)
    def show_quote_result(self, res, known): self._quote.show_result(res, known)
    