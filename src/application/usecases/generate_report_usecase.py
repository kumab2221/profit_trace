"""Generate report use case."""

from datetime import date

from src.application.dtos.member_workload_dto import (
    IdlePeriod,
    MemberWorkloadDTO,
    ProjectDistribution,
)
from src.application.dtos.project_dto import ProjectDTO
from src.application.dtos.report_dto import ReportDTO, ReportSummary
from src.domain.repositories.member_repository import MemberRepository
from src.domain.repositories.project_repository import ProjectRepository
from src.domain.repositories.work_record_repository import WorkRecordRepository
from src.domain.services.consumption_rate_calculator import ConsumptionRateCalculator


class GenerateReportUseCase:
    """レポート生成ユースケース."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        work_record_repo: WorkRecordRepository,
        member_repo: MemberRepository,
        calc: ConsumptionRateCalculator | None = None,
    ) -> None:
        """初期化.

        Args:
            project_repo: プロジェクトリポジトリ
            work_record_repo: 工数実績リポジトリ
            member_repo: メンバーリポジトリ
            calc: 消化率計算サービス（省略時は新規インスタンス）
        """
        self.project_repo = project_repo
        self.work_record_repo = work_record_repo
        self.member_repo = member_repo
        self.calc = calc or ConsumptionRateCalculator()

    def execute(self) -> ReportDTO:
        """レポートを生成する.

        Returns:
            レポート DTO
        """
        # プロジェクト一覧取得
        projects = self.project_repo.find_all()

        # 全工数実績取得
        all_work_records = self.work_record_repo.find_all()

        # メンバー一覧取得
        members = self.member_repo.find_all()

        # プロジェクト DTO を生成
        project_dtos: list[ProjectDTO] = []
        total_contracted_hours = 0.0
        total_consumed_hours = 0.0
        active_projects = 0

        for project in projects:
            # プロジェクトの工数実績をフィルタリング
            project_records = [
                record
                for record in all_work_records
                if record.project_name == project.name
            ]

            # 消化済み工数を計算
            consumed_hours = sum(record.hours for record in project_records)

            # 消化率を計算
            consumption_rate = self.calc.calculate_rate(project, all_work_records)

            # DTO を生成
            dto = ProjectDTO.from_entity(project, consumed_hours, consumption_rate)
            project_dtos.append(dto)

            # サマリー計算
            total_contracted_hours += project.contracted_hours
            total_consumed_hours += consumed_hours

            # 稼働中プロジェクトのカウント
            if project.is_active(date.today()):
                active_projects += 1

        # メンバー稼働状況 DTO を生成
        member_dtos: list[MemberWorkloadDTO] = []
        for member in members:
            # メンバーの工数実績を取得
            member_records = [
                record
                for record in all_work_records
                if record.member_name == member.member_name
            ]

            if not member_records:
                continue

            # 総工数を計算
            total_hours = sum(record.hours for record in member_records)

            # プロジェクト別の工数配分を計算
            project_hours: dict[str, float] = {}
            for record in member_records:
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

            # 稼働していない期間を計算（簡易版）
            idle_periods: list[IdlePeriod] = []

            member_dtos.append(
                MemberWorkloadDTO(
                    member_name=member.member_name,
                    total_hours=total_hours,
                    project_distribution=project_distribution,
                    idle_periods=idle_periods,
                )
            )

        # サマリーを生成
        overall_consumption_rate = (
            total_consumed_hours / total_contracted_hours
            if total_contracted_hours > 0
            else 0.0
        )

        summary = ReportSummary(
            total_projects=len(projects),
            active_projects=active_projects,
            total_members=len(members),
            total_contracted_hours=total_contracted_hours,
            total_consumed_hours=total_consumed_hours,
            overall_consumption_rate=overall_consumption_rate,
        )

        # レポート DTO を生成
        return ReportDTO(
            projects=project_dtos, members=member_dtos, summary=summary
        )
