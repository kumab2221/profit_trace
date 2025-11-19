"""Tests for MemberRepositoryImpl."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from src.domain.entities.member import Member
from src.infrastructure.database.initializer import DatabaseInitializer
from src.infrastructure.repositories.member_repository_impl import (
    MemberRepositoryImpl,
)


@pytest.fixture
def db_path() -> Generator[str, None, None]:
    """一時的なデータベースパスを提供する."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test.db"
        yield str(db_file)


@pytest.fixture
def repository(db_path: str) -> MemberRepositoryImpl:
    """テスト用のリポジトリインスタンスを提供する."""
    DatabaseInitializer.initialize_database(db_path)
    return MemberRepositoryImpl(db_path)


def test_save_and_find_by_name(repository: MemberRepositoryImpl) -> None:
    """メンバーを保存して名前で検索できることを確認する."""
    member = Member(member_name="Alice")
    repository.save(member)

    result = repository.find_by_name("Alice")
    assert result is not None
    assert result.member_name == "Alice"


def test_find_by_name_not_found(repository: MemberRepositoryImpl) -> None:
    """存在しないメンバー名で検索した場合Noneを返すことを確認する."""
    result = repository.find_by_name("NonExistent")
    assert result is None


def test_find_all(repository: MemberRepositoryImpl) -> None:
    """全てのメンバーを取得できることを確認する."""
    members = [
        Member(member_name="Alice"),
        Member(member_name="Bob"),
        Member(member_name="Charlie"),
    ]
    for member in members:
        repository.save(member)

    results = repository.find_all()
    assert len(results) == 3
    # 名前順でソートされているはず
    assert results[0].member_name == "Alice"
    assert results[1].member_name == "Bob"
    assert results[2].member_name == "Charlie"


def test_save_duplicate(repository: MemberRepositoryImpl) -> None:
    """重複したメンバー名を保存しても問題ないことを確認する."""
    member = Member(member_name="Alice")
    repository.save(member)
    repository.save(member)  # 2回目の保存はIGNOREされる

    results = repository.find_all()
    assert len(results) == 1


def test_delete_all(repository: MemberRepositoryImpl) -> None:
    """全てのメンバーを削除できることを確認する."""
    member = Member(member_name="Alice")
    repository.save(member)

    repository.delete_all()
    results = repository.find_all()
    assert len(results) == 0
