import QtQuick
import QtQuick.Controls.Basic

Switch {
    id: control
    implicitHeight: 26
    implicitWidth: 46
    padding: 0

    indicator: Rectangle {
        implicitWidth: 46
        implicitHeight: 26
        radius: 13
        color: control.checked ? Theme.accent : Theme.border
        Behavior on color { ColorAnimation { duration: 140 } }
        Rectangle {
            x: control.checked ? parent.width - width - 3 : 3
            anchors.verticalCenter: parent.verticalCenter
            width: 20
            height: 20
            radius: 10
            color: "white"
            Behavior on x { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
        }
    }
    contentItem: Item {}

    HoverHandler { cursorShape: Qt.PointingHandCursor }
}
