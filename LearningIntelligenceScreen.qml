import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
    color: "#F4F6FA"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        PageHeader {
            Layout.fillWidth: true
            pageTitle: "Learning Intelligence"
            pageSubtitle: "AI-POWERED INSIGHTS"
            rightContent: [
                AppButton { label: "Export Report"; variant: "secondary"; small: true }
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

                RowLayout {
                    Layout.fillWidth: true
                    Layout.margins: 24
                    spacing: 14

                    Repeater {
                        model: backend.intelligenceStats
                        delegate: StatCard {
                            Layout.fillWidth: true
                            cardTitle: modelData.title
                            value: modelData.value
                            subtitle: modelData.subtitle
                            trend: modelData.trend
                            trendUp: modelData.trendUp
                            accentColor: modelData.accentColor
                            valueColor: modelData.valueColor
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
                        height: 220
                        radius: 12
                        color: "#FFFFFF"

                        ColumnLayout {
                            anchors { fill: parent; margins: 20 }
                            spacing: 10

                            Text { text: "Daily Study Time (minutes)"; font.pixelSize: 12; font.bold: true; color: "#1A2332" }

                            Canvas {
                                id: studyChart
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                property var points: backend.studyTrend
                                onPointsChanged: requestPaint()

                                onPaint: {
                                    var ctx = getContext("2d")
                                    ctx.clearRect(0, 0, width, height)

                                    var pts = points
                                    var n = pts.length
                                    if (n === 0)
                                        return
                                    var mn = Math.min.apply(Math, pts) - 5
                                    var mx = Math.max.apply(Math, pts) + 5
                                    var rng = Math.max(1, mx - mn)
                                    var pad = 8

                                    function px(i) { return pad + (i / Math.max(1, n - 1)) * (width - 2 * pad) }
                                    function py(v) { return height - pad - ((v - mn) / rng) * (height - 2 * pad) }

                                    var grad = ctx.createLinearGradient(0, 0, 0, height)
                                    grad.addColorStop(0, "rgba(59,130,246,0.25)")
                                    grad.addColorStop(1, "rgba(59,130,246,0.02)")
                                    ctx.beginPath()
                                    ctx.moveTo(px(0), py(pts[0]))
                                    for (var i = 1; i < n; i++) ctx.lineTo(px(i), py(pts[i]))
                                    ctx.lineTo(px(n - 1), height)
                                    ctx.lineTo(px(0), height)
                                    ctx.closePath()
                                    ctx.fillStyle = grad
                                    ctx.fill()

                                    ctx.beginPath()
                                    ctx.strokeStyle = "#3B82F6"
                                    ctx.lineWidth = 2
                                    ctx.moveTo(px(0), py(pts[0]))
                                    for (var j = 1; j < n; j++) ctx.lineTo(px(j), py(pts[j]))
                                    ctx.stroke()

                                    ctx.fillStyle = "#3B82F6"
                                    for (var k = 0; k < n; k++) {
                                        ctx.beginPath()
                                        ctx.arc(px(k), py(pts[k]), 3, 0, 2 * Math.PI)
                                        ctx.fill()
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 1
                        height: 220
                        radius: 12
                        color: "#FFFFFF"

                        ColumnLayout {
                            anchors { fill: parent; margins: 20 }
                            spacing: 8
                            Text { text: "Subject Confidence"; font.pixelSize: 12; font.bold: true; color: "#1A2332" }

                            Repeater {
                                model: backend.subjectConfidence
                                delegate: ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 3

                                    RowLayout {
                                        Text { text: modelData.subject; font.pixelSize: 11; color: "#374151"; Layout.fillWidth: true }
                                        Text { text: modelData.pct + "%"; font.pixelSize: 10; font.bold: true; color: modelData.color }
                                    }

                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 6; radius: 3
                                        color: "#F1F5F9"
                                        Rectangle { width: parent.width * (modelData.pct / 100); height: parent.height; radius: parent.radius; color: modelData.color }
                                    }
                                }
                            }
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
                        height: 160
                        radius: 12
                        color: "#FFFFFF"

                        ColumnLayout {
                            anchors { fill: parent; margins: 20 }
                            spacing: 10
                            Text { text: "Study Activity Heatmap"; font.pixelSize: 12; font.bold: true; color: "#1A2332" }

                            Grid {
                                columns: 8
                                rows: 7
                                spacing: 4

                                Repeater {
                                    model: backend.activityHeatmap
                                    delegate: Rectangle {
                                        width: 16; height: 16; radius: 3
                                        color: modelData < 20 ? "#F1F5F9" : (modelData < 45 ? "#BFDBFE" : (modelData < 70 ? "#60A5FA" : "#2563EB"))
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 160
                        radius: 12
                        color: "#FFFFFF"

                        ColumnLayout {
                            anchors { fill: parent; margins: 20 }
                            spacing: 8

                            Text { text: "Topic Balance"; font.pixelSize: 12; font.bold: true; color: "#1A2332" }

                            Canvas {
                                id: radarCanvas
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                property var vals: backend.topicBalance
                                onValsChanged: requestPaint()

                                onPaint: {
                                    var ctx = getContext("2d")
                                    ctx.clearRect(0, 0, width, height)

                                    var cx = width / 2
                                    var cy = height / 2
                                    var r = Math.min(width, height) / 2 - 12
                                    var labels = ["Bio", "Math", "Phy", "Chem", "Hist"]
                                    var vals = backend.topicBalance
                                    var n = labels.length

                                    ctx.strokeStyle = "#E2E8F0"
                                    ctx.lineWidth = 1
                                    for (var ring = 1; ring <= 4; ring++) {
                                        ctx.beginPath()
                                        for (var i = 0; i <= n; i++) {
                                            var a = (i / n) * 2 * Math.PI - Math.PI / 2
                                            var x = cx + Math.cos(a) * r * ring / 4
                                            var y = cy + Math.sin(a) * r * ring / 4
                                            i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
                                        }
                                        ctx.closePath()
                                        ctx.stroke()
                                    }

                                    ctx.beginPath()
                                    for (var k = 0; k <= n; k++) {
                                        var ak = (k / n) * 2 * Math.PI - Math.PI / 2
                                        var xk = cx + Math.cos(ak) * r * vals[k % n]
                                        var yk = cy + Math.sin(ak) * r * vals[k % n]
                                        k === 0 ? ctx.moveTo(xk, yk) : ctx.lineTo(xk, yk)
                                    }
                                    ctx.closePath()
                                    ctx.fillStyle = "rgba(59,130,246,0.15)"
                                    ctx.fill()
                                    ctx.strokeStyle = "#3B82F6"
                                    ctx.lineWidth = 2
                                    ctx.stroke()
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 160
                        radius: 12
                        color: "#FFFFFF"

                        ColumnLayout {
                            anchors { fill: parent; margins: 20 }
                            spacing: 8

                            Text { text: "Flashcard Stats"; font.pixelSize: 12; font.bold: true; color: "#1A2332" }

                            Repeater {
                                model: backend.flashcardStats
                                delegate: RowLayout {
                                    Layout.fillWidth: true
                                    Rectangle { width: 8; height: 8; radius: 4; color: modelData.color }
                                    Text { text: modelData.label; font.pixelSize: 11; color: "#64748B"; Layout.fillWidth: true }
                                    Text { text: modelData.value; font.pixelSize: 12; font.bold: true; color: "#1A2332" }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
