"""Project repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Project


class ProjectRepository(ABC):
    """プロジェクトエンティティの永続化インターフェース."""

    @abstractmethod
    def find_all(self) -> List[Project]:
        """全プロジェクトを取得する.

        Returns:
            プロジェクトのリスト
        """
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Project]:
        """プロジェクト名で検索する.

        Args:
            name: プロジェクト名

        Returns:
            プロジェクト（見つからない場合は None）
        """
        pass

    @abstractmethod
    def save(self, project: Project) -> None:
        """プロジェクトを保存する.

        Args:
            project: 保存するプロジェクト
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """全プロジェクトを削除する（再インポート時に使用）."""
        pass
