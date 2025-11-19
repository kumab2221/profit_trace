"""Work record repository implementation with SQLite."""

import sqlite3
from datetime import date

from src.domain.entities.work_record import WorkRecord
from src.domain.repositories.work_record_repository import WorkRecordRepository


class WorkRecordRepositoryImpl(WorkRecordRepository):
    """工数実績リポジトリの SQLite 実装."""

    def __init__(self, db_path: str) -> None:
        """初期化.

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path

    def find_all(self) -> list[WorkRecord]:
        """全ての工数実績を取得する.

        Returns:
            工数実績のリスト
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT record_id, date, hours, member_name, project_name, memo
                FROM work_records
                ORDER BY date DESC
                """
            )
            rows = cursor.fetchall()
            return [
                WorkRecord(
                    record_id=row[0],
                    date=date.fromisoformat(row[1]),
                    hours=row[2],
                    member_name=row[3],
                    project_name=row[4],
                    memo=row[5],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def find_by_project(self, project_name: str) -> list[WorkRecord]:
        """プロジェクト名で工数実績を検索する.

        Args:
            project_name: プロジェクト名

        Returns:
            工数実績のリスト
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT record_id, date, hours, member_name, project_name, memo
                FROM work_records
                WHERE project_name = ?
                ORDER BY date DESC
                """,
                (project_name,),
            )
            rows = cursor.fetchall()
            return [
                WorkRecord(
                    record_id=row[0],
                    date=date.fromisoformat(row[1]),
                    hours=row[2],
                    member_name=row[3],
                    project_name=row[4],
                    memo=row[5],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def find_by_member(self, member_name: str) -> list[WorkRecord]:
        """メンバー名で工数実績を検索する.

        Args:
            member_name: メンバー名

        Returns:
            工数実績のリスト
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT record_id, date, hours, member_name, project_name, memo
                FROM work_records
                WHERE member_name = ?
                ORDER BY date DESC
                """,
                (member_name,),
            )
            rows = cursor.fetchall()
            return [
                WorkRecord(
                    record_id=row[0],
                    date=date.fromisoformat(row[1]),
                    hours=row[2],
                    member_name=row[3],
                    project_name=row[4],
                    memo=row[5],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def find_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[WorkRecord]:
        """日付範囲で工数実績を検索する.

        Args:
            start_date: 開始日
            end_date: 終了日

        Returns:
            工数実績のリスト
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT record_id, date, hours, member_name, project_name, memo
                FROM work_records
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
                """,
                (start_date.isoformat(), end_date.isoformat()),
            )
            rows = cursor.fetchall()
            return [
                WorkRecord(
                    record_id=row[0],
                    date=date.fromisoformat(row[1]),
                    hours=row[2],
                    member_name=row[3],
                    project_name=row[4],
                    memo=row[5],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def save_bulk(self, records: list[WorkRecord]) -> None:
        """工数実績を一括保存する（INSERT or UPDATE）.

        Args:
            records: 保存する工数実績のリスト
        """
        if not records:
            return

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            data = [
                (
                    record.record_id,
                    record.date.isoformat(),
                    record.hours,
                    record.member_name,
                    record.project_name,
                    record.memo,
                )
                for record in records
            ]
            cursor.executemany(
                """
                INSERT INTO work_records (record_id, date, hours, member_name, project_name, memo)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    date = excluded.date,
                    hours = excluded.hours,
                    member_name = excluded.member_name,
                    project_name = excluded.project_name,
                    memo = excluded.memo
                """,
                data,
            )
            conn.commit()
        finally:
            conn.close()

    def delete_all(self) -> None:
        """全ての工数実績を削除する."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM work_records")
            conn.commit()
        finally:
            conn.close()
