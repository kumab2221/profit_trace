"""Test for Project entity."""

import pytest
from datetime import date

from src.domain.entities import Project


class TestProject:
    """Project エンティティのテストクラス."""

    def test_valid_project(self) -> None:
        """正常なプロジェクトを作成できることを確認."""
        project = Project(
            project_id="test-001",
            name="テストプロジェクト",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            contracted_hours=1000.0,
        )
        assert project.project_id == "test-001"
        assert project.name == "テストプロジェクト"
        assert project.contracted_hours == 1000.0

    def test_contracted_hours_must_be_positive(self) -> None:
        """contracted_hours が正数でない場合に ValueError を発生させることを確認."""
        with pytest.raises(ValueError, match="contracted_hours must be positive"):
            Project(
                project_id="test-002",
                name="無効なプロジェクト",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                contracted_hours=0.0,
            )

        with pytest.raises(ValueError, match="contracted_hours must be positive"):
            Project(
                project_id="test-003",
                name="無効なプロジェクト",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                contracted_hours=-100.0,
            )

    def test_start_date_must_be_before_end_date(self) -> None:
        """start_date が end_date 以降の場合に ValueError を発生させることを確認."""
        with pytest.raises(ValueError, match="start_date must be before end_date"):
            Project(
                project_id="test-004",
                name="無効なプロジェクト",
                start_date=date(2025, 12, 31),
                end_date=date(2025, 1, 1),
                contracted_hours=1000.0,
            )

        with pytest.raises(ValueError, match="start_date must be before end_date"):
            Project(
                project_id="test-005",
                name="無効なプロジェクト",
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 1),
                contracted_hours=1000.0,
            )

    def test_calculate_remaining_hours(self) -> None:
        """残工数を正しく計算できることを確認."""
        project = Project(
            project_id="test-006",
            name="テストプロジェクト",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            contracted_hours=1000.0,
        )
        assert project.calculate_remaining_hours(300.0) == 700.0
        assert project.calculate_remaining_hours(1000.0) == 0.0
        assert project.calculate_remaining_hours(0.0) == 1000.0

    def test_is_active(self) -> None:
        """プロジェクトが稼働中かどうかを正しく判定できることを確認."""
        project = Project(
            project_id="test-007",
            name="テストプロジェクト",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            contracted_hours=1000.0,
        )
        assert project.is_active(date(2025, 6, 1)) is True
        assert project.is_active(date(2025, 1, 1)) is True
        assert project.is_active(date(2025, 12, 31)) is True
        assert project.is_active(date(2024, 12, 31)) is False
        assert project.is_active(date(2026, 1, 1)) is False
