"""Consumption rate calculator domain service."""

from src.domain.entities.project import Project
from src.domain.entities.work_record import WorkRecord


class ConsumptionRateCalculator:
    """工数消化率を計算するドメインサービス."""

    @staticmethod
    def calculate_rate(project: Project, work_records: list[WorkRecord]) -> float:
        """工数消化率を計算する.

        Args:
            project: プロジェクト情報
            work_records: 工数実績のリスト（全プロジェクト含む）

        Returns:
            工数消化率（0.0 〜 1.0）。契約時間が0の場合は0.0を返す。
        """
        if project.contracted_hours <= 0:
            return 0.0

        # プロジェクトに該当する工数実績をフィルタリング
        consumed_hours = sum(
            record.hours
            for record in work_records
            if record.project_name == project.name
        )

        # 消化率を計算（最大1.0）
        rate = consumed_hours / project.contracted_hours
        return min(rate, 1.0)
