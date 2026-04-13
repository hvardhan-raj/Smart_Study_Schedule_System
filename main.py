from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from backend import StudyFlowBackend
from config.logging import configure_logging
from config.settings import settings
from ui import NavigationController


def main() -> int:
    logger = configure_logging()
    settings.ensure_directories()

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    project_dir = Path(__file__).resolve().parent
    backend = StudyFlowBackend(project_dir / "studyflow_data.json")
    navigation = NavigationController()
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("navigation", navigation)
    engine.addImportPath(str(project_dir))
    engine.load(str(project_dir / "Main.qml"))
    logger.info("Application startup completed")

    if not engine.rootObjects():
        logger.error("No QML root objects were loaded")
        return 1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
