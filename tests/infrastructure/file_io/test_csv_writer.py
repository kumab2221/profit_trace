"""Tests for CSVWriter."""

import tempfile
from collections.abc import Generator
from datetime import date
from pathlib import Path

import pytest

from src.domain.entities.project import Project
from src.domain.entities.work_record import WorkRecord
from src.infrastructure.file_io.csv_writer import CSVWriter


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """一時ディレクトリを提供する."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_write_projects_success(temp_dir: Path) -> None:
    """プロジェクトを CSV に正常に書き込めることを確認する."""
    projects = [
        Project(
            project_id="proj-001",
            name="Project A",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            contracted_hours=1000.0,
        ),
        Project(
            project_id="proj-002",
            name="Project B",
            start_date=date(2025, 6, 1),
            end_date=date(2025, 11, 30),
            contracted_hours=500.0,
        ),
    ]

    csv_path = temp_dir / "projects.csv"
    CSVWriter.write_projects(projects, str(csv_path))

    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "project_id,name,start_date,end_date,contracted_hours" in content
    assert "proj-001,Project A,2025-01-01,2025-12-31,1000.0" in content
    assert "proj-002,Project B,2025-06-01,2025-11-30,500.0" in content


def test_write_projects_creates_directory(temp_dir: Path) -> None:
    """存在しないディレクトリを自動作成することを確認する."""
    projects = [
        Project(
            project_id="proj-001",
            name="Project A",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            contracted_hours=1000.0,
        )
    ]

    csv_path = temp_dir / "subdir" / "projects.csv"
    CSVWriter.write_projects(projects, str(csv_path))

    assert csv_path.exists()


def test_write_projects_empty_list(temp_dir: Path) -> None:
    """空のリストでも CSV を書き込めることを確認する."""
    csv_path = temp_dir / "projects.csv"
    CSVWriter.write_projects([], str(csv_path))

    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "project_id,name,start_date,end_date,contracted_hours" in content


def test_write_work_records_success(temp_dir: Path) -> None:
    """工数実績を CSV に正常に書き込めることを確認する."""
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
            project_name="Project B",
            memo="",
        ),
    ]

    csv_path = temp_dir / "work_records.csv"
    CSVWriter.write_work_records(records, str(csv_path))

    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "record_id,date,hours,member_name,project_name,memo" in content
    assert "rec-001,2025-01-10,8.0,Alice,Project A,Task 1" in content
    assert "rec-002,2025-01-11,6.0,Bob,Project B," in content


def test_write_work_records_with_empty_memo(temp_dir: Path) -> None:
    """memo が空文字列の場合でも正常に書き込めることを確認する."""
    records = [
        WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 10),
            hours=8.0,
            member_name="Alice",
            project_name="Project A",
            memo="",
        )
    ]

    csv_path = temp_dir / "work_records.csv"
    CSVWriter.write_work_records(records, str(csv_path))

    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    # 空文字列は空として出力される
    assert "rec-001,2025-01-10,8.0,Alice,Project A," in content
