"""Factor estimator domain service."""

from dataclasses import dataclass
from datetime import date

from src.domain.entities.project import Project
from src.domain.entities.work_record import WorkRecord
from src.domain.repositories.workday_calendar_repository import (
    WorkdayCalendarRepository,
)


@dataclass
class Factor:
    """工数余剰要因.

    Attributes:
        factor_type: 要因タイプ（"early_completion", "low_workload", "holidays"など）
        description: 要因の説明
        impact_hours: 影響工数
    """

    factor_type: str
    description: str
    impact_hours: float


class FactorEstimator:
    """工数余剰要因を推定するドメインサービス."""

    @staticmethod
    def estimate_factors(
        project: Project,
        work_records: list[WorkRecord],
        calendar: WorkdayCalendarRepository,
    ) -> list[Factor]:
        """工数余剰要因を推定する.

        Args:
            project: プロジェクト情報
            work_records: 工数実績のリスト（全プロジェクト含む）
            calendar: 営業日カレンダー

        Returns:
            推定された要因のリスト
        """
        factors: list[Factor] = []

        # プロジェクトの工数実績を抽出
        project_records = [
            record for record in work_records if record.project_name == project.name
        ]

        # 消費工数を計算
        consumed_hours = sum(record.hours for record in project_records)
        remaining_hours = project.contracted_hours - consumed_hours

        # 余剰工数がない場合は空リストを返す
        if remaining_hours <= 0:
            return factors

        # 要因1: 早期完了（プロジェクト終了前に工数消化が停止）
        if project_records:
            last_work_date = max(record.date for record in project_records)
            remaining_workdays = calendar.count_workdays(
                last_work_date, project.end_date
            )
            if remaining_workdays > 0:
                # 最終作業日から終了日まで営業日がある = 早期完了の可能性
                factors.append(
                    Factor(
                        factor_type="early_completion",
                        description=f"プロジェクトが予定より早く完了した可能性（最終作業日: {last_work_date.isoformat()}）",
                        impact_hours=remaining_hours,
                    )
                )

        # 要因2: 低稼働率（営業日数に対して実績日数が少ない）
        total_workdays = calendar.count_workdays(project.start_date, project.end_date)
        actual_workdays = len(set(record.date for record in project_records))
        if actual_workdays < total_workdays * 0.7:  # 稼働率70%未満
            underutilized_days = total_workdays - actual_workdays
            estimated_impact = (
                remaining_hours * (underutilized_days / total_workdays)
                if total_workdays > 0
                else 0
            )
            factors.append(
                Factor(
                    factor_type="low_workload",
                    description=f"稼働率が低い（実績: {actual_workdays}日 / 営業日: {total_workdays}日）",
                    impact_hours=estimated_impact,
                )
            )

        # 要因3: 休日・休暇の影響
        # 実際に営業日なのに作業記録がない日数をカウント
        work_dates = set(record.date for record in project_records)
        missing_workdays = 0
        current_date = project.start_date
        while current_date <= project.end_date:
            if calendar.is_workday(current_date) and current_date not in work_dates:
                missing_workdays += 1
            current_date = date.fromordinal(current_date.toordinal() + 1)

        if missing_workdays > total_workdays * 0.3:  # 欠勤日が30%超
            estimated_impact = (
                remaining_hours * (missing_workdays / total_workdays)
                if total_workdays > 0
                else 0
            )
            factors.append(
                Factor(
                    factor_type="holidays",
                    description=f"休日・休暇の影響が大きい（未稼働営業日: {missing_workdays}日）",
                    impact_hours=estimated_impact,
                )
            )

        return factors
