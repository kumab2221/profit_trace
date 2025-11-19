"""Workload analyzer domain service."""

from dataclasses import dataclass
from datetime import date

from src.domain.entities.work_record import WorkRecord


@dataclass
class WorkloadAnalysis:
    """メンバーの稼働状況分析結果.

    Attributes:
        member_name: メンバー名
        total_hours: 総工数
        average_hours_per_day: 1日あたり平均工数
        workdays_count: 稼働日数
        max_hours_per_day: 1日最大工数
        min_hours_per_day: 1日最小工数（0を除く）
    """

    member_name: str
    total_hours: float
    average_hours_per_day: float
    workdays_count: int
    max_hours_per_day: float
    min_hours_per_day: float


class WorkloadAnalyzer:
    """メンバー別稼働状況を分析するドメインサービス."""

    @staticmethod
    def analyze_member_workload(
        member_name: str,
        work_records: list[WorkRecord],
        start_date: date,
        end_date: date,
    ) -> WorkloadAnalysis:
        """メンバーの稼働状況を分析する.

        Args:
            member_name: 分析対象のメンバー名
            work_records: 工数実績のリスト（全メンバー含む）
            start_date: 分析期間の開始日
            end_date: 分析期間の終了日

        Returns:
            稼働状況分析結果

        Raises:
            ValueError: 該当するメンバーの工数実績が存在しない場合
        """
        # メンバーの工数実績をフィルタリング
        member_records = [
            record
            for record in work_records
            if record.member_name == member_name
            and start_date <= record.date <= end_date
        ]

        if not member_records:
            raise ValueError(f"No work records found for member: {member_name}")

        # 日付ごとの工数を集計
        daily_hours: dict[date, float] = {}
        for record in member_records:
            if record.date not in daily_hours:
                daily_hours[record.date] = 0.0
            daily_hours[record.date] += record.hours

        # 統計を計算
        total_hours = sum(daily_hours.values())
        workdays_count = len(daily_hours)
        average_hours_per_day = total_hours / workdays_count if workdays_count > 0 else 0.0
        max_hours_per_day = max(daily_hours.values()) if daily_hours else 0.0
        min_hours_per_day = min(daily_hours.values()) if daily_hours else 0.0

        return WorkloadAnalysis(
            member_name=member_name,
            total_hours=total_hours,
            average_hours_per_day=average_hours_per_day,
            workdays_count=workdays_count,
            max_hours_per_day=max_hours_per_day,
            min_hours_per_day=min_hours_per_day,
        )
