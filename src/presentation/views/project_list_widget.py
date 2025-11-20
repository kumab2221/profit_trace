"""Project list widget."""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.presentation.viewmodels.project_list_viewmodel import ProjectListViewModel


class ProjectListWidget(QWidget):
    """プロジェクト一覧画面."""

    # Signals
    project_selected = Signal(str)  # project_name

    def __init__(self, view_model: ProjectListViewModel) -> None:
        """初期化.

        Args:
            view_model: プロジェクト一覧 ViewModel
        """
        super().__init__()
        self.view_model = view_model

        # UI コンポーネント
        self.table = QTableWidget()
        self.refresh_button = QPushButton("更新")

        # レイアウト
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)

        # テーブル設定
        self._setup_table()

        # Signal/Slot 接続
        self.refresh_button.clicked.connect(self.view_model.on_refresh_requested)
        self.view_model.projects_updated.connect(self.update_table)
        self.view_model.error_occurred.connect(self.show_error)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)

        # 初期表示
        self.view_model.on_refresh_requested()

    def _setup_table(self) -> None:
        """テーブルの初期設定."""
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["プロジェクト名", "開始日", "終了日", "契約工数", "消化工数", "消化率", "状態"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

    @Slot(list)
    def update_table(self, projects: list) -> None:
        """プロジェクト一覧を更新する.

        Args:
            projects: プロジェクト DTO のリスト
        """
        self.table.setRowCount(len(projects))

        for row, project in enumerate(projects):
            self.table.setItem(row, 0, QTableWidgetItem(project.name))
            self.table.setItem(
                row, 1, QTableWidgetItem(project.start_date.isoformat())
            )
            self.table.setItem(row, 2, QTableWidgetItem(project.end_date.isoformat()))
            self.table.setItem(
                row, 3, QTableWidgetItem(f"{project.contracted_hours:.2f}")
            )
            self.table.setItem(
                row, 4, QTableWidgetItem(f"{project.consumed_hours:.2f}")
            )
            self.table.setItem(
                row, 5, QTableWidgetItem(f"{project.consumption_rate * 100:.1f}%")
            )
            self.table.setItem(row, 6, QTableWidgetItem(project.status))

            # ステータスに応じて行の色を変更
            if project.status == "遅延":
                for col in range(7):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(Qt.yellow)
            elif project.status == "余剰":
                for col in range(7):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(Qt.lightGray)

    @Slot(str)
    def show_error(self, message: str) -> None:
        """エラーダイアログを表示する.

        Args:
            message: エラーメッセージ
        """
        QMessageBox.critical(self, "エラー", message)

    @Slot(int, int)
    def _on_cell_double_clicked(self, row: int, column: int) -> None:
        """セルがダブルクリックされた時の処理.

        Args:
            row: 行番号
            column: 列番号

        Signal:
            project_selected: プロジェクトが選択された
        """
        project_name_item = self.table.item(row, 0)
        if project_name_item:
            project_name = project_name_item.text()
            self.project_selected.emit(project_name)
