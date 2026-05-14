from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ScanRow:
    fila_id: int
    articulo: str
    cantidad: int
    precio_prov: float
    precio_cli: float
    margen: float
    motivo: Optional[str] = None


@dataclass
class PriceStats:
    acum_gt_1000: float = 0.0
    count_gt_1000: int = 0
    acum_gt_500: float = 0.0
    count_gt_500: int = 0
    acum_rest: float = 0.0
    count_rest: int = 0

    def add_margin(self, cantidad: int, margen: float) -> None:
        if cantidad >= 1000:
            self.acum_gt_1000 += margen
            self.count_gt_1000 += 1
        elif cantidad >= 500:
            self.acum_gt_500 += margen
            self.count_gt_500 += 1
        else:
            self.acum_rest += margen
            self.count_rest += 1

    def promedio_para_cantidad(self, cantidad: int, margen_defecto: float = 35.0) -> float:
        # Definimos qué acumulador y contador usar según la cantidad solicitada
        if cantidad >= 1000:
            acum, count = self.acum_gt_1000, self.count_gt_1000
        elif cantidad >= 500:
            acum, count = self.acum_gt_500, self.count_gt_500
        else:
            acum, count = self.acum_rest, self.count_rest

        # Si hay datos para ESE rango específico, promediamos
        if count > 0:
            return round(acum / count, 2)
        
        # Si no hay datos, red de seguridad (35%)
        return margen_defecto

    def merge(self, other: "PriceStats") -> None:
        self.acum_gt_1000 += other.acum_gt_1000
        self.count_gt_1000 += other.count_gt_1000
        self.acum_gt_500 += other.acum_gt_500
        self.count_gt_500 += other.count_gt_500
        self.acum_rest += other.acum_rest
        self.count_rest += other.count_rest


@dataclass
class FileScanReport:
    file_name: str
    sheet_name: Optional[str] = None
    matched_rows: List[ScanRow] = field(default_factory=list)
    failed_rows: List[ScanRow] = field(default_factory=list)
    stats: PriceStats = field(default_factory=PriceStats)
    error_message: Optional[str] = None


@dataclass
class ArchetypeData:
    """Representa un arquetipo con métricas por tier de cantidad."""

    nombre_arquetipo: str
    categoria: str
    margen_tier_100: float = 0.0
    casos_tier_100: int = 0
    margen_tier_500: float = 0.0
    casos_tier_500: int = 0
    margen_tier_1000: float = 0.0
    casos_tier_1000: int = 0
    actualizado_en: str = ""
    confianza_general: float = 0.0


@dataclass
class BenchmarkingMatrix:
    """Matriz completa de benchmarking por categoría."""

    categoria: str
    arquetipos: List[ArchetypeData] = field(default_factory=list)
    fecha_generacion: str = ""
    total_registros_procesados: int = 0

    def get_arquetipo_por_nombre(self, nombre: str) -> Optional[ArchetypeData]:
        nombre_norm = str(nombre or "").strip().lower()
        if not nombre_norm:
            return None

        for arquetipo in self.arquetipos:
            if arquetipo.nombre_arquetipo.strip().lower() == nombre_norm:
                return arquetipo
        return None

    def get_margen_para_cantidad(self, nombre_arquetipo: str, cantidad: int) -> float:
        arquetipo = self.get_arquetipo_por_nombre(nombre_arquetipo)
        if arquetipo is None:
            return 35.0

        if cantidad >= 1000:
            return arquetipo.margen_tier_1000 if arquetipo.casos_tier_1000 > 0 else 35.0
        if cantidad >= 500:
            return arquetipo.margen_tier_500 if arquetipo.casos_tier_500 > 0 else 35.0
        return arquetipo.margen_tier_100 if arquetipo.casos_tier_100 > 0 else 35.0
