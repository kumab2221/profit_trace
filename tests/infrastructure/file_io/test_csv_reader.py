"""Tests for CSVReader."""

import tempfile
from collections.abc import Generator
from datetime import date
from pathlib import Path

import pytest

from src.infrastructure.file_io.csv_reader import CSVReader


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """一時ディレクトリを提供する."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_read_projects_success(temp_dir: Path) -> None:
    """プロジェクト CSV を正常に読み込めることを確認する."""
    csv_path = temp_dir / "projects.csv"
    csv_path.write_text(
        "project_id,name,start_date,end_date,contracted_hours\n"
        "proj-001,Project A,2025-01-01,2025-12-31,1000.0\n"
        "proj-002,Project B,2025-06-01,2025-11-30,500.0\n",
        encoding="utf-8",
    )

    projects = CSVReader.read_projects(str(csv_path))

    assert len(projects) == 2
    assert projects[0].project_id == "proj-001"
    assert projects[0].name == "Project A"
    assert projects[0].start_date == date(2025, 1, 1)
    assert projects[0].end_date == date(2025, 12, 31)
    assert projects[0].contracted_hours == 1000.0


def test_read_projects_file_not_found() -> None:
    """存在しないファイルを読み込もうとした場合に例外が発生することを確認する."""
    with pytest.raises(FileNotFoundError):
        CSVReader.read_projects("nonexistent.csv")


def test_read_projects_missing_column(temp_dir: Path) -> None:
    """必須カラムが欠けている場合に例外が発生することを確認する."""
    csv_path = temp_dir / "projects.csv"
    csv_path.write_text(
        "project_id,name,start_date\n" "proj-001,Project A,2025-01-01\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required column"):
        CSVReader.read_projects(str(csv_path))


def test_read_projects_invalid_date(temp_dir: Path) -> None:
    """日付フォーマットが不正な場合に例外が発生することを確認する."""
    csv_path = temp_dir / "projects.csv"
    csv_path.write_text(
        "project_id,name,start_date,end_date,contracted_hours\n"
        "proj-001,Project A,invalid-date,2025-12-31,1000.0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid data format"):
        CSVReader.read_projects(str(csv_path))


def test_read_work_records_success(temp_dir: Path) -> None:
    """工数実績 CSV を正常に読み込めることを確認する."""
    csv_path = temp_dir / "work_records.csv"
    csv_path.write_text(
        "record_id,date,hours,member_name,project_name,memo\n"
        "rec-001,2025-01-10,8.0,Alice,Project A,Task 1\n"
        "rec-002,2025-01-11,6.0,Bob,Project B,\n",
        encoding="utf-8",
    )

    records = CSVReader.read_work_records(str(csv_path))

    assert len(records) == 2
    assert records[0].record_id == "rec-001"
    assert records[0].date == date(2025, 1, 10)
    assert records[0].hours == 8.0
    assert records[0].member_name == "Alice"
    assert records[0].project_name == "Project A"
    assert records[0].memo == "Task 1"
    assert records[1].memo == ""


def test_read_work_records_file_not_found() -> None:
    """存在しないファイルを読み込もうとした場合に例外が発生することを確認する."""
    with pytest.raises(FileNotFoundError):
        CSVReader.read_work_records("nonexistent.csv")


def test_read_work_records_invalid_hours(temp_dir: Path) -> None:
    """時間が不正な場合に例外が発生することを確認する."""
    csv_path = temp_dir / "work_records.csv"
    csv_path.write_text(
        "record_id,date,hours,member_name,project_name,memo\n"
        "rec-001,2025-01-10,invalid,Alice,Project A,Task 1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid data format"):
        CSVReader.read_work_records(str(csv_path))
