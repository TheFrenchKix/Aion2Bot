import QtQuick
import QtQuick.Layouts

// Carte arrondie avec titre de section ; le contenu va dans `content`.
Rectangle {
    id: card
    property string title: ""
    property string caption: ""
    default property alias content: body.data

    implicitHeight: col.implicitHeight + 36
    radius: Theme.radiusCard
    color: Theme.surface
    border.color: Theme.border
    border.width: 1

    ColumnLayout {
        id: col
        anchors.fill: parent
        anchors.margins: 18
        spacing: 12

        ColumnLayout {
            spacing: 2
            visible: card.title !== ""
            Text {
                text: card.title.toUpperCase()
                color: Theme.textMuted
                font.family: Theme.font
                font.pixelSize: 11
                font.weight: Font.DemiBold
                font.letterSpacing: 1.2
            }
            Text {
                visible: card.caption !== ""
                text: card.caption
                color: Theme.textFaint
                font.family: Theme.font
                font.pixelSize: 12
            }
        }
        ColumnLayout {
            id: body
            Layout.fillWidth: true
            spacing: 6
        }
    }
}
