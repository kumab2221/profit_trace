"""Get burndown chart use case."""

from datetime import date

from src.application.dtos.burndown_chart_dto import BurndownChartDTO
from src.domain.repositories.project_repository import ProjectRepository
from src.domain.repositories.work_record_repository import WorkRecordRepository
from src.domain.repositories.workday_calendar_repository import (
    WorkdayCalendarRepository,
)
from src.domain.services.burndown_calculator import BurndownCalculator


class DataNotFoundError(Exception):
    """データが見つからないエラー."""

    pass


class GetBurndownChartUseCase:
    """バーンダウンチャートデータ取得ユースケース."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        work_record_repo: WorkRecordRepository,
        calendar_repo: WorkdayCalendarRepository,
        burndown_calc: BurndownCalculator | None = None,
    ) -> None:
        """初期化.

        Args:
            project_repo: プロジェクトリポジトリ
            work_record_repo: 工数実績リポジトリ
            calendar_repo: 営業日カレンダーリポジトリ
            burndown_calc: バーンダウン計算サービス（省略時は新規インスタンス）
        """
        self.project_repo = project_repo
        self.work_record_repo = work_record_repo
        self.calendar_repo = calendar_repo
        self.burndown_calc = burndown_calc or BurndownCalculator()

    def execute(self, project_name: str) -> BurndownChartDTO:
        """バーンダウンチャートデータを取得する.

        Args:
            project_name: プロジェクト名

        Returns:
            バーンダウンチャート DTO

        Raises:
            DataNotFoundError: プロジェクトが見つからない場合
        """
        # プロジェクト取得
        project = self.project_repo.find_by_name(project_name)
        if project is None:
            raise DataNotFoundError(f"Project not found: {project_name}")

        # 工数実績取得
        work_records = self.work_record_repo.find_by_project(project_name)

        # 理想線計算
        ideal_line = self.burndown_calc.calculate_ideal_line(
            project, self.calendar_repo
        )

        # 実績線計算
        actual_line = self.burndown_calc.calculate_actual_line(
            project, work_records, self.calendar_repo
        )

        # DTO 生成
        return BurndownChartDTO(
            project_name=project_name,
            ideal_line=ideal_line,
            actual_line=actual_line,
            current_date_marker=date.today(),
        )
