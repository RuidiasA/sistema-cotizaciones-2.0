from typing import Callable # Eliminamos Dict ya que no se usa
import customtkinter as ctk

class QuoteView(ctk.CTkFrame):
    def __init__(self, master, on_quote: Callable[[str, int, float], None], on_clear: Callable[[], None] = None) -> None:
        super().__init__(master, fg_color="#fff", corner_radius=15)
        self._on_quote = on_quote
        self._on_clear = on_clear or (lambda: None)
        
        # Configuramos pesos de columnas para que el producto sea flexible
        # y los demás campos tengan su espacio justo dentro de los 300px del sidebar.
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure((1, 2, 3), weight=0)

        self._title = ctk.CTkLabel(
            self, text="⚡ Calculadora Rápida", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#e67e22"
        )
        self._title.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 5), sticky="w")

        # Botón de limpiar en la esquina superior derecha
        self._clear_button = ctk.CTkButton(
            self, text="🗑", command=self._handle_clear,
            fg_color="#95a5a6", hover_color="#7f8c8d", width=35, height=32,
            font=ctk.CTkFont(size=14)
        )
        self._clear_button.grid(row=0, column=3, padx=(5, 15), pady=(15, 5), sticky="e")

        # Campo: Producto (Flexible)
        self._producto_entry = ctk.CTkEntry(self, placeholder_text="Producto...", height=32)
        self._producto_entry.grid(row=1, column=0, padx=(15, 5), pady=10, sticky="ew")

        # Campo: Cantidad (Ancho fijo para evitar que desaparezca)
        self._cantidad_entry = ctk.CTkEntry(self, placeholder_text="Cant.", width=55, height=32)
        self._cantidad_entry.grid(row=1, column=1, padx=5, pady=10)

        # Campo: Precio (Ancho fijo)
        self._precio_entry = ctk.CTkEntry(self, placeholder_text="Costo S/.", width=85, height=32)
        self._precio_entry.grid(row=1, column=2, padx=5, pady=10)

        # Botón de acción
        self._quote_button = ctk.CTkButton(
            self, text="Ok", command=self._handle_quote,
            fg_color="#e67e22", hover_color="#d35400", width=45, height=32
        )
        self._quote_button.grid(row=1, column=3, padx=(5, 15), pady=10)

    def _handle_quote(self):
        """Captura los datos y valida tipos antes de enviar al controlador."""
        try:
            prod = self._producto_entry.get().strip()
            cant_text = self._cantidad_entry.get().strip()
            prec_text = self._precio_entry.get().strip()

            if not cant_text or not prec_text:
                return

            cant = int(cant_text)
            prec = float(prec_text)
            
            # Si llegamos aquí, los datos son válidos
            self._on_quote(prod, cant, prec)
            
        except ValueError:
            pass

    def _handle_clear(self):
        """Limpia los inputs y llama al callback para limpiar las tarjetas."""
        self._producto_entry.delete(0, "end")
        self._cantidad_entry.delete(0, "end")
        self._precio_entry.delete(0, "end")
        self._on_clear()

    def show_result(self, result: dict, known_product: bool):
        """Muestra el resultado final calculado por el QuoteService."""
        # Este método puede quedar vacío ya que ahora las tarjetas se actualizan directamente
        pass