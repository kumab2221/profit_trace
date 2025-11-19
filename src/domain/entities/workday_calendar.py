"""WorkdayCalendar entity."""

import re
from dataclasses import dataclass


@dataclass
class WorkdayCalendar:
    """営業日カレンダーを表すエンティティ.

    Attributes:
        year_month: 年月（"YYYY-MM" 形式）
        day: 日（1-31）
        is_workday: 営業日フラグ（True: 営業日、False: 休日）
    """

    year_month: str
    day: int
    is_workday: bool

    def __post_init__(self) -> None:
        """エンティティのバリデーションを実行する.

        Raises:
            ValueError: year_month が "YYYY-MM" 形式でない場合
            ValueError: day が 1-31 の範囲外の場合
        """
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", self.year_month):
            raise ValueError("year_month must be in YYYY-MM format")
        if not 1 <= self.day <= 31:
            raise ValueError("day must be between 1 and 31")
