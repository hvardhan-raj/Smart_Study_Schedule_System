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
            pageSubtitle: "DAILY REVISION BOARD"
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
                spacing: 18

                Rectangle {
                    Layout.fillWidth: true
                    Layout.leftMargin: 24
                    Layout.rightMargin: 24
                    implicitHeight: 70
                    radius: 18
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#0F4C81" }
                        GradientStop { position: 1.0; color: "#2563EB" }
                    }

                    RowLayout {
                        anchors { fill: parent; leftMargin: 28; rightMargin: 28 }
                        spacing: 14

                        Rectangle {
                            width: 34
                            height: 34
                            radius: 10
                            color: Qt.rgba(1, 1, 1, 0.16)

                            Text {
                                anchors.centerIn: parent
                                text: backend.dashboardBanner.emoji
                                font.pixelSize: 18
                                color: "white"
                            }
                        }

                        ColumnLayout {
                            spacing: 2

                            Text {
                                text: backend.dashboardBanner.headline
                                font.pixelSize: 14
                                font.bold: true
                                color: "white"
                            }

                            Text {
                                text: backend.dashboardBanner.detail
                                font.pixelSize: 11
                                color: "#BFDBFE"
                            }
                        }

                        Item { Layout.fillWidth: true }

                        Rectangle {
                            radius: 12
                            color: Qt.rgba(255, 255, 255, 0.12)
                            implicitWidth: focusLabel.implicitWidth + 18
                            implicitHeight: 30

                            Text {
                                id: focusLabel
                                anchors.centerIn: parent
                                text: "Focus score " + backend.dashboardFocus.score + "%"
                                font.pixelSize: 11
                                font.bold: true
                                color: "white"
                            }
                        }
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

                    Repeater {
                        model: backend.dashboardColumns
                        delegate: Rectangle {
                            property var columnData: modelData
                            Layout.fillWidth: true
                            Layout.preferredWidth: 1
                            radius: 18
                            color: "#FFFFFF"
                            border.width: 1
                            border.color: Qt.rgba(columnData.accentColor.r, columnData.accentColor.g, columnData.accentColor.b, 0.18)
                            implicitHeight: 560

                            ColumnLayout {
                                anchors { fill: parent; margins: 18 }
                                spacing: 14

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8

                                    Rectangle {
                                        width: 10
                                        height: 10
                                        radius: 5
                                        color: columnData.accentColor
                                    }

                                    ColumnLayout {
                                        spacing: 2

                                        Text {
                                            text: columnData.title
                                            font.pixelSize: 15
                                            font.bold: true
                                            color: "#1A2332"
                                        }

                                        Text {
                                            text: columnData.subtitle
                                            font.pixelSize: 10
                                            color: "#94A3B8"
                                        }
                                    }

                                    Item { Layout.fillWidth: true }

                                    TagPill {
                                        tagText: columnData.count + " items"
                                        tagColor: columnData.accentColor
                                    }
                                }

                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    contentWidth: availableWidth
                                    clip: true

                                    ColumnLayout {
                                        width: parent.width
                                        spacing: 10

                                        Repeater {
                                            model: columnData.items
                                            delegate: DashboardTaskCard {
                                                Layout.fillWidth: true
                                                taskData: modelData
                                                accentColor: columnData.accentColor
                                            }
                                        }

                                        Item {
                                            visible: columnData.items.length === 0
                                            Layout.fillWidth: true
                                            implicitHeight: 180

                                            ColumnLayout {
                                                anchors.centerIn: parent
                                                spacing: 6

                                                Text {
                                                    text: columnData.key === "upcoming" ? "No upcoming tasks yet" : "All clear"
                                                    font.pixelSize: 13
                                                    font.bold: true
                                                    color: "#1A2332"
                                                    Layout.alignment: Qt.AlignHCenter
                                                }

                                                Text {
                                                    text: columnData.key === "upcoming"
                                                        ? "New revisions will appear here as the schedule fills out."
                                                        : "Nothing waiting in this column right now."
                                                    font.pixelSize: 10
                                                    color: "#94A3B8"
                                                    horizontalAlignment: Text.AlignHCenter
                                                    wrapMode: Text.WordWrap
                                                    Layout.alignment: Qt.AlignHCenter
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
}
