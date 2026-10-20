import QtQuick
import QtQuick.Layouts

// Option sélectionnable. Si `available` est faux : grisée, non cliquable, raison affichée.
Rectangle {
    id: root
    property string label: ""
    property string description: ""
    property string reason: ""
    property bool available: true
    property bool selected: false
    signal picked

    Layout.fillWidth: true
    implicitHeight: 50
    radius: Theme.radiusControl
    color: selected ? Theme.accentSoft : (mouse.containsMouse && available ? Theme.surfaceHi : "transparent")
    border.width: 1
    border.color: selected ? Theme.accent : (mouse.containsMouse && available ? Theme.borderHi : Theme.border)
    opacity: available ? 1.0 : 0.62

    Behavior on color { ColorAnimation { duration: 120 } }
    Behavior on border.color { ColorAnimation { duration: 120 } }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 14
        anchors.rightMargin: 14
        spacing: 12

        // Pastille radio
        Rectangle {
            Layout.preferredWidth: 18
            Layout.preferredHeight: 18
            radius: 9
            color: "transparent"
            border.width: 2
            border.color: root.selected ? Theme.accent : Theme.borderHi
            Rectangle {
                anchors.centerIn: parent
                width: root.selected ? 8 : 0
                height: width
                radius: width / 2
                color: Theme.accent
                Behavior on width { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 1
            Text {
                text: root.label
                color: Theme.text
                font.family: Theme.font
                font.pixelSize: 13
                font.weight: Font.DemiBold
            }
            Text {
                Layout.fillWidth: true
                text: root.available ? root.description : root.reason
                color: root.available ? Theme.textMuted : Theme.danger
                font.family: Theme.font
                font.pixelSize: 11
                elide: Text.ElideRight
            }
        }

        // Badge d'état
        Rectangle {
            visible: !root.available
            implicitWidth: badgeText.implicitWidth + 16
            implicitHeight: 22
            radius: 11
            color: Qt.rgba(1, 0.42, 0.42, 0.12)
            Text {
                id: badgeText
                anchors.centerIn: parent
                text: "Indisponible"
                color: Theme.danger
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
        enabled: root.available
        cursorShape: root.available ? Qt.PointingHandCursor : Qt.ForbiddenCursor
        onClicked: root.picked()
    }

    // Raison complète au survol pour les textes tronqués
    ToolTipArea { anchors.fill: parent; text: root.available ? root.description : root.reason }
}
