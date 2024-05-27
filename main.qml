import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 480
    height: 640
    title: "GPIO Button Example with QML"

    Rectangle {
        id: mainRect
        anchors.fill: parent
        color: "black"

        Text {
            id: infoText
            text: "Press the button"
            anchors.centerIn: parent
            color: "white"
            font.pointSize: 20
        }

        function buttonHeld() {
            infoText.text = "Button Held"
        }
    }
}
