import re
from typing import Any, Dict, List, Optional, Tuple
from .text_utils import normalizar_texto

class VariationService:
    def __init__(self, variaciones_por_categoria: Dict[str, Dict[str, Any]]) -> None:
        """
        variaciones_por_categoria ahora recibe la estructura de:
        {
            "Macro-Categoria": {
                "global_exclude": [...],
                "subcategorias": {
                    "categoria": [ {"tags": [...], "exclude": [...]}, ... ]
                }
            }
        }
        """
        self._variaciones = variaciones_por_categoria

    def get_categories(self) -> List[str]:
        categorias: List[str] = []
        for macro in sorted(self._variaciones.keys()):
            categorias.append(macro)
            subcategorias = self._variaciones.get(macro, {}).get("subcategorias", {})
            for sub in sorted(subcategorias.keys()):
                categorias.append(f"{macro} > {sub}")
        return categorias

    def _resolve_category(self, categoria: str) -> Tuple[Optional[str], Optional[str]]:
        categoria = (categoria or "").strip()
        if not categoria:
            return None, None

        if ">" in categoria:
            macro, sub = [part.strip() for part in categoria.split(">", 1)]
            if macro and sub:
                return macro, sub

        if categoria in self._variaciones:
            return categoria, None

        for macro, info in self._variaciones.items():
            subcategorias = info.get("subcategorias", {})
            if categoria in subcategorias:
                return macro, categoria

        return None, None

    def _get_clusters(self, categoria: str) -> List[Dict[str, Any]]:
        macro, sub = self._resolve_category(categoria)
        if not macro:
            return []

        subcategorias = self._variaciones.get(macro, {}).get("subcategorias", {})
        if sub:
            return subcategorias.get(sub, [])

        clusters: List[Dict[str, Any]] = []
        for sub_clusters in subcategorias.values():
            clusters.extend(sub_clusters)
        return clusters

    def get_variations(self, categoria: str, keyword: str) -> Dict[str, List[str]]:
        """
        Busca el clúster circular. Retorna un pack de búsqueda:
        {"tags": List[str], "exclude": List[str]}
        """
        keyword_norm = normalizar_texto(keyword or "")
        clusters = self._get_clusters(categoria)
        
        # 1. Búsqueda por Keyword (Circularidad)
        if keyword_norm:
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
        if clusters:
            all_tags = []
            for cluster in clusters:
                all_tags.extend(cluster["tags"])
            return {"tags": all_tags, "exclude": []}

        return {"tags": [], "exclude": []}

    def get_global_search_pack(self) -> Dict[str, List[str]]:
        """
        Retorna un search_pack global para escanear una sola vez toda la carpeta.
        No aplica excludes por categoría para no descartar productos válidos de otras familias.
        """
        tags_unicos = []
        vistos = set()
        for subcategorias in self._variaciones.values():
            for clusters in subcategorias.get("subcategorias", {}).values():
                for cluster in clusters:
                    for tag in cluster.get("tags", []):
                        tag_norm = normalizar_texto(tag)
                        if not tag_norm or tag_norm in vistos:
                            continue
                        vistos.add(tag_norm)
                        tags_unicos.append(tag)
        return {"tags": tags_unicos, "exclude": []}

    def matches_category(self, categoria: str, texto_producto: str) -> bool:
        """
        Determina si un texto de producto pertenece a una categoría concreta
        según sus tags y excludes.
        """
        if not categoria:
            return True

        clusters = self._get_clusters(categoria)
        if not clusters:
            return True

        texto_norm = normalizar_texto(texto_producto or "")
        if not texto_norm:
            return False

        tags: List[str] = []
        excludes: List[str] = []
        macro, _ = self._resolve_category(categoria)
        global_excludes = []
        if macro:
            global_excludes = self._variaciones.get(macro, {}).get("global_exclude", [])

        for cluster in clusters:
            tags.extend(cluster.get("tags", []))
            excludes.extend(cluster.get("exclude", []))

        excludes.extend(global_excludes)

        # Si aparece un exclude, se descarta inmediatamente.
        for exc in excludes:
            exc_norm = normalizar_texto(exc)
            if not exc_norm:
                continue
            if re.search(rf"\b{re.escape(exc_norm)}\b", texto_norm):
                return False

        for tag in tags:
            tag_norm = normalizar_texto(tag)
            if not tag_norm:
                continue
            if re.search(rf"\b{re.escape(tag_norm)}\b", texto_norm):
                return True

        return False

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
        for subcategorias in self._variaciones.values():
            for clusters in subcategorias.get("subcategorias", {}).values():
                for cluster in clusters:
                    flat_list.extend(cluster["tags"])
        return flat_list