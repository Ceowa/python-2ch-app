import os
import re
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

FOLDER_NAME_FROM_LINK_PATTERN = r"/(\d+)(\.html)?(#.*)?/?$"
DVACH = "https://2ch.hk"
ARCHIVACH = "https://arhivach.top"
IMAGE_EXT = [".jpg", ".png", ".gif"]
VIDEO_EXT = [".mp4", ".webm"]

class Downloader:
    def __init__(self, urls, output_path, max_workers=5, log_level=logging.INFO, log_file=None):
        self.urls = urls
        self.output_path = output_path
        self.max_workers = max_workers
        self.log_level = log_level
        self.log_file = log_file
        self.logger = self._configure_logging()

    def _configure_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.log_level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        return logger

    def start_download(self):
        links_and_folder_names = {}
        for link in self.urls:
            match = re.search(FOLDER_NAME_FROM_LINK_PATTERN, link)
            if match:
                links_and_folder_names[link] = match.group(1)
            else:
                self.logger.error(f"Incorrect link: {link}")
                return

        for k, v in links_and_folder_names.items():
            if "2ch" in k:
                self.download_from_host(self.output_path + v, "2ch", k)
            elif "arhivach" in k:
                self.download_from_host(self.output_path + v, "arhivach", k)

    def download_from_host(self, output_path, host_type, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all(
                "a",
                href=lambda href: href
                and (
                    href.endswith(".jpg")
                    or href.endswith(".png")
                    or href.endswith(".gif")
                    or href.endswith(".mp4")
                    or href.endswith(".webm")
                ),
            )
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for link in links:
                    executor.submit(self.download_file, link, output_path, host_type)
            self.logger.info(f"Downloaded all files from {url} successfully!")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}")

    def download_file(self, link, output_path, host_type):
        try:
            link_href = link["href"]
            if host_type == "2ch":
                path = DVACH + link_href
            elif host_type == "arhivach":
                if any(extension in link_href for extension in IMAGE_EXT):
                    path = ARCHIVACH + link_href
                elif any(extension in link_href for extension in VIDEO_EXT):
                    path = link_href
            if link_href.endswith(tuple(IMAGE_EXT)):
                save_folder = os.path.join(output_path, 'images')
            elif link_href.endswith(tuple(VIDEO_EXT)):
                save_folder = os.path.join(output_path, 'videos')
            else:
                save_folder = output_path
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
            filename = os.path.join(save_folder, os.path.basename(path))
            if os.path.exists(filename):
                self.logger.info(f"File {filename} already exists. Skipping download.")
                return
            with open(filename, "wb") as file:
                file.write(requests.get(path).content)
            self.logger.info(f"Downloaded {filename} successfully!")
        except Exception as e:
            self.logger.error(f"An error occurred while downloading file {link['href']}: {str(e)}")
