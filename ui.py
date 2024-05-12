import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QProgressBar, QHBoxLayout
from PyQt5.QtGui import QIcon  # Добавляем QIcon для использования иконки
from downloader import Downloader

class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Downloader')
        self.setWindowIcon(QIcon('ico.svg'))  # Устанавливаем иконку из файла ico.svg

        layout = QVBoxLayout()

        # Вертикальный layout для закрепленных ссылок
        self.linksLayout = QVBoxLayout()

        self.urlInput = QLineEdit()
        self.urlInput.setStyleSheet("padding: 6px; border: 1px solid #ced4da; border-radius: 4px;")
        layout.addWidget(QLabel('Введите ссылки:'))
        layout.addLayout(self.linksLayout)  # Добавляем layout для закрепленных ссылок
        layout.addWidget(self.urlInput)

        # Кнопка "+" для добавления ссылки
        self.addButton = QPushButton('+')
        self.addButton.setStyleSheet("padding: 8px 12px; background-color: #007bff; color: #fff; border: none; border-radius: 4px;")
        self.addButton.clicked.connect(self.addLink)
        layout.addWidget(self.addButton)

        self.outputPathInput = QLineEdit()
        self.outputPathInput.setStyleSheet("padding: 6px; border: 1px solid #ced4da; border-radius: 4px;")
        layout.addWidget(QLabel('Выберите папку загрузки:'))
        layout.addWidget(self.outputPathInput)

        self.browseButton = QPushButton('Обзор...')
        self.browseButton.setStyleSheet("padding: 8px 12px; background-color: #007bff; color: #fff; border: none; border-radius: 4px;")
        self.browseButton.clicked.connect(self.selectOutputPath)
        layout.addWidget(self.browseButton)

        self.startButton = QPushButton('Начать загрузку')
        self.startButton.setStyleSheet("padding: 8px 12px; background-color: #28a745; color: #fff; border: none; border-radius: 4px;")
        self.startButton.clicked.connect(self.startDownload)
        layout.addWidget(self.startButton)

        self.statusLabel = QLabel('')
        layout.addWidget(self.statusLabel)

        self.progressBar = QProgressBar()
        self.progressBar.setStyleSheet("QProgressBar { border: 1px solid #ced4da; border-radius: 4px; background-color: #fff; } QProgressBar::chunk { background-color: #28a745; }")
        layout.addWidget(self.progressBar)

        self.setLayout(layout)

        # Список для хранения ссылок
        self.links = []

    def addLink(self):
        link = self.urlInput.text()
        if link:
            self.links.append(link)
            self.urlInput.clear()
            self.updateLinks()  # Обновляем отображение закрепленных ссылок

    def updateLinks(self):
        # Очищаем предыдущее содержимое layout
        for i in reversed(range(self.linksLayout.count())):
            widget = self.linksLayout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Добавляем новые ссылки в layout
        for link in self.links:
            label = QLabel(link)
            self.linksLayout.addWidget(label)

    def selectOutputPath(self):
        outputPath = QFileDialog.getExistingDirectory(self, 'Выберите папку')
        if outputPath:
            self.outputPathInput.setText(outputPath)

    def startDownload(self):
        output_path = self.outputPathInput.text()

        # Создаем отдельный поток для выполнения загрузки файлов
        self.download_thread = threading.Thread(target=self.downloadFiles, args=(self.links, output_path))
        self.download_thread.start()

    def downloadFiles(self, urls, output_path):
        downloader = Downloader(urls, output_path, self.statusLabel, self.progressBar)
        downloader.start_download()

if __name__ == "__main__":
    app = QApplication([])
    downloader_app = DownloaderApp()
    downloader_app.show()
    app.exec_()
