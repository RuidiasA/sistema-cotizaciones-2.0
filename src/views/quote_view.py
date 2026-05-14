from typing import Callable # Eliminamos Dict ya que no se usa
import customtkinter as ctk

class QuoteView(ctk.CTkFrame):
    def __init__(self, master, on_quote: Callable[[str, int, float], None]) -> None:
        super().__init__(master, fg_color="#fff", corner_radius=15)
        self._on_quote = on_quote
        
        # Configuramos pesos de columnas para que el producto sea flexible
        # y los demás campos tengan su espacio justo dentro de los 300px del sidebar.
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure((1, 2, 3), weight=0)

        self._title = ctk.CTkLabel(
            self, text="⚡ Calculadora Rápida", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#e67e22"
        )
        self._title.grid(row=0, column=0, columnspan=4, padx=20, pady=(15, 5), sticky="w")

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

        # Etiqueta de resultados y errores
        self._result_label = ctk.CTkLabel(
            self, text="Resultados aparecerán aquí",
            font=ctk.CTkFont(size=12, slant="italic"), 
            text_color="gray"
        )
        self._result_label.grid(row=2, column=0, columnspan=4, padx=20, pady=(0, 15), sticky="w")

    def _handle_quote(self):
        """Captura los datos y valida tipos antes de enviar al controlador."""
        try:
            prod = self._producto_entry.get().strip()
            cant_text = self._cantidad_entry.get().strip()
            prec_text = self._precio_entry.get().strip()

            if not cant_text or not prec_text:
                self._show_error("Faltan datos")
                return

            cant = int(cant_text)
            prec = float(prec_text)
            
            # Si llegamos aquí, los datos son válidos
            self._on_quote(prod, cant, prec)
            
        except ValueError:
            # Ahora sí usamos el helper de error para dar feedback real
            self._show_error("Números inválidos")

    def _show_error(self, message: str) -> None:
        """Muestra mensajes de error visuales en la calculadora."""
        self._result_label.configure(text=f"❌ {message}", text_color="#e74c3c")

    def show_result(self, result: dict, known_product: bool):
        """Muestra el resultado final calculado por el QuoteService."""
        aviso = "" if known_product else "⚠️ (35%) "
        text = f"{aviso}S/. {result['precio_unit']:.2f} (Total: S/. {result['total']:.2f})"
        
        # Color naranja para productos conocidos, rojo para genéricos
        color = "#e67e22" if known_product else "#f10f0f"
        
        self._result_label.configure(text=text, text_color=color)