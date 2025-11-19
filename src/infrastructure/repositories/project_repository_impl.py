"""Project repository implementation with SQLite."""

import sqlite3
from datetime import date

from src.domain.entities.project import Project
from src.domain.repositories.project_repository import ProjectRepository


class ProjectRepositoryImpl(ProjectRepository):
    """プロジェクトリポジトリの SQLite 実装."""

    def __init__(self, db_path: str) -> None:
        """初期化.

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path

    def find_all(self) -> list[Project]:
        """全てのプロジェクトを取得する.

        Returns:
            プロジェクトのリスト
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT project_id, name, start_date, end_date, contracted_hours
                FROM projects
                ORDER BY start_date DESC
                """
            )
            rows = cursor.fetchall()
            return [
                Project(
                    project_id=row[0],
                    name=row[1],
                    start_date=date.fromisoformat(row[2]),
                    end_date=date.fromisoformat(row[3]),
                    contracted_hours=row[4],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def find_by_name(self, name: str) -> Project | None:
        """名前でプロジェクトを検索する.

        Args:
            name: プロジェクト名

        Returns:
            プロジェクト（存在しない場合は None）
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT project_id, name, start_date, end_date, contracted_hours
                FROM projects
                WHERE name = ?
                """,
                (name,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Project(
                project_id=row[0],
                name=row[1],
                start_date=date.fromisoformat(row[2]),
                end_date=date.fromisoformat(row[3]),
                contracted_hours=row[4],
            )
        finally:
            conn.close()

    def save(self, project: Project) -> None:
        """プロジェクトを保存する（INSERT or UPDATE）.

        Args:
            project: 保存するプロジェクト
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO projects (project_id, name, start_date, end_date, contracted_hours)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    name = excluded.name,
                    start_date = excluded.start_date,
                    end_date = excluded.end_date,
                    contracted_hours = excluded.contracted_hours
                """,
                (
                    project.project_id,
                    project.name,
                    project.start_date.isoformat(),
                    project.end_date.isoformat(),
                    project.contracted_hours,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def delete_all(self) -> None:
        """全てのプロジェクトを削除する."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects")
            conn.commit()
        finally:
            conn.close()
