import os
import re
import requests
from bs4 import BeautifulSoup

class Downloader:
    def __init__(self):
        pass

    def download_content(self, url, output_path, file_extensions=None):
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
                    and (file_extensions is None or href.endswith(tuple(file_extensions))),
                )

                # Create directory if it does not exist
                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                total_files = len(links)
                downloaded_files = 0

                # Download each file
                for link in links:
                    link_href = link["href"]
                    path = url + link_href  # Construct full URL

                    # Extract filename from URL
                    filename = os.path.join(output_path, path.split("/")[-1])

                    # Download and save file
                    with open(filename, "wb") as file:
                        file.write(requests.get(path).content)

                    downloaded_files += 1
                    yield (downloaded_files / total_files) * 100, filename  # Yield progress and filename
            else:
                yield None, f"Failed to download from {url}. Status code: {response.status_code}"
        except Exception as e:
            yield None, f"An error occurred: {str(e)}"
