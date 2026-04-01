import QtQuick 2.15

// Global design tokens — import this file anywhere with:
//   
//   Theme { id: theme }
QtObject {
    // ── Colours ──────────────────────────────────────────────
    readonly property color bg:           "#F4F6FA"
    readonly property color surface:      "#FFFFFF"
    readonly property color surfaceAlt:   "#F0F3F8"
    readonly property color border:       "#E2E8F0"

    // Sidebar
    readonly property color sidebarBg:    "#1E2A3A"
    readonly property color sidebarText:  "#8FA3B8"
    readonly property color sidebarActive:"#FFFFFF"
    readonly property color sidebarAccent:"#3B82F6"

    // Text
    readonly property color textPrimary:  "#1A2332"
    readonly property color textSecondary:"#64748B"
    readonly property color textMuted:    "#94A3B8"

    // Accent
    readonly property color accent:       "#3B82F6"
    readonly property color accentLight:  "#EFF6FF"

    // Status
    readonly property color success:      "#10B981"
    readonly property color warning:      "#F59E0B"
    readonly property color danger:       "#EF4444"
    readonly property color purple:       "#8B5CF6"

    // ── Typography ───────────────────────────────────────────
    readonly property string fontFamily:  "Segoe UI"
    readonly property int    fontSm:      11
    readonly property int    fontBase:    13
    readonly property int    fontLg:      18

    // ── Sidebar width ────────────────────────────────────────
    readonly property int sidebarW:  200
}
