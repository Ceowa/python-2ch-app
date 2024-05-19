import logging

from apiDownloader import Downloader as dwn

# Список ссылок для загрузки
urls = [
    "https://2ch.hk/gg/res/1773979.html"
]

# Путь для сохранения файлов
output_path = "/path/to/save/files/"

# Создаем экземпляр загрузчика
downloader = dwn(urls, output_path)

# Настраиваем параметры загрузки
downloader.max_workers = 10  # количество одновременных потоков
downloader.log_level = logging.DEBUG  # уровень логирования
downloader.log_file = "/path/to/logfile.log"  # файл журнала

# Запускаем загрузку файлов
downloader.start_download()
