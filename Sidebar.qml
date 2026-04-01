import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

// ─────────────────────────────────────────────────────────────────
//  Sidebar  –  left navigation panel, matches the prototype exactly
// ─────────────────────────────────────────────────────────────────
Rectangle {
    id: root
    width:  200
    color:  "#1E2A3A"

    // Which page is active? 0=Dashboard 1=Tasks 2=Curriculum
    // 3=Schedule 4=Calendar 5=Intelligence 6=Notifications 7=Settings
    property int  activePage: 0
    signal pageSelected(int index)

    // ── logo / app name ──────────────────────────────────────
    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Item { height: 24 }

        // App icon + name
        RowLayout {
            Layout.leftMargin: 18
            spacing: 10

            Rectangle {
                width: 30; height: 30
                radius: 8
                color: "#3B82F6"

                Text {
                    anchors.centerIn: parent
                    text: "S"
                    font.pixelSize: 16
                    font.bold: true
                    color: "white"
                }
            }

            ColumnLayout {
                spacing: 1
                Text {
                    text: "StudyFlow"
                    font.pixelSize: 13
                    font.bold: true
                    color: "#FFFFFF"
                }
                Text {
                    text: "Smart Study Schedule"
                    font.pixelSize: 9
                    color: "#8FA3B8"
                }
            }
        }

        Item { height: 28 }

        // ── section label ─────────────────────────────────────
        Text {
            Layout.leftMargin: 18
            text: "MAIN MENU"
            font.pixelSize: 9
            font.letterSpacing: 1.5
            color: "#4A6080"
        }

        Item { height: 8 }

        // ── nav items ─────────────────────────────────────────
        Repeater {
            model: [
                { icon: "⊞", label: "Dashboard"          },
                { icon: "✓", label: "Task Inbox"          },
                { icon: "◫", label: "Curriculum Map"      },
                { icon: "⊟", label: "Revision Schedule"   },
                { icon: "▦", label: "Calendar"            },
                { icon: "↗", label: "Learning Intelligence"},
                { icon: "🔔", label: "Notifications"      },
            ]

            delegate: SidebarItem {
                label:    modelData.label
                icon:     modelData.icon
                active:   (index === root.activePage)
                onClicked: root.pageSelected(index)
            }
        }

        Item { Layout.fillHeight: true }

        // ── bottom section ────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#2D3F54"
            Layout.leftMargin: 18
            Layout.rightMargin: 18
        }

        Item { height: 12 }

        SidebarItem {
            label:  "Settings"
            icon:   "⚙"
            active: (root.activePage === 7)
            onClicked: root.pageSelected(7)
        }

        // User avatar row
        RowLayout {
            Layout.leftMargin: 14
            Layout.rightMargin: 14
            Layout.bottomMargin: 20
            spacing: 10

            Rectangle {
                width: 32; height: 32; radius: 16
                color: "#3B82F6"
                Text { anchors.centerIn: parent; text: "A"; color: "white"; font.pixelSize: 13; font.bold: true }
            }

            ColumnLayout {
                spacing: 1
                Text { text: backend.userProfile.name;  font.pixelSize: 11; font.bold: true; color: "#FFFFFF" }
                Text { text: backend.userProfile.title; font.pixelSize: 9;  color: "#8FA3B8" }
            }

            Item { Layout.fillWidth: true }
        }
    }
}
