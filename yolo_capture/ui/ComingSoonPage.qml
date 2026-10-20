import QtQuick
import QtQuick.Layouts

// Page réservée à une future fonctionnalité.
Item {
    property string title: ""
    property string description: ""

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 10
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 56
            Layout.preferredHeight: 56
            radius: 16
            color: Theme.surfaceHi
            Text {
                anchors.centerIn: parent
                text: "▦"
                color: Theme.textMuted
                font.pixelSize: 24
            }
        }
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: title
            color: Theme.text
            font.family: Theme.font
            font.pixelSize: 18
            font.weight: Font.DemiBold
        }
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: description + "\nDisponible dans une prochaine version."
            horizontalAlignment: Text.AlignHCenter
            color: Theme.textMuted
            font.family: Theme.font
            font.pixelSize: 13
        }
    }
}
