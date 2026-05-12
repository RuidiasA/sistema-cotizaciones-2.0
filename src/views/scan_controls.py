from typing import Callable, List
import customtkinter as ctk
from tkinter import filedialog

class ScanControls(ctk.CTkFrame):
    def __init__(
        self,
        master,
        categories: List[str],
        default_folder: str,
        on_scan: Callable[[str, str, str], None],
    ) -> None:
        # Usamos un fondo ligeramente más oscuro que el #ccc general para dar profundidad
        super().__init__(master, fg_color="#d9d9d9", corner_radius=0)
        self._on_scan = on_scan

        # --- SECCIÓN: CARPETA ---
        self._section_folder = ctk.CTkLabel(self, text="📁 UBICACIÓN DE DATOS", 
                                           font=ctk.CTkFont(size=11, weight="bold"), text_color="#555")
        self._section_folder.pack(anchor="w", padx=15, pady=(20, 5))

        self._folder_entry = ctk.CTkEntry(self, placeholder_text="Ruta del Excel...", height=35)
        self._folder_entry.insert(0, default_folder)
        self._folder_entry.pack(fill="x", padx=15, pady=5)

        self._browse_button = ctk.CTkButton(self, text="Cambiar Carpeta", 
                                           command=self._browse, 
                                           fg_color="#7f8c8d", hover_color="#95a5a6")
        self._browse_button.pack(fill="x", padx=15, pady=5)

        # Separador visual
        ctk.CTkLabel(self, text="", height=1).pack(pady=10)

        # --- SECCIÓN: FILTROS ---
        self._section_filter = ctk.CTkLabel(self, text="🔍 FILTROS DE BÚSQUEDA", 
                                           font=ctk.CTkFont(size=11, weight="bold"), text_color="#555")
        self._section_filter.pack(anchor="w", padx=15, pady=(0, 5))

        self._category_menu = ctk.CTkOptionMenu(self, values=["Todas"] + categories, 
                                               fg_color="#e67e22", button_color="#d35400",
                                               button_hover_color="#e67e22", height=35)
        self._category_menu.set("Todas")
        self._category_menu.pack(fill="x", padx=15, pady=5)

        self._keyword_entry = ctk.CTkEntry(self, placeholder_text="Palabra clave (ej. casaca)...", height=35)
        self._keyword_entry.pack(fill="x", padx=15, pady=5)

        # --- BOTÓN DE ACCIÓN ---
        self._scan_button = ctk.CTkButton(self, text="INICIAR ESCANEO", 
                                         command=self._handle_scan,
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         fg_color="#e67e22", hover_color="#d35400",
                                         height=45)
        self._scan_button.pack(fill="x", padx=15, pady=30)

        # --- ESTADO ---
        self._status_label = ctk.CTkLabel(self, text="● Sistema Listo", 
                                         font=ctk.CTkFont(size=16, slant="italic"),
                                         text_color="#27ae60")
        self._status_label.pack(side="bottom", pady=20)

    def _browse(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self._folder_entry.delete(0, "end")
            self._folder_entry.insert(0, folder)

    def _handle_scan(self) -> None:
        folder = self._folder_entry.get().strip()
        categoria = self._category_menu.get()
        if categoria == "Todas":
            categoria = ""
        keyword = self._keyword_entry.get().strip()
        self._on_scan(folder, categoria, keyword)

    def set_status(self, text: str) -> None:
        # Lógica UX: Cambiar color si es error o éxito
        color = "#e67e22" if "Error" in text else "#27ae60"
        self._status_label.configure(text=f"● {text}", text_color=color)