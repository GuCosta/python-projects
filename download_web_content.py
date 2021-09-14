from bs4 import BeautifulSoup
import requests
import os

BASE_URL = "https://worldradiohistory.com/Archive-Short-Wave-Television/40s/"
DOWNLOAD_DIRECTORY = "worldradio_40s"

response = requests.get(BASE_URL)
page_html = response.text
soup = BeautifulSoup(page_html, "html.parser")
file_links = soup.select("td a")

def download(url):
    filename = url.rsplit("/", 1)[1]
    r = requests.get(url, allow_redirects=True)
    if not os.path.exists(DOWNLOAD_DIRECTORY):
        os.makedirs(DOWNLOAD_DIRECTORY)
    open(DOWNLOAD_DIRECTORY + '/' + filename, 'wb').write(r.content)

for link in file_links:
    href = link["href"]
    # print(link_href)

    if ".pdf" in href:
        full_url = BASE_URL + link["href"]
        print("Downloading: " + full_url)
        download(full_url)
