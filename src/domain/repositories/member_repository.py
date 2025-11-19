"""Member repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Member


class MemberRepository(ABC):
    """メンバーエンティティの永続化インターフェース."""

    @abstractmethod
    def find_all(self) -> List[Member]:
        """全メンバーを取得する.

        Returns:
            メンバーのリスト
        """
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Member]:
        """メンバー名で検索する.

        Args:
            name: メンバー名

        Returns:
            メンバー（見つからない場合は None）
        """
        pass

    @abstractmethod
    def save(self, member: Member) -> None:
        """メンバーを保存する.

        Args:
            member: 保存するメンバー
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """全メンバーを削除する（再インポート時に使用）."""
        pass
