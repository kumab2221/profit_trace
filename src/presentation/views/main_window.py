"""Main window."""

import logging

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.presentation.viewmodels.import_viewmodel import ImportViewModel
from src.presentation.viewmodels.main_viewmodel import MainViewModel
from src.presentation.viewmodels.member_workload_viewmodel import (
    MemberWorkloadViewModel,
)
from src.presentation.viewmodels.project_detail_viewmodel import (
    ProjectDetailViewModel,
)
from src.presentation.viewmodels.project_list_viewmodel import ProjectListViewModel
from src.presentation.viewmodels.report_viewmodel import ReportViewModel
from src.presentation.views.import_dialog import ImportDialog
from src.presentation.views.member_workload_widget import MemberWorkloadWidget
from src.presentation.views.project_detail_widget import ProjectDetailWidget
from src.presentation.views.project_list_widget import ProjectListWidget
from src.presentation.views.report_widget import ReportWidget


class MainWindow(QMainWindow):
    """メイン画面."""

    def __init__(
        self,
        main_vm: MainViewModel,
        project_list_vm: ProjectListViewModel,
        project_detail_vm: ProjectDetailViewModel,
        member_workload_vm: MemberWorkloadViewModel,
        report_vm: ReportViewModel,
        import_vm: ImportViewModel,
        logger: logging.Logger | None = None,
    ) -> None:
        """初期化.

        Args:
            main_vm: メイン ViewModel
            project_list_vm: プロジェクト一覧 ViewModel
            project_detail_vm: プロジェクト詳細 ViewModel
            member_workload_vm: メンバー稼働状況 ViewModel
            report_vm: レポート ViewModel
            import_vm: インポート ViewModel
            logger: ロガー（省略時は標準ロガー）
        """
        super().__init__()
        self.main_vm = main_vm
        self.logger = logger or logging.getLogger(__name__)

        self.setWindowTitle("Profit Trace - 工数管理システム")
        self.setMinimumSize(1024, 768)

        # メニューバー
        self._create_menu_bar()

        # 画面ウィジェット
        self.project_list_widget = ProjectListWidget(project_list_vm)
        self.project_detail_widget = ProjectDetailWidget(project_detail_vm)
        self.member_workload_widget = MemberWorkloadWidget(member_workload_vm)
        self.report_widget = ReportWidget(report_vm)

        # インポートダイアログ
        self.import_dialog = ImportDialog(import_vm)

        # スタックウィジェット（画面切り替え用）
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.project_list_widget)  # index 0
        self.stacked_widget.addWidget(self.project_detail_widget)  # index 1
        self.stacked_widget.addWidget(self.member_workload_widget)  # index 2
        self.stacked_widget.addWidget(self.report_widget)  # index 3

        # 中央ウィジェット
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Signal/Slot 接続
        self._connect_signals(project_list_vm, project_detail_vm, member_workload_vm)

        # 初期画面を表示
        self.show_project_list()

    def _create_menu_bar(self) -> None:
        """メニューバーを作成."""
        menu_bar = self.menuBar()

        # ファイルメニュー
        file_menu = menu_bar.addMenu("ファイル(&F)")
        import_action = file_menu.addAction("インポート(&I)")
        import_action.triggered.connect(self._on_import_action_triggered)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("終了(&X)")
        exit_action.triggered.connect(self.close)

        # 表示メニュー
        view_menu = menu_bar.addMenu("表示(&V)")
        project_list_action = view_menu.addAction("プロジェクト一覧(&P)")
        project_list_action.triggered.connect(self.show_project_list)
        report_action = view_menu.addAction("レポート(&R)")
        report_action.triggered.connect(self.show_report)

    def _connect_signals(
        self,
        project_list_vm: ProjectListViewModel,
        project_detail_vm: ProjectDetailViewModel,
        member_workload_vm: MemberWorkloadViewModel,
    ) -> None:
        """Signal/Slot を接続.

        Args:
            project_list_vm: プロジェクト一覧 ViewModel
            project_detail_vm: プロジェクト詳細 ViewModel
            member_workload_vm: メンバー稼働状況 ViewModel
        """
        # プロジェクト一覧画面からの遷移
        self.project_list_widget.project_selected.connect(self.show_project_detail)

        # プロジェクト詳細画面の戻るボタン
        self.project_detail_widget.back_button.clicked.connect(self.show_project_list)

        # メンバー稼働状況画面の戻るボタン
        self.member_workload_widget.back_button.clicked.connect(
            self.show_project_list
        )

        # MainViewModel の画面遷移 Signal
        self.main_vm.screen_changed.connect(self._on_screen_changed)

    @Slot()
    def show_project_list(self) -> None:
        """プロジェクト一覧画面を表示."""
        self.stacked_widget.setCurrentIndex(0)
        self.main_vm.on_project_list_requested()
        self.logger.info("Switched to project list screen")

    @Slot(str)
    def show_project_detail(self, project_name: str) -> None:
        """プロジェクト詳細画面を表示.

        Args:
            project_name: プロジェクト名
        """
        self.stacked_widget.setCurrentIndex(1)
        self.project_detail_widget.view_model.on_project_changed(project_name)
        self.main_vm.on_project_selected(project_name)
        self.logger.info(f"Switched to project detail screen: {project_name}")

    @Slot(str)
    def show_member_workload(self, member_name: str) -> None:
        """メンバー稼働状況画面を表示.

        Args:
            member_name: メンバー名
        """
        self.stacked_widget.setCurrentIndex(2)
        self.member_workload_widget.view_model.on_member_changed(member_name)
        self.main_vm.on_member_selected(member_name)
        self.logger.info(f"Switched to member workload screen: {member_name}")

    @Slot()
    def show_report(self) -> None:
        """レポート画面を表示."""
        self.stacked_widget.setCurrentIndex(3)
        self.main_vm.on_report_requested()
        self.logger.info("Switched to report screen")

    @Slot()
    def _on_import_action_triggered(self) -> None:
        """インポートメニューがクリックされた時の処理."""
        self.import_dialog.exec()

    @Slot(str, object)
    def _on_screen_changed(self, screen_name: str, parameter) -> None:
        """画面が変更された時の処理.

        Args:
            screen_name: 画面名
            parameter: パラメータ
        """
        if screen_name == "project_list":
            self.show_project_list()
        elif screen_name == "project_detail" and parameter:
            self.show_project_detail(parameter)
        elif screen_name == "member_workload" and parameter:
            self.show_member_workload(parameter)
        elif screen_name == "report":
            self.show_report()
        elif screen_name == "import":
            self._on_import_action_triggered()
