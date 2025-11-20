"""Import result dataclass."""

from dataclasses import dataclass, field


@dataclass
class ImportResult:
    """インポート結果.

    Attributes:
        success: 成功フラグ
        imported_count: インポート件数
        errors: エラーメッセージのリスト
    """

    success: bool
    imported_count: int = 0
    errors: list[str] = field(default_factory=list)
