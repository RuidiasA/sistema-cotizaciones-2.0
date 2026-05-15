import sys
from pathlib import Path

# Ensure project root is on sys.path so `src` package is importable when running tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.services.text_utils import es_servicio_o_logistica

tests = [
    'IGV',
    'IGV 18%',
    'igv',
    'SERVICIOS',
    'SERVICIO X',
    'Producto con IGV 18%',
    'Envio urbano',
    'Flete',
    'Subtotal pedido',
    'Pago de servicio',
    'Camisa algodón 100%'
]

for t in tests:
    print(f"{t} -> {es_servicio_o_logistica(t)}")
