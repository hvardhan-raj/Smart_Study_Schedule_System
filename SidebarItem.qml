import QtQuick 2.15
import QtQuick.Layouts 1.15

// Single navigation row in the sidebar
Item {
    id: root
    width:  parent.width
    height: 38

    property string label:  ""
    property string icon:   ""
    property bool   active: false

    signal clicked()

    // hover state
    property bool hovered: false

    Rectangle {
        anchors { left: parent.left; right: parent.right; leftMargin: 10; rightMargin: 10 }
        height: parent.height - 4
        anchors.verticalCenter: parent.verticalCenter
        radius: 8
        color: root.active   ? "#2D4A6A" :
               root.hovered  ? "#253547" : "transparent"

        // active indicator strip
        Rectangle {
            visible: root.active
            width: 3; height: 20
            radius: 2
            color: "#3B82F6"
            anchors { left: parent.left; verticalCenter: parent.verticalCenter; leftMargin: -1 }
        }

        RowLayout {
            anchors { fill: parent; leftMargin: 14 }
            spacing: 10

            Text {
                text: root.icon
                font.pixelSize: 13
                color: root.active ? "#FFFFFF" : "#8FA3B8"
            }

            Text {
                text: root.label
                font.pixelSize: 12
                font.weight: root.active ? Font.Medium : Font.Normal
                color: root.active ? "#FFFFFF" : "#8FA3B8"
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered:  root.hovered = true
        onExited:   root.hovered = false
        onClicked:  root.clicked()
        cursorShape: Qt.PointingHandCursor
    }
}
