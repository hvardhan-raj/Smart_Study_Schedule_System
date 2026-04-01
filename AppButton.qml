import QtQuick 2.15

// ── AppButton ──────────────────────────────────────────────────
//  variant: "primary" | "secondary" | "danger" | "ghost"
Rectangle {
    id: root
    property string label:   "Button"
    property string variant: "primary"   // primary | secondary | danger | ghost
    property bool   small:   false

    signal clicked()

    implicitWidth:  btnLabel.implicitWidth + (small ? 24 : 32)
    implicitHeight: small ? 28 : 34
    radius: implicitHeight / 2

    property bool _hov: false

    color: {
        if (variant === "primary")   return _hov ? "#2563EB" : "#3B82F6"
        if (variant === "secondary") return _hov ? "#F0F3F8" : "#FFFFFF"
        if (variant === "danger")    return _hov ? "#DC2626" : "#EF4444"
        return "transparent"
    }

    border.color: {
        if (variant === "secondary") return "#E2E8F0"
        if (variant === "ghost")     return _hov ? "#3B82F6" : "transparent"
        return "transparent"
    }
    border.width: 1

    Text {
        id: btnLabel
        anchors.centerIn: parent
        text: root.label
        font.pixelSize: root.small ? 11 : 12
        font.bold: true
        color: {
            if (root.variant === "primary")   return "#FFFFFF"
            if (root.variant === "danger")    return "#FFFFFF"
            if (root.variant === "ghost")     return root._hov ? "#3B82F6" : "#64748B"
            return "#374151"
        }
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered:  root._hov = true
        onExited:   root._hov = false
        onClicked:  root.clicked()
        cursorShape: Qt.PointingHandCursor
    }
}
