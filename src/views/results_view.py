from typing import Iterable
import customtkinter as ctk
from tkinter import ttk
from ..models.entities import ScanRow

class ResultsView(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Ajustamos pesos para dar más espacio a la tabla

        # 1. KPI CARDS (Sin cambios, ya funcionan bien)
        self._kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self._card_1000 = self._create_kpi_card(self._kpi_frame, "Margen 1000", 0)
        self._card_500 = self._create_kpi_card(self._kpi_frame, "Margen 500", 1)
        self._card_rest = self._create_kpi_card(self._kpi_frame, "Margen Resto", 2)

        # 2. CONTENEDOR DE TABLA (Para manejar scrollbars mejor)
        self._table_container = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#bdc3c7")
        self._table_container.grid(row=1, column=0, sticky="nsew")
        self._table_container.grid_columnconfigure(0, weight=1)
        self._table_container.grid_rowconfigure(0, weight=1)

        self._setup_table_style()
        
        columns = ("fila", "articulo", "cantidad", "prov", "cli", "margen")
        self._table = ttk.Treeview(self._table_container, columns=columns, show="headings")
        
        # --- CONFIGURACIÓN DE COLUMNAS OPTIMIZADA ---
        self._table.heading("fila", text="CASOS")
        self._table.column("fila", width=60, minwidth=60, stretch=False, anchor="center")

        self._table.heading("articulo", text="ARTÍCULO / DETALLE")
        self._table.column("articulo", width=280, minwidth=200, stretch=True)
        self._table.heading("cantidad", text="CANT.")
        self._table.column("cantidad", width=70, minwidth=70, stretch=False, anchor="center")

        self._table.heading("prov", text="COSTO PROV.")
        self._table.column("prov", width=100, minwidth=100, stretch=False, anchor="center")

        self._table.heading("cli", text="PRECIO CLI.")
        self._table.column("cli", width=100, minwidth=100, stretch=False, anchor="center")

        self._table.heading("margen", text="MARGEN %")
        self._table.column("margen", width=90, minwidth=90, stretch=False, anchor="center")

        # --- SCROLLBAR MINIMALISTA ---
        # Usamos CTkScrollbar en lugar de ttk.Scrollbar
        self._scrollbar = ctk.CTkScrollbar(
            self._table_container, 
            orientation="vertical", 
            command=self._table.yview,
            width=16,
            fg_color="transparent",
            button_color="#e67e22",
            button_hover_color="#d35400",
            corner_radius=10
        )
        
        # Vincular el Treeview con el nuevo scrollbar
        self._table.configure(yscrollcommand=self._scrollbar.set)

        # Ubicación en el grid
        self._table.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        self._scrollbar.grid(row=0, column=1, sticky="ns", padx=(2, 5), pady=15)

        # 3. CONSOLA DE LOGS (Más compacta)
        self._log = ctk.CTkTextbox(self, height=100, fg_color="#ffffff", border_color="#bdc3c7", border_width=1, font=("Consolas", 11))
        self._log.grid(row=2, column=0, sticky="ew", pady=(20, 0))

    def _create_kpi_card(self, master, title, col):
        card = ctk.CTkFrame(master, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#bdc3c7")
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        master.grid_columnconfigure(col, weight=1)
        
        ctk.CTkLabel(card, text=title, text_color="#7f8c8d", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(15, 0))
        val = ctk.CTkLabel(card, text="0.00%", text_color="#e67e22", font=ctk.CTkFont(size=26, weight="bold"))
        val.pack(pady=(0, 15))
        return val

    def _setup_table_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configuración del cuerpo de la tabla
        style.configure("Treeview", 
                        background="#ffffff", 
                        foreground="#2c3e50", 
                        rowheight=35, 
                        fieldbackground="#ffffff", 
                        borderwidth=0,
                        font=("Segoe UI", 10))
        
        # FIX: Configuración de encabezados (Forzamos color de fuente y fondo)
        style.configure("Treeview.Heading", 
                        background="#e67e22", 
                        foreground="#ffffff", # Letras blancas explícitas
                        relief="flat",
                        padding=5,
                        font=("Segoe UI", 10, "bold"))
        
        # Evitar que el encabezado cambie a colores feos al pasar el mouse
        style.map("Treeview.Heading",
                  background=[('active', '#d35400')],
                  foreground=[('active', '#ffffff')])

        style.map("Treeview", background=[('selected', '#f39c12')], foreground=[('selected', '#ffffff')])

    # --- MÉTODOS DE COMUNICACIÓN ---
    def clear(self) -> None:
        self._log.delete("1.0", "end")
        for item in self._table.get_children():
            self._table.delete(item)
        self._card_1000.configure(text="0.00%")
        self._card_500.configure(text="0.00%")
        self._card_rest.configure(text="0.00%")

    def append_log(self, text: str) -> None:
        self._log.insert("end", f" {text}\n")
        self._log.see("end")

    def add_rows(self, rows: Iterable[ScanRow]) -> None:
        for row in rows:
            self._table.insert("", "end", values=(
                row.fila_id,
                row.articulo,
                row.cantidad,
                f"S/. {row.precio_prov:.2f}",
                f"S/. {row.precio_cli:.2f}",
                f"{row.margen:.2f}%"
            ))

    def set_stats_text(self, text: str) -> None:
        try:
            import re
            matches = re.findall(r"(\d+\.\d+)%", text)
            if len(matches) >= 3:
                self._card_1000.configure(text=f"{matches[0]}%")
                self._card_500.configure(text=f"{matches[1]}%")
                self._card_rest.configure(text=f"{matches[2]}%")
        except Exception:
            pass