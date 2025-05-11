import os
import sys

import requests
from PyQt5.Qt import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PIL import Image, ImageOps

SCREEN_SIZE = [600, 500]


class YandexMapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.needs_reload = True
        self.location = [37.530887, 55.703118]
        self.location_delta = 0.02
        self.layer = "map"
        self.current_org = None
        self.theme = "light"
        self.initUI()

    def getImage(self):
        map_request = "http://static-maps.yandex.ru/1.x/"

        map_params = {
            "ll": f"{self.location[0]},{self.location[1]}",
            "spn": f"{self.location_delta},{self.location_delta}",
            "l": self.layer
        }

        if self.current_org is not None:
            map_params["pt"] = f"{self.current_org[2][0]},{self.current_org[2][1]},pm2dgl"

        response = requests.get(map_request, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        if self.theme == "dark":
            self.invert_image(self.map_file)  # Инвертируем цвета, если темная тема

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

        self.search = QLineEdit(self)
        self.search.move(0, 450)
        self.search.resize(520, 20)

        self.searchButton = QPushButton("Искать", self)
        self.searchButton.move(520, 450)
        self.searchButton.resize(80, 20)
        self.searchButton.clicked.connect(self.locate_point)

        self.theme_switch = QCheckBox("Темная тема", self)
        self.theme_switch.move(0, 470)
        self.theme_switch.stateChanged.connect(self.change_theme)

    def invert_image(self, image_path):
        try:
            image = Image.open(image_path).convert("RGB")  # Конвертируем в RGB
            inverted_image = ImageOps.invert(image)
            inverted_image.save(image_path)
        except Exception as e:
            print(f"Ошибка инвертирования изображения: {e}")

    def get_address(self):
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"  # ВАШ API КЛЮЧ!

        search_params = {
            "apikey": api_key,
            "text": self.search.text(),
            "lang": "ru_RU",
            "ll": f"{self.location[0]},{self.location[1]}",
            "type": "biz"
        }

        data = requests.get(search_api_server, params=search_params)
        json_data = data.json()  # Исправлено: data -> data.json()

        # Обработка случая, когда ничего не найдено
        if not json_data["features"]:
            print("По запросу ничего не найдено.")
            return

        organization = json_data["features"][0]
        name = organization["properties"]["CompanyMetaData"]["name"]
        address = organization["properties"]["CompanyMetaData"]["address"]
        point = organization["geometry"]["coordinates"]

        self.current_org = (name, address, point)

    def locate_point(self):
        self.get_address()
        if self.current_org:  # Проверка на случай, если ничего не найдено
            self.location = self.current_org[2][:]
            self.needs_reload = True
            self.repaint()

    def change_theme(self, state):
        if state == Qt.Checked:
            self.theme = "dark"
        else:
            self.theme = "light"
        self.needs_reload = True
        self.repaint()

    def paintEvent(self, event):
        if self.needs_reload:
            self.getImage()
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)
            self.needs_reload = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.location_delta += 0.01
            self.needs_reload = True
        elif event.key() == Qt.Key_PageDown:
            self.location_delta -= 0.01
            self.needs_reload = True
        elif event.key() == Qt.Key_Up:
            self.location[1] += self.location_delta / 2
            self.needs_reload = True
        elif event.key() == Qt.Key_Down:
            self.location[1] -= self.location_delta / 2
            self.needs_reload = True
        self.repaint()

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YandexMapWidget()
    ex.show()
    sys.exit(app.exec())