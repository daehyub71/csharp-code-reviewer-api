"""
C# Code Reviewer - Main Application Entry Point

This is the main entry point for the C# Code Reviewer application.
It initializes the PySide6 QApplication and creates the main window.

Features:
- OpenAI GPT / Anthropic Claude API integration
- High DPI scaling
- Dark theme stylesheet
- Environment variable configuration
"""

import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ui.main_window import MainWindow


# Ensure logs directory exists
logs_dir = Path("logs")
logs_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_api_configuration() -> tuple[bool, str]:
    """
    Check if API keys are configured

    Returns:
        Tuple of (is_configured, message)
    """
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')

    if not openai_key and not anthropic_key:
        return False, (
            "No API keys configured!\n\n"
            "Please set either:\n"
            "- OPENAI_API_KEY (for GPT models)\n"
            "- ANTHROPIC_API_KEY (for Claude models)\n\n"
            "Create a .env file in the project root:\n"
            "OPENAI_API_KEY=sk-...\n"
            "or\n"
            "ANTHROPIC_API_KEY=sk-ant-..."
        )

    if openai_key:
        logger.info("✓ OpenAI API key configured")
    if anthropic_key:
        logger.info("✓ Anthropic API key configured")

    return True, ""


def main():
    """Main application entry point."""

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create the application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("C# Code Reviewer (API)")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Code Review Team")

    # Load stylesheet
    stylesheet_path = Path(__file__).parent.parent / "resources" / "styles" / "dark_theme.qss"
    if stylesheet_path.exists():
        with open(stylesheet_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())

    logger.info("=" * 80)
    logger.info("C# Code Reviewer (API Version) starting...")
    logger.info("=" * 80)

    # Check API configuration
    is_configured, error_message = check_api_configuration()

    if not is_configured:
        logger.error("API keys not configured")
        QMessageBox.critical(
            None,
            "API Configuration Missing",
            error_message
        )
        sys.exit(1)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    exit_code = app.exec()

    logger.info("Application shutting down...")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
