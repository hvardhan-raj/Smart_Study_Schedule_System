import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    property string sectionTitle: "Section"
    default property alias content: innerCol.data

    implicitHeight: innerCol.implicitHeight + 48
    radius: 12
    color: "#FFFFFF"

    ColumnLayout {
        id: innerCol
        anchors { fill: parent; margins: 20 }
        spacing: 0

        Text {
            text: root.sectionTitle
            font.pixelSize: 11
            font.letterSpacing: 1.2
            font.bold: true
            color: "#94A3B8"
        }

        Item { height: 12 }
    }
}
