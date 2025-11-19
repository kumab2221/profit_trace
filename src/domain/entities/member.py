"""Member entity."""

from dataclasses import dataclass


@dataclass
class Member:
    """メンバー情報を表すエンティティ.

    Attributes:
        member_name: メンバー名
    """

    member_name: str

    def __post_init__(self) -> None:
        """エンティティのバリデーションを実行する.

        Raises:
            ValueError: member_name が空文字列の場合
        """
        if not self.member_name:
            raise ValueError("member_name must not be empty")
