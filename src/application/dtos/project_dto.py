"""Project DTO for presentation layer."""

from dataclasses import dataclass
from datetime import date

from src.domain.entities.project import Project


@dataclass
class ProjectDTO:
    """プロジェクト情報を Presentation 層に渡すための DTO.

    Attributes:
        name: プロジェクト名
        start_date: 業務開始日
        end_date: 業務終了日
        contracted_hours: 契約工数（時間）
        consumed_hours: 消化済み工数（時間）
        consumption_rate: 工数消化率（0.0 ~ 1.0以上）
        status: ステータス（"正常" / "遅延" / "余剰"）
    """

    name: str
    start_date: date
    end_date: date
    contracted_hours: float
    consumed_hours: float
    consumption_rate: float
    status: str

    @staticmethod
    def from_entity(
        project: Project, consumed_hours: float, consumption_rate: float
    ) -> "ProjectDTO":
        """エンティティから DTO を生成する.

        Args:
            project: プロジェクトエンティティ
            consumed_hours: 消化済み工数
            consumption_rate: 工数消化率

        Returns:
            ProjectDTO
        """
        # 消化率に基づいてステータスを判定（±5% 以内が正常）
        if consumption_rate < 0.95:
            status = "遅延"
        elif consumption_rate > 1.05:
            status = "余剰"
        else:
            status = "正常"

        return ProjectDTO(
            name=project.name,
            start_date=project.start_date,
            end_date=project.end_date,
            contracted_hours=project.contracted_hours,
            consumed_hours=consumed_hours,
            consumption_rate=consumption_rate,
            status=status,
        )
