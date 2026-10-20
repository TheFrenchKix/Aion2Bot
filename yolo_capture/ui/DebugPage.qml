import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Flickable {
    id: flick
    clip: true
    contentWidth: width
    contentHeight: col.implicitHeight + 40
    boundsBehavior: Flickable.StopAtBounds
    ScrollBar.vertical: ScrollBar {
        policy: flick.contentHeight > flick.height ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
        contentItem: Rectangle { implicitWidth: 6; radius: 3; color: Theme.borderHi }
    }
    onVisibleChanged: if (visible) backend.refreshDataset()

    ColumnLayout {
        id: col
        x: 24
        y: 20
        width: flick.width - 48 - (flick.ScrollBar.vertical.visible ? 10 : 0)
        spacing: Theme.spacing

        // ───────────── Auto-trainer ─────────────
        Card {
            Layout.fillWidth: true
            title: "Auto-trainer"
            caption: "Agrandir le dataset automatiquement pendant l'exécution"

            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    Text {
                        Layout.fillWidth: true
                        text: "Activer l'auto-trainer"
                        color: Theme.text
                        font.family: Theme.font
                        font.pixelSize: 13
                    }
                    Text {
                        Layout.fillWidth: true
                        text: backend.autoTrainerAvailable
                              ? "Enregistre une image à chaque série de N images où le modèle détecte quelque chose."
                              : "Nécessite un modèle de détection valide (page Général)."
                        color: backend.autoTrainerAvailable ? Theme.textMuted : Theme.danger
                        font.family: Theme.font
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                    }
                }
                ToggleSwitch {
                    id: autoSwitch
                    Layout.preferredWidth: 46
                    Layout.maximumWidth: 46
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    enabled: backend.autoTrainerAvailable
                    checked: backend.autoTrainer
                    onToggled: {
                        backend.autoTrainer = checked
                        checked = Qt.binding(() => backend.autoTrainer)  // reste synchronise avec le backend
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Theme.border }

            RowLayout {
                Layout.fillWidth: true
                opacity: backend.autoTrainer ? 1.0 : 0.45
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    Text {
                        Layout.fillWidth: true
                        text: "Intervalle d'enregistrement"
                        color: Theme.text
                        font.family: Theme.font
                        font.pixelSize: 13
                    }
                    Text {
                        Layout.fillWidth: true
                        text: "Une image sauvegardée toutes les N images avec détection (défaut : 1000)"
                        color: Theme.textMuted
                        font.family: Theme.font
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                    }
                }
                StyledSpin {
                    enabled: backend.autoTrainer
                    from: 10
                    to: 100000
                    stepSize: 100
                    value: backend.autoInterval
                    onValueModified: backend.autoInterval = value
                }
            }

            RowLayout {
                Layout.fillWidth: true
                opacity: backend.autoTrainer ? 1.0 : 0.45
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    Text {
                        Layout.fillWidth: true
                        text: "Enregistrer aussi les prédictions du modèle"
                        color: Theme.text
                        font.family: Theme.font
                        font.pixelSize: 13
                    }
                    Text {
                        Layout.fillWidth: true
                        text: "Optionnel, dans pre_labels/ : simple référence, jamais utilisé pour l'entraînement"
                        color: Theme.textMuted
                        font.family: Theme.font
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                    }
                }
                ToggleSwitch {
                    Layout.preferredWidth: 46
                    Layout.maximumWidth: 46
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    enabled: backend.autoTrainer
                    checked: backend.autoLabels
                    onToggled: backend.autoLabels = checked
                }
            }
        }

        // ───────────── Dataset ─────────────
        Card {
            Layout.fillWidth: true
            title: "Dataset généré"
            caption: "Dossier de sortie de l'auto-trainer"

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 42
                radius: Theme.radiusControl
                color: Theme.bg
                border.width: 1
                border.color: Theme.border
                Text {
                    anchors.fill: parent
                    anchors.leftMargin: 14
                    anchors.rightMargin: 14
                    verticalAlignment: Text.AlignVCenter
                    text: backend.datasetPath
                    color: Theme.textMuted
                    font.family: "Consolas"
                    font.pixelSize: 12
                    elide: Text.ElideMiddle
                }
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                Rectangle {
                    implicitWidth: countText.implicitWidth + 20
                    implicitHeight: 28
                    radius: 14
                    color: Theme.accentSoft
                    Text {
                        id: countText
                        anchors.centerIn: parent
                        text: backend.datasetCount + (backend.datasetCount > 1 ? " images" : " image")
                        color: Theme.accent
                        font.family: Theme.font
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                    }
                }
                Item { Layout.fillWidth: true }
                PillButton {
                    text: "↻"
                    implicitWidth: 42
                    leftPadding: 0
                    rightPadding: 0
                    onClicked: backend.refreshDataset()
                    ToolTipArea { anchors.fill: parent; text: "Recompter les images" }
                }
                PillButton {
                    text: "Ouvrir le dossier"
                    onClicked: backend.openDatasetFolder()
                }
            }
            Text {
                Layout.fillWidth: true
                Layout.topMargin: 4
                text: "Ces images sont brutes : labellisez-les dans la page Dataset (auto-labellisation) "
                      + "avant de les intégrer au modèle."
                color: Theme.textFaint
                font.family: Theme.font
                font.pixelSize: 11
                wrapMode: Text.WordWrap
            }
        }
    }
}
