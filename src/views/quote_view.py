from typing import Callable, Dict
import customtkinter as ctk

class QuoteView(ctk.CTkFrame):
    def __init__(self, master, on_quote: Callable[[str, int, float], None]) -> None:
        super().__init__(master, fg_color="#fff", corner_radius=15)
        self._on_quote = on_quote

        # Configuración de grid
        self.grid_columnconfigure((0, 1, 2), weight=1)

        # Título con acento de color (UI/UX)
        self._title = ctk.CTkLabel(
            self, text="⚡ Calculadora de Cotización Rápida", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="#e67e22"
        )
        self._title.grid(row=0, column=0, columnspan=4, padx=20, pady=(15, 10), sticky="w")

        # Inputs en una sola fila (Mejor flujo visual)
        self._producto_entry = ctk.CTkEntry(self, placeholder_text="Nombre del producto...", height=35)
        self._producto_entry.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="ew")

        self._cantidad_entry = ctk.CTkEntry(self, placeholder_text="Cant.", width=80, height=35)
        self._cantidad_entry.grid(row=1, column=1, padx=10, pady=10)

        self._precio_entry = ctk.CTkEntry(self, placeholder_text="Precio Prov. S/.", width=120, height=35)
        self._precio_entry.grid(row=1, column=2, padx=10, pady=10)

        self._quote_button = ctk.CTkButton(
            self, text="Calcular", 
            command=self._handle_quote,
            font=ctk.CTkFont(weight="bold"),
            fg_color="#e67e22",
            hover_color="#d35400",
            width=120,
            height=35
        )
        self._quote_button.grid(row=1, column=3, padx=(10, 20), pady=10)

        # Área de resultados (Clean Design)
        self._result_label = ctk.CTkLabel(
            self, text="Ingresa los datos para calcular el margen",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="gray"
        )
        self._result_label.grid(row=2, column=0, columnspan=4, padx=20, pady=(0, 15), sticky="w")

    def _handle_quote(self) -> None:
        """Lógica para capturar datos y enviarlos al controlador."""
        producto = self._producto_entry.get().strip()
        try:
            # Validaciones UX básicas
            cant_str = self._cantidad_entry.get().strip()
            precio_str = self._precio_entry.get().strip()
            
            if not cant_str or not precio_str:
                self._show_error("Completa cantidad y precio.")
                return

            cantidad = int(cant_str)
            precio = float(precio_str)
            
            if cantidad <= 0 or precio <= 0:
                self._show_error("Deben ser mayores a 0.")
                return
                
            self._on_quote(producto, cantidad, precio)
            
        except ValueError:
            self._show_error("Usa números válidos.")

    def _show_error(self, message: str) -> None:
        self._result_label.configure(text=message, text_color="#e74c3c")

    def show_result(self, result: Dict[str, float], known_product: bool) -> None:
        """Muestra el resultado final con jerarquía visual."""
        aviso = "" if known_product else "⚠️ Producto no encontrado (Usando 35%) | "
        
        # Formateo de texto con énfasis en el Total
        text = (
            f"{aviso}Margen: {result['margen']:.2f}%  •  "
            f"Unitario: S/. {result['precio_unit']:.2f}  •  "
            f"TOTAL: S/. {result['total']:.2f}"
        )
        
        self._result_label.configure(
            text=text, 
            text_color="#2ecc71" if known_product else "#f1c40f",
            font=ctk.CTkFont(size=14, weight="bold" if known_product else "normal")
        )