from typing import Dict

from ..models.entities import PriceStats


class QuoteService:
    def create_quote(
        self,
        product_name: str,
        cantidad: int,
        precio_prov: float,
        stats: PriceStats,
        margen_defecto: float = 35.0,
    ) -> Dict[str, float]:
        margen = stats.promedio_para_cantidad(cantidad, margen_defecto)
        precio_unit = round(precio_prov * (1 + (margen / 100)), 2)
        total = round(precio_unit * cantidad, 2)
        return {
            "margen": margen,
            "precio_unit": precio_unit,
            "total": total,
        }
