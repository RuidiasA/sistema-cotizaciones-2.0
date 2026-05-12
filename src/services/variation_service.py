from typing import Dict, List

from .text_utils import normalizar_texto


class VariationService:
    def __init__(self, variaciones_por_categoria: Dict[str, List[str]]) -> None:
        self._variaciones = variaciones_por_categoria

    def get_categories(self) -> List[str]:
        return sorted(self._variaciones.keys())

    def get_variations(self, categoria: str, keyword: str) -> List[str]:
        # 1. Si hay keyword, es la prioridad absoluta
        if keyword:
            return [keyword.strip()]

        # 2. Si no hay keyword pero sí categoría (y no es "Todas")
        categoria_norm = normalizar_texto(categoria or "")
        if categoria_norm and categoria_norm != normalizar_texto("Todas"):
            for name, values in self._variaciones.items():
                if normalizar_texto(name) == categoria_norm:
                    return list(values)
            return [categoria]

        # 3. Si no hay nada seleccionado o es "Todas", devolvemos lista vacía
        # Esto indica "Sin filtro de producto"
        return []

    def is_known_product(self, product_name: str) -> bool:
        prod_norm = normalizar_texto(product_name or "")
        if not prod_norm:
            return False
        for variation in self._all_variations():
            var_norm = normalizar_texto(variation)
            if prod_norm in var_norm or var_norm in prod_norm:
                return True
        return False

    def _all_variations(self) -> List[str]:
        return [v for grupo in self._variaciones.values() for v in grupo]
