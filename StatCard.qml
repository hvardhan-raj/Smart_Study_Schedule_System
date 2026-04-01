import QtQuick 2.15
import QtQuick.Layouts 1.15

// ── StatCard  ──────────────────────────────────────────────────
//  White rounded card with title, big value, subtitle & optional trend
Rectangle {
    id: root

    property string cardTitle:   "LABEL"
    property string value:       "—"
    property string subtitle:    ""
    property string trend:       ""           // e.g. "↑ 12%"
    property bool   trendUp:     true
    property color  valueColor:  "#1A2332"
    property color  accentColor: "#3B82F6"

    width:  160
    height: 100
    radius: 12
    color:  "#FFFFFF"

    layer.enabled: true
    layer.effect: null    // replace with DropShadow when QtGraphicalEffects available

    // subtle top accent bar
    Rectangle {
        width: 32; height: 3; radius: 2
        color: root.accentColor
        anchors { top: parent.top; left: parent.left; topMargin: 0; leftMargin: 16 }
    }

    ColumnLayout {
        anchors { fill: parent; margins: 16 }
        spacing: 4

        Text {
            text: root.cardTitle
            font.pixelSize: 9
            font.letterSpacing: 1.2
            color: "#94A3B8"
        }

        Text {
            text: root.value
            font.pixelSize: 22
            font.bold: true
            color: root.valueColor
        }

        RowLayout {
            spacing: 6
            visible: root.subtitle !== "" || root.trend !== ""

            Text {
                visible: root.trend !== ""
                text: root.trend
                font.pixelSize: 10
                font.bold: true
                color: root.trendUp ? "#10B981" : "#EF4444"
            }

            Text {
                text: root.subtitle
                font.pixelSize: 10
                color: "#94A3B8"
                elide: Text.ElideRight
            }
        }
    }
}
