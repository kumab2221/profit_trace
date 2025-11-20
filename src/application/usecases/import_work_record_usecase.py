"""Import work record use case."""

import logging
import uuid
from pathlib import Path

import pandas as pd

from src.application.dtos.import_result import ImportResult
from src.domain.entities.member import Member
from src.domain.entities.work_record import WorkRecord
from src.domain.repositories.member_repository import MemberRepository
from src.domain.repositories.work_record_repository import WorkRecordRepository


class ImportWorkRecordUseCase:
    """工数実績データの CSV インポートユースケース."""

    def __init__(
        self,
        work_record_repo: WorkRecordRepository,
        member_repo: MemberRepository,
        logger: logging.Logger | None = None,
    ) -> None:
        """初期化.

        Args:
            work_record_repo: 工数実績リポジトリ
            member_repo: メンバーリポジトリ
            logger: ロガー（省略時は標準ロガー）
        """
        self.work_record_repo = work_record_repo
        self.member_repo = member_repo
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, file_path: str | Path) -> ImportResult:
        """工数実績データの CSV インポート.

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
            work_records: list[WorkRecord] = []
            member_names: set[str] = set()

            for _, row in df.iterrows():
                try:
                    work_record = WorkRecord(
                        record_id=str(uuid.uuid4()),
                        date=pd.to_datetime(row["日付"]).date(),
                        hours=float(row["工数"]),
                        member_name=str(row["メンバー"]),
                        project_name=str(row["プロジェクト"]),
                        memo=str(row.get("備考", "")),
                    )
                    work_records.append(work_record)
                    member_names.add(work_record.member_name)
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Skipped invalid row: {row}, error: {e}")

            # 既存データ削除
            self.work_record_repo.delete_all()
            self.member_repo.delete_all()

            # 新しいデータ保存
            self.work_record_repo.save_bulk(work_records)

            # メンバー情報保存
            for member_name in member_names:
                self.member_repo.save(Member(member_name=member_name))

            self.logger.info(
                f"Imported {len(work_records)} work records and {len(member_names)} members"
            )
            return ImportResult(success=True, imported_count=len(work_records))

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
        required_columns = ["日付", "工数", "メンバー", "プロジェクト"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return ImportResult(
                success=False,
                errors=[f"必須列が不足しています: {', '.join(missing_columns)}"],
            )

        # 日付フォーマットチェック
        try:
            pd.to_datetime(df["日付"])
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
