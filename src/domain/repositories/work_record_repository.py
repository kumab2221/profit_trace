"""WorkRecord repository interface."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from ..entities import WorkRecord


class WorkRecordRepository(ABC):
    """工数実績エンティティの永続化インターフェース."""

    @abstractmethod
    def find_all(self) -> List[WorkRecord]:
        """全工数実績を取得する.

        Returns:
            工数実績のリスト
        """
        pass

    @abstractmethod
    def find_by_project(self, project_name: str) -> List[WorkRecord]:
        """プロジェクト名で工数実績を検索する.

        Args:
            project_name: プロジェクト名

        Returns:
            工数実績のリスト
        """
        pass

    @abstractmethod
    def find_by_member(self, member_name: str) -> List[WorkRecord]:
        """メンバー名で工数実績を検索する.

        Args:
            member_name: メンバー名

        Returns:
            工数実績のリスト
        """
        pass

    @abstractmethod
    def find_by_date_range(self, start: date, end: date) -> List[WorkRecord]:
        """日付範囲で工数実績を検索する.

        Args:
            start: 開始日
            end: 終了日

        Returns:
            工数実績のリスト
        """
        pass

    @abstractmethod
    def save_bulk(self, records: List[WorkRecord]) -> None:
        """工数実績を一括保存する（パフォーマンス最適化）.

        Args:
            records: 保存する工数実績のリスト
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """全工数実績を削除する（再インポート時に使用）."""
        pass
