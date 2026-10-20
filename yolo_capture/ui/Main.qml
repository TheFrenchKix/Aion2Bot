import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

ApplicationWindow {
    id: win
    visible: true
    title: "Aion2Bot - Configuration"
    width: 980
    height: Math.min(820, Screen.desktopAvailableHeight - 40)
    minimumWidth: width
    maximumWidth: width
    minimumHeight: 560
    flags: Qt.Window | Qt.FramelessWindowHint
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

            // ───────────── Contenu ─────────────
            Flickable {
                id: flick
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                contentWidth: width
                contentHeight: columns.implicitHeight + 40
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar {
                    policy: flick.contentHeight > flick.height ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
                    contentItem: Rectangle { implicitWidth: 6; radius: 3; color: Theme.borderHi }
                }

                RowLayout {
                    id: columns
                    x: 24
                    y: 20
                    width: flick.width - 48 - (flick.ScrollBar.vertical.visible ? 10 : 0)
                    spacing: Theme.spacing

                    // ── Colonne gauche ──
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 1
                        Layout.alignment: Qt.AlignTop
                        spacing: Theme.spacing

                        Card {
                            Layout.fillWidth: true
                            title: "Fenêtre cible"
                            caption: "Application à capturer"
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                StyledCombo {
                                    Layout.fillWidth: true
                                    model: backend.windowTitles
                                    currentIndex: backend.windowIndex
                                    placeholder: "Sélectionner une fenêtre…"
                                    onActivated: (i) => backend.setWindowIndex(i)
                                }
                                PillButton {
                                    text: "↻"
                                    implicitWidth: 42
                                    leftPadding: 0
                                    rightPadding: 0
                                    onClicked: backend.refreshWindows()
                                    ToolTipArea { anchors.fill: parent; text: "Actualiser la liste" }
                                }
                            }
                        }

                        Card {
                            Layout.fillWidth: true
                            title: "Modèle YOLO"
                            caption: "Modèles du dossier « models » (.onnx, .pt)"
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                StyledCombo {
                                    Layout.fillWidth: true
                                    model: backend.modelLabels
                                    currentIndex: backend.modelIndex
                                    onActivated: (i) => backend.setModelIndex(i)
                                    // la liste est rescannee a chaque ouverture
                                    Component.onCompleted: popup.aboutToShow.connect(backend.refreshModels)
                                }
                                PillButton {
                                    text: "↻"
                                    implicitWidth: 42
                                    leftPadding: 0
                                    rightPadding: 0
                                    onClicked: backend.refreshModels()
                                    ToolTipArea { anchors.fill: parent; text: "Actualiser la liste" }
                                }
                                PillButton {
                                    text: "Dossier"
                                    onClicked: backend.openModelsFolder()
                                    ToolTipArea { anchors.fill: parent; text: "Ouvrir le dossier models" }
                                }
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                Rectangle {
                                    Layout.preferredWidth: 8
                                    Layout.preferredHeight: 8
                                    radius: 4
                                    color: backend.modelNeutral ? Theme.textFaint
                                         : (backend.modelOk ? Theme.success : Theme.danger)
                                }
                                Text {
                                    Layout.fillWidth: true
                                    text: backend.modelInfo
                                    color: backend.modelNeutral ? Theme.textMuted
                                         : (backend.modelOk ? Theme.success : Theme.danger)
                                    font.family: Theme.font
                                    font.pixelSize: 12
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }

                        Card {
                            Layout.fillWidth: true
                            title: "Méthode de capture"
                            caption: "Les méthodes incompatibles avec cette machine sont désactivées"
                            Repeater {
                                model: backend.captureOptions
                                delegate: ChoiceCard {
                                    required property var modelData
                                    label: modelData.label
                                    description: modelData.description
                                    reason: modelData.reason
                                    available: modelData.available
                                    selected: modelData.key === backend.captureKey
                                    onPicked: backend.selectCapture(modelData.key)
                                }
                            }
                        }

                    }

                    // ── Colonne droite ──
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 1
                        Layout.alignment: Qt.AlignTop
                        spacing: Theme.spacing


                        Card {
                            Layout.fillWidth: true
                            title: "Accélération de l'inférence"
                            caption: "Matériel utilisé pour exécuter le modèle"
                            Repeater {
                                model: backend.providerOptions
                                delegate: ChoiceCard {
                                    required property var modelData
                                    label: modelData.label
                                    description: modelData.description
                                    reason: modelData.reason
                                    available: modelData.available
                                    selected: modelData.key === backend.providerKey
                                    onPicked: backend.selectProvider(modelData.key)
                                }
                            }
                        }

                        Card {
                            Layout.fillWidth: true
                            title: "Paramètres"
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 14
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 4
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Text {
                                            Layout.fillWidth: true
                                            text: "Seuil de confiance"
                                            color: Theme.text
                                            font.family: Theme.font
                                            font.pixelSize: 13
                                        }
                                        Rectangle {
                                            implicitWidth: confText.implicitWidth + 18
                                            implicitHeight: 24
                                            radius: 12
                                            color: Theme.accentSoft
                                            Text {
                                                id: confText
                                                anchors.centerIn: parent
                                                text: backend.conf.toFixed(2)
                                                color: Theme.accent
                                                font.family: Theme.font
                                                font.pixelSize: 12
                                                font.weight: Font.DemiBold
                                            }
                                        }
                                    }
                                    StyledSlider {
                                        Layout.fillWidth: true
                                        from: 0.05
                                        to: 0.95
                                        value: backend.conf
                                        onMoved: backend.conf = value
                                    }
                                }
                                RowLayout {
                                    Layout.fillWidth: true
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 1
                                        Text {
                                            Layout.fillWidth: true
                                            text: "Aperçu en direct"
                                            color: Theme.text
                                            font.family: Theme.font
                                            font.pixelSize: 13
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            text: "Affiche les détections sur la fenêtre capturée"
                                            color: Theme.textMuted
                                            font.family: Theme.font
                                            font.pixelSize: 11
                                        }
                                    }
                                    ToggleSwitch {
                                        Layout.preferredWidth: 46
                                        Layout.maximumWidth: 46
                                        Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                                        checked: backend.preview
                                        onToggled: backend.preview = checked
                                    }
                                }
                            }
                        }
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
