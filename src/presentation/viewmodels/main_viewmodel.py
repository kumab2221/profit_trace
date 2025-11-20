"""Main view model."""

from PySide6.QtCore import QObject, Signal, Slot


class MainViewModel(QObject):
    """メイン画面の状態管理を行う ViewModel."""

    # Signals
    screen_changed = Signal(str, object)  # (screen_name, parameter)

    def __init__(self) -> None:
        """初期化."""
        super().__init__()
        self._current_screen = "project_list"

    @property
    def current_screen(self) -> str:
        """現在の画面名を取得する.

        Returns:
            現在の画面名
        """
        return self._current_screen

    @Slot()
    def on_import_requested(self) -> None:
        """インポート画面への遷移を要求.

        Signal:
            screen_changed: ("import", None)
        """
        self._current_screen = "import"
        self.screen_changed.emit("import", None)

    @Slot(str)
    def on_project_selected(self, project_name: str) -> None:
        """プロジェクト詳細画面への遷移を要求.

        Args:
            project_name: プロジェクト名

        Signal:
            screen_changed: ("project_detail", project_name)
        """
        self._current_screen = "project_detail"
        self.screen_changed.emit("project_detail", project_name)

    @Slot(str)
    def on_member_selected(self, member_name: str) -> None:
        """メンバー稼働状況画面への遷移を要求.

        Args:
            member_name: メンバー名

        Signal:
            screen_changed: ("member_workload", member_name)
        """
        self._current_screen = "member_workload"
        self.screen_changed.emit("member_workload", member_name)

    @Slot()
    def on_report_requested(self) -> None:
        """レポート画面への遷移を要求.

        Signal:
            screen_changed: ("report", None)
        """
        self._current_screen = "report"
        self.screen_changed.emit("report", None)

    @Slot()
    def on_project_list_requested(self) -> None:
        """プロジェクト一覧画面への遷移を要求.

        Signal:
            screen_changed: ("project_list", None)
        """
        self._current_screen = "project_list"
        self.screen_changed.emit("project_list", None)
