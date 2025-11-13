"""
C# Syntax Highlighter for Code Editor

This module provides syntax highlighting for C# code using QSyntaxHighlighter.
Color scheme based on VS Code Dark+ theme.
"""

from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression
import re


class CSharpSyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for C# code.

    Color scheme (VS Code Dark+):
    - Keywords: #569CD6 (blue)
    - Strings: #CE9178 (orange)
    - Comments: #6A9955 (green)
    - Numbers: #B5CEA8 (light green)
    - Classes/Types: #4EC9B0 (cyan)
    - Functions: #DCDCAA (yellow)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Define text formats
        self.highlighting_rules = []

        # Keyword format (blue)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        # C# keywords
        keywords = [
            'abstract', 'as', 'base', 'bool', 'break', 'byte', 'case', 'catch',
            'char', 'checked', 'class', 'const', 'continue', 'decimal', 'default',
            'delegate', 'do', 'double', 'else', 'enum', 'event', 'explicit',
            'extern', 'false', 'finally', 'fixed', 'float', 'for', 'foreach',
            'goto', 'if', 'implicit', 'in', 'int', 'interface', 'internal',
            'is', 'lock', 'long', 'namespace', 'new', 'null', 'object',
            'operator', 'out', 'override', 'params', 'private', 'protected',
            'public', 'readonly', 'ref', 'return', 'sbyte', 'sealed', 'short',
            'sizeof', 'stackalloc', 'static', 'string', 'struct', 'switch',
            'this', 'throw', 'true', 'try', 'typeof', 'uint', 'ulong',
            'unchecked', 'unsafe', 'ushort', 'using', 'var', 'virtual', 'void',
            'volatile', 'while'
        ]

        for keyword in keywords:
            pattern = QRegularExpression(r'\b' + keyword + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))

        # Class/Type format (cyan)
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))

        # Match PascalCase identifiers (likely classes/types)
        class_pattern = QRegularExpression(r'\b[A-Z][a-zA-Z0-9]*\b')
        self.highlighting_rules.append((class_pattern, class_format))

        # Function format (yellow)
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))

        # Match function calls: identifier followed by (
        function_pattern = QRegularExpression(r'\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()')
        self.highlighting_rules.append((function_pattern, function_format))

        # String format (orange)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))

        # Match strings: "..." or @"..."
        string_pattern = QRegularExpression(r'@?"(?:[^"\\]|\\.)*"')
        self.highlighting_rules.append((string_pattern, string_format))

        # Character format (orange)
        char_format = QTextCharFormat()
        char_format.setForeground(QColor("#CE9178"))

        # Match characters: '.'
        char_pattern = QRegularExpression(r"'(?:[^'\\]|\\.)'")
        self.highlighting_rules.append((char_pattern, char_format))

        # Number format (light green)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))

        # Match numbers: integers, floats, hex
        number_pattern = QRegularExpression(r'\b(?:0[xX][0-9a-fA-F]+|\d+\.?\d*[fFdDmM]?)\b')
        self.highlighting_rules.append((number_pattern, number_format))

        # Single-line comment format (green)
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6A9955"))
        self.comment_format.setFontItalic(True)

        comment_pattern = QRegularExpression(r'//[^\n]*')
        self.highlighting_rules.append((comment_pattern, self.comment_format))

        # Multi-line comment format (green)
        self.multiline_comment_format = QTextCharFormat()
        self.multiline_comment_format.setForeground(QColor("#6A9955"))
        self.multiline_comment_format.setFontItalic(True)

        self.comment_start_expression = QRegularExpression(r'/\*')
        self.comment_end_expression = QRegularExpression(r'\*/')

        # Preprocessor directives format (gray)
        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor("#9B9B9B"))

        preprocessor_pattern = QRegularExpression(r'^\s*#.*$')
        self.highlighting_rules.append((preprocessor_pattern, preprocessor_format))

        # XML documentation comment format (green)
        xml_doc_format = QTextCharFormat()
        xml_doc_format.setForeground(QColor("#6A9955"))
        xml_doc_format.setFontItalic(True)

        xml_doc_pattern = QRegularExpression(r'///[^\n]*')
        self.highlighting_rules.append((xml_doc_pattern, xml_doc_format))

    def highlightBlock(self, text):
        """
        Highlight a single block of text.

        Args:
            text: The text to highlight
        """
        # Apply all single-line highlighting rules
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, format)

        # Handle multi-line comments
        self.setCurrentBlockState(0)

        start_index = 0
        if self.previousBlockState() != 1:
            match = self.comment_start_expression.match(text)
            start_index = match.capturedStart() if match.hasMatch() else -1

        while start_index >= 0:
            match = self.comment_end_expression.match(text, start_index)
            if match.hasMatch():
                end_index = match.capturedStart()
                comment_length = end_index - start_index + match.capturedLength()
                self.setFormat(start_index, comment_length, self.multiline_comment_format)

                # Look for next comment start
                match = self.comment_start_expression.match(text, start_index + comment_length)
                start_index = match.capturedStart() if match.hasMatch() else -1
            else:
                # Comment continues to next block
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
                self.setFormat(start_index, comment_length, self.multiline_comment_format)
                break


# Test the highlighter
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QPlainTextEdit, QVBoxLayout, QWidget

    app = QApplication(sys.argv)

    # Create test widget
    widget = QWidget()
    widget.setWindowTitle("C# Syntax Highlighter Test")
    widget.resize(800, 600)

    layout = QVBoxLayout(widget)

    # Create editor
    editor = QPlainTextEdit()
    font = QFont("Monaco, Consolas", 12)
    font.setStyleHint(QFont.StyleHint.Monospace)
    editor.setFont(font)

    # Apply syntax highlighter
    highlighter = CSharpSyntaxHighlighter(editor.document())

    # Set test code
    test_code = """using System;
using System.Collections.Generic;

namespace TestNamespace
{
    /// <summary>
    /// Test class for syntax highlighting
    /// </summary>
    public class TestClass
    {
        private int _value = 42;
        private string _name = "Hello, World!";

        // This is a single-line comment
        public void ProcessData(string data)
        {
            if (string.IsNullOrEmpty(data))
            {
                throw new ArgumentNullException(nameof(data));
            }

            /* This is a
               multi-line comment */
            var result = data.ToUpper();
            Console.WriteLine(result);

            #if DEBUG
            Console.WriteLine("Debug mode");
            #endif
        }

        public int Calculate(int x, int y)
        {
            double z = 3.14159;
            int hex = 0xFF00;
            char c = 'A';

            return x + y + (int)z;
        }
    }
}"""

    editor.setPlainText(test_code)
    layout.addWidget(editor)

    widget.show()
    sys.exit(app.exec())
