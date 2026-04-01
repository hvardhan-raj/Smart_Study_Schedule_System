from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from backend import StudyFlowBackend


def main() -> int:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    project_dir = Path(__file__).resolve().parent
    backend = StudyFlowBackend(project_dir / "studyflow_data.json")
    engine.rootContext().setContextProperty("backend", backend)
    engine.addImportPath(str(project_dir))
    engine.load(str(project_dir / "Main.qml"))

    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
