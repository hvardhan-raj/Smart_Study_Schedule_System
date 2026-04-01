import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
    color: "#F4F6FA"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        PageHeader {
            Layout.fillWidth: true
            pageTitle: "Task Inbox"
            pageSubtitle: "PENDING REVISIONS"
            rightContent: [
                AppButton { label: "Mark All Done"; variant: "secondary"; small: true; onClicked: backend.markAllTasksDone() },
                AppButton { label: "+ Add Task"; variant: "primary"; small: true }
            ]
        }

        Rectangle {
            Layout.fillWidth: true
            height: 44
            color: "#FFFFFF"
            border.color: "#E2E8F0"

            RowLayout {
                anchors { fill: parent; leftMargin: 24 }
                spacing: 0

                Repeater {
                    model: backend.taskFilters
                    delegate: Item {
                        height: 44
                        implicitWidth: tabLbl.implicitWidth + 32

                        Rectangle { visible: modelData.active; anchors.bottom: parent.bottom; width: parent.width; height: 2; color: "#3B82F6" }

                        Text {
                            id: tabLbl
                            anchors.centerIn: parent
                            text: modelData.label
                            font.pixelSize: 12
                            font.bold: modelData.active
                            color: modelData.active ? "#3B82F6" : "#64748B"
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: backend.setTaskFilter(modelData.key)
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                Rectangle {
                    width: 130; height: 28; radius: 6
                    color: "#F4F6FA"; border.color: "#E2E8F0"
                    Layout.alignment: Qt.AlignVCenter
                    RowLayout {
                        anchors { fill: parent; leftMargin: 10; rightMargin: 10 }
                        Text { text: "All Subjects"; font.pixelSize: 11; color: "#64748B" }
                        Item { Layout.fillWidth: true }
                        Text { text: "v"; font.pixelSize: 10; color: "#94A3B8" }
                    }
                }
                Item { width: 24 }
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: availableWidth
            clip: true

            ColumnLayout {
                width: parent.width
                spacing: 0

                Rectangle {
                    Layout.fillWidth: true
                    height: 36
                    color: "#F8FAFC"
                    border.color: "#E2E8F0"

                    RowLayout {
                        anchors { fill: parent; leftMargin: 24; rightMargin: 24 }
                        spacing: 0

                        Rectangle { width: 16; height: 16; radius: 4; color: "transparent"; border.color: "#CBD5E1"; border.width: 1 }
                        Item { width: 12 }

                        Repeater {
                            model: [
                                { lbl: "TOPIC / SUBJECT", fw: 3 },
                                { lbl: "DIFFICULTY", fw: 1 },
                                { lbl: "SCHEDULED", fw: 1 },
                                { lbl: "CONFIDENCE", fw: 1 },
                                { lbl: "STATUS", fw: 1 },
                                { lbl: "ACTIONS", fw: 1 }
                            ]
                            delegate: Text {
                                Layout.fillWidth: modelData.fw > 1
                                Layout.preferredWidth: modelData.fw === 1 ? 80 : -1
                                text: modelData.lbl
                                font.pixelSize: 9
                                font.letterSpacing: 1
                                color: "#94A3B8"
                            }
                        }
                    }
                }

                Repeater {
                    model: backend.inboxTasks

                    delegate: Rectangle {
                        property int taskConfidence: modelData.confidence
                        Layout.fillWidth: true
                        height: 56
                        color: index % 2 === 0 ? "#FFFFFF" : "#FAFBFD"
                        border.color: "#F1F5F9"

                        RowLayout {
                            anchors { fill: parent; leftMargin: 24; rightMargin: 24 }
                            spacing: 0

                            Rectangle { width: 16; height: 16; radius: 4; color: "transparent"; border.color: "#CBD5E1"; border.width: 1 }
                            Item { width: 12 }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                Text { text: modelData.topic; font.pixelSize: 12; font.bold: true; color: "#1A2332"; elide: Text.ElideRight }
                                TagPill { tagText: modelData.subjectShort; tagColor: modelData.subjectColor; implicitHeight: 16 }
                            }

                            TagPill { Layout.preferredWidth: 80; tagText: modelData.difficulty; tagColor: modelData.difficultyColor }
                            Text { Layout.preferredWidth: 80; text: modelData.scheduledText; font.pixelSize: 11; color: "#64748B"; elide: Text.ElideRight }

                            Row {
                                Layout.preferredWidth: 80
                                spacing: 2
                                Repeater {
                                    model: 5
                                    Text { text: "*"; font.pixelSize: 12; color: index < taskConfidence ? "#F59E0B" : "#E2E8F0" }
                                }
                            }

                            TagPill { Layout.preferredWidth: 80; tagText: modelData.status; tagColor: modelData.statusColor }

                            RowLayout {
                                Layout.preferredWidth: 92
                                spacing: 6
                                AppButton { label: "Review"; variant: "primary"; small: true; onClicked: backend.markTaskDone(modelData.id) }
                                AppButton { label: "Skip"; variant: "secondary"; small: true; onClicked: backend.skipTask(modelData.id) }
                            }
                        }
                    }
                }
            }
        }
    }
}
