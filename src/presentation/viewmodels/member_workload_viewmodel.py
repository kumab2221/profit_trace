"""Member workload view model."""

import logging

from PySide6.QtCore import QObject, Signal, Slot

from src.application.usecases.get_member_workload_usecase import (
    GetMemberWorkloadUseCase,
)


class MemberWorkloadViewModel(QObject):
    """メンバー稼働状況の状態管理を行う ViewModel."""

    # Signals
    workload_updated = Signal(object)  # MemberWorkloadDTO
    error_occurred = Signal(str)

    def __init__(
        self, use_case: GetMemberWorkloadUseCase, logger: logging.Logger | None = None
    ) -> None:
        """初期化.

        Args:
            use_case: メンバー稼働状況取得ユースケース
            logger: ロガー（省略時は標準ロガー）
        """
        super().__init__()
        self.use_case = use_case
        self.logger = logger or logging.getLogger(__name__)
        self._current_member_name: str | None = None

    @Slot(str)
    def on_member_changed(self, member_name: str) -> None:
        """メンバーが変更された時の処理.

        Args:
            member_name: メンバー名

        Signal:
            workload_updated: 稼働状況を更新
            error_occurred: エラーが発生した場合
        """
        self._current_member_name = member_name
        self._load_workload()

    @Slot()
    def on_refresh_requested(self) -> None:
        """再読み込みを要求.

        Signal:
            workload_updated: 稼働状況を更新
            error_occurred: エラーが発生した場合
        """
        if self._current_member_name:
            self._load_workload()

    def _load_workload(self) -> None:
        """稼働状況を読み込む."""
        if not self._current_member_name:
            return

        try:
            workload_data = self.use_case.execute(self._current_member_name)
            self.workload_updated.emit(workload_data)
            self.logger.info(
                f"Workload updated for member: {self._current_member_name}"
            )
        except Exception as e:
            error_message = f"メンバー稼働状況の取得に失敗しました: {e}"
            self.logger.error(error_message, exc_info=True)
            self.error_occurred.emit(error_message)
