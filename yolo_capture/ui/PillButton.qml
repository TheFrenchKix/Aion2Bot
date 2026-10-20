import QtQuick
import QtQuick.Controls.Basic

// variant : "primary" (dégradé accent), "secondary" (bordure), "ghost" (discret)
Button {
    id: control
    property string variant: "secondary"
    implicitHeight: 42
    leftPadding: 22
    rightPadding: 22
    hoverEnabled: true
    font.family: Theme.font
    font.pixelSize: 13
    font.weight: Font.DemiBold

    contentItem: Text {
        text: control.text
        font: control.font
        color: !control.enabled ? Theme.textFaint
             : (control.variant === "primary" ? "white" : Theme.text)
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    background: Rectangle {
        radius: Theme.radiusControl
        opacity: control.down ? 0.85 : 1.0
        border.width: control.variant === "secondary" ? 1 : 0
        border.color: control.hovered ? Theme.borderHi : Theme.border
        color: control.variant === "ghost" ? (control.hovered ? Theme.surfaceHi : "transparent")
             : (control.variant === "secondary" ? (control.hovered ? Theme.surfaceHi : Theme.surface)
             : "transparent")
        gradient: control.variant === "primary" && control.enabled ? grad : null
        Rectangle {  // état désactivé du bouton principal
            anchors.fill: parent
            radius: parent.radius
            visible: control.variant === "primary" && !control.enabled
            color: Theme.surfaceHi
        }
        Gradient {
            id: grad
            orientation: Gradient.Horizontal
            GradientStop { position: 0.0; color: control.hovered ? "#76A0FF" : Theme.accent }
            GradientStop { position: 1.0; color: control.hovered ? "#917BFF" : Theme.accentAlt }
        }
        Behavior on color { ColorAnimation { duration: 120 } }
    }

    HoverHandler { cursorShape: control.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor }
}
