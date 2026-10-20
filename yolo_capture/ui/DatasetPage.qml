import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Flickable {
    id: flick
    clip: true
    contentWidth: width
    contentHeight: columns.implicitHeight + 40
    boundsBehavior: Flickable.StopAtBounds
    ScrollBar.vertical: ScrollBar {
        policy: flick.contentHeight > flick.height ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
        contentItem: Rectangle { implicitWidth: 6; radius: 3; color: Theme.borderHi }
    }
    onVisibleChanged: if (visible) backend.refreshLabelStats()

    RowLayout {
        id: columns
        x: 24
        y: 20
        width: flick.width - 48 - (flick.ScrollBar.vertical.visible ? 10 : 0)
        spacing: Theme.spacing

        // ───────────── Colonne gauche : images + auto-labellisation ─────────────
        ColumnLayout {
            Layout.fillWidth: true
            Layout.preferredWidth: 1
            Layout.alignment: Qt.AlignTop
            spacing: Theme.spacing

            Card {
                Layout.fillWidth: true
                title: "1 · Images à labelliser"
                caption: "Images enregistrées par l'auto-trainer (page Debug)"

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Repeater {
                        model: [
                            { label: "Images", value: backend.imagesTotal, color: Theme.text },
                            { label: "Labellisées", value: backend.imagesLabeled, color: Theme.success },
                            { label: "Restantes", value: backend.imagesTotal - backend.imagesLabeled,
                              color: Theme.warning }
                        ]
                        delegate: Rectangle {
                            required property var modelData
                            Layout.fillWidth: true
                            implicitHeight: 62
                            radius: Theme.radiusControl
                            color: Theme.bg
                            border.width: 1
                            border.color: Theme.border
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 0
                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.value
                                    color: modelData.color
                                    font.family: Theme.font
                                    font.pixelSize: 22
                                    font.weight: Font.Bold
                                }
                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.label
                                    color: Theme.textMuted
                                    font.family: Theme.font
                                    font.pixelSize: 11
                                }
                            }
                        }
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Item { Layout.fillWidth: true }
                    PillButton {
                        text: "↻"
                        implicitWidth: 42
                        leftPadding: 0
                        rightPadding: 0
                        onClicked: backend.refreshLabelStats()
                        ToolTipArea { anchors.fill: parent; text: "Recompter" }
                    }
                    PillButton { text: "Ouvrir les images"; onClicked: backend.openDatasetFolder() }
                }
            }

            Card {
                Layout.fillWidth: true
                title: "2 · Auto-labellisation"
                caption: "Génère les labels au format YOLO, avec un aperçu annoté pour contrôle"

                Repeater {
                    model: backend.labelMethods
                    delegate: ChoiceCard {
                        required property var modelData
                        label: modelData.label
                        description: modelData.description
                        reason: modelData.reason
                        available: modelData.available
                        selected: modelData.key === backend.labelMethod
                        onPicked: backend.selectLabelMethod(modelData.key)
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    visible: backend.labelMethod === "references"
                    spacing: 8
                    Text {
                        Layout.fillWidth: true
                        text: backend.referencesInfo
                        color: Theme.textMuted
                        font.family: Theme.font
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                    }
                    PillButton { text: "Dossier references"; onClicked: backend.openReferences() }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: 6
                    spacing: 4
                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            Layout.fillWidth: true
                            text: backend.labelMethod === "model" ? "Seuil de confiance" : "Seuil de correspondance"
                            color: Theme.text
                            font.family: Theme.font
                            font.pixelSize: 13
                        }
                        Rectangle {
                            implicitWidth: thrText.implicitWidth + 18
                            implicitHeight: 24
                            radius: 12
                            color: Theme.accentSoft
                            Text {
                                id: thrText
                                anchors.centerIn: parent
                                text: backend.labelThreshold.toFixed(2)
                                color: Theme.accent
                                font.family: Theme.font
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                            }
                        }
                    }
                    StyledSlider {
                        Layout.fillWidth: true
                        from: 0.3
                        to: 0.98
                        value: backend.labelThreshold
                        onMoved: backend.labelThreshold = value
                    }
                    Text {
                        Layout.fillWidth: true
                        text: "Plus haut : moins de faux positifs, mais plus d'objets manqués."
                        color: Theme.textFaint
                        font.family: Theme.font
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 1
                        Text {
                            Layout.fillWidth: true
                            text: "Écraser les labels existants"
                            color: Theme.text
                            font.family: Theme.font
                            font.pixelSize: 13
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "Sinon, seules les images sans label sont traitées"
                            color: Theme.textMuted
                            font.family: Theme.font
                            font.pixelSize: 11
                        }
                    }
                    ToggleSwitch {
                        Layout.preferredWidth: 46
                        Layout.maximumWidth: 46
                        Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        checked: backend.labelOverwrite
                        onToggled: backend.labelOverwrite = checked
                    }
                }

                // Progression
                Rectangle {
                    Layout.fillWidth: true
                    Layout.topMargin: 6
                    implicitHeight: 8
                    radius: 4
                    color: Theme.border
                    visible: backend.labelBusy || backend.labelProgress > 0
                    Rectangle {
                        width: parent.width * backend.labelProgress
                        height: parent.height
                        radius: 4
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: Theme.accent }
                            GradientStop { position: 1.0; color: Theme.accentAlt }
                        }
                        Behavior on width { NumberAnimation { duration: 120 } }
                    }
                }
                Text {
                    Layout.fillWidth: true
                    visible: backend.labelStatus !== ""
                    text: backend.labelStatus
                    color: backend.labelStatus.indexOf("Erreur") === 0 ? Theme.danger
                         : (backend.labelBusy ? Theme.textMuted : Theme.success)
                    font.family: Theme.font
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    PillButton { text: "Voir les aperçus"; onClicked: backend.openPreviews() }
                    Item { Layout.fillWidth: true }
                    PillButton {
                        text: backend.labelBusy ? "En cours…" : "Labelliser les images"
                        variant: "primary"
                        enabled: backend.canLabel
                        onClicked: backend.runAutoLabel()
                    }
                }
            }
        }

        // ───────────── Colonne droite : dataset + entraînement ─────────────
        ColumnLayout {
            Layout.fillWidth: true
            Layout.preferredWidth: 1
            Layout.alignment: Qt.AlignTop
            spacing: Theme.spacing

            Card {
                Layout.fillWidth: true
                title: "3 · Contrôle"
                caption: "Vérifier les labels avant de les intégrer au modèle"
                Text {
                    Layout.fillWidth: true
                    text: "Ouvrez les aperçus : chaque image labellisée y est dessinée avec ses boîtes. "
                          + "Pour corriger une image, éditez son fichier dataset_auto/labels/<nom>.txt "
                          + "(CVAT, Label Studio, labelImg…) ; pour l'exclure, supprimez ce fichier. "
                          + "Les images sans détection restent sans label et ne sont pas utilisées : "
                          + "labellisez-les à la main si elles contiennent l'objet."
                    color: Theme.textMuted
                    font.family: Theme.font
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                }
                RowLayout {
                    Layout.fillWidth: true
                    Item { Layout.fillWidth: true }
                    PillButton { text: "Voir les aperçus"; onClicked: backend.openPreviews() }
                }
            }

            Card {
                Layout.fillWidth: true
                title: "4 · Dataset d'entraînement"
                caption: "Images labellisées, réparties en train (80 %) / validation (20 %)"

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Item { Layout.fillWidth: true }
                    PillButton { text: "Ouvrir le dossier"; onClicked: backend.openTrainDataset() }
                    PillButton {
                        text: "Construire le dataset"
                        variant: "primary"
                        enabled: backend.imagesLabeled >= 2
                        onClicked: backend.buildDataset()
                    }
                }
                Text {
                    Layout.fillWidth: true
                    visible: backend.buildStatus !== ""
                    text: backend.buildStatus
                    color: backend.buildOk ? Theme.success : Theme.danger
                    font.family: Theme.font
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                }
            }

            Card {
                Layout.fillWidth: true
                title: "5 · Intégration au modèle"
                caption: "Fine-tuning à partir du dernier modèle de « models »"

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
                        verticalAlignment: Text.AlignVCenter
                        text: "> " + backend.trainCommand
                        color: Theme.accent
                        font.family: "Consolas"
                        font.pixelSize: 13
                    }
                }
                Text {
                    Layout.fillWidth: true
                    text: "À lancer dans un terminal (nécessite ultralytics). Options : --model, --epochs, "
                          + "--imgsz. Le meilleur modèle est copié dans models/ et apparaît "
                          + "automatiquement dans la liste de la page Général."
                    color: Theme.textMuted
                    font.family: Theme.font
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
