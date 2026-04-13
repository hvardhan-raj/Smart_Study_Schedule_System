import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    color: "#F4F6FA"

    function digestData() {
        if (typeof backend !== "undefined" && backend.todayDigest)
            return backend.todayDigest

        var latest = (typeof backend !== "undefined" && backend.notifications && backend.notifications.length > 0)
            ? backend.notifications[0]
            : null
        var sessions = (typeof backend !== "undefined" && backend.selectedDaySessions) ? backend.selectedDaySessions : []
        var nextSession = sessions.length > 0 ? sessions[0] : null

        return {
            summary: latest ? (latest.body || latest.title || "") : "No new alerts right now.",
            nextSession: nextSession
                ? ("Next session: " + (nextSession.subject || "Study") + " for " + ((nextSession.duration !== undefined && nextSession.duration !== null) ? (nextSession.duration + " min") : "--"))
                : "No sessions scheduled."
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        PageHeader {
            Layout.fillWidth: true
            pageTitle: "Notifications & Alerts"
            pageSubtitle: "STAY ON TRACK"
            rightContent: [
                AppButton { label: "Mark All Read"; variant: "secondary"; small: true; onClicked: backend.markAllNotificationsRead() }
            ]
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.margins: 24
            spacing: 16
            Layout.fillHeight: true

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredWidth: 2
                implicitHeight: notifCol.implicitHeight + 32
                radius: 12
                color: "#FFFFFF"

                ColumnLayout {
                    id: notifCol
                    anchors { fill: parent; margins: 20 }
                    spacing: 0

                    Text { text: "Recent Notifications"; font.pixelSize: 14; font.bold: true; color: "#1A2332" }
                    Item { height: 14 }

                    Repeater {
                        model: backend.notifications
                        delegate: Rectangle {
                            Layout.fillWidth: true
                            height: 72
                            radius: 8
                            color: modelData.read ? "transparent" : "#FAFEFF"
                            border.color: modelData.read ? "#F1F5F9" : "#E0F2FE"
                            border.width: 1

                            RowLayout {
                                anchors { fill: parent; margins: 14 }
                                spacing: 12
                                Rectangle { width: 3; height: 40; radius: 2; color: modelData.color }
                                Text { text: modelData.icon; font.pixelSize: 16; color: "#1A2332" }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2
                                    Text { text: modelData.title; font.pixelSize: 12; font.bold: !modelData.read; color: "#1A2332" }
                                    Text { text: modelData.body; font.pixelSize: 11; color: "#64748B"; elide: Text.ElideRight; Layout.fillWidth: true }
                                }

                                ColumnLayout {
                                    spacing: 6
                                    Text { text: modelData.time; font.pixelSize: 10; color: "#94A3B8"; Layout.alignment: Qt.AlignRight }
                                    Rectangle { visible: !modelData.read; width: 8; height: 8; radius: 4; color: "#3B82F6"; Layout.alignment: Qt.AlignRight }
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
                    implicitHeight: settingsCol.implicitHeight + 32
                    radius: 12
                    color: "#FFFFFF"

                    ColumnLayout {
                        id: settingsCol
                        anchors { fill: parent; margins: 20 }
                        spacing: 12
                        Text { text: "Alert Settings"; font.pixelSize: 13; font.bold: true; color: "#1A2332" }

                        Repeater {
                            model: backend.alertSettings
                            delegate: RowLayout {
                                Layout.fillWidth: true
                                Text { text: modelData.label; font.pixelSize: 12; color: "#374151"; Layout.fillWidth: true }

                                Rectangle {
                                    width: 38; height: 20; radius: 10
                                    color: modelData.on ? "#3B82F6" : "#CBD5E1"

                                    Rectangle { width: 16; height: 16; radius: 8; color: "white"; anchors.verticalCenter: parent.verticalCenter; x: modelData.on ? parent.width - width - 2 : 2 }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: backend.toggleAlertSetting(modelData.key)
                                    }
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 130
                    radius: 12
                    color: "#EFF6FF"
                    border.color: "#BFDBFE"

                    ColumnLayout {
                        anchors { fill: parent; margins: 16 }
                        spacing: 6
                        Text { text: "Today's Digest"; font.pixelSize: 12; font.bold: true; color: "#1D4ED8" }
                        Text { text: root.digestData().summary; font.pixelSize: 11; color: "#1E40AF" }
                        Rectangle { Layout.fillWidth: true; height: 1; color: "#BFDBFE" }
                        Text { text: root.digestData().nextSession; font.pixelSize: 11; color: "#374151" }
                        AppButton { label: "View Schedule"; variant: "primary"; small: true }
                    }
                }
            }
        }
    }
}
