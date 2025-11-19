"""WorkRecord entity."""

from dataclasses import dataclass
from datetime import date


@dataclass
class WorkRecord:
    """工数実績データを表すエンティティ.

    Attributes:
        record_id: レコード ID（UUID）
        date: 作業日
        hours: 工数（時間、小数点以下2桁）
        member_name: メンバー名
        project_name: プロジェクト名
        memo: 備考（オプション）
    """

    record_id: str
    date: date
    hours: float
    member_name: str
    project_name: str
    memo: str = ""

    def __post_init__(self) -> None:
        """エンティティのバリデーションを実行する.

        Raises:
            ValueError: hours が負数の場合
            ValueError: member_name が空文字列の場合
            ValueError: project_name が空文字列の場合
        """
        if self.hours < 0:
            raise ValueError("hours must be non-negative")
        if not self.member_name:
            raise ValueError("member_name must not be empty")
        if not self.project_name:
            raise ValueError("project_name must not be empty")
