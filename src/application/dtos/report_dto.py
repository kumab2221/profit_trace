"""Report DTO for presentation layer."""

from dataclasses import dataclass

from src.application.dtos.member_workload_dto import MemberWorkloadDTO
from src.application.dtos.project_dto import ProjectDTO


@dataclass
class ReportSummary:
    """レポートのサマリー情報.

    Attributes:
        total_projects: 総プロジェクト数
        active_projects: 稼働中プロジェクト数
        total_members: 総メンバー数
        total_contracted_hours: 総契約工数（時間）
        total_consumed_hours: 総消化工数（時間）
        overall_consumption_rate: 全体の工数消化率（0.0 ~ 1.0以上）
    """

    total_projects: int
    active_projects: int
    total_members: int
    total_contracted_hours: float
    total_consumed_hours: float
    overall_consumption_rate: float


@dataclass
class ReportDTO:
    """レポートデータを Presentation 層に渡すための DTO.

    Attributes:
        projects: プロジェクト情報のリスト
        members: メンバー別稼働状況のリスト
        summary: サマリー情報
    """

    projects: list[ProjectDTO]
    members: list[MemberWorkloadDTO]
    summary: ReportSummary
