import re
import unicodedata

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


def recortar_detalle(valor, max_len: int = 40) -> str:
    if pd.isna(valor):
        return ""
    texto = re.sub(r"\s+", " ", str(valor)).strip()
    if len(texto) <= max_len:
        return texto
    return texto[: max_len - 3].rstrip() + "..."
