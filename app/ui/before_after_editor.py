"""
Before/After Split Code Editor

This module provides a split-view code editor with Before (input) and After (output) panels.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPlainTextEdit, QPushButton, QLabel, QFrame, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QRect, QSize
from PySide6.QtGui import QFont, QTextCursor, QColor, QPainter, QTextFormat

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.utils.syntax_highlighter import CSharpSyntaxHighlighter


class LineNumberArea(QWidget):
    """Line number area widget for CodeEditor."""

    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        """Return size hint for line number area."""
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        """Paint line numbers."""
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Enhanced QPlainTextEdit for code editing with line numbers and syntax highlighting."""

    def __init__(self, parent=None, read_only=False):
        super().__init__(parent)

        # Set monospace font
        font = QFont("Monaco, Consolas, Courier New", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Configure editor
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(40)  # 4 spaces
        self.setReadOnly(read_only)

        # Placeholder text
        if not read_only:
            self.setPlaceholderText("Paste your C# code here...")

        # Line number area
        self.line_number_area = LineNumberArea(self)

        # Connect signals for line number updates
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # Initialize line number area
        self.update_line_number_area_width(0)
        self.highlight_current_line()

        # Syntax highlighter (will be set by EditorPanel)
        self.highlighter = None

    def line_number_area_width(self):
        """Calculate width for line number area."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        # Width = 10px padding + digit width + 10px padding
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits + 10
        return space

    def update_line_number_area_width(self, _):
        """Update viewport margins when line count changes."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Update line number area when editor scrolls."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def highlight_current_line(self):
        """Highlight the current line."""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2a2a2a")  # Slightly lighter than background

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def line_number_area_paint_event(self, event):
        """Paint line numbers in the line number area."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#252526"))  # Dark background

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Draw line numbers
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))  # Gray text
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1


class EditorPanel(QWidget):
    """Single editor panel with label and copy button."""

    copy_clicked = Signal()  # Signal emitted when copy button is clicked

    def __init__(self, title: str, read_only: bool = False, parent=None):
        super().__init__(parent)

        self.title = title
        self.read_only = read_only

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Header with title and copy button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 5, 5, 5)

        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Copy button
        self.copy_button = QPushButton("📋 Copy")
        self.copy_button.setFixedWidth(80)
        self.copy_button.clicked.connect(self.copy_clicked)
        header_layout.addWidget(self.copy_button)

        layout.addLayout(header_layout)

        # Editor
        self.editor = CodeEditor(read_only=read_only)

        # Apply syntax highlighter
        self.highlighter = CSharpSyntaxHighlighter(self.editor.document())

        layout.addWidget(self.editor)

    def get_text(self) -> str:
        """Get editor text content."""
        return self.editor.toPlainText()

    def set_text(self, text: str):
        """Set editor text content."""
        self.editor.setPlainText(text)

    def clear(self):
        """Clear editor content."""
        self.editor.clear()

    def copy_to_clipboard(self):
        """Copy editor content to clipboard."""
        self.editor.selectAll()
        self.editor.copy()
        # Clear selection
        cursor = self.editor.textCursor()
        cursor.clearSelection()
        self.editor.setTextCursor(cursor)


class BeforeAfterEditor(QWidget):
    """Split-view code editor with Before and After panels."""

    # Signals
    before_text_changed = Signal(str)  # Emitted when before text changes
    after_text_changed = Signal(str)   # Emitted when after text changes

    def __init__(self, parent=None):
        super().__init__(parent)

        # Scroll synchronization state
        self.scroll_sync_enabled = True
        self._is_syncing = False  # Prevent infinite loop

        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Control bar for scroll sync toggle
        control_bar = QHBoxLayout()
        control_bar.setContentsMargins(5, 0, 5, 5)

        # Scroll sync checkbox
        self.sync_checkbox = QCheckBox("Synchronize Scrolling")
        self.sync_checkbox.setChecked(True)
        self.sync_checkbox.setStyleSheet("font-size: 12px;")
        self.sync_checkbox.stateChanged.connect(self._on_sync_toggle)
        control_bar.addWidget(self.sync_checkbox)

        control_bar.addStretch()

        layout.addLayout(control_bar)

        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Before panel (editable)
        self.before_panel = EditorPanel("Before (Original Code)", read_only=False)
        self.before_panel.copy_clicked.connect(self._on_before_copy)
        self.before_panel.editor.textChanged.connect(self._on_before_text_changed)

        # After panel (read-only)
        self.after_panel = EditorPanel("After (Improved Code)", read_only=True)
        self.after_panel.copy_clicked.connect(self._on_after_copy)
        self.after_panel.editor.textChanged.connect(self._on_after_text_changed)

        # Connect scroll events for synchronization
        self.before_panel.editor.verticalScrollBar().valueChanged.connect(self._on_before_scroll)
        self.after_panel.editor.verticalScrollBar().valueChanged.connect(self._on_after_scroll)

        # Add panels to splitter
        self.splitter.addWidget(self.before_panel)
        self.splitter.addWidget(self.after_panel)

        # Set equal split (50:50)
        self.splitter.setSizes([1000, 1000])

        # Add splitter to layout
        layout.addWidget(self.splitter)

    def get_before_text(self) -> str:
        """Get text from Before editor."""
        return self.before_panel.get_text()

    def get_after_text(self) -> str:
        """Get text from After editor."""
        return self.after_panel.get_text()

    def set_before_text(self, text: str):
        """Set text in Before editor."""
        self.before_panel.set_text(text)

    def set_after_text(self, text: str):
        """Set text in After editor."""
        self.after_panel.set_text(text)

    def clear_before(self):
        """Clear Before editor."""
        self.before_panel.clear()

    def clear_after(self):
        """Clear After editor."""
        self.after_panel.clear()

    def clear_all(self):
        """Clear both editors."""
        self.clear_before()
        self.clear_after()

    def _on_before_copy(self):
        """Handle Before copy button click."""
        self.before_panel.copy_to_clipboard()

    def _on_after_copy(self):
        """Handle After copy button click."""
        self.after_panel.copy_to_clipboard()

    def _on_before_text_changed(self):
        """Handle Before text changed."""
        text = self.get_before_text()
        self.before_text_changed.emit(text)

    def _on_after_text_changed(self):
        """Handle After text changed."""
        text = self.get_after_text()
        self.after_text_changed.emit(text)

    def _on_sync_toggle(self, state):
        """Handle scroll sync checkbox toggle."""
        self.scroll_sync_enabled = (state == Qt.CheckState.Checked.value)

    def _on_before_scroll(self, value):
        """Handle Before editor scroll event."""
        if self.scroll_sync_enabled and not self._is_syncing:
            self._is_syncing = True
            self._sync_scroll(self.before_panel.editor, self.after_panel.editor)
            self._is_syncing = False

    def _on_after_scroll(self, value):
        """Handle After editor scroll event."""
        if self.scroll_sync_enabled and not self._is_syncing:
            self._is_syncing = True
            self._sync_scroll(self.after_panel.editor, self.before_panel.editor)
            self._is_syncing = False

    def _sync_scroll(self, source_editor, target_editor):
        """Synchronize scroll position from source to target editor."""
        source_scrollbar = source_editor.verticalScrollBar()
        target_scrollbar = target_editor.verticalScrollBar()

        # Get scroll position as percentage
        source_max = source_scrollbar.maximum()
        target_max = target_scrollbar.maximum()

        if source_max > 0:
            # Calculate percentage of scroll
            percentage = source_scrollbar.value() / source_max

            # Apply to target
            if target_max > 0:
                target_value = int(percentage * target_max)
                target_scrollbar.setValue(target_value)


# Test the editor
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create editor
    editor = BeforeAfterEditor()
    editor.setWindowTitle("Before/After Code Editor Test")
    editor.resize(1200, 600)

    # Set sample text
    before_code = """using System;

public class Example
{
    public void ProcessData(string data)
    {
        var result = data.ToUpper();
        Console.WriteLine(result);
    }
}"""

    after_code = """using System;

public class Example
{
    public void ProcessData(string data)
    {
        if (string.IsNullOrEmpty(data))
            throw new ArgumentNullException(nameof(data));

        var result = data.ToUpper();
        Console.WriteLine(result);
    }
}"""

    editor.set_before_text(before_code)
    editor.set_after_text(after_code)

    editor.show()

    sys.exit(app.exec())
