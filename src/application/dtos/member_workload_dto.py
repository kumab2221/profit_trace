"""Member workload DTO for presentation layer."""

from dataclasses import dataclass
from datetime import date


@dataclass
class ProjectDistribution:
    """プロジェクト別の工数配分.

    Attributes:
        project_name: プロジェクト名
        hours: 工数（時間）
        percentage: 割合（0.0 ~ 1.0）
    """

    project_name: str
    hours: float
    percentage: float


@dataclass
class IdlePeriod:
    """稼働していない期間.

    Attributes:
        start_date: 開始日
        end_date: 終了日
        days: 日数
    """

    start_date: date
    end_date: date
    days: int


@dataclass
class MemberWorkloadDTO:
    """メンバー別稼働状況を Presentation 層に渡すための DTO.

    Attributes:
        member_name: メンバー名
        total_hours: 総工数（時間）
        project_distribution: プロジェクト別の工数配分リスト
        idle_periods: 稼働していない期間のリスト
    """

    member_name: str
    total_hours: float
    project_distribution: list[ProjectDistribution]
    idle_periods: list[IdlePeriod]
