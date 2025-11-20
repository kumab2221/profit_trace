"""Factor analysis DTO for presentation layer."""

from dataclasses import dataclass


@dataclass
class Factor:
    """工数余剰要因.

    Attributes:
        category: 要因カテゴリ（"休日出勤" / "深夜作業" / "複数PJ掛け持ち" / "その他"）
        description: 要因の説明
        impact_hours: 影響工数（時間）
        confidence: 確信度（0.0 ~ 1.0）
    """

    category: str
    description: str
    impact_hours: float
    confidence: float


@dataclass
class FactorAnalysisDTO:
    """工数余剰要因分析を Presentation 層に渡すための DTO.

    Attributes:
        project_name: プロジェクト名
        factors: 要因のリスト
        confidence_level: 全体的な確信度（0.0 ~ 1.0）
    """

    project_name: str
    factors: list[Factor]
    confidence_level: float
