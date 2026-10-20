import QtQuick
import QtQuick.Controls.Basic

// Info-bulle arrondie, affichée après un court délai de survol.
MouseArea {
    id: area
    property string text: ""
    acceptedButtons: Qt.NoButton
    hoverEnabled: true

    ToolTip {
        visible: area.containsMouse && area.text !== ""
        delay: 500
        text: area.text
        contentItem: Text {
            text: area.text
            color: Theme.text
            font.family: Theme.font
            font.pixelSize: 12
            wrapMode: Text.WordWrap
        }
        background: Rectangle {
            color: Theme.surfaceHi
            radius: 8
            border.color: Theme.borderHi
        }
    }
}
