from typing import Dict, List, Any
from .text_utils import normalizar_texto

class VariationService:
    def __init__(self, variaciones_por_categoria: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        variaciones_por_categoria ahora recibe la estructura de:
        { "categoria": [ {"tags": [...], "exclude": [...]}, ... ] }
        """
        self._variaciones = variaciones_por_categoria

    def get_categories(self) -> List[str]:
        return sorted(self._variaciones.keys())

    def get_variations(self, categoria: str, keyword: str) -> Dict[str, List[str]]:
        """
        Busca el clúster circular. Retorna un pack de búsqueda:
        {"tags": List[str], "exclude": List[str]}
        """
        """Retorna el Search Pack: {'tags': [...], 'exclude': [...]}"""
        keyword_norm = normalizar_texto(keyword or "")
        
        # 1. Búsqueda por Keyword (Circularidad)
        if keyword_norm:
            clusters = self._variaciones.get(categoria, [])
            for cluster in clusters:
                tags_norm = [normalizar_texto(t) for t in cluster["tags"]]
                if keyword_norm in tags_norm:
                    return {
                        "tags": cluster["tags"],
                        "exclude": cluster["exclude"]
                    }
            # Fallback si no está en el diccionario
            return {"tags": [keyword.strip()], "exclude": []}

        # 2. Búsqueda por Categoría (Ver todo lo de 'Bolsos', etc.)
        if categoria in self._variaciones:
            all_tags = []
            for cluster in self._variaciones[categoria]:
                all_tags.extend(cluster["tags"])
            return {"tags": all_tags, "exclude": []}

        return {"tags": [], "exclude": []}

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
        """Extrae todos los tags de todos los clústeres de todas las categorías"""
        flat_list = []
        for clusters in self._variaciones.values():
            for cluster in clusters:
                flat_list.extend(cluster["tags"])
        return flat_list