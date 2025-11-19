"""Tests for WorkRecordRepositoryImpl."""

import tempfile
from collections.abc import Generator
from datetime import date
from pathlib import Path

import pytest

from src.domain.entities.work_record import WorkRecord
from src.infrastructure.database.initializer import DatabaseInitializer
from src.infrastructure.repositories.work_record_repository_impl import (
    WorkRecordRepositoryImpl,
)


@pytest.fixture
def db_path() -> Generator[str, None, None]:
    """一時的なデータベースパスを提供する."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test.db"
        yield str(db_file)


@pytest.fixture
def repository(db_path: str) -> WorkRecordRepositoryImpl:
    """テスト用のリポジトリインスタンスを提供する."""
    DatabaseInitializer.initialize_database(db_path)
    return WorkRecordRepositoryImpl(db_path)


def test_save_bulk_and_find_by_project(
    repository: WorkRecordRepositoryImpl,
) -> None:
    """工数実績を一括保存してプロジェクトで検索できることを確認する."""
    records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 10),
            hours=8.0,
            member_name="Alice",
            project_name="Project A",
            memo="Task 1",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 11),
            hours=6.0,
            member_name="Bob",
            project_name="Project A",
            memo="Task 2",
        ),
    ]

    repository.save_bulk(records)
    results = repository.find_by_project("Project A")

    assert len(results) == 2
    # 日付の降順でソートされているはず
    assert results[0].record_id == "rec-002"
    assert results[1].record_id == "rec-001"


def test_find_by_member(repository: WorkRecordRepositoryImpl) -> None:
    """メンバーで工数実績を検索できることを確認する."""
    records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 10),
            hours=8.0,
            member_name="Alice",
            project_name="Project A",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 11),
            hours=6.0,
            member_name="Alice",
            project_name="Project B",
        ),
    ]

    repository.save_bulk(records)
    results = repository.find_by_member("Alice")

    assert len(results) == 2
    assert all(r.member_name == "Alice" for r in results)


def test_find_by_date_range(repository: WorkRecordRepositoryImpl) -> None:
    """日付範囲で工数実績を検索できることを確認する."""
    records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 5),
            hours=8.0,
            member_name="Alice",
            project_name="Project A",
        ),
        WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 10),
            hours=6.0,
            member_name="Bob",
            project_name="Project A",
        ),
        WorkRecord(
            record_id="rec-003",
            date=date(2025, 1, 15),
            hours=7.0,
            member_name="Charlie",
            project_name="Project A",
        ),
    ]

    repository.save_bulk(records)
    results = repository.find_by_date_range(date(2025, 1, 8), date(2025, 1, 12))

    assert len(results) == 1
    assert results[0].record_id == "rec-002"


def test_save_bulk_update(repository: WorkRecordRepositoryImpl) -> None:
    """既存の工数実績を更新できることを確認する."""
    record = WorkRecord(
        record_id="rec-001",
        date=date(2025, 1, 10),
        hours=8.0,
        member_name="Alice",
        project_name="Project A",
        memo="Original",
    )
    repository.save_bulk([record])

    # 同じrecord_idで更新
    updated_record = WorkRecord(
        record_id="rec-001",
        date=date(2025, 1, 10),
        hours=10.0,
        member_name="Alice",
        project_name="Project A",
        memo="Updated",
    )
    repository.save_bulk([updated_record])

    results = repository.find_by_project("Project A")
    assert len(results) == 1
    assert results[0].hours == 10.0
    assert results[0].memo == "Updated"


def test_delete_all(repository: WorkRecordRepositoryImpl) -> None:
    """全ての工数実績を削除できることを確認する."""
    record = WorkRecord(
        record_id="rec-001",
        date=date(2025, 1, 10),
        hours=8.0,
        member_name="Alice",
        project_name="Project A",
    )
    repository.save_bulk([record])

    repository.delete_all()
    results = repository.find_by_project("Project A")
    assert len(results) == 0


def test_save_bulk_empty_list(repository: WorkRecordRepositoryImpl) -> None:
    """空のリストを保存しても問題ないことを確認する."""
    repository.save_bulk([])
    results = repository.find_by_project("Project A")
    assert len(results) == 0
