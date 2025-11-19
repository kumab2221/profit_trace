"""Member repository implementation with SQLite."""

import sqlite3

from src.domain.entities.member import Member
from src.domain.repositories.member_repository import MemberRepository


class MemberRepositoryImpl(MemberRepository):
    """メンバーリポジトリの SQLite 実装."""

    def __init__(self, db_path: str) -> None:
        """初期化.

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path

    def find_all(self) -> list[Member]:
        """全てのメンバーを取得する.

        Returns:
            メンバーのリスト
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT member_name
                FROM members
                ORDER BY member_name
                """
            )
            rows = cursor.fetchall()
            return [Member(member_name=row[0]) for row in rows]
        finally:
            conn.close()

    def find_by_name(self, name: str) -> Member | None:
        """名前でメンバーを検索する.

        Args:
            name: メンバー名

        Returns:
            メンバー（存在しない場合は None）
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT member_name
                FROM members
                WHERE member_name = ?
                """,
                (name,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Member(member_name=row[0])
        finally:
            conn.close()

    def save(self, member: Member) -> None:
        """メンバーを保存する（INSERT or IGNORE）.

        Args:
            member: 保存するメンバー
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO members (member_name)
                VALUES (?)
                ON CONFLICT(member_name) DO NOTHING
                """,
                (member.member_name,),
            )
            conn.commit()
        finally:
            conn.close()

    def delete_all(self) -> None:
        """全てのメンバーを削除する."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members")
            conn.commit()
        finally:
            conn.close()
