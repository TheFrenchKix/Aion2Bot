pragma Singleton
import QtQuick

QtObject {
    // Surfaces
    readonly property color bg: "#0E1016"
    readonly property color surface: "#151821"
    readonly property color surfaceHi: "#1B1F2B"
    readonly property color border: "#262B38"
    readonly property color borderHi: "#343A4B"

    // Texte
    readonly property color text: "#E8EAF0"
    readonly property color textMuted: "#8A92A6"
    readonly property color textFaint: "#5C6478"

    // Accent & états
    readonly property color accent: "#5B8CFF"
    readonly property color accentAlt: "#7B61FF"
    readonly property color accentSoft: "#1B2540"
    readonly property color success: "#3DDC97"
    readonly property color danger: "#FF6B6B"
    readonly property color warning: "#F5B84B"

    // Formes
    readonly property int radiusWindow: 18
    readonly property int radiusCard: 14
    readonly property int radiusControl: 10
    readonly property int spacing: 14

    readonly property string font: "Segoe UI Variable Text, Segoe UI, Inter, sans-serif"
}
