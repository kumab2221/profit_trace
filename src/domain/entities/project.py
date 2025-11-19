"""Project entity."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Project:
    """プロジェクト契約情報を表すエンティティ.

    Attributes:
        project_id: プロジェクト ID（UUID）
        name: プロジェクト名
        start_date: 業務開始日
        end_date: 業務終了日
        contracted_hours: 契約工数（時間）
    """

    project_id: str
    name: str
    start_date: date
    end_date: date
    contracted_hours: float

    def __post_init__(self) -> None:
        """エンティティのバリデーションを実行する.

        Raises:
            ValueError: contracted_hours が正数でない場合
            ValueError: start_date が end_date 以降の場合
        """
        if self.contracted_hours <= 0:
            raise ValueError("contracted_hours must be positive")
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")

    def calculate_remaining_hours(self, consumed_hours: float) -> float:
        """残工数を計算する.

        Args:
            consumed_hours: 消化済み工数（時間）

        Returns:
            残工数（時間）
        """
        return self.contracted_hours - consumed_hours

    def is_active(self, current_date: date) -> bool:
        """プロジェクトが稼働中かどうかを判定する.

        Args:
            current_date: 判定対象の日付

        Returns:
            稼働中の場合 True、そうでない場合 False
        """
        return self.start_date <= current_date <= self.end_date
