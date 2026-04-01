import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    color: "#F4F6FA"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        PageHeader {
            Layout.fillWidth: true
            pageTitle: "Curriculum Map"
            pageSubtitle: "ALL SUBJECTS & TOPICS"
            rightContent: [
                AppButton { label: "+ Add Subject"; variant: "secondary"; small: true },
                AppButton { label: "+ Add Topic"; variant: "primary"; small: true }
            ]
        }

        Rectangle {
            Layout.fillWidth: true
            height: 52
            color: "#FFFFFF"
            border.color: "#E2E8F0"

            RowLayout {
                anchors { fill: parent; leftMargin: 24; rightMargin: 24 }
                spacing: 10

                Rectangle {
                    width: 240; height: 32; radius: 8
                    color: "#F4F6FA"; border.color: "#E2E8F0"
                    RowLayout {
                        anchors { fill: parent; leftMargin: 10; rightMargin: 10 }
                        spacing: 6
                        Text { text: "?"; font.pixelSize: 12; color: "#94A3B8" }
                        Text { text: "Search topics..."; font.pixelSize: 12; color: "#CBD5E1" }
                    }
                }

                Repeater {
                    model: ["All", "Easy", "Medium", "Hard"]
                    delegate: Rectangle {
                        property bool sel: modelData === backend.curriculumDifficulty
                        height: 28
                        implicitWidth: chipLbl.implicitWidth + 20
                        radius: 14
                        color: sel ? "#3B82F6" : "#F4F6FA"
                        border.color: sel ? "#3B82F6" : "#E2E8F0"

                        Text { id: chipLbl; anchors.centerIn: parent; text: modelData; font.pixelSize: 11; font.bold: sel; color: sel ? "#FFFFFF" : "#64748B" }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: backend.setCurriculumDifficulty(modelData)
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                Row {
                    spacing: 4
                    Repeater {
                        model: ["Grid", "List"]
                        delegate: Rectangle {
                            width: 64; height: 28; radius: 6
                            color: index === 0 ? "#EFF6FF" : "transparent"
                            border.color: index === 0 ? "#BFDBFE" : "#E2E8F0"
                            Text { anchors.centerIn: parent; text: modelData; font.pixelSize: 11; color: index === 0 ? "#3B82F6" : "#64748B" }
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 48
            color: "#F8FAFC"
            border.color: "#E2E8F0"

            RowLayout {
                anchors { fill: parent; leftMargin: 24; rightMargin: 24 }
                spacing: 32

                Repeater {
                    model: backend.curriculumSummary.stats
                    delegate: RowLayout {
                        spacing: 6
                        Rectangle { width: 8; height: 8; radius: 4; color: modelData.color }
                        Text { text: modelData.label; font.pixelSize: 11; color: "#64748B" }
                        Text { text: modelData.value; font.pixelSize: 12; font.bold: true; color: "#1A2332" }
                    }
                }

                Item { Layout.fillWidth: true }
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

                Repeater {
                    model: backend.curriculumSubjects
                    delegate: ColumnLayout {
                        property color subjectAccent: modelData.accentColor
                        Layout.fillWidth: true
                        spacing: 0

                        Rectangle {
                            Layout.fillWidth: true
                            height: 44
                            color: "#FFFFFF"
                            border.color: "#F1F5F9"

                            RowLayout {
                                anchors { fill: parent; leftMargin: 24; rightMargin: 24 }
                                spacing: 12

                                Rectangle {
                                    width: 28; height: 28; radius: 8
                                    color: Qt.rgba(parseInt(modelData.accentColor.slice(1,3),16)/255, parseInt(modelData.accentColor.slice(3,5),16)/255, parseInt(modelData.accentColor.slice(5,7),16)/255, 0.12)
                                    Text { anchors.centerIn: parent; text: modelData.iconText; font.pixelSize: 14 }
                                }

                                Text { text: modelData.subjectName; font.pixelSize: 14; font.bold: true; color: "#1A2332" }
                                TagPill { tagText: modelData.topicCount + " topics"; tagColor: modelData.accentColor }
                                Item { Layout.fillWidth: true }
                                Text { text: "Active"; font.pixelSize: 11; color: "#94A3B8" }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: topicsRow.implicitHeight + 20
                            color: "#F8FAFC"
                            border.color: "#F1F5F9"

                            RowLayout {
                                id: topicsRow
                                anchors { fill: parent; margins: 16 }
                                spacing: 12

                                Repeater {
                                    model: modelData.topics
                                    delegate: Rectangle {
                                        property int topicConfidence: modelData.confidence
                                        Layout.fillWidth: true
                                        height: 120
                                        radius: 10
                                        color: "#FFFFFF"
                                        border.color: "#E2E8F0"

                                        Rectangle { width: parent.width; height: 3; radius: 2; anchors.top: parent.top; color: modelData.difficultyColor }

                                        ColumnLayout {
                                            anchors { fill: parent; margins: 12; topMargin: 14 }
                                            spacing: 6

                                            Text { text: modelData.name; font.pixelSize: 12; font.bold: true; color: "#1A2332"; elide: Text.ElideRight; Layout.fillWidth: true }

                                            RowLayout {
                                                spacing: 6
                                                TagPill { tagText: modelData.difficulty; tagColor: modelData.difficultyColor }

                                                Row {
                                                    spacing: 1
                                                    Repeater {
                                                        model: 5
                                                        Text { text: "*"; font.pixelSize: 10; color: index < topicConfidence ? "#F59E0B" : "#E2E8F0" }
                                                    }
                                                }
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 3

                                                RowLayout {
                                                    Text { text: "Progress"; font.pixelSize: 9; color: "#94A3B8"; Layout.fillWidth: true }
                                                    Text { text: modelData.progress + "%"; font.pixelSize: 9; font.bold: true; color: "#374151" }
                                                }

                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    height: 5; radius: 3
                                                    color: "#F1F5F9"
                                                    Rectangle { width: parent.width * (modelData.progress / 100); height: parent.height; radius: parent.radius; color: subjectAccent }
                                                }
                                            }

                                            RowLayout {
                                                spacing: 6
                                                AppButton { label: "Review"; variant: "primary"; small: true; Layout.fillWidth: true }
                                                AppButton { label: "Edit"; variant: "secondary"; small: true }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Item { height: 24 }
            }
        }
    }
}
