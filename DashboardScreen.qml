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
            pageTitle: "Dashboard"
            pageSubtitle: "SMART STUDY SCHEDULE"
            rightContent: [
                AppButton { label: "+ Start Session"; variant: "primary"; small: true; onClicked: backend.startSession() }
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

                Rectangle {
                    Layout.fillWidth: true
                    height: 52
                    color: "#3B82F6"

                    RowLayout {
                        anchors { fill: parent; leftMargin: 28; rightMargin: 28 }

                        Text { text: backend.dashboardBanner.emoji; font.pixelSize: 20 }
                        Text { text: backend.dashboardBanner.headline; font.pixelSize: 13; font.bold: true; color: "white" }
                        Item { Layout.fillWidth: true }
                        Text { text: backend.dashboardBanner.detail; font.pixelSize: 11; color: "#BFDBFE" }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.margins: 24
                    spacing: 14

                    Repeater {
                        model: backend.dashboardStats
                        delegate: StatCard {
                            Layout.fillWidth: true
                            cardTitle: modelData.title
                            value: modelData.value
                            subtitle: modelData.subtitle
                            trend: modelData.trend
                            trendUp: modelData.trendUp
                            valueColor: modelData.valueColor
                            accentColor: modelData.accentColor
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: 24
                    Layout.rightMargin: 24
                    Layout.bottomMargin: 24
                    spacing: 16

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 2
                        implicitHeight: taskCol.implicitHeight + 32
                        radius: 12
                        color: "#FFFFFF"

                        ColumnLayout {
                            id: taskCol
                            anchors { fill: parent; margins: 20 }
                            spacing: 10

                            RowLayout {
                                Text { text: "Today's Tasks"; font.pixelSize: 14; font.bold: true; color: "#1A2332" }
                                Item { Layout.fillWidth: true }
                                TagPill { tagText: backend.todayTasks.length + " remaining"; tagColor: "#3B82F6" }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Repeater {
                                    model: ["TOPIC", "SUBJECT", "DIFFICULTY", "TIME", "STATUS"]
                                    Text {
                                        Layout.fillWidth: index === 0
                                        text: modelData
                                        font.pixelSize: 9
                                        font.letterSpacing: 1
                                        color: "#94A3B8"
                                    }
                                }
                            }

                            Rectangle { Layout.fillWidth: true; height: 1; color: "#F1F5F9" }

                            Repeater {
                                model: backend.todayTasks
                                delegate: RowLayout {
                                    Layout.fillWidth: true
                                    height: 36
                                    spacing: 8

                                    Text { Layout.fillWidth: true; text: modelData.name; font.pixelSize: 12; color: "#1A2332"; elide: Text.ElideRight }
                                    TagPill { tagText: modelData.subjectShort; tagColor: modelData.subjectColor }
                                    TagPill { tagText: modelData.difficulty; tagColor: modelData.difficultyColor }
                                    Text { text: modelData.time; font.pixelSize: 11; color: "#64748B"; Layout.preferredWidth: 28 }
                                    TagPill { tagText: modelData.status; tagColor: modelData.statusColor }
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
                            height: 170
                            radius: 12
                            color: "#FFFFFF"

                            ColumnLayout {
                                anchors { fill: parent; margins: 20 }
                                spacing: 8

                                Text { text: "True Confidence"; font.pixelSize: 13; font.bold: true; color: "#1A2332" }

                                Rectangle {
                                    width: 90
                                    height: 90
                                    radius: 45
                                    color: "#EFF6FF"
                                    Layout.alignment: Qt.AlignHCenter

                                    Rectangle {
                                        width: 70
                                        height: 70
                                        radius: 35
                                        color: "#FFFFFF"
                                        anchors.centerIn: parent

                                        ColumnLayout {
                                            anchors.centerIn: parent
                                            spacing: 0
                                            Text { text: backend.dashboardFocus.score + "%"; font.pixelSize: 18; font.bold: true; color: "#3B82F6"; Layout.alignment: Qt.AlignHCenter }
                                            Text { text: "score"; font.pixelSize: 9; color: "#94A3B8"; Layout.alignment: Qt.AlignHCenter }
                                        }
                                    }
                                }

                                Text { text: backend.dashboardFocus.nextRevision; font.pixelSize: 10; color: "#94A3B8"; Layout.alignment: Qt.AlignHCenter }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 120
                            radius: 12
                            color: "#FFFFFF"

                            ColumnLayout {
                                anchors { fill: parent; margins: 16 }
                                spacing: 6
                                Text { text: "This Week"; font.pixelSize: 13; font.bold: true; color: "#1A2332" }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 6

                                    Repeater {
                                        model: backend.dashboardWeekBars
                                        delegate: ColumnLayout {
                                            spacing: 3
                                            Item { Layout.fillHeight: true }
                                            Rectangle { width: 10; height: Math.max(16, modelData * 0.5); radius: 3; color: index === 3 ? "#3B82F6" : "#BFDBFE" }
                                            Text { text: ["M","T","W","T","F","S","S"][index]; font.pixelSize: 8; color: "#94A3B8" }
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
