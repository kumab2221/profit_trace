"""Import project use case."""

import logging
import uuid
from pathlib import Path

import pandas as pd

from src.application.dtos.import_result import ImportResult
from src.domain.entities.project import Project
from src.domain.repositories.project_repository import ProjectRepository


class ImportProjectUseCase:
    """プロジェクト契約情報の CSV インポートユースケース."""

    def __init__(
        self, project_repo: ProjectRepository, logger: logging.Logger | None = None
    ) -> None:
        """初期化.

        Args:
            project_repo: プロジェクトリポジトリ
            logger: ロガー（省略時は標準ロガー）
        """
        self.project_repo = project_repo
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, file_path: str | Path) -> ImportResult:
        """プロジェクト契約情報の CSV インポート.

        Args:
            file_path: CSV ファイルパス

        Returns:
            ImportResult: インポート結果
        """
        try:
            # CSV 読み込み
            df = pd.read_csv(file_path, encoding="utf-8")

            # バリデーション
            validation_result = self._validate_format(df)
            if not validation_result.success:
                self.logger.error(f"Validation failed: {validation_result.errors}")
                return validation_result

            # エンティティ生成
            projects: list[Project] = []
            for _, row in df.iterrows():
                try:
                    project = Project(
                        project_id=str(uuid.uuid4()),
                        name=str(row["プロジェクト"]),
                        start_date=pd.to_datetime(row["開始日"]).date(),
                        end_date=pd.to_datetime(row["終了日"]).date(),
                        contracted_hours=float(row["工数"]),
                    )
                    projects.append(project)
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Skipped invalid row: {row}, error: {e}")

            # 既存データ削除
            self.project_repo.delete_all()

            # 新しいデータ保存
            for project in projects:
                self.project_repo.save(project)

            self.logger.info(f"Imported {len(projects)} projects")
            return ImportResult(success=True, imported_count=len(projects))

        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return ImportResult(
                success=False, errors=[f"ファイルが見つかりません: {file_path}"]
            )
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return ImportResult(
                success=False, errors=[f"予期しないエラーが発生しました: {e}"]
            )

    def _validate_format(self, df: pd.DataFrame) -> ImportResult:
        """CSV フォーマットのバリデーション.

        Args:
            df: pandas DataFrame

        Returns:
            ImportResult: バリデーション結果
        """
        required_columns = ["プロジェクト", "開始日", "終了日", "工数"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return ImportResult(
                success=False,
                errors=[f"必須列が不足しています: {', '.join(missing_columns)}"],
            )

        # 日付フォーマットチェック
        try:
            pd.to_datetime(df["開始日"])
            pd.to_datetime(df["終了日"])
        except Exception as e:
            return ImportResult(
                success=False, errors=[f"日付フォーマットが不正です: {e}"]
            )

        # 工数の数値チェック
        if not pd.to_numeric(df["工数"], errors="coerce").notna().all():
            return ImportResult(
                success=False, errors=["工数が数値ではない行があります"]
            )

        return ImportResult(success=True)
