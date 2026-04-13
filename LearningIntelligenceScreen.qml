import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#F4F6FA"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        PageHeader {
            Layout.fillWidth: true
            pageTitle: "Learning Intelligence"
            pageSubtitle: "ANALYTICS, RECALL HEALTH, AND STUDY INSIGHTS"
            rightContent: [
                AppButton {
                    label: "Export Report"
                    variant: "secondary"
                    small: true
                    onClicked: backend.exportLearningReport()
                }
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

                RowLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: 24
                    Layout.rightMargin: 24
                    Layout.topMargin: 24
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
                    spacing: 18

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 3
                        implicitHeight: 300
                        radius: 18
                        color: "#FFFFFF"
                        border.color: "#E2E8F0"

                        ColumnLayout {
                            anchors { fill: parent; margins: 22 }
                            spacing: 14

                            RowLayout {
                                Layout.fillWidth: true
                                Text {
                                    text: "Study Trend"
                                    font.pixelSize: 15
                                    font.bold: true
                                    color: "#1A2332"
                                    Layout.fillWidth: true
                                }
                                TagPill {
                                    tagText: "14 days"
                                    tagColor: "#3B82F6"
                                }
                            }

                            Text {
                                text: "Minutes logged per session, normalized into a compact trend line."
                                font.pixelSize: 11
                                color: "#64748B"
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                            }

                            Canvas {
                                id: studyChart
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                property var values: backend.studyTrend
                                onValuesChanged: requestPaint()

                                onPaint: {
                                    var ctx = getContext("2d")
                                    ctx.clearRect(0, 0, width, height)
                                    var values = studyChart.values || []
                                    if (values.length === 0)
                                        return

                                    var minValue = Math.min.apply(Math, values)
                                    var maxValue = Math.max.apply(Math, values)
                                    var range = Math.max(1, maxValue - minValue)
                                    var padX = 18
                                    var padY = 18

                                    function xAt(i) {
                                        return padX + (i / Math.max(1, values.length - 1)) * (width - padX * 2)
                                    }

                                    function yAt(value) {
                                        return height - padY - ((value - minValue) / range) * (height - padY * 2)
                                    }

                                    ctx.strokeStyle = "#E2E8F0"
                                    ctx.lineWidth = 1
                                    for (var line = 0; line < 4; line++) {
                                        var y = padY + line * ((height - padY * 2) / 3)
                                        ctx.beginPath()
                                        ctx.moveTo(padX, y)
                                        ctx.lineTo(width - padX, y)
                                        ctx.stroke()
                                    }

                                    var gradient = ctx.createLinearGradient(0, 0, 0, height)
                                    gradient.addColorStop(0, "rgba(59, 130, 246, 0.28)")
                                    gradient.addColorStop(1, "rgba(59, 130, 246, 0.02)")
                                    ctx.beginPath()
                                    ctx.moveTo(xAt(0), yAt(values[0]))
                                    for (var i = 1; i < values.length; i++)
                                        ctx.lineTo(xAt(i), yAt(values[i]))
                                    ctx.lineTo(xAt(values.length - 1), height - padY)
                                    ctx.lineTo(xAt(0), height - padY)
                                    ctx.closePath()
                                    ctx.fillStyle = gradient
                                    ctx.fill()

                                    ctx.beginPath()
                                    ctx.moveTo(xAt(0), yAt(values[0]))
                                    for (var j = 1; j < values.length; j++)
                                        ctx.lineTo(xAt(j), yAt(values[j]))
                                    ctx.strokeStyle = "#2563EB"
                                    ctx.lineWidth = 3
                                    ctx.stroke()

                                    for (var k = 0; k < values.length; k++) {
                                        ctx.beginPath()
                                        ctx.arc(xAt(k), yAt(values[k]), 4, 0, Math.PI * 2)
                                        ctx.fillStyle = "#FFFFFF"
                                        ctx.fill()
                                        ctx.strokeStyle = "#2563EB"
                                        ctx.lineWidth = 2
                                        ctx.stroke()
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 2
                        implicitHeight: 300
                        radius: 18
                        color: "#FFFFFF"
                        border.color: "#E2E8F0"

                        ColumnLayout {
                            anchors { fill: parent; margins: 22 }
                            spacing: 12

                            Text {
                                text: "Subject Confidence"
                                font.pixelSize: 15
                                font.bold: true
                                color: "#1A2332"
                            }

                            Repeater {
                                model: backend.subjectConfidence
                                delegate: ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 5

                                    RowLayout {
                                        Layout.fillWidth: true
                                        Text {
                                            text: modelData.subject
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: "#334155"
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            text: modelData.pct + "%"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: modelData.color
                                        }
                                    }

                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 8
                                        radius: 4
                                        color: "#EEF2F7"
                                        Rectangle {
                                            width: parent.width * (modelData.pct / 100)
                                            height: parent.height
                                            radius: parent.radius
                                            color: modelData.color
                                        }
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
                    spacing: 18

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 2
                        implicitHeight: 265
                        radius: 18
                        color: "#FFFFFF"
                        border.color: "#E2E8F0"

                        ColumnLayout {
                            anchors { fill: parent; margins: 22 }
                            spacing: 14

                            Text {
                                text: "Activity Heatmap"
                                font.pixelSize: 15
                                font.bold: true
                                color: "#1A2332"
                            }

                            Grid {
                                columns: 8
                                rows: 7
                                spacing: 7
                                Layout.alignment: Qt.AlignHCenter

                                Repeater {
                                    model: backend.activityHeatmap
                                    delegate: Rectangle {
                                        width: 22
                                        height: 22
                                        radius: 6
                                        color: modelData < 20 ? "#EEF2F7" : (modelData < 45 ? "#BFDBFE" : (modelData < 75 ? "#60A5FA" : "#2563EB"))
                                    }
                                }
                            }

                            Text {
                                text: "Darker cells indicate more minutes or completed reviews on that day."
                                font.pixelSize: 11
                                color: "#64748B"
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 3
                        implicitHeight: 265
                        radius: 18
                        color: "#FFFFFF"
                        border.color: "#E2E8F0"

                        ColumnLayout {
                            anchors { fill: parent; margins: 22 }
                            spacing: 10

                            Text {
                                text: "Subject Health"
                                font.pixelSize: 15
                                font.bold: true
                                color: "#1A2332"
                            }

                            Repeater {
                                model: backend.analyticsSubjectRows
                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    height: 42
                                    radius: 12
                                    color: "#F8FAFC"
                                    border.color: "#E2E8F0"

                                    RowLayout {
                                        anchors { fill: parent; leftMargin: 12; rightMargin: 12 }
                                        spacing: 10

                                        Rectangle {
                                            width: 8
                                            height: 24
                                            radius: 4
                                            color: modelData.color
                                        }

                                        Text {
                                            text: modelData.subject
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: "#1A2332"
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }

                                        TagPill {
                                            tagText: modelData.risk + " risk"
                                            tagColor: modelData.risk === "High" ? "#EF4444" : (modelData.risk === "Medium" ? "#F59E0B" : "#10B981")
                                        }

                                        Text {
                                            text: modelData.nextAction
                                            font.pixelSize: 11
                                            color: "#64748B"
                                            width: 120
                                            elide: Text.ElideRight
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.leftMargin: 24
                    Layout.rightMargin: 24
                    Layout.bottomMargin: 24
                    implicitHeight: insightGrid.implicitHeight + 44
                    radius: 18
                    color: "#0F172A"

                    ColumnLayout {
                        id: insightGrid
                        anchors { fill: parent; margins: 22 }
                        spacing: 14

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "AI Study Insights"
                                font.pixelSize: 15
                                font.bold: true
                                color: "#FFFFFF"
                                Layout.fillWidth: true
                            }
                            Text {
                                text: "Generated from task history and topic confidence"
                                font.pixelSize: 11
                                color: "#94A3B8"
                            }
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            columnSpacing: 12
                            rowSpacing: 12

                            Repeater {
                                model: backend.intelligenceInsights
                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 118
                                    radius: 14
                                    color: "#1E293B"
                                    border.color: "#334155"

                                    ColumnLayout {
                                        anchors { fill: parent; margins: 14 }
                                        spacing: 8

                                        RowLayout {
                                            Layout.fillWidth: true
                                            Rectangle {
                                                width: 8
                                                height: 8
                                                radius: 4
                                                color: modelData.color
                                            }
                                            Text {
                                                text: modelData.severity
                                                font.pixelSize: 10
                                                font.bold: true
                                                color: modelData.color
                                                Layout.fillWidth: true
                                            }
                                        }

                                        Text {
                                            text: modelData.title
                                            font.pixelSize: 13
                                            font.bold: true
                                            color: "#F8FAFC"
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }

                                        Text {
                                            text: modelData.body
                                            font.pixelSize: 11
                                            color: "#CBD5E1"
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
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
