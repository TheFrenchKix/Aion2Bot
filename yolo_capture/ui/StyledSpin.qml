import QtQuick
import QtQuick.Controls.Basic

SpinBox {
    id: control
    editable: true
    implicitHeight: 42
    implicitWidth: 190
    font.family: Theme.font
    font.pixelSize: 14
    // pas de separateur de milliers : "1000" plutot que "1 000"
    textFromValue: function (v) { return String(v) }
    valueFromText: function (t) { return parseInt(t) || control.from }

    contentItem: TextInput {
        text: control.textFromValue(control.value)
        font: control.font
        color: Theme.text
        selectionColor: Theme.accent
        horizontalAlignment: Qt.AlignHCenter
        verticalAlignment: Qt.AlignVCenter
        readOnly: !control.editable
        validator: control.validator
        inputMethodHints: Qt.ImhDigitsOnly
    }

    up.indicator: Rectangle {
        x: control.mirrored ? 0 : parent.width - width
        width: 42
        height: parent.height
        radius: Theme.radiusControl
        color: control.up.pressed ? Theme.accentSoft : (control.up.hovered ? Theme.surfaceHi : "transparent")
        Text { anchors.centerIn: parent; text: "+"; color: Theme.textMuted; font.pixelSize: 18 }
    }
    down.indicator: Rectangle {
        x: control.mirrored ? parent.width - width : 0
        width: 42
        height: parent.height
        radius: Theme.radiusControl
        color: control.down.pressed ? Theme.accentSoft : (control.down.hovered ? Theme.surfaceHi : "transparent")
        Text { anchors.centerIn: parent; text: "−"; color: Theme.textMuted; font.pixelSize: 18 }
    }

    background: Rectangle {
        radius: Theme.radiusControl
        color: Theme.bg
        border.width: 1
        border.color: control.activeFocus ? Theme.accent : Theme.border
        opacity: control.enabled ? 1.0 : 0.5
    }
}
