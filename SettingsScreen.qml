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
            pageTitle: "Settings"
            pageSubtitle: "APP CONFIGURATION"
            rightContent: [
                AppButton { label: "Save Changes"; variant: "primary"; small: true; onClicked: backend.saveSettings() }
            ]
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: availableWidth
            clip: true

            RowLayout {
                width: parent.width
                spacing: 16

                Repeater {
                    model: backend.settingsColumns
                    delegate: ColumnLayout {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 1
                        Layout.topMargin: 24
                        Layout.leftMargin: index === 0 ? 24 : 0
                        Layout.rightMargin: index === 1 ? 24 : 0
                        spacing: 16

                        Repeater {
                            model: modelData
                            delegate: SettingsSection {
                                Layout.fillWidth: true
                                sectionTitle: modelData.title

                                Repeater {
                                    model: modelData.rows
                                    delegate: SettingsRow {
                                        label: modelData.label
                                        value: modelData.value || ""
                                        valueColor: modelData.valueColor || "#374151"
                                        isToggle: modelData.kind === "toggle"
                                        toggleOn: modelData.toggleOn || false
                                        isDanger: modelData.kind === "danger"
                                        dangerLabel: modelData.dangerLabel || ""
                                        settingKey: modelData.key || ""
                                        onToggled: backend.toggleSetting(settingKey)
                                        onDangerClicked: backend.clearHistory()
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
