"""Get member workload use case."""

from datetime import date, timedelta

from src.application.dtos.member_workload_dto import (
    IdlePeriod,
    MemberWorkloadDTO,
    ProjectDistribution,
)
from src.domain.repositories.work_record_repository import WorkRecordRepository
from src.domain.repositories.workday_calendar_repository import (
    WorkdayCalendarRepository,
)


class GetMemberWorkloadUseCase:
    """メンバー別稼働状況取得ユースケース."""

    def __init__(
        self,
        work_record_repo: WorkRecordRepository,
        calendar_repo: WorkdayCalendarRepository,
    ) -> None:
        """初期化.

        Args:
            work_record_repo: 工数実績リポジトリ
            calendar_repo: 営業日カレンダーリポジトリ
        """
        self.work_record_repo = work_record_repo
        self.calendar_repo = calendar_repo

    def execute(self, member_name: str) -> MemberWorkloadDTO:
        """メンバー別稼働状況を取得する.

        Args:
            member_name: メンバー名

        Returns:
            メンバー稼働状況 DTO

        Raises:
            ValueError: メンバーの工数実績が存在しない場合
        """
        # メンバーの工数実績取得
        work_records = self.work_record_repo.find_by_member(member_name)

        if not work_records:
            raise ValueError(f"No work records found for member: {member_name}")

        # 総工数を計算
        total_hours = sum(record.hours for record in work_records)

        # プロジェクト別の工数配分を計算
        project_hours: dict[str, float] = {}
        for record in work_records:
            if record.project_name not in project_hours:
                project_hours[record.project_name] = 0.0
            project_hours[record.project_name] += record.hours

        project_distribution = [
            ProjectDistribution(
                project_name=project_name,
                hours=hours,
                percentage=hours / total_hours if total_hours > 0 else 0.0,
            )
            for project_name, hours in project_hours.items()
        ]

        # 稼働していない期間を計算
        idle_periods = self._calculate_idle_periods(work_records)

        # DTO 生成
        return MemberWorkloadDTO(
            member_name=member_name,
            total_hours=total_hours,
            project_distribution=project_distribution,
            idle_periods=idle_periods,
        )

    def _calculate_idle_periods(self, work_records: list) -> list[IdlePeriod]:
        """稼働していない期間を計算する.

        Args:
            work_records: 工数実績のリスト

        Returns:
            稼働していない期間のリスト
        """
        if not work_records:
            return []

        # 稼働日を抽出してソート
        work_dates = sorted(set(record.date for record in work_records))

        if len(work_dates) < 2:
            return []

        # 連続していない期間を検出
        idle_periods: list[IdlePeriod] = []
        for i in range(len(work_dates) - 1):
            current_date = work_dates[i]
            next_date = work_dates[i + 1]

            # 2日以上の間隔がある場合
            gap_days = (next_date - current_date).days - 1
            if gap_days > 0:
                idle_start = current_date + timedelta(days=1)
                idle_end = next_date - timedelta(days=1)
                idle_periods.append(
                    IdlePeriod(
                        start_date=idle_start, end_date=idle_end, days=gap_days
                    )
                )

        return idle_periods
