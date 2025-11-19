"""Workday calendar repository implementation with SQLite."""

import sqlite3
from datetime import date

from src.domain.entities.workday_calendar import WorkdayCalendar
from src.domain.repositories.workday_calendar_repository import (
    WorkdayCalendarRepository,
)


class WorkdayCalendarRepositoryImpl(WorkdayCalendarRepository):
    """営業日カレンダーリポジトリの SQLite 実装."""

    def __init__(self, db_path: str) -> None:
        """初期化.

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path

    def find_all(self) -> list[WorkdayCalendar]:
        """全ての営業日カレンダーを取得する.

        Returns:
            営業日カレンダーのリスト
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT year_month, day, is_workday
                FROM workday_calendars
                ORDER BY year_month, day
                """
            )
            rows = cursor.fetchall()
            return [
                WorkdayCalendar(
                    year_month=row[0], day=row[1], is_workday=bool(row[2])
                )
                for row in rows
            ]
        finally:
            conn.close()

    def find_by_year_month(self, year_month: str) -> list[WorkdayCalendar]:
        """年月で営業日カレンダーを検索する.

        Args:
            year_month: 年月（"YYYY-MM" 形式）

        Returns:
            営業日カレンダーのリスト
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT year_month, day, is_workday
                FROM workday_calendars
                WHERE year_month = ?
                ORDER BY day
                """,
                (year_month,),
            )
            rows = cursor.fetchall()
            return [
                WorkdayCalendar(
                    year_month=row[0], day=row[1], is_workday=bool(row[2])
                )
                for row in rows
            ]
        finally:
            conn.close()

    def is_workday(self, target_date: date) -> bool:
        """指定日が営業日かどうか判定する.

        Args:
            target_date: 判定する日付

        Returns:
            営業日の場合 True、そうでない場合 False
        """
        year_month = target_date.strftime("%Y-%m")
        day = target_date.day

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT is_workday
                FROM workday_calendars
                WHERE year_month = ? AND day = ?
                """,
                (year_month, day),
            )
            row = cursor.fetchone()
            # データがない場合はデフォルトで営業日とする
            return bool(row[0]) if row else True
        finally:
            conn.close()

    def count_workdays(self, start_date: date, end_date: date) -> int:
        """期間内の営業日数をカウントする.

        Args:
            start_date: 開始日
            end_date: 終了日

        Returns:
            営業日数
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # 日付範囲内の全ての日付を生成してチェック
            current_date = start_date
            count = 0
            while current_date <= end_date:
                year_month = current_date.strftime("%Y-%m")
                day = current_date.day

                cursor.execute(
                    """
                    SELECT is_workday
                    FROM workday_calendars
                    WHERE year_month = ? AND day = ?
                    """,
                    (year_month, day),
                )
                row = cursor.fetchone()
                # データがない場合はデフォルトで営業日とする
                if row is None or bool(row[0]):
                    count += 1

                # 次の日へ
                from datetime import timedelta

                current_date = current_date + timedelta(days=1)

            return count
        finally:
            conn.close()

    def save_bulk(self, calendars: list[WorkdayCalendar]) -> None:
        """営業日カレンダーを一括保存する（INSERT or UPDATE）.

        Args:
            calendars: 保存する営業日カレンダーのリスト
        """
        if not calendars:
            return

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            data = [
                (calendar.year_month, calendar.day, int(calendar.is_workday))
                for calendar in calendars
            ]
            cursor.executemany(
                """
                INSERT INTO workday_calendars (year_month, day, is_workday)
                VALUES (?, ?, ?)
                ON CONFLICT(year_month, day) DO UPDATE SET
                    is_workday = excluded.is_workday
                """,
                data,
            )
            conn.commit()
        finally:
            conn.close()

    def delete_all(self) -> None:
        """全ての営業日カレンダーを削除する."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workday_calendars")
            conn.commit()
        finally:
            conn.close()
