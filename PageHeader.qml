import QtQuick 2.15
import QtQuick.Layouts 1.15

// Top header bar present on every screen
Item {
    id: root
    height: 60
    property string pageTitle:    "Page Title"
    property string pageSubtitle: "Subtitle"
    function avatarInitials() {
        var profile = (typeof backend !== "undefined" && backend.userProfile) ? backend.userProfile : {}
        if (profile.initials)
            return profile.initials

        var source = profile.name || profile.display_name || ""
        var parts = source.trim().split(/\s+/).filter(function(part) { return part.length > 0 })
        if (parts.length === 0)
            return "U"

        var initials = parts.slice(0, 2).map(function(part) { return part.charAt(0).toUpperCase() }).join("")
        return initials || "U"
    }

    // slots for right-side buttons — set from parent
    property alias rightContent: rightSlot.data

    Rectangle {
        anchors.fill: parent
        color: "#FFFFFF"
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: "#E2E8F0" }

        RowLayout {
            anchors { fill: parent; leftMargin: 28; rightMargin: 20 }
            spacing: 0

            ColumnLayout {
                spacing: 1
                Text {
                    text: root.pageTitle
                    font.pixelSize: 16
                    font.bold: true
                    color: "#1A2332"
                }
                Text {
                    text: root.pageSubtitle
                    font.pixelSize: 10
                    color: "#94A3B8"
                }
            }

            Item { Layout.fillWidth: true }

            // right-hand action buttons injected by parent
            Row {
                id: rightSlot
                spacing: 8
            }

            Item { width: 16 }

            // Search
            Rectangle {
                width: 160; height: 30; radius: 15
                color: "#F4F6FA"
                border.color: "#E2E8F0"
                RowLayout {
                    anchors { fill: parent; leftMargin: 10; rightMargin: 10 }
                    Text { text: "🔍"; font.pixelSize: 11; color: "#94A3B8" }
                    Text { text: "Search…";   font.pixelSize: 11; color: "#CBD5E1" }
                }
            }

            Item { width: 8 }

            // Notification bell
            Rectangle {
                width: 30; height: 30; radius: 15
                color: "#F4F6FA"
                Text { anchors.centerIn: parent; text: "🔔"; font.pixelSize: 13 }

                Rectangle {
                    width: 8; height: 8; radius: 4
                    color: "#EF4444"
                    anchors { top: parent.top; right: parent.right; topMargin: 3; rightMargin: 3 }
                }
            }

            Item { width: 6 }

            // Avatar
            Rectangle {
                width: 30; height: 30; radius: 15
                color: "#3B82F6"
                Text { anchors.centerIn: parent; text: root.avatarInitials(); color: "white"; font.pixelSize: 13; font.bold: true }
            }
        }
    }
}
