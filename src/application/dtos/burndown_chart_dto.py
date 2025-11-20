"""Burndown chart DTO for presentation layer."""

from dataclasses import dataclass
from datetime import date

from src.domain.services.burndown_calculator import Point


@dataclass
class BurndownChartDTO:
    """バーンダウンチャートデータを Presentation 層に渡すための DTO.

    Attributes:
        project_name: プロジェクト名
        ideal_line: 理想線のデータポイントリスト
        actual_line: 実績線のデータポイントリスト
        current_date_marker: 現在日付のマーカー
    """

    project_name: str
    ideal_line: list[Point]
    actual_line: list[Point]
    current_date_marker: date
