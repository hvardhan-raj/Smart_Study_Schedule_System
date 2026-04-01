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
            pageTitle: "Revision Schedule"
            pageSubtitle: "SPACED REPETITION PLANNER"
            rightContent: [
                AppButton { label: "Regenerate"; variant: "secondary"; small: true },
                AppButton { label: "Export"; variant: "secondary"; small: true },
                AppButton { label: "+ Add Session"; variant: "primary"; small: true }
            ]
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: availableWidth
            clip: true

            ColumnLayout {
                width: parent.width
                spacing: 0

                RowLayout {
                    Layout.fillWidth: true
                    Layout.margins: 24
                    spacing: 16

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 3
                        implicitHeight: calGrid.implicitHeight + 32
                        radius: 12
                        color: "#FFFFFF"

                        ColumnLayout {
                            id: calGrid
                            anchors { fill: parent; margins: 20 }
                            spacing: 12

                            RowLayout {
                                Text { text: "<"; font.pixelSize: 14; color: "#64748B" }
                                Text { text: backend.scheduleTitle; font.pixelSize: 13; font.bold: true; color: "#1A2332"; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                                Text { text: ">"; font.pixelSize: 14; color: "#64748B" }
                            }

                            RowLayout {
                                spacing: 8

                                Repeater {
                                    model: backend.scheduleDays

                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        implicitHeight: dayCol.implicitHeight + 16
                                        radius: 10
                                        color: modelData.isCurrent ? "#EFF6FF" : "#F8FAFC"
                                        border.color: modelData.isCurrent ? "#BFDBFE" : "#E2E8F0"

                                        ColumnLayout {
                                            id: dayCol
                                            anchors { fill: parent; margins: 10 }
                                            spacing: 6

                                            Text { text: modelData.day; font.pixelSize: 9; font.letterSpacing: 1.2; color: "#94A3B8"; Layout.alignment: Qt.AlignHCenter }
                                            Text { text: modelData.date; font.pixelSize: 16; font.bold: true; color: modelData.isCurrent ? "#3B82F6" : "#1A2332"; Layout.alignment: Qt.AlignHCenter }
                                            Rectangle { Layout.fillWidth: true; height: 1; color: "#E2E8F0" }

                                            Repeater {
                                                model: modelData.tasks
                                                delegate: Rectangle {
                                                    Layout.fillWidth: true
                                                    height: 28
                                                    radius: 6
                                                    color: ["#EFF6FF","#ECFDF5","#F5F3FF","#FFFBEB","#FEF2F2"][index % 5]
                                                    Text {
                                                        anchors.fill: parent
                                                        anchors.leftMargin: 6
                                                        anchors.rightMargin: 6
                                                        text: modelData
                                                        font.pixelSize: 9
                                                        color: "#374151"
                                                        elide: Text.ElideRight
                                                        verticalAlignment: Text.AlignVCenter
                                                    }
                                                }
                                            }

                                            Text { visible: modelData.tasks.length === 0; text: "-"; font.pixelSize: 11; color: "#CBD5E1"; Layout.alignment: Qt.AlignHCenter }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 1
                        spacing: 14

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: dueList.implicitHeight + 32
                            radius: 12
                            color: "#FFFFFF"

                            ColumnLayout {
                                id: dueList
                                anchors { fill: parent; margins: 20 }
                                spacing: 8

                                RowLayout {
                                    Text { text: "Next Due"; font.pixelSize: 13; font.bold: true; color: "#1A2332" }
                                    Item { Layout.fillWidth: true }
                                    Text { text: "View all"; font.pixelSize: 10; color: "#3B82F6" }
                                }

                                Repeater {
                                    model: backend.nextDueTasks
                                    delegate: RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 8
                                        Rectangle { width: 6; height: 6; radius: 3; color: modelData.color }
                                        Text { Layout.fillWidth: true; text: modelData.name; font.pixelSize: 11; color: "#374151"; elide: Text.ElideRight }
                                        Text { text: modelData.when; font.pixelSize: 10; color: "#94A3B8" }
                                    }
                                }
                            }
                        }

                        Rectangle {
                            visible: backend.aiSuggestion.visible
                            Layout.fillWidth: true
                            height: 110
                            radius: 12
                            color: "#EFF6FF"
                            border.color: "#BFDBFE"

                            ColumnLayout {
                                anchors { fill: parent; margins: 16 }
                                spacing: 6

                                RowLayout {
                                    Text { text: "AI"; font.pixelSize: 14 }
                                    Text { text: "AI Suggestion"; font.pixelSize: 12; font.bold: true; color: "#1D4ED8" }
                                }

                                Text { text: backend.aiSuggestion.text; font.pixelSize: 11; color: "#1E40AF"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                RowLayout {
                                    AppButton { label: "Accept"; variant: "primary"; small: true; onClicked: backend.acceptSuggestion() }
                                    AppButton { label: "Dismiss"; variant: "ghost"; small: true; onClicked: backend.dismissSuggestion() }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 130
                            radius: 12
                            color: "#FFFFFF"

                            ColumnLayout {
                                anchors { fill: parent; margins: 16 }
                                spacing: 6
                                Text { text: "Week Completion"; font.pixelSize: 13; font.bold: true; color: "#1A2332" }

                                RowLayout {
                                    spacing: 16

                                    Rectangle {
                                        width: 70; height: 70; radius: 35
                                        color: "#EFF6FF"
                                        Rectangle {
                                            width: 52; height: 52; radius: 26
                                            color: "#FFFFFF"; anchors.centerIn: parent
                                            Text { anchors.centerIn: parent; text: backend.weekCompletion.score + "%"; font.pixelSize: 16; font.bold: true; color: "#3B82F6" }
                                        }
                                    }

                                    ColumnLayout {
                                        spacing: 4
                                        Repeater {
                                            model: [
                                                { lbl: "Completed", val: backend.weekCompletion.completed, col: "#10B981" },
                                                { lbl: "Remaining", val: backend.weekCompletion.remaining, col: "#F59E0B" },
                                                { lbl: "Missed", val: backend.weekCompletion.missed, col: "#EF4444" }
                                            ]
                                            delegate: RowLayout {
                                                spacing: 6
                                                Rectangle { width: 8; height: 8; radius: 4; color: modelData.col }
                                                Text { text: modelData.lbl; font.pixelSize: 11; color: "#64748B" }
                                                Text { text: modelData.val; font.pixelSize: 11; font.bold: true; color: "#1A2332" }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
