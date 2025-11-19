"""Burndown calculator domain service."""

from dataclasses import dataclass
from datetime import date, timedelta

from src.domain.entities.project import Project
from src.domain.entities.work_record import WorkRecord
from src.domain.repositories.workday_calendar_repository import (
    WorkdayCalendarRepository,
)


@dataclass
class Point:
    """バーンダウンチャートのデータポイント.

    Attributes:
        date: 日付
        remaining_hours: 残工数
    """

    date: date
    remaining_hours: float


class CalculationError(Exception):
    """計算エラー."""

    pass


class BurndownCalculator:
    """バーンダウンチャートの理想線・実績線を計算するドメインサービス."""

    @staticmethod
    def calculate_ideal_line(
        project: Project, calendar: WorkdayCalendarRepository
    ) -> list[Point]:
        """理想線を計算する.

        Args:
            project: プロジェクト情報
            calendar: 営業日カレンダー

        Returns:
            理想線のデータポイントリスト

        Raises:
            CalculationError: 営業日数が0の場合
        """
        workdays = calendar.count_workdays(project.start_date, project.end_date)
        if workdays == 0:
            raise CalculationError("No workdays found in project period")

        ideal_hours_per_day = project.contracted_hours / workdays
        remaining_hours = project.contracted_hours
        points: list[Point] = []

        current_date = project.start_date
        while current_date <= project.end_date:
            if calendar.is_workday(current_date):
                remaining_hours -= ideal_hours_per_day
            points.append(Point(date=current_date, remaining_hours=remaining_hours))
            current_date += timedelta(days=1)

        return points

    @staticmethod
    def calculate_actual_line(
        project: Project,
        work_records: list[WorkRecord],
        calendar: WorkdayCalendarRepository,
    ) -> list[Point]:
        """実績線を計算する.

        Args:
            project: プロジェクト情報
            work_records: 工数実績のリスト（プロジェクトでフィルタ済み）
            calendar: 営業日カレンダー

        Returns:
            実績線のデータポイントリスト
        """
        # 日付ごとの工数を集計
        daily_hours: dict[date, float] = {}
        for record in work_records:
            if record.project_name == project.name:
                if record.date not in daily_hours:
                    daily_hours[record.date] = 0.0
                daily_hours[record.date] += record.hours

        # 実績線を計算
        remaining_hours = project.contracted_hours
        points: list[Point] = []

        current_date = project.start_date
        while current_date <= project.end_date:
            # 当日の実績工数を減算
            if current_date in daily_hours:
                remaining_hours -= daily_hours[current_date]
            points.append(Point(date=current_date, remaining_hours=remaining_hours))
            current_date += timedelta(days=1)

        return points
