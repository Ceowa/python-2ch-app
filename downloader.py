import os
import re
import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import Qt

FOLDER_NAME_FROM_LINK_PATTERN = r"/(\d+)(\.html)?(#.*)?/?$"
DVACH = "https://2ch.hk"
ARCHIVACH = "https://arhivach.top"
IMAGE_EXT = [".jpg", ".png", ".gif"]
VIDEO_EXT = [".mp4", ".webm"]

class Downloader:
    def __init__(self, urls, output_path, status_label, progress_bar):
        self.urls = urls
        self.output_path = output_path
        self.status_label = status_label
        self.progress_bar = progress_bar

    def start_download(self):
        links_and_folder_names = {}

        # Extract links and folder names
        for link in self.urls:
            match = re.search(FOLDER_NAME_FROM_LINK_PATTERN, link)
            if match:
                links_and_folder_names[link] = match.group(1)
            else:
                self.status_label.setText(f"Incorrect link: {link}")
                return

        # Download content from each link
        for k, v in links_and_folder_names.items():
            if "2ch" in k:
                self.downloader(self.output_path + v, "2ch", k)
            elif "arhivach" in k:
                self.downloader(self.output_path + v, "arhivach", k)

    def downloader(self, output_path, host_type, url):
        try:
            # Get response from the URL
            response = requests.get(url)

            # Check if the response is successful
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Find links to download
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

                # Create directory if it does not exist
                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                total_files = len(links)
                downloaded_files = 0

                # Download each file
                for link in links:
                    link_href = link["href"]

                    # Construct full URL based on host type
                    if host_type == "2ch":
                        path = DVACH + link_href
                    elif host_type == "arhivach":
                        if any(extension in link_href for extension in IMAGE_EXT):
                            path = ARCHIVACH + link_href
                        elif any(extension in link_href for extension in VIDEO_EXT):
                            path = link_href

                    # Extract filename from URL
                    filename = os.path.join(output_path, path.split("/")[-1])

                    # Download and save file
                    with open(filename, "wb") as file:
                        file.write(requests.get(path).content)

                    downloaded_files += 1
                    progress = int(downloaded_files / total_files * 100)
                    self.progress_bar.setValue(progress)
                    self.status_label.setText(f"Downloaded {filename} successfully!")
            else:
                self.status_label.setText(f"Failed to download from {url}. Status code: {response.status_code}")
        except Exception as e:
            self.status_label.setText(f"An error occurred: {str(e)}")
