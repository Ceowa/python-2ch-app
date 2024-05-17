import os
import threading

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
                             QProgressBar, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

from downloader import Downloader

class MediaViewer(QWidget):
    def __init__(self, folder_path):
        super().__init__()
        self.setWindowTitle('Media Viewer')
        self.folder_path = folder_path
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.file_list_widget = QListWidget()
        layout.addWidget(self.file_list_widget)
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.load_files()
        self.setLayout(layout)

    def load_files(self):
        self.file_list_widget.clear()
        files = os.listdir(self.folder_path)
        for file in files:
            item = QListWidgetItem(file)
            self.file_list_widget.addItem(item)
        self.file_list_widget.itemClicked.connect(self.play_media)

    def play_media(self, item):
        file_name = item.text()
        file_path = os.path.join(self.folder_path, file_name)
        if file_path.lower().endswith(('.mp4', '.avi', '.mov')):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.media_player.play()
        elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # Здесь можно добавить код для отображения изображений
            pass

class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Downloader')
        self.setWindowIcon(QIcon('ico.svg'))
        self.media_viewer = None
        self.initUI()
        self.links = []

    def initUI(self):
        layout = QVBoxLayout()

        # Поле ввода URL
        self.urlInput = QLineEdit()
        self.urlInput.setStyleSheet("""
        QLineEdit {padding: 6px; border: 1px solid #ced4da; border-radius: 4px;}
        """)
        layout.addWidget(QLabel('Введите ссылки:'))
        layout.addWidget(self.urlInput)

        # Кнопка добавления ссылки
        self.addButton = QPushButton('+')
        self.addButton.setStyleSheet("""
        QPushButton {
            display: inline-block;
            cursor: pointer; 
            font-size:32px;
            font-type:semibold;
            text-decoration:none;
            padding:5px 33px;
            color:#0095ff;
            background:#ffff0;
            border-radius:12px;
            border:1px solid #0095ff;
        }
        QPushButton:hover {
            background:#108ee8;
            color:#ffffff;
            border:1px solid #0095ff;
            transition: all 0.2s ease;
        }
        """)
        self.addButton.clicked.connect(self.addLink)
        layout.addWidget(self.addButton)

        # Список закрепленных ссылок
        self.linksLayout = QVBoxLayout()
        layout.addLayout(self.linksLayout)

        # Поле выбора пути для загрузки файлов
        self.outputPathInput = QLineEdit()
        self.outputPathInput.setStyleSheet("padding: 6px; border: 1px solid #ced4da; border-radius: 4px;")
        layout.addWidget(QLabel('Выберите папку загрузки:'))
        layout.addWidget(self.outputPathInput)

        # Кнопка выбора папки
        self.browseButton = QPushButton('Обзор...')
        self.browseButton.setStyleSheet("""
        QPushButton {
            display: inline-block;
            cursor: pointer; 
            font-size:32px;
            font-type:semibold;
            text-decoration:none;
            padding:5px 33px;
            color:#0095ff;
            background:#ffff0;
            border-radius:12px;
            border:1px solid #0095ff;
        }
        QPushButton:hover {
            background:#108ee8;
            color:#ffffff;
            border:1px solid #0095ff;
            transition: all 0.2s ease;
        }
        """)
        self.browseButton.clicked.connect(self.selectOutputPath)
        layout.addWidget(self.browseButton)

        # Кнопка начала загрузки
        self.startButton = QPushButton('Начать загрузку')
        self.startButton.setStyleSheet("""
        QPushButton {
            display: inline-block;
            cursor: pointer; 
            font-size:34px;
            font-type:semibold;
            text-decoration:none;
            padding:5px 33px;
            color:#0095ff;
            background:#ffff0;
            border-radius:12px;
            border:1px solid #0095ff;
        }
        QPushButton:hover {
            background:#108ee8;
            color:#ffffff;
            cursor:pointer;
            border:1px solid #0095ff;
            transition: all 0.2s ease;
        }
        """)
        self.startButton.clicked.connect(self.startDownload)
        layout.addWidget(self.startButton)

        self.statusLabel = QLabel('')
        layout.addWidget(self.statusLabel)

        # Полоса прогресса загрузки
        self.progressBar = QProgressBar()
        self.progressBar.setStyleSheet("""
        QProgressBar { border: 1px solid #212121; border-radius: 4px; background-color: #1a1a1a; } 
        QProgressBar::chunk { background-color: #28a745; }
        """)
        layout.addWidget(self.progressBar)

        # Кнопка просмотра медиа файлов
        self.viewMediaButton = QPushButton('Просмотреть медиа')
        self.viewMediaButton.setStyleSheet("""
        QPushButton {
            display: inline-block;
            cursor: pointer; 
            font-size:32px;
            font-type:semibold;
            text-decoration:none;
            padding:5px 33px;
            color:#0095ff;
            background:#ffff0;
            border-radius:12px;
            border:1px solid #0095ff;
        }
        QPushButton:hover {
            background:#108ee8;
            color:#ffffff;
            border:1px solid #0095ff;
            transition: all 0.2s ease;
        }
        """)
        self.viewMediaButton.clicked.connect(self.open_media_viewer)
        layout.addWidget(self.viewMediaButton)

        self.setLayout(layout)

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
            self.linksLayout.addWidget(label)

    def selectOutputPath(self):
        outputPath = QFileDialog.getExistingDirectory(self, 'Выберите папку')
        if outputPath:
            self.outputPathInput.setText(outputPath)

    def startDownload(self):
        output_path = self.outputPathInput.text()
        if not output_path or not self.links:
            self.statusLabel.setText('Пожалуйста, укажите путь для загрузки и добавьте ссылки.')
            return

        self.statusLabel.setText('Загрузка начата...')
        self.progressBar.setValue(0)
        self.download_thread = threading.Thread(target=self.downloadFiles, args=(self.links, output_path))
        self.download_thread.start()

    def downloadFiles(self, urls, output_path):
        downloader = Downloader(urls, output_path, self.statusLabel, self.progressBar)
        downloader.start_download()

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
