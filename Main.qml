import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15



ApplicationWindow {
    id: root
    width:  1280
    height: 800
    visible: true
    title:  "StudyFlow – Smart Study Schedule"

    // Shell: sidebar (fixed left) + content (fills rest)
    RowLayout {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            id: sidebar
            Layout.fillHeight: true
            activePage: contentStack.currentIndex
            onPageSelected: function(idx) { contentStack.currentIndex = idx }
        }

        StackLayout {
            id: contentStack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: 0

            DashboardScreen          {}   // 0
            TaskInboxScreen          {}   // 1
            CurriculumMapScreen      {}   // 2
            RevisionScheduleScreen   {}   // 3
            CalendarScreen           {}   // 4
            LearningIntelligenceScreen {}  // 5
            NotificationsScreen      {}   // 6
            SettingsScreen           {}   // 7
        }
    }
}
