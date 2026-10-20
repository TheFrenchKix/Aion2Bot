import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

ApplicationWindow {
    id: win
    visible: true
    title: "Aion2Bot - Configuration"
    width: 1140
    height: Math.min(820, Screen.desktopAvailableHeight - 40)
    minimumWidth: width
    maximumWidth: width
    minimumHeight: 560
    flags: Qt.Window | Qt.FramelessWindowHint

    property int page: 0
    readonly property var pages: [
        { label: "Général", glyph: "\u2699", soon: false },
        { label: "Debug", glyph: "\u25C8", soon: false },
        { label: "Dataset", glyph: "\u25A4", soon: false },
        { label: "Instances", glyph: "\u25A6", soon: true }
    ]
    color: "transparent"

    Rectangle {
        id: frame
        anchors.fill: parent
        radius: Theme.radiusWindow
        color: Theme.bg
        border.width: 1
        border.color: Theme.border

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 1
            spacing: 0

            // ───────────── Barre de titre ─────────────
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 64

                DragHandler { onActiveChanged: if (active) win.startSystemMove() }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 24
                    anchors.rightMargin: 16
                    spacing: 14

                    Rectangle {
                        Layout.preferredWidth: 34
                        Layout.preferredHeight: 34
                        radius: 10
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: Theme.accent }
                            GradientStop { position: 1.0; color: Theme.accentAlt }
                        }
                        Text {
                            anchors.centerIn: parent
                            text: "A"
                            color: "white"
                            font.family: Theme.font
                            font.pixelSize: 17
                            font.weight: Font.Bold
                        }
                    }
                    ColumnLayout {
                        spacing: 0
                        Text {
                            text: "Aion2Bot"
                            color: Theme.text
                            font.family: Theme.font
                            font.pixelSize: 16
                            font.weight: Font.Bold
                        }
                        Text {
                            text: "Configuration de la capture et de la détection"
                            color: Theme.textMuted
                            font.family: Theme.font
                            font.pixelSize: 12
                        }
                    }
                    Item { Layout.fillWidth: true }

                    Repeater {
                        model: [{ glyph: "–", action: "min" }, { glyph: "✕", action: "close" }]
                        delegate: Rectangle {
                            required property var modelData
                            Layout.preferredWidth: 34
                            Layout.preferredHeight: 34
                            radius: 17
                            color: wm.containsMouse
                                   ? (modelData.action === "close" ? Qt.rgba(1, 0.42, 0.42, 0.18) : Theme.surfaceHi)
                                   : "transparent"
                            Text {
                                anchors.centerIn: parent
                                text: modelData.glyph
                                color: wm.containsMouse && modelData.action === "close" ? Theme.danger : Theme.textMuted
                                font.pixelSize: modelData.action === "close" ? 13 : 16
                            }
                            MouseArea {
                                id: wm
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: modelData.action === "close" ? backend.quit() : win.showMinimized()
                            }
                        }
                    }
                }
                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: Theme.border
                }
            }

            // ───────────── Navigation + pages ─────────────
            // Ajouter un sous-menu : une entree dans `pages` + une page dans le StackLayout (meme ordre).
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 0

                Item {
                    Layout.preferredWidth: 216
                    Layout.fillHeight: true

                    Rectangle {
                        anchors.right: parent.right
                        width: 1
                        height: parent.height
                        color: Theme.border
                    }
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        anchors.rightMargin: 15
                        spacing: 6

                        Text {
                            Layout.leftMargin: 10
                            Layout.topMargin: 6
                            Layout.bottomMargin: 6
                            text: "MENU"
                            color: Theme.textFaint
                            font.family: Theme.font
                            font.pixelSize: 11
                            font.weight: Font.DemiBold
                            font.letterSpacing: 1.2
                        }
                        Repeater {
                            model: win.pages
                            delegate: NavItem {
                                required property var modelData
                                required property int index
                                label: modelData.label
                                glyph: modelData.glyph
                                soon: modelData.soon
                                active: win.page === index
                                onClicked: win.page = index
                            }
                        }
                        Item { Layout.fillHeight: true }
                    }
                }

                StackLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: win.page

                    GeneralPage {}
                    DebugPage {}
                    DatasetPage {}
                    ComingSoonPage {
                        title: "Instances"
                        description: "Gestion de plusieurs fenêtres en parallèle."
                    }
                }
            }

            // ───────────── Pied de page ─────────────
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 76

                Rectangle {
                    width: parent.width
                    height: 1
                    color: Theme.border
                }
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 24
                    anchors.rightMargin: 24
                    spacing: 10

                    Text {
                        Layout.fillWidth: true
                        visible: backend.hint !== ""
                        text: "⚠  " + backend.hint
                        color: Theme.warning
                        font.family: Theme.font
                        font.pixelSize: 12
                        elide: Text.ElideRight
                    }
                    Item { Layout.fillWidth: true; visible: backend.hint === "" }

                    PillButton {
                        text: "Quitter"
                        variant: "ghost"
                        onClicked: backend.quit()
                    }
                    PillButton {
                        text: "Lancer  →"
                        variant: "primary"
                        implicitWidth: 150
                        enabled: backend.canLaunch
                        onClicked: backend.launch()
                    }
                }
            }
        }
    }
}
