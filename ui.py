import json
import os
import threading
import webbrowser
import qdarkstyle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QPushButton, QFileDialog,
                             QDesktopWidget, QDialog)
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QHeaderView, QLabel, QVBoxLayout
from downloader import Downloader

class MediaViewer(QWidget):
    def __init__(self, folder_path):
        super().__init__()
        self.setStyleSheet(qdarkstyle.load_stylesheet())

        self.setWindowTitle('Media Viewer')
        self.folder_path = folder_path
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Создание таблицы для отображения медиа файлов
        self.media_table = QTableWidget()
        self.media_table.setColumnCount(1)  # Одна колонка: имя файла
        self.media_table.setHorizontalHeaderLabels(['File Name'])
        self.media_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.media_table)

        self.load_files()
        self.setLayout(layout)

    def load_files(self):
        self.load_from_directory(self.folder_path)

    def load_from_directory(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                item = QTableWidgetItem(file)
                self.media_table.setRowCount(self.media_table.rowCount() + 1)
                self.media_table.setItem(self.media_table.rowCount() - 1, 0, item)
                item.setData(0, file_path)

        self.media_table.cellDoubleClicked.connect(self.open_media)

    def open_media(self, row, column):
        file_path = self.media_table.item(row, 0).data(0)
        webbrowser.open(file_path)

class SettingsDialog(QDialog):
    def __init__(self, default_download_path, default_threads, default_log_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Настройки')
        self.default_download_path = default_download_path
        self.default_threads = default_threads
        self.default_log_file = default_log_file
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Поле для выбора папки загрузки по умолчанию
        self.defaultPathInput = QLineEdit(self.default_download_path)
        self.defaultPathInput.setMaximumWidth(1280)
        self.defaultPathInput.setMaximumHeight(50)
        layout.addWidget(QLabel('Папка загрузки по умолчанию:'))
        layout.addWidget(self.defaultPathInput)

        # Кнопка для выбора папки
        self.selectPathButton = QPushButton('Выбрать папку...')
        self.selectPathButton.clicked.connect(self.selectDefaultPath)
        layout.addWidget(self.selectPathButton)

        # Поле для выбора количества потоков
        self.threadsInput = QLineEdit(str(self.default_threads))
        self.threadsInput.setMaximumWidth(1280)
        self.threadsInput.setMaximumHeight(50)
        layout.addWidget(QLabel('Количество потоков для загрузки:'))
        layout.addWidget(self.threadsInput)

        # Поле для выбора файла логов
        self.logFileInput = QLineEdit(self.default_log_file)
        self.logFileInput.setMaximumWidth(1280)
        self.logFileInput.setMaximumHeight(50)
        layout.addWidget(QLabel('Файл для сохранения логов:'))
        layout.addWidget(self.logFileInput)

        # Кнопка для выбора файла логов
        self.selectLogFileButton = QPushButton('Выбрать файл...')
        self.selectLogFileButton.clicked.connect(self.selectLogFile)
        layout.addWidget(self.selectLogFileButton)

        # Кнопка для сохранения параметров в файл
        self.saveButton = QPushButton('Сохранить параметры')
        self.saveButton.setMaximumWidth(1280)
        self.saveButton.setMaximumHeight(50)
        self.saveButton.clicked.connect(self.saveSettings)
        layout.addWidget(self.saveButton)


        self.setLayout(layout)

    def saveSettings(self):
        settings = {
            'download_path': self.defaultPathInput.text(),
            'threads': int(self.threadsInput.text()),
            'log_file': self.logFileInput.text()
        }
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
            QMessageBox.information(self, 'Сохранено', 'Настройки успешно сохранены в файл settings.json')
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Не удалось сохранить настройки: {str(e)}')

    def selectDefaultPath(self):
        selected_path = QFileDialog.getExistingDirectory(self, 'Выберите папку для загрузки по умолчанию')
        if selected_path:
            self.defaultPathInput.setText(selected_path)

    def selectLogFile(self):
        selected_file, _ = QFileDialog.getOpenFileName(self, 'Выберите файл для сохранения логов')
        if selected_file:
            self.logFileInput.setText(selected_file)

class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(qdarkstyle.load_stylesheet())

        self.setWindowTitle('Downloader')
        self.setWindowIcon(QIcon('ico.svg'))
        self.default_download_path = os.path.expanduser("~")  # Путь по умолчанию - домашняя директория пользователя
        self.default_threads = 5
        self.default_log_file = 'log.log'
        self.loadSettings()
        self.media_viewer = None
        self.initUI()
        self.links = []

        # Центрирование окна
        self.center()

    def initUI(self):
        layout = QVBoxLayout()

        self.settingsButton = QPushButton('Настройки')
        self.settingsButton.setMaximumWidth(1280)
        self.settingsButton.setMaximumHeight(50)
        self.settingsButton.setStyleSheet(self.get_common_stylesheet())
        self.settingsButton.clicked.connect(self.open_settings)
        layout.addWidget(self.settingsButton, alignment=Qt.AlignCenter)


        # Поле ввода URL
        self.urlInput = QLineEdit()
        self.urlInput.setMaximumWidth(1280)
        self.urlInput.setMaximumHeight(50)
        self.urlInput.setStyleSheet(self.get_common_stylesheet())
        layout.addWidget(QLabel('Введите ссылки:'), alignment=Qt.AlignCenter)
        layout.addWidget(self.urlInput, alignment=Qt.AlignCenter)

        # Кнопка добавления ссылки
        self.addButton = QPushButton('+')
        self.addButton.setMaximumWidth(1280)
        self.addButton.setMaximumHeight(50)
        self.addButton.setStyleSheet(self.get_common_stylesheet())
        self.addButton.clicked.connect(self.addLink)
        layout.addWidget(self.addButton, alignment=Qt.AlignCenter)

        # Список закрепленных ссылок
        self.linksLayout = QVBoxLayout()
        layout.addLayout(self.linksLayout)

        # Поле выбора пути для загрузки файлов
        self.outputPathInput = QLineEdit()
        self.outputPathInput.setMaximumWidth(1280)
        self.outputPathInput.setMaximumHeight(50)
        self.outputPathInput.setStyleSheet(self.get_common_stylesheet())
        layout.addWidget(QLabel('Выберите папку загрузки:'), alignment=Qt.AlignCenter)
        layout.addWidget(self.outputPathInput, alignment=Qt.AlignCenter)

        # Кнопка выбора папки
        self.browseButton = QPushButton('Обзор...')
        self.browseButton.setMaximumWidth(1280)
        self.browseButton.setMaximumHeight(50)
        self.browseButton.setStyleSheet(self.get_common_stylesheet())
        self.browseButton.clicked.connect(self.selectOutputPath)
        layout.addWidget(self.browseButton, alignment=Qt.AlignCenter)

        # Кнопка начала загрузки
        self.startButton = QPushButton('Начать загрузку')
        self.startButton.setMaximumWidth(1280)
        self.startButton.setMaximumHeight(50)
        self.startButton.setStyleSheet(self.get_common_stylesheet())
        self.startButton.clicked.connect(self.startDownload)
        layout.addWidget(self.startButton, alignment=Qt.AlignCenter)

        self.statusLabel = QLabel('')
        self.statusLabel.setMaximumWidth(1280)
        self.statusLabel.setMaximumHeight(50)
        self.statusLabel.setStyleSheet(self.get_common_stylesheet())
        layout.addWidget(self.statusLabel, alignment=Qt.AlignCenter)

        # Кнопка просмотра медиа файлов
        self.viewMediaButton = QPushButton('Просмотреть медиа')
        self.viewMediaButton.setMaximumWidth(1280)
        self.viewMediaButton.setMaximumHeight(50)
        self.viewMediaButton.setStyleSheet(self.get_common_stylesheet())
        self.viewMediaButton.clicked.connect(self.open_media_viewer)
        layout.addWidget(self.viewMediaButton, alignment=Qt.AlignCenter)

        # Кнопка для выбора папки по умолчанию
        self.setDefaultPathButton = QPushButton('Выбрать папку по умолчанию')
        self.setDefaultPathButton.setMaximumWidth(1280)
        self.setDefaultPathButton.setMaximumHeight(50)
        self.setDefaultPathButton.setStyleSheet(self.get_common_stylesheet())
        self.setDefaultPathButton.clicked.connect(self.selectDefaultPathFromSettings)
        layout.addWidget(self.setDefaultPathButton, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def open_settings(self):
        try:
            settings_dialog = SettingsDialog(self.default_download_path, self.default_threads, self.default_log_file,
                                             self)
            settings_dialog.exec_()
        except Exception as e:
            print("Error:", e)
        if settings_dialog.exec_():
            self.default_download_path = settings_dialog.defaultPathInput.text()
            self.default_threads = int(settings_dialog.threadsInput.text())
            self.default_log_file = settings_dialog.logFileInput.text()

    def loadSettings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.default_download_path = settings.get('download_path', os.path.expanduser("~"))
                self.default_threads = settings.get('threads', 5)
                self.default_log_file = settings.get('log_file', 'download.log')
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Не удалось загрузить настройки из файла: {str(e)}')

    def get_common_stylesheet(self):
        return """
            font-size: 16px;
            padding: 5px 9px 5px 9px;
            margin:0;
            max-width: 600px;
            min-width: 300px;
            border-radius: 4px;
        """

    def center(self):
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        self_geometry = self.frameGeometry()
        self_geometry.moveCenter(screen_center)
        self.move(self_geometry.topLeft())

    def addLink(self):
        link = self.urlInput.text().strip()
        if link:
            self.links.append(link)
            self.urlInput.clear()
            self.updateLinks()

    def updateLinks(self):
        for i in reversed(range(self.linksLayout.count())):
            widget = self.linksLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for link in self.links:
            label = QLabel(link)
            label.setMaximumWidth(1280)
            label.setMaximumHeight(50)
            label.setStyleSheet(self.get_common_stylesheet())
            self.linksLayout.addWidget(label, alignment=Qt.AlignCenter)

    def selectOutputPath(self):
        outputPath = QFileDialog.getExistingDirectory(self, 'Выберите папку')
        if outputPath:
            self.outputPathInput.setText(outputPath)

    def startDownload(self):
        if not self.links:
            self.statusLabel.setText('Пожалуйста, добавьте ссылки.')
            return


        self.statusLabel.setText('Загрузка начата...')
        self.download_thread = threading.Thread(target=self.downloadFiles, args=(self.links,))
        self.download_thread.start()

    def downloadFiles(self, urls):
        downloader = Downloader(urls, self.default_download_path, self.statusLabel)
        downloader.start_download()

    def selectDefaultPathFromSettings(self):
        self.outputPathInput.setText(self.default_download_path)
    def open_media_viewer(self):
        folder_path = self.outputPathInput.text()
        if os.path.isdir(folder_path):
            self.media_viewer = MediaViewer(folder_path)
            self.media_viewer.show()
        else:
            self.statusLabel.setText('Пожалуйста, выберите корректную папку.')



if __name__ == "__main__":
    app = QApplication([])
    downloader_app = DownloaderApp()
    downloader_app.show()
    app.exec_()
