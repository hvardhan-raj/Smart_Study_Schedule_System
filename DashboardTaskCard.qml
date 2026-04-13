import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property var taskData: ({})
    property color accentColor: "#3B82F6"

    radius: 14
    color: "#FFFFFF"
    border.width: 1
    border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.18)
    implicitHeight: cardContent.implicitHeight + 28

    ColumnLayout {
        id: cardContent
        anchors.fill: parent
        anchors.margins: 14
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            TagPill {
                tagText: taskData.subjectShort || taskData.subject || ""
                tagColor: taskData.subjectColor || "#64748B"
            }

            TagPill {
                tagText: taskData.difficulty || ""
                tagColor: taskData.difficultyColor || "#64748B"
                outlined: true
            }

            Item { Layout.fillWidth: true }

            Text {
                text: (taskData.urgencyScore || 0) + " pts"
                font.pixelSize: 10
                color: "#94A3B8"
            }
        }

        Text {
            Layout.fillWidth: true
            text: taskData.name || ""
            wrapMode: Text.WordWrap
            font.pixelSize: 14
            font.bold: true
            color: "#1A2332"
        }

        Text {
            Layout.fillWidth: true
            text: taskData.scheduledText || ""
            wrapMode: Text.WordWrap
            font.pixelSize: 11
            color: "#64748B"
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Rectangle {
                radius: 8
                color: "#F8FAFC"
                border.color: "#E2E8F0"
                border.width: 1
                implicitWidth: confidenceText.implicitWidth + 14
                implicitHeight: 24

                Text {
                    id: confidenceText
                    anchors.centerIn: parent
                    text: taskData.confidenceLabel || ""
                    font.pixelSize: 10
                    color: "#475569"
                }
            }

            Item { Layout.fillWidth: true }

            TagPill {
                tagText: taskData.status || ""
                tagColor: taskData.statusColor || accentColor
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            Repeater {
                model: [
                    { label: "Again", rating: 1, color: "#EF4444" },
                    { label: "Hard", rating: 2, color: "#F59E0B" },
                    { label: "Good", rating: 3, color: "#10B981" },
                    { label: "Easy", rating: 4, color: "#3B82F6" }
                ]

                delegate: Rectangle {
                    radius: 9
                    color: taskData.isCompleted ? "#E2E8F0" : Qt.rgba(modelData.color.r, modelData.color.g, modelData.color.b, 0.12)
                    border.width: 1
                    border.color: taskData.isCompleted ? "#CBD5E1" : Qt.rgba(modelData.color.r, modelData.color.g, modelData.color.b, 0.24)
                    implicitWidth: labelText.implicitWidth + 14
                    implicitHeight: 28

                    Text {
                        id: labelText
                        anchors.centerIn: parent
                        text: modelData.label
                        font.pixelSize: 10
                        font.bold: true
                        color: taskData.isCompleted ? "#64748B" : modelData.color
                    }

                    MouseArea {
                        anchors.fill: parent
                        enabled: !taskData.isCompleted
                        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                        onClicked: backend.completeRevision(taskData.id, modelData.rating)
                    }
                }
            }
        }
    }
}
