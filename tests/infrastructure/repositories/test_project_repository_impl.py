"""Tests for ProjectRepositoryImpl."""

import tempfile
from collections.abc import Generator
from datetime import date
from pathlib import Path

import pytest

from src.domain.entities.project import Project
from src.infrastructure.database.initializer import DatabaseInitializer
from src.infrastructure.repositories.project_repository_impl import (
    ProjectRepositoryImpl,
)


@pytest.fixture
def db_path() -> Generator[str, None, None]:
    """一時的なデータベースパスを提供する."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test.db"
        yield str(db_file)


@pytest.fixture
def repository(db_path: str) -> ProjectRepositoryImpl:
    """テスト用のリポジトリインスタンスを提供する."""
    DatabaseInitializer.initialize_database(db_path)
    return ProjectRepositoryImpl(db_path)


def test_save_and_find_by_name(repository: ProjectRepositoryImpl) -> None:
    """プロジェクトを保存して名前で検索できることを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        contracted_hours=1000.0,
    )

    repository.save(project)
    result = repository.find_by_name("Test Project")

    assert result is not None
    assert result.project_id == "proj-001"
    assert result.name == "Test Project"
    assert result.start_date == date(2025, 1, 1)
    assert result.end_date == date(2025, 12, 31)
    assert result.contracted_hours == 1000.0


def test_find_by_name_not_found(repository: ProjectRepositoryImpl) -> None:
    """存在しないプロジェクト名で検索した場合Noneを返すことを確認する."""
    result = repository.find_by_name("NonExistent")
    assert result is None


def test_find_all(repository: ProjectRepositoryImpl) -> None:
    """全てのプロジェクトを取得できることを確認する."""
    project1 = Project(
        project_id="proj-001",
        name="Project A",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 6, 30),
        contracted_hours=500.0,
    )
    project2 = Project(
        project_id="proj-002",
        name="Project B",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 12, 31),
        contracted_hours=800.0,
    )

    repository.save(project1)
    repository.save(project2)

    results = repository.find_all()
    assert len(results) == 2
    # 開始日の降順でソートされているはず
    assert results[0].name == "Project B"
    assert results[1].name == "Project A"


def test_save_update(repository: ProjectRepositoryImpl) -> None:
    """既存のプロジェクトを更新できることを確認する."""
    project = Project(
        project_id="proj-001",
        name="Original Name",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        contracted_hours=1000.0,
    )
    repository.save(project)

    # 同じproject_idで更新
    updated_project = Project(
        project_id="proj-001",
        name="Updated Name",
        start_date=date(2025, 2, 1),
        end_date=date(2025, 11, 30),
        contracted_hours=1200.0,
    )
    repository.save(updated_project)

    result = repository.find_by_name("Updated Name")
    assert result is not None
    assert result.project_id == "proj-001"
    assert result.contracted_hours == 1200.0

    # 古い名前では見つからない
    assert repository.find_by_name("Original Name") is None


def test_delete_all(repository: ProjectRepositoryImpl) -> None:
    """全てのプロジェクトを削除できることを確認する."""
    project = Project(
        project_id="proj-001",
        name="Test Project",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        contracted_hours=1000.0,
    )
    repository.save(project)

    repository.delete_all()
    results = repository.find_all()
    assert len(results) == 0
