"""
폴더 선택 위젯

폴더 구조를 트리로 표시하고 C# 파일을 선택하는 UI 컴포넌트입니다.
재귀 탐색, 체크박스 선택, 파일 필터링 기능을 제공합니다.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTreeView, QLabel, QFileDialog, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QDir
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from pathlib import Path
from typing import List, Set
import os


class FolderSelectWidget(QWidget):
    """폴더 선택 및 트리 표시 위젯"""

    # 시그널: 선택된 파일 목록이 변경될 때 발생
    files_changed = Signal(list)  # List[str] - 파일 경로 목록

    # 제외할 폴더 목록
    EXCLUDED_FOLDERS = {'.git', '.vs', '.vscode', 'bin', 'obj', 'node_modules', 'packages'}

    # 최대 파일 개수 제한
    MAX_FILE_COUNT = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folder = None
        self.all_files: List[str] = []  # 모든 C# 파일 경로
        self.checked_files: Set[str] = set()  # 체크된 파일 경로
        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 상단: 폴더 선택 영역
        top_layout = QHBoxLayout()

        # 폴더 선택 버튼
        self.select_folder_btn = QPushButton("📂 폴더 선택")
        self.select_folder_btn.setFixedHeight(36)
        self.select_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5689;
            }
        """)
        self.select_folder_btn.clicked.connect(self._select_folder)
        top_layout.addWidget(self.select_folder_btn)

        # 선택된 폴더 경로 레이블
        self.folder_label = QLabel("📁 선택된 폴더: 없음")
        self.folder_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 10pt;
                padding: 8px;
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 4px;
            }
        """)
        top_layout.addWidget(self.folder_label, 1)

        layout.addLayout(top_layout)

        # 파일 개수 정보 레이블
        self.info_label = QLabel("💡 폴더를 선택하면 C# 파일 목록이 표시됩니다")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #858585;
                font-size: 9pt;
                padding: 6px;
            }
        """)
        layout.addWidget(self.info_label)

        # 트리 뷰
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                font-size: 10pt;
            }
            QTreeView::item {
                padding: 4px;
                border-bottom: 1px solid #2d2d30;
            }
            QTreeView::item:hover {
                background-color: #2a2d2e;
            }
            QTreeView::item:selected {
                background-color: #094771;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                image: url(:/icons/branch-closed.png);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                image: url(:/icons/branch-open.png);
            }
        """)

        # 트리 모델 초기화
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["파일/폴더", "개수"])
        self.tree_view.setModel(self.model)
        self.model.itemChanged.connect(self._on_item_changed)

        # 헤더 설정
        header = self.tree_view.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        layout.addWidget(self.tree_view)

        # 하단: 버튼 영역
        bottom_layout = QHBoxLayout()

        # 전체 선택 버튼
        self.select_all_btn = QPushButton("✅ 전체 선택")
        self.select_all_btn.setEnabled(False)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover:enabled {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #3e3e42;
                color: #858585;
            }
        """)
        self.select_all_btn.clicked.connect(self._select_all)
        bottom_layout.addWidget(self.select_all_btn)

        # 전체 해제 버튼
        self.deselect_all_btn = QPushButton("❌ 전체 해제")
        self.deselect_all_btn.setEnabled(False)
        self.deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #858585;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover:enabled {
                background-color: #a0a0a0;
            }
            QPushButton:disabled {
                background-color: #3e3e42;
                color: #858585;
            }
        """)
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        bottom_layout.addWidget(self.deselect_all_btn)

        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)

    def _select_folder(self):
        """폴더 선택 다이얼로그 표시"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "C# 프로젝트 폴더 선택",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if folder:
            self._load_folder(folder)

    def _load_folder(self, folder_path: str):
        """폴더 로드 및 트리 구성"""
        self.selected_folder = folder_path
        self.folder_label.setText(f"📁 선택된 폴더: {folder_path}")

        # 진행 상태 표시
        self.info_label.setText("🔍 C# 파일 검색 중...")
        self.tree_view.setEnabled(False)

        # 모델 초기화
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["파일/폴더", "개수"])

        # C# 파일 재귀 탐색
        self.all_files = []
        self.checked_files = set()

        try:
            self._scan_folder(folder_path)

            # 파일 개수 체크
            if len(self.all_files) == 0:
                QMessageBox.warning(
                    self,
                    "파일 없음",
                    "선택한 폴더에 C# 파일(.cs)이 없습니다."
                )
                self.info_label.setText("⚠️ C# 파일이 없습니다")
                self.tree_view.setEnabled(False)
                return

            if len(self.all_files) > self.MAX_FILE_COUNT:
                reply = QMessageBox.question(
                    self,
                    "파일 개수 초과",
                    f"총 {len(self.all_files)}개의 C# 파일이 발견되었습니다.\n"
                    f"최대 {self.MAX_FILE_COUNT}개까지만 분석할 수 있습니다.\n\n"
                    f"처음 {self.MAX_FILE_COUNT}개 파일만 표시하시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.all_files = self.all_files[:self.MAX_FILE_COUNT]
                else:
                    self.info_label.setText("❌ 파일 개수가 너무 많습니다")
                    return

            # 트리 구성
            self._build_tree(folder_path)

            # UI 활성화
            self.tree_view.setEnabled(True)
            self.select_all_btn.setEnabled(True)
            self.deselect_all_btn.setEnabled(True)

            # 트리 확장
            self.tree_view.expandToDepth(1)

            # 정보 레이블 업데이트
            self.info_label.setText(
                f"📊 총 {len(self.all_files)}개 파일 | "
                f"✅ {len(self.checked_files)}개 선택됨"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"폴더 로드 중 오류가 발생했습니다:\n{str(e)}"
            )
            self.tree_view.setEnabled(False)

    def _scan_folder(self, folder_path: str):
        """재귀적으로 폴더 탐색하여 C# 파일 수집"""
        for root, dirs, files in os.walk(folder_path):
            # 제외 폴더 필터링 (in-place 수정)
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_FOLDERS]

            # C# 파일 필터링
            for file in files:
                if file.endswith('.cs'):
                    file_path = os.path.join(root, file)
                    self.all_files.append(file_path)

    def _build_tree(self, root_path: str):
        """트리 구조 구성"""
        # 루트 폴더 아이템
        root_item = QStandardItem(f"📁 {Path(root_path).name}")
        root_item.setCheckable(True)
        root_item.setCheckState(Qt.Unchecked)
        root_item.setData(root_path, Qt.UserRole)
        root_item.setData("folder", Qt.UserRole + 1)

        count_item = QStandardItem(f"{len(self.all_files)}개")
        count_item.setEditable(False)

        self.model.appendRow([root_item, count_item])

        # 파일 경로를 트리 구조로 변환
        file_tree = {}
        for file_path in self.all_files:
            rel_path = os.path.relpath(file_path, root_path)
            parts = Path(rel_path).parts

            current = file_tree
            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {}
                current = current[part]

        # 재귀적으로 트리 구성
        self._build_tree_recursive(root_item, file_tree, root_path)

    def _build_tree_recursive(self, parent_item: QStandardItem, tree: dict, current_path: str):
        """재귀적으로 트리 아이템 구성"""
        for name, subtree in sorted(tree.items()):
            full_path = os.path.join(current_path, name)

            if subtree:  # 폴더
                folder_item = QStandardItem(f"📁 {name}")
                folder_item.setCheckable(True)
                folder_item.setCheckState(Qt.Unchecked)
                folder_item.setData(full_path, Qt.UserRole)
                folder_item.setData("folder", Qt.UserRole + 1)

                # 폴더 내 파일 개수 계산
                file_count = self._count_files_in_subtree(subtree)
                count_item = QStandardItem(f"{file_count}개")
                count_item.setEditable(False)

                parent_item.appendRow([folder_item, count_item])
                self._build_tree_recursive(folder_item, subtree, full_path)

            else:  # 파일
                file_item = QStandardItem(f"📄 {name}")
                file_item.setCheckable(True)
                file_item.setCheckState(Qt.Unchecked)
                file_item.setData(full_path, Qt.UserRole)
                file_item.setData("file", Qt.UserRole + 1)

                # 파일 크기 표시
                try:
                    size = os.path.getsize(full_path)
                    size_item = QStandardItem(self._format_size(size))
                    size_item.setEditable(False)
                except:
                    size_item = QStandardItem("-")
                    size_item.setEditable(False)

                parent_item.appendRow([file_item, size_item])

    def _count_files_in_subtree(self, tree: dict) -> int:
        """서브트리 내 파일 개수 계산"""
        count = 0
        for name, subtree in tree.items():
            if subtree:  # 폴더
                count += self._count_files_in_subtree(subtree)
            else:  # 파일
                count += 1
        return count

    def _on_item_changed(self, item: QStandardItem):
        """아이템 체크 상태 변경 시 호출"""
        # 시그널 일시 차단 (재귀 방지)
        self.model.itemChanged.disconnect(self._on_item_changed)

        file_path = item.data(Qt.UserRole)
        item_type = item.data(Qt.UserRole + 1)
        check_state = item.checkState()

        if item_type == "file":
            # 파일: checked_files 업데이트
            if check_state == Qt.Checked:
                self.checked_files.add(file_path)
            else:
                self.checked_files.discard(file_path)

        elif item_type == "folder":
            # 폴더: 하위 아이템 모두 변경
            self._check_children_recursive(item, check_state)

        # 부모 아이템 체크 상태 업데이트
        self._update_parent_check_state(item)

        # 정보 레이블 업데이트
        self.info_label.setText(
            f"📊 총 {len(self.all_files)}개 파일 | "
            f"✅ {len(self.checked_files)}개 선택됨"
        )

        # 시그널 발생
        self.files_changed.emit(list(self.checked_files))

        # 시그널 재연결
        self.model.itemChanged.connect(self._on_item_changed)

    def _check_children_recursive(self, parent: QStandardItem, check_state: Qt.CheckState):
        """하위 아이템 재귀적으로 체크 상태 변경"""
        for row in range(parent.rowCount()):
            child = parent.child(row, 0)
            if child and child.isCheckable():
                child.setCheckState(check_state)

                # 파일인 경우 checked_files 업데이트
                child_type = child.data(Qt.UserRole + 1)
                child_path = child.data(Qt.UserRole)

                if child_type == "file":
                    if check_state == Qt.Checked:
                        self.checked_files.add(child_path)
                    else:
                        self.checked_files.discard(child_path)

                # 재귀 호출
                self._check_children_recursive(child, check_state)

    def _update_parent_check_state(self, item: QStandardItem):
        """부모 아이템의 체크 상태 업데이트"""
        parent = item.parent()
        if not parent:
            return

        # 모든 자식의 체크 상태 확인
        all_checked = True
        all_unchecked = True

        for row in range(parent.rowCount()):
            child = parent.child(row, 0)
            if child and child.isCheckable():
                state = child.checkState()
                if state != Qt.Checked:
                    all_checked = False
                if state != Qt.Unchecked:
                    all_unchecked = False

        # 부모 상태 업데이트
        if all_checked:
            parent.setCheckState(Qt.Checked)
        elif all_unchecked:
            parent.setCheckState(Qt.Unchecked)
        else:
            parent.setCheckState(Qt.PartiallyChecked)

        # 재귀적으로 상위 부모 업데이트
        self._update_parent_check_state(parent)

    def _select_all(self):
        """전체 선택"""
        root_item = self.model.item(0, 0)
        if root_item:
            # 시그널 차단
            self.model.itemChanged.disconnect(self._on_item_changed)

            root_item.setCheckState(Qt.Checked)
            self._check_children_recursive(root_item, Qt.Checked)

            # 정보 레이블 업데이트
            self.info_label.setText(
                f"📊 총 {len(self.all_files)}개 파일 | "
                f"✅ {len(self.checked_files)}개 선택됨"
            )

            # 시그널 발생
            self.files_changed.emit(list(self.checked_files))

            # 시그널 재연결
            self.model.itemChanged.connect(self._on_item_changed)

    def _deselect_all(self):
        """전체 해제"""
        root_item = self.model.item(0, 0)
        if root_item:
            # 시그널 차단
            self.model.itemChanged.disconnect(self._on_item_changed)

            root_item.setCheckState(Qt.Unchecked)
            self._check_children_recursive(root_item, Qt.Unchecked)

            # 정보 레이블 업데이트
            self.info_label.setText(
                f"📊 총 {len(self.all_files)}개 파일 | "
                f"✅ {len(self.checked_files)}개 선택됨"
            )

            # 시그널 발생
            self.files_changed.emit(list(self.checked_files))

            # 시그널 재연결
            self.model.itemChanged.connect(self._on_item_changed)

    def _format_size(self, size: int) -> str:
        """파일 크기를 읽기 쉬운 형식으로 변환"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def get_selected_files(self) -> List[str]:
        """선택된 파일 경로 목록 반환"""
        return list(self.checked_files)

    def clear(self):
        """선택 초기화"""
        self.selected_folder = None
        self.all_files = []
        self.checked_files = set()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["파일/폴더", "개수"])
        self.folder_label.setText("📁 선택된 폴더: 없음")
        self.info_label.setText("💡 폴더를 선택하면 C# 파일 목록이 표시됩니다")
        self.select_all_btn.setEnabled(False)
        self.deselect_all_btn.setEnabled(False)
        self.tree_view.setEnabled(False)
