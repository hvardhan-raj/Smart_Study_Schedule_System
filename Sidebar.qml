import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: 220
    color: "#111827"

    property int  activePage: 0
    property var  pages: []
    signal pageSelected(int index)

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── Logo ──────────────────────────────────────────────────────
        Item { height: 22 }

        RowLayout {
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            spacing: 11

            Rectangle {
                width: 36; height: 36
                radius: 11
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#3B82F6" }
                    GradientStop { position: 1.0; color: "#1D4ED8" }
                }
                Text {
                    anchors.centerIn: parent
                    text: "S"
                    font.pixelSize: 17
                    font.bold: true
                    color: "white"
                }
            }

            ColumnLayout {
                spacing: 1
                Text {
                    text: "StudyFlow"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#FFFFFF"
                    font.family: "Segoe UI"
                }
                Text {
                    text: "Smart Study Schedule"
                    font.pixelSize: 9
                    color: "#6B7C94"
                    font.family: "Segoe UI"
                }
            }
        }

        Item { height: 28 }

        // ── Nav label ────────────────────────────────────────────────
        Text {
            Layout.leftMargin: 20
            text: "NAVIGATION"
            font.pixelSize: 9
            font.letterSpacing: 1.8
            font.bold: true
            color: "#4B5E73"
            font.family: "Segoe UI"
        }

        Item { height: 6 }

        // ── Nav items ────────────────────────────────────────────────
        Repeater {
            model: root.pages.length > 0 ? root.pages.slice(0, 8) : []
            delegate: SidebarItem {
                label:    modelData.label
                icon:     modelData.icon
                active:   (index === root.activePage)
                onClicked: root.pageSelected(index)
            }
        }

        Item { Layout.fillHeight: true }

        // ── Divider ──────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            height: 1
            color: "#1F2F40"
        }

        Item { height: 14 }

        // ── User row ─────────────────────────────────────────────────
        RowLayout {
            Layout.leftMargin: 16
            Layout.rightMargin: 16
            Layout.bottomMargin: 18
            spacing: 10

            Rectangle {
                width: 34; height: 34; radius: 17
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#3B82F6" }
                    GradientStop { position: 1.0; color: "#1D4ED8" }
                }
                Text {
                    anchors.centerIn: parent
                    text: {
                        var name = backend.userProfile.name || "U"
                        return name.charAt(0).toUpperCase()
                    }
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                }
            }

            ColumnLayout {
                spacing: 1
                Text {
                    text: backend.userProfile.name || "User"
                    font.pixelSize: 12
                    font.bold: true
                    color: "#FFFFFF"
                    font.family: "Segoe UI"
                    elide: Text.ElideRight
                    Layout.maximumWidth: 110
                }
                Text {
                    text: backend.userProfile.plan || "Learner"
                    font.pixelSize: 9
                    color: "#6B7C94"
                    font.family: "Segoe UI"
                }
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                width: 26; height: 26; radius: 13
                color: "#1F2F40"
                Text {
                    anchors.centerIn: parent
                    text: "⚙"
                    font.pixelSize: 11
                    color: "#6B7C94"
                }
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.pageSelected(8)
                }
            }
        }
    }
}
