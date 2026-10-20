import QtQuick
import QtQuick.Controls.Basic

ComboBox {
    id: control
    implicitHeight: 42
    leftPadding: 14
    rightPadding: 40
    font.family: Theme.font
    font.pixelSize: 13

    delegate: ItemDelegate {
        width: control.width - 16
        height: 38
        highlighted: control.highlightedIndex === index
        contentItem: Text {
            text: control.textRole ? (modelData[control.textRole] ?? modelData) : modelData
            color: index === control.currentIndex ? Theme.accent : Theme.text
            font: control.font
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            radius: 8
            color: parent.highlighted ? Theme.surfaceHi : "transparent"
        }
    }

    indicator: Text {
        x: control.width - width - 14
        y: (control.height - height) / 2
        text: "⌄"          // chevron
        color: Theme.textMuted
        font.pixelSize: 18
        rotation: control.popup.visible ? 180 : 0
        Behavior on rotation { NumberAnimation { duration: 150 } }
    }

    contentItem: Text {
        text: control.displayText !== "" ? control.displayText : control.placeholder
        color: control.displayText !== "" ? Theme.text : Theme.textFaint
        font: control.font
        elide: Text.ElideRight
        verticalAlignment: Text.AlignVCenter
    }
    property string placeholder: "Sélectionner…"

    background: Rectangle {
        radius: Theme.radiusControl
        color: Theme.bg
        border.width: 1
        border.color: control.popup.visible || control.activeFocus ? Theme.accent
                    : (control.hovered ? Theme.borderHi : Theme.border)
        Behavior on border.color { ColorAnimation { duration: 120 } }
    }

    popup: Popup {
        y: control.height + 6
        width: control.width
        padding: 8
        implicitHeight: Math.min(contentItem.implicitHeight + 16, 260)
        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator {}
        }
        background: Rectangle {
            radius: Theme.radiusControl + 2
            color: Theme.surface
            border.color: Theme.borderHi
        }
    }
}
