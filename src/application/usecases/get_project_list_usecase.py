"""Get project list use case."""

from src.application.dtos.project_dto import ProjectDTO
from src.domain.repositories.project_repository import ProjectRepository
from src.domain.repositories.work_record_repository import WorkRecordRepository
from src.domain.services.consumption_rate_calculator import ConsumptionRateCalculator


class GetProjectListUseCase:
    """プロジェクト一覧取得ユースケース."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        work_record_repo: WorkRecordRepository,
        calc: ConsumptionRateCalculator | None = None,
    ) -> None:
        """初期化.

        Args:
            project_repo: プロジェクトリポジトリ
            work_record_repo: 工数実績リポジトリ
            calc: 消化率計算サービス（省略時は新規インスタンス）
        """
        self.project_repo = project_repo
        self.work_record_repo = work_record_repo
        self.calc = calc or ConsumptionRateCalculator()

    def execute(self) -> list[ProjectDTO]:
        """プロジェクト一覧を取得する.

        Returns:
            プロジェクト DTO のリスト
        """
        # プロジェクト一覧取得
        projects = self.project_repo.find_all()

        # 全工数実績取得
        all_work_records = self.work_record_repo.find_all()

        # DTO に変換
        project_dtos: list[ProjectDTO] = []
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

        return project_dtos
