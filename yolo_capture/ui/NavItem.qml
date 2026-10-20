import QtQuick
import QtQuick.Layouts

// Entrée du menu latéral. `soon` : section pas encore disponible (non cliquable).
Rectangle {
    id: root
    property string label: ""
    property string glyph: ""
    property bool active: false
    property bool soon: false
    signal clicked

    Layout.fillWidth: true
    implicitHeight: 44
    radius: Theme.radiusControl
    color: active ? Theme.accentSoft : (mouse.containsMouse && !soon ? Theme.surfaceHi : "transparent")
    Behavior on color { ColorAnimation { duration: 120 } }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        spacing: 12
        opacity: root.soon ? 0.55 : 1.0

        Rectangle {
            Layout.preferredWidth: 28
            Layout.preferredHeight: 28
            radius: 8
            color: root.active ? Theme.accent : Theme.surfaceHi
            Text {
                anchors.centerIn: parent
                text: root.glyph
                color: root.active ? "white" : Theme.textMuted
                font.pixelSize: 14
            }
        }
        Text {
            Layout.fillWidth: true
            text: root.label
            color: root.active ? Theme.text : Theme.textMuted
            font.family: Theme.font
            font.pixelSize: 13
            font.weight: root.active ? Font.DemiBold : Font.Normal
        }
        Rectangle {
            visible: root.soon
            implicitWidth: soonText.implicitWidth + 14
            implicitHeight: 20
            radius: 10
            color: Theme.surfaceHi
            Text {
                id: soonText
                anchors.centerIn: parent
                text: "Bientôt"
                color: Theme.textMuted
                font.family: Theme.font
                font.pixelSize: 10
                font.weight: Font.DemiBold
            }
        }
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.soon ? Qt.ForbiddenCursor : Qt.PointingHandCursor
        onClicked: if (!root.soon) root.clicked()
    }
}
