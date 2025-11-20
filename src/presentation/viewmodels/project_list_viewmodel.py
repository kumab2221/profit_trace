"""Project list view model."""

import logging

from PySide6.QtCore import QObject, Signal, Slot

from src.application.usecases.get_project_list_usecase import GetProjectListUseCase


class ProjectListViewModel(QObject):
    """プロジェクト一覧の状態管理を行う ViewModel."""

    # Signals
    projects_updated = Signal(list)  # List[ProjectDTO]
    error_occurred = Signal(str)

    def __init__(
        self, use_case: GetProjectListUseCase, logger: logging.Logger | None = None
    ) -> None:
        """初期化.

        Args:
            use_case: プロジェクト一覧取得ユースケース
            logger: ロガー（省略時は標準ロガー）
        """
        super().__init__()
        self.use_case = use_case
        self.logger = logger or logging.getLogger(__name__)

    @Slot()
    def on_refresh_requested(self) -> None:
        """プロジェクト一覧の更新を要求.

        Signal:
            projects_updated: プロジェクト一覧を更新
            error_occurred: エラーが発生した場合
        """
        try:
            projects = self.use_case.execute()
            self.projects_updated.emit(projects)
            self.logger.info(f"Projects updated: {len(projects)} projects")
        except Exception as e:
            error_message = f"プロジェクト一覧の取得に失敗しました: {e}"
            self.logger.error(error_message, exc_info=True)
            self.error_occurred.emit(error_message)

    @Slot(str)
    def on_project_clicked(self, project_name: str) -> None:
        """プロジェクトがクリックされた時の処理.

        Args:
            project_name: クリックされたプロジェクト名

        Note:
            実際の画面遷移は MainViewModel で行う
        """
        self.logger.info(f"Project clicked: {project_name}")
