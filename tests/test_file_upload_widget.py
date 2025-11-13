"""
FileUploadWidget 단위 테스트

파일 업로드 위젯의 주요 기능을 테스트합니다.
"""

import pytest
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# 프로젝트 루트를 PYTHONPATH에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.ui.file_upload_widget import FileUploadWidget, FileListWidget


@pytest.fixture(scope="module")
def qapp():
    """QApplication fixture"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def widget(qapp):
    """FileUploadWidget fixture"""
    w = FileUploadWidget()
    yield w
    w.close()


@pytest.fixture
def test_cs_file(tmp_path):
    """테스트용 C# 파일 생성"""
    cs_file = tmp_path / "Test.cs"
    cs_file.write_text(
        "public class Test { public void Method() { } }",
        encoding='utf-8'
    )
    return str(cs_file)


@pytest.fixture
def large_cs_file(tmp_path):
    """크기 제한 초과 파일 생성 (1MB+)"""
    cs_file = tmp_path / "Large.cs"
    content = "// Large file\n" * 100000  # ~1.4MB
    cs_file.write_text(content, encoding='utf-8')
    return str(cs_file)


@pytest.fixture
def non_utf8_file(tmp_path):
    """UTF-8이 아닌 파일 생성"""
    cs_file = tmp_path / "NonUTF8.cs"
    cs_file.write_bytes(b'\xff\xfe\x00\x00')  # Invalid UTF-8
    return str(cs_file)


class TestFileUploadWidget:
    """FileUploadWidget 테스트 클래스"""

    def test_initial_state(self, widget):
        """초기 상태 확인"""
        assert widget.selected_files == []
        assert widget.counter_label.text() == "총 0개 파일"
        assert not widget.remove_btn.isEnabled()
        assert not widget.clear_btn.isEnabled()

    def test_add_valid_file(self, widget, test_cs_file):
        """유효한 파일 추가 테스트"""
        # 프로그래밍 방식으로 파일 추가 (UI 다이얼로그 없이)
        is_valid, error_msg = widget._validate_file(test_cs_file)

        assert is_valid
        assert error_msg == ""

    def test_add_invalid_extension(self, widget, tmp_path):
        """잘못된 확장자 파일 거부 테스트"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("test", encoding='utf-8')

        is_valid, error_msg = widget._validate_file(str(txt_file))

        assert not is_valid
        assert "C# 파일(.cs)이 아닙니다" in error_msg

    def test_add_large_file(self, widget, large_cs_file):
        """크기 초과 파일 거부 테스트"""
        is_valid, error_msg = widget._validate_file(large_cs_file)

        assert not is_valid
        assert "초과합니다" in error_msg

    def test_add_non_utf8_file(self, widget, non_utf8_file):
        """UTF-8이 아닌 파일 거부 테스트"""
        is_valid, error_msg = widget._validate_file(non_utf8_file)

        assert not is_valid
        assert "UTF-8 인코딩" in error_msg or "파일 읽기 오류" in error_msg

    def test_add_nonexistent_file(self, widget):
        """존재하지 않는 파일 거부 테스트"""
        is_valid, error_msg = widget._validate_file("/nonexistent/file.cs")

        assert not is_valid
        assert "존재하지 않습니다" in error_msg

    def test_get_selected_files(self, widget, test_cs_file):
        """선택된 파일 목록 조회 테스트"""
        # 파일 추가
        widget.selected_files.append(test_cs_file)

        files = widget.get_selected_files()

        assert len(files) == 1
        assert files[0] == test_cs_file

    def test_clear_files(self, widget, test_cs_file):
        """파일 전체 제거 테스트"""
        # 파일 추가
        widget.selected_files.append(test_cs_file)
        widget._add_list_item(test_cs_file)

        # 전체 제거
        widget.clear_files()

        assert len(widget.selected_files) == 0
        assert widget.file_list.count() == 1  # Placeholder item

    def test_format_size(self, widget):
        """파일 크기 포맷팅 테스트"""
        assert widget._format_size(100) == "100.0 B"
        assert widget._format_size(1024) == "1.0 KB"
        assert widget._format_size(1024 * 1024) == "1.0 MB"
        assert widget._format_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_files_changed_signal(self, widget, test_cs_file, qtbot):
        """파일 변경 시그널 테스트"""
        # 시그널 스파이 생성
        with qtbot.waitSignal(widget.files_changed, timeout=1000) as blocker:
            widget.selected_files.append(test_cs_file)
            widget.files_changed.emit(widget.selected_files)

        # 시그널이 발생했는지 확인
        assert blocker.signal_triggered
        assert len(blocker.args[0]) == 1


class TestFileListWidget:
    """FileListWidget 테스트 클래스"""

    @pytest.fixture
    def file_list(self, qapp):
        """FileListWidget fixture"""
        widget = FileListWidget()
        yield widget
        widget.close()

    def test_initial_state(self, file_list):
        """초기 상태 확인"""
        assert file_list.acceptDrops()
        assert not file_list._is_drag_active

    def test_update_drag_style(self, file_list):
        """드래그 스타일 업데이트 테스트"""
        # 드래그 활성화
        file_list._update_drag_style(True)
        # 스타일이 변경되었는지 확인 (스타일시트에 파란색 포함)
        assert "#094771" in file_list.styleSheet() or "#0e639c" in file_list.styleSheet()

        # 드래그 비활성화
        file_list._update_drag_style(False)
        # 기본 스타일로 복원 (회색 배경)
        assert "#252526" in file_list.styleSheet()


# 통합 테스트
class TestIntegration:
    """통합 테스트"""

    def test_full_workflow(self, widget, test_cs_file, tmp_path):
        """전체 워크플로우 테스트"""
        # 1. 초기 상태
        assert len(widget.selected_files) == 0

        # 2. 유효한 파일 추가
        cs_file2 = tmp_path / "Test2.cs"
        cs_file2.write_text("public class Test2 { }", encoding='utf-8')

        widget.selected_files.append(test_cs_file)
        widget._add_list_item(test_cs_file)

        widget.selected_files.append(str(cs_file2))
        widget._add_list_item(str(cs_file2))

        # 3. 파일 개수 확인
        assert len(widget.selected_files) == 2

        # 4. 파일 목록 조회
        files = widget.get_selected_files()
        assert len(files) == 2

        # 5. 전체 제거
        widget.clear_files()
        assert len(widget.selected_files) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
