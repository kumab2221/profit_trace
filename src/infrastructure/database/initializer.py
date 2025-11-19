"""Database initializer for SQLite."""

import sqlite3
from pathlib import Path


class DatabaseInitializer:
    """SQLite データベースの初期化クラス."""

    @staticmethod
    def initialize_database(db_path: str) -> None:
        """データベースを初期化する（テーブルとインデックスを作成）.

        Args:
            db_path: データベースファイルのパス
        """
        # データベースファイルのディレクトリを作成
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        try:
            DatabaseInitializer.create_tables(conn)
            DatabaseInitializer.create_indexes(conn)
        finally:
            conn.close()

    @staticmethod
    def create_tables(conn: sqlite3.Connection) -> None:
        """テーブルを作成する.

        Args:
            conn: SQLite コネクション
        """
        cursor = conn.cursor()

        # プロジェクトテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            contracted_hours REAL NOT NULL
        )
        """)

        # 工数実績テーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_records (
            record_id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            hours REAL NOT NULL,
            member_name TEXT NOT NULL,
            project_name TEXT NOT NULL,
            memo TEXT,
            FOREIGN KEY (project_name) REFERENCES projects(name)
        )
        """)

        # 営業日カレンダーテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS workday_calendars (
            year_month TEXT NOT NULL,
            day INTEGER NOT NULL,
            is_workday INTEGER NOT NULL,
            PRIMARY KEY (year_month, day)
        )
        """)

        # メンバーテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_name TEXT PRIMARY KEY
        )
        """)

        conn.commit()

    @staticmethod
    def create_indexes(conn: sqlite3.Connection) -> None:
        """インデックスを作成する（パフォーマンス最適化）.

        Args:
            conn: SQLite コネクション
        """
        cursor = conn.cursor()

        # 工数実績テーブルのインデックス
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_work_records_project
        ON work_records(project_name)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_work_records_member
        ON work_records(member_name)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_work_records_date
        ON work_records(date)
        """)

        conn.commit()
