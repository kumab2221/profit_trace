"""Test for WorkRecord entity."""

import pytest
from datetime import date

from src.domain.entities import WorkRecord


class TestWorkRecord:
    """WorkRecord エンティティのテストクラス."""

    def test_valid_work_record(self) -> None:
        """正常な工数実績を作成できることを確認."""
        record = WorkRecord(
            record_id="rec-001",
            date=date(2025, 1, 15),
            hours=8.5,
            member_name="山田太郎",
            project_name="テストプロジェクト",
            memo="通常作業",
        )
        assert record.record_id == "rec-001"
        assert record.hours == 8.5
        assert record.member_name == "山田太郎"
        assert record.project_name == "テストプロジェクト"
        assert record.memo == "通常作業"

    def test_work_record_with_default_memo(self) -> None:
        """memo がデフォルト値（空文字列）で作成できることを確認."""
        record = WorkRecord(
            record_id="rec-002",
            date=date(2025, 1, 15),
            hours=8.0,
            member_name="山田太郎",
            project_name="テストプロジェクト",
        )
        assert record.memo == ""

    def test_hours_must_be_non_negative(self) -> None:
        """hours が負数の場合に ValueError を発生させることを確認."""
        with pytest.raises(ValueError, match="hours must be non-negative"):
            WorkRecord(
                record_id="rec-003",
                date=date(2025, 1, 15),
                hours=-1.0,
                member_name="山田太郎",
                project_name="テストプロジェクト",
            )

    def test_member_name_must_not_be_empty(self) -> None:
        """member_name が空文字列の場合に ValueError を発生させることを確認."""
        with pytest.raises(ValueError, match="member_name must not be empty"):
            WorkRecord(
                record_id="rec-004",
                date=date(2025, 1, 15),
                hours=8.0,
                member_name="",
                project_name="テストプロジェクト",
            )

    def test_project_name_must_not_be_empty(self) -> None:
        """project_name が空文字列の場合に ValueError を発生させることを確認."""
        with pytest.raises(ValueError, match="project_name must not be empty"):
            WorkRecord(
                record_id="rec-005",
                date=date(2025, 1, 15),
                hours=8.0,
                member_name="山田太郎",
                project_name="",
            )

    def test_hours_can_be_zero(self) -> None:
        """hours が 0 の場合も有効であることを確認."""
        record = WorkRecord(
            record_id="rec-006",
            date=date(2025, 1, 15),
            hours=0.0,
            member_name="山田太郎",
            project_name="テストプロジェクト",
        )
        assert record.hours == 0.0
