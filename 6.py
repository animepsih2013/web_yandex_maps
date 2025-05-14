import os
import sys
import requests
from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 450
MIN_SCALE = 0
MAX_SCALE = 17
MOVE_STEP = 0.05


class MapViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.coordinates = [37.618423, 55.751244]  # Longitude, Latitude (Москва)
        self.scale = 50
        self.map_style = 'map'
        self.marker_coordinates = self.coordinates.copy()  # Store initial marker coordinates
        self.validate_inputs()
        self.fetch_map_image()
        self.setup_ui()

    def validate_inputs(self):
        if not (0 < self.scale <= 100):
            print('Масштаб должен быть введен в диапазоне от 1 до 100!')
            sys.exit(1)
        self.scale = round(0.17 * self.scale)
        self.scale = max(MIN_SCALE, min(self.scale, MAX_SCALE))

    def fetch_map_image(self):
        map_url = (f"http://static-maps.yandex.ru/1.x/?ll={self.coordinates[0]},{self.coordinates[1]}&z={self.scale}"
                   f"&size={SCREEN_WIDTH},{SCREEN_HEIGHT}&l={self.map_style}&pt={self.marker_coordinates[0]},{self.marker_coordinates[1]},pm2rdm")
        response = requests.get(map_url)

        if not response.ok:
            print('Ошибка выполнения запроса:')
            print(map_url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def setup_ui(self):
        self.setGeometry(100, 100, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setWindowTitle('Отображение карты')

        self.pixmap = QPixmap(self.map_file)
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.pixmap)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Введите запрос для поиска объекта...")

        self.search_button = QPushButton("Искать", self)
        self.search_button.clicked.connect(self.search_object)

        self.reset_button = QPushButton("Сброс поискового результата", self)
        self.reset_button.clicked.connect(self.reset_search_result)

        self.theme_button = QPushButton("Сменить тему", self)
        self.theme_button.clicked.connect(self.toggle_map_style)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.reset_button)  # Добавляем кнопку сброса
        layout.addWidget(self.theme_button)
        self.setLayout(layout)

    def search_object(self):
        query = self.search_input.text()
        if not query:
            print("Запрос для поиска не может быть пустым.")
            return

        search_url = f"https://geocode-maps.yandex.ru/1.x/?apikey=8013b162-6b42-4997-9691-77b7074026e0&geocode={query}&format=json"
        response = requests.get(search_url)

        if response.ok:
            json_response = response.json()
            try:
                coords = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point'][
                    'pos'].split()
                self.marker_coordinates = [float(coords[0]), float(coords[1])]
                self.coordinates = self.marker_coordinates.copy()
                self.update_map_image()
            except IndexError:
                print("Объект не найден.")
        else:
            print("Ошибка выполнения запроса поиска.")
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def reset_search_result(self):
        self.coordinates = [37.618423, 55.751244]
        self.marker_coordinates = self.coordinates.copy()
        self.update_map_image()
        self.search_input.clear()

    def toggle_map_style(self):
        self.map_style = 'skl' if self.map_style == 'map' else 'map'
        self.update_map_image()

    def update_map_image(self):
        self.fetch_map_image()
        self.pixmap = QPixmap(self.map_file)
        self.image_label.setPixmap(self.pixmap)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == 16777238:
            self.scale = min(self.scale + 1, MAX_SCALE)
            self.update_map_image()
        elif event.key() == 16777239:
            self.scale = max(self.scale - 1, MIN_SCALE)
            self.update_map_image()
        elif event.key() == 16777234:
            self.coordinates[0] -= MOVE_STEP
            self.update_map_image()
        elif event.key() == 16777236:
            self.coordinates[0] += MOVE_STEP
            self.update_map_image()
        elif event.key() == 16777235:
            self.coordinates[1] += MOVE_STEP
            self.update_map_image()
        elif event.key() == 16777237:
            self.coordinates[1] -= MOVE_STEP
            self.update_map_image()

    def closeEvent(self, event):
        if os.path.exists(self.map_file):
            os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = MapViewer()
    viewer.show()
    sys.exit(app.exec())
