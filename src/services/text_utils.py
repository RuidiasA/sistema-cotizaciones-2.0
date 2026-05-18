import re
import unicodedata
from typing import Optional

import pandas as pd


def limpiar_y_entero(val) -> int:
    try:
        if pd.isna(val):
            return 0
        s = str(val).lower().replace(",", "").strip()
        num_match = re.findall(r"\d+\.?\d*", s)
        if num_match:
            return int(float(num_match[0]))
        return 0
    except Exception:
        return 0


def limpiar_precio(val) -> float:
    try:
        if pd.isna(val):
            return 0.0
        s = (
            str(val)
            .lower()
            .replace("s/.", "")
            .replace("s/", "")
            .replace(",", "")
            .strip()
        )
        matches = re.findall(r"\d+\.?\d*", s)
        return float(matches[0]) if matches else 0.0
    except Exception:
        return 0.0


def normalizar_texto(texto: str) -> str:
    base = unicodedata.normalize("NFKD", str(texto).lower())
    sin_tildes = "".join(ch for ch in base if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", sin_tildes).strip()


def recortar_detalle(valor, max_len: int = 70) -> str:
    if pd.isna(valor):
        return ""
    texto = re.sub(r"\s+", " ", str(valor)).strip()
    if len(texto) <= max_len:
        return texto
    return texto[: max_len - 3].rstrip() + "..."


_MATERIALES_BASE = (
    "NOTEX",
    "TASLAN",
    "NYLON",
    "SOFTSHELL",
    "JERSEY",
    "LINO",
    "DRILL",
    "IMPERMEABLE",
    "ALGODON",
    "POLIESTER",
    "CATIONI",
    "LONA LABRADA",
    "LINO SERMAT",
    "TETRON",
)

_SEGMENTOS_CALIDAD = (
    "PUBLICITARIO",
    "CORPORATIVO",
    "CORPORATIVA",
)

_PALABRAS_SERVICIO = (
    "MOVILIDAD",
    "ENVIO",
    "EMBALAJE",
    "ROTULADO",
    "FLETE",
    "SERVICIO",
    "SERV",
    "DESCRIPCION"
    "DISEÑO BROCHURE",
    "DISEÑO LOGO",
    "DISEÑO REVISTA"
)

_RUIDO_ESPECIFICACION = (
    "ADICIONAL",
    "PAGO",
    "TOTAL",
    "GRANDE",
    "PEQUENO",
    "PEQUENA",
    "MEDIANO",
    "MEDIANA",
    "MODELO",
    "COLOR",
    "TIPO",
    "FABRICACION",
    "NACIONAL",
    "TALLA",
    
)


def extraer_material(texto: str) -> Optional[str]:
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return None

    for material in _MATERIALES_BASE:
        material_norm = normalizar_texto(material)
        if re.search(rf"\b{re.escape(material_norm)}\b", texto_norm):
            return material
    return None


def extraer_segmento_calidad(texto: str) -> Optional[str]:
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return None

    for segmento in _SEGMENTOS_CALIDAD:
        segmento_norm = normalizar_texto(segmento)
        if re.search(rf"\b{re.escape(segmento_norm)}s?\b", texto_norm):
            return segmento

        if segmento_norm.endswith("a"):
            plural_femenino = f"{segmento_norm[:-1]}as"
            if re.search(rf"\b{re.escape(plural_femenino)}\b", texto_norm):
                return segmento
    return None


def remover_ruido_de_especificacion(texto: str) -> str:
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return ""

    tokens = texto_norm.split()
    ruido_norm = {normalizar_texto(p) for p in _RUIDO_ESPECIFICACION}
    tokens_filtrados = [tok for tok in tokens if tok not in ruido_norm]
    return " ".join(tokens_filtrados).upper().strip()


def es_servicio_o_logistica(texto: str) -> bool:
    texto_norm = normalizar_texto(texto)
    if not texto_norm:
        return False

    for keyword in _PALABRAS_SERVICIO:
        kw_norm = normalizar_texto(keyword)
        if re.search(rf"\b{re.escape(kw_norm)}\b", texto_norm):
            return True
    return False
