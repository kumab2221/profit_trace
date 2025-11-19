"""WorkdayCalendar repository interface."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from ..entities import WorkdayCalendar


class WorkdayCalendarRepository(ABC):
    """営業日カレンダーエンティティの永続化インターフェース."""

    @abstractmethod
    def find_all(self) -> List[WorkdayCalendar]:
        """全営業日カレンダーを取得する.

        Returns:
            営業日カレンダーのリスト
        """
        pass

    @abstractmethod
    def find_by_year_month(self, year_month: str) -> List[WorkdayCalendar]:
        """年月で営業日カレンダーを検索する.

        Args:
            year_month: 年月（"YYYY-MM" 形式）

        Returns:
            営業日カレンダーのリスト
        """
        pass

    @abstractmethod
    def is_workday(self, target_date: date) -> bool:
        """指定日が営業日かどうかを判定する.

        Args:
            target_date: 判定対象の日付

        Returns:
            営業日の場合 True、そうでない場合 False
        """
        pass

    @abstractmethod
    def count_workdays(self, start: date, end: date) -> int:
        """期間内の営業日数を計算する.

        Args:
            start: 開始日
            end: 終了日

        Returns:
            営業日数
        """
        pass

    @abstractmethod
    def save_bulk(self, calendars: List[WorkdayCalendar]) -> None:
        """営業日カレンダーを一括保存する.

        Args:
            calendars: 保存する営業日カレンダーのリスト
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """全営業日カレンダーを削除する（再インポート時に使用）."""
        pass
