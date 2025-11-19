"""Test for Member entity."""

import pytest

from src.domain.entities import Member


class TestMember:
    """Member エンティティのテストクラス."""

    def test_valid_member(self) -> None:
        """正常なメンバーを作成できることを確認."""
        member = Member(member_name="山田太郎")
        assert member.member_name == "山田太郎"

    def test_member_name_must_not_be_empty(self) -> None:
        """member_name が空文字列の場合に ValueError を発生させることを確認."""
        with pytest.raises(ValueError, match="member_name must not be empty"):
            Member(member_name="")
