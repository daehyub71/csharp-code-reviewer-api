"""
파일 업로드 위젯

C# 파일을 선택하고 관리하는 UI 컴포넌트입니다.
드래그 앤 드롭, 파일 검증, 파일 목록 표시 기능을 제공합니다.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QFileDialog,
    QMessageBox, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QMimeData, QFileInfo
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from pathlib import Path
from typing import List, Optional
import os


class FilePreviewDialog(QDialog):
    """파일 미리보기 다이얼로그"""

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self._init_ui()
        self._load_file()

    def _init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(f"미리보기 - {Path(self.file_path).name}")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # 파일 정보 레이블
        file_info = QFileInfo(self.file_path)
        info_text = (
            f"파일명: {file_info.fileName()}\n"
            f"크기: {self._format_size(file_info.size())}\n"
            f"경로: {file_info.absoluteFilePath()}"
        )

        info_label = QLabel(info_text)
        info_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                color: #cccccc;
            }
        """)
        layout.addWidget(info_label)

        # 코드 미리보기 (읽기 전용)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                border: 1px solid #3e3e42;
            }
        """)
        layout.addWidget(self.text_edit)

        # 닫기 버튼
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        layout.addWidget(close_btn)

    def _load_file(self):
        """파일 내용 로드"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_edit.setPlainText(content)
        except UnicodeDecodeError:
            self.text_edit.setPlainText("⚠️ UTF-8 인코딩이 아닌 파일입니다. 내용을 표시할 수 없습니다.")
        except Exception as e:
            self.text_edit.setPlainText(f"❌ 파일 읽기 오류: {str(e)}")

    def _format_size(self, size: int) -> str:
        """파일 크기 포맷팅"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class FileListWidget(QListWidget):
    """드래그 앤 드롭을 지원하는 파일 리스트 위젯"""

    files_dropped = Signal(list)  # 파일이 드롭되었을 때 시그널

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                color: #cccccc;
                border: 2px dashed #3e3e42;
                border-radius: 4px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3e3e42;
            }
            QListWidget::item:selected {
                background-color: #094771;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)

        # 드롭 영역 하이라이트 상태
        self._is_drag_active = False

    def dragEnterEvent(self, event: QDragEnterEvent):
        """드래그 진입 이벤트"""
        if event.mimeData().hasUrls():
            # .cs 파일이 하나라도 있는지 확인
            cs_files = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.toLocalFile().endswith('.cs')
            ]

            if cs_files:
                event.acceptProposedAction()
                self._is_drag_active = True
                self._update_drag_style(True)
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """드래그 떠남 이벤트"""
        self._is_drag_active = False
        self._update_drag_style(False)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        """드롭 이벤트"""
        if event.mimeData().hasUrls():
            cs_files = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.toLocalFile().endswith('.cs')
            ]

            if cs_files:
                self.files_dropped.emit(cs_files)
                event.acceptProposedAction()

        self._is_drag_active = False
        self._update_drag_style(False)

    def _update_drag_style(self, active: bool):
        """드래그 상태에 따라 스타일 업데이트"""
        if active:
            self.setStyleSheet("""
                QListWidget {
                    background-color: #094771;
                    color: white;
                    border: 2px solid #0e639c;
                    border-radius: 4px;
                    padding: 10px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #3e3e42;
                }
                QListWidget::item:selected {
                    background-color: #0e639c;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QListWidget {
                    background-color: #252526;
                    color: #cccccc;
                    border: 2px dashed #3e3e42;
                    border-radius: 4px;
                    padding: 10px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #3e3e42;
                }
                QListWidget::item:selected {
                    background-color: #094771;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #2a2d2e;
                }
            """)


class FileUploadWidget(QWidget):
    """
    파일 업로드 위젯

    C# 파일을 선택하고 관리하는 UI 컴포넌트입니다.
    - 파일 추가/제거
    - 드래그 앤 드롭
    - 파일 검증 (크기, 인코딩)
    - 파일 미리보기
    """

    files_changed = Signal(list)  # 파일 목록이 변경되었을 때 시그널

    # 파일 크기 제한 (1MB)
    MAX_FILE_SIZE = 1 * 1024 * 1024

    def __init__(self, parent=None):
        super().__init__(parent)

        # 선택된 파일 목록 (절대 경로)
        self.selected_files: List[str] = []

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 헤더 (제목 + 파일 카운터)
        header_layout = QHBoxLayout()

        title_label = QLabel("📁 파일 선택")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #cccccc;
            }
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.counter_label = QLabel("총 0개 파일")
        self.counter_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #858585;
                padding: 4px 8px;
                background-color: #3e3e42;
                border-radius: 4px;
            }
        """)
        header_layout.addWidget(self.counter_label)

        layout.addLayout(header_layout)

        # 파일 리스트
        self.file_list = FileListWidget()
        self.file_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.file_list)

        # 플레이스홀더 메시지
        self._update_placeholder()

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 파일 추가 버튼
        self.add_btn = QPushButton("📂 파일 추가")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """)
        button_layout.addWidget(self.add_btn)

        # 선택 제거 버튼
        self.remove_btn = QPushButton("🗑️ 선택 제거")
        self.remove_btn.setEnabled(False)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #3e3e42;
                color: #cccccc;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover:enabled {
                background-color: #c5303a;
                color: white;
            }
            QPushButton:pressed:enabled {
                background-color: #a02830;
            }
            QPushButton:disabled {
                background-color: #2d2d30;
                color: #656565;
            }
        """)
        button_layout.addWidget(self.remove_btn)

        # 전체 제거 버튼
        self.clear_btn = QPushButton("🧹 전체 제거")
        self.clear_btn.setEnabled(False)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #3e3e42;
                color: #cccccc;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover:enabled {
                background-color: #c5303a;
                color: white;
            }
            QPushButton:pressed:enabled {
                background-color: #a02830;
            }
            QPushButton:disabled {
                background-color: #2d2d30;
                color: #656565;
            }
        """)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 힌트 메시지
        hint_label = QLabel("💡 힌트: .cs 파일을 드래그 앤 드롭하거나 '파일 추가' 버튼을 클릭하세요")
        hint_label.setStyleSheet("""
            QLabel {
                color: #858585;
                font-size: 9pt;
                padding: 8px;
                background-color: #2d2d30;
                border-radius: 4px;
                border-left: 3px solid #0e639c;
            }
        """)
        layout.addWidget(hint_label)

    def _connect_signals(self):
        """시그널 연결"""
        self.add_btn.clicked.connect(self._on_add_files)
        self.remove_btn.clicked.connect(self._on_remove_selected)
        self.clear_btn.clicked.connect(self._on_clear_all)
        self.file_list.files_dropped.connect(self._on_files_dropped)
        self.file_list.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_add_files(self):
        """파일 추가 버튼 클릭"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("C# Files (*.cs)")

        if file_dialog.exec():
            selected = file_dialog.selectedFiles()
            self._add_files(selected)

    def _on_remove_selected(self):
        """선택된 파일 제거"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)

            row = self.file_list.row(item)
            self.file_list.takeItem(row)

        self._update_ui()
        self.files_changed.emit(self.selected_files)

    def _on_clear_all(self):
        """전체 파일 제거"""
        reply = QMessageBox.question(
            self,
            "전체 제거 확인",
            f"선택된 {len(self.selected_files)}개 파일을 모두 제거하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.selected_files.clear()
            self.file_list.clear()
            self._update_ui()
            self.files_changed.emit(self.selected_files)

    def _on_files_dropped(self, file_paths: List[str]):
        """파일 드롭 이벤트"""
        self._add_files(file_paths)

    def _on_selection_changed(self):
        """선택 변경 이벤트"""
        has_selection = len(self.file_list.selectedItems()) > 0
        self.remove_btn.setEnabled(has_selection)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """아이템 더블클릭 - 미리보기"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            dialog = FilePreviewDialog(file_path, self)
            dialog.exec()

    def _add_files(self, file_paths: List[str]):
        """파일 추가 (검증 포함)"""
        added_count = 0
        skipped_count = 0
        error_messages = []

        for file_path in file_paths:
            # 중복 체크
            if file_path in self.selected_files:
                skipped_count += 1
                continue

            # 파일 검증
            is_valid, error_msg = self._validate_file(file_path)

            if is_valid:
                self.selected_files.append(file_path)
                self._add_list_item(file_path)
                added_count += 1
            else:
                error_messages.append(f"• {Path(file_path).name}: {error_msg}")
                skipped_count += 1

        # 결과 메시지
        if error_messages:
            msg = f"추가됨: {added_count}개\n건너뜀: {skipped_count}개\n\n오류:\n" + "\n".join(error_messages[:5])
            if len(error_messages) > 5:
                msg += f"\n... 외 {len(error_messages) - 5}개"

            QMessageBox.warning(self, "파일 추가 결과", msg)
        elif added_count > 0:
            QMessageBox.information(
                self,
                "파일 추가 완료",
                f"{added_count}개 파일이 추가되었습니다."
            )

        self._update_ui()
        if added_count > 0:
            self.files_changed.emit(self.selected_files)

    def _validate_file(self, file_path: str) -> tuple[bool, str]:
        """
        파일 검증

        Returns:
            (유효 여부, 오류 메시지)
        """
        # 파일 존재 확인
        if not os.path.exists(file_path):
            return False, "파일이 존재하지 않습니다"

        # .cs 확장자 확인
        if not file_path.endswith('.cs'):
            return False, "C# 파일(.cs)이 아닙니다"

        # 파일 크기 확인
        file_size = os.path.getsize(file_path)
        if file_size > self.MAX_FILE_SIZE:
            return False, f"파일 크기가 {self._format_size(self.MAX_FILE_SIZE)}를 초과합니다"

        # UTF-8 인코딩 확인
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError:
            return False, "UTF-8 인코딩이 아닙니다"
        except Exception as e:
            return False, f"파일 읽기 오류: {str(e)}"

        return True, ""

    def _add_list_item(self, file_path: str):
        """리스트 아이템 추가"""
        file_info = QFileInfo(file_path)

        # 아이템 텍스트: 파일명 + 크기
        item_text = f"📄 {file_info.fileName()}  ({self._format_size(file_info.size())})"

        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        item.setToolTip(file_path)  # 툴팁에 전체 경로 표시

        self.file_list.addItem(item)

    def _update_ui(self):
        """UI 상태 업데이트"""
        file_count = len(self.selected_files)

        # 카운터 업데이트
        self.counter_label.setText(f"총 {file_count}개 파일")

        # 버튼 활성화 상태
        self.clear_btn.setEnabled(file_count > 0)

        # 플레이스홀더 업데이트
        self._update_placeholder()

    def _update_placeholder(self):
        """플레이스홀더 메시지 업데이트"""
        if len(self.selected_files) == 0:
            placeholder = QListWidgetItem("📂 파일을 추가하거나 여기에 드래그 앤 드롭하세요")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            placeholder.setForeground(Qt.GlobalColor.gray)
            self.file_list.clear()
            self.file_list.addItem(placeholder)

    def _format_size(self, size: int) -> str:
        """파일 크기 포맷팅"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    # Public 메서드

    def get_selected_files(self) -> List[str]:
        """선택된 파일 목록 반환"""
        return self.selected_files.copy()

    def clear_files(self):
        """모든 파일 제거"""
        self.selected_files.clear()
        self.file_list.clear()
        self._update_ui()
        self.files_changed.emit(self.selected_files)

    def add_files_programmatically(self, file_paths: List[str]):
        """프로그래밍 방식으로 파일 추가 (UI 없이)"""
        self._add_files(file_paths)


# 사용 예제
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # FileUploadWidget 테스트
    widget = FileUploadWidget()
    widget.setWindowTitle("파일 업로드 위젯 테스트")
    widget.resize(600, 500)

    # 파일 변경 시그널 연결
    def on_files_changed(files):
        print(f"✅ 파일 변경: {len(files)}개")
        for i, f in enumerate(files, 1):
            print(f"   {i}. {f}")

    widget.files_changed.connect(on_files_changed)

    widget.show()

    sys.exit(app.exec())
