"""Import dialog."""

from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.presentation.viewmodels.import_viewmodel import ImportViewModel


class ImportDialog(QDialog):
    """ファイルインポート画面."""

    def __init__(self, view_model: ImportViewModel) -> None:
        """初期化.

        Args:
            view_model: インポート ViewModel
        """
        super().__init__()
        self.view_model = view_model

        self.setWindowTitle("ファイルインポート")
        self.setMinimumWidth(400)

        # UI コンポーネント
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(
            ["プロジェクト契約情報 (CSV)", "工数実績データ (CSV)", "休日マスタ (JSON)"]
        )
        self.file_path_label = QLabel("ファイルが選択されていません")
        self.select_file_button = QPushButton("ファイルを選択")
        self.import_button = QPushButton("インポート")
        self.import_button.setEnabled(False)
        self.close_button = QPushButton("閉じる")

        # レイアウト
        layout = QVBoxLayout()
        layout.addWidget(QLabel("ファイルタイプ:"))
        layout.addWidget(self.file_type_combo)
        layout.addWidget(self.file_path_label)
        layout.addWidget(self.select_file_button)
        layout.addWidget(self.import_button)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        # Signal/Slot 接続
        self.select_file_button.clicked.connect(self._on_select_file_clicked)
        self.import_button.clicked.connect(self._on_import_clicked)
        self.close_button.clicked.connect(self.close)
        self.view_model.import_completed.connect(self.show_import_success)
        self.view_model.error_occurred.connect(self.show_error)

        self._selected_file_path: str | None = None

    @Slot()
    def _on_select_file_clicked(self) -> None:
        """ファイル選択ボタンがクリックされた時の処理."""
        # ファイルタイプに応じて拡張子フィルタを設定
        file_type_index = self.file_type_combo.currentIndex()
        if file_type_index == 2:  # 休日マスタ
            file_filter = "JSON Files (*.json)"
        else:  # CSV ファイル
            file_filter = "CSV Files (*.csv)"

        # ファイル選択ダイアログを表示
        file_path, _ = QFileDialog.getOpenFileName(
            self, "インポートファイルを選択", "", file_filter
        )

        if file_path:
            self._selected_file_path = file_path
            self.file_path_label.setText(f"選択されたファイル: {Path(file_path).name}")
            self.import_button.setEnabled(True)

    @Slot()
    def _on_import_clicked(self) -> None:
        """インポートボタンがクリックされた時の処理."""
        if not self._selected_file_path:
            return

        # ファイルタイプを判定
        file_type_index = self.file_type_combo.currentIndex()
        file_type_map = {
            0: "project",
            1: "work_record",
            2: "calendar",
        }
        file_type = file_type_map.get(file_type_index, "project")

        # インポート実行
        self.import_button.setEnabled(False)
        self.select_file_button.setEnabled(False)
        self.view_model.on_file_selected(file_type, self._selected_file_path)

    @Slot(object)
    def show_import_success(self, result) -> None:
        """インポート成功ダイアログを表示する.

        Args:
            result: インポート結果（ImportResult）
        """
        self.import_button.setEnabled(True)
        self.select_file_button.setEnabled(True)

        message = f"インポートが完了しました。\n\nインポート件数: {result.imported_count}件"
        QMessageBox.information(self, "インポート完了", message)

    @Slot(str)
    def show_error(self, message: str) -> None:
        """エラーダイアログを表示する.

        Args:
            message: エラーメッセージ
        """
        self.import_button.setEnabled(True)
        self.select_file_button.setEnabled(True)

        QMessageBox.critical(self, "エラー", message)
