from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
import multiprocessing
import time
import concurrent.futures
import os
from fake_useragent import UserAgent

class DownloadChapter:
    def __init__(self, book_num):
        self.book_num = book_num
        self.ua = UserAgent()
        self.public_headers = {
            'user-agent': self.ua.random,
            "Accept-Encoding": "gzip, deflate, br",
        }
        self.session = requests.Session()
        self.session.headers.update(self.public_headers)

    def get_url(self, url):
        request = requests.get(url=url, headers=self.public_headers, timeout=5)
        if request.status_code == 200:
            request.encoding = request.apparent_encoding
            request = request.text
            request.encode('utf-8')
            print(request)
            soup = BeautifulSoup(request, 'html.parser')
            with open(f"{self.book_num}.txt", "w", encoding="utf-8") as txt_file:
                txt_file.write(soup.prettify())
            print("網頁內容已成功寫入網頁內容.txt")
        else:
            print(f'無法下載網頁 - {url}')

    def get_title_and_chapter(self):
        with open(f'{self.book_num}.txt', 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        title = soup.find('title').text.strip().split("最")[0].strip()
        print(title)

        if not os.path.exists(title):
            os.makedirs(title)

        chapters = soup.select('.catalog li a')
        chapter_links = []

        for chapter in chapters:
            if chapter == "#":
                continue
            chapter_url = chapter['href']
            chapter_title = chapter.text.strip()
            chapter_links.append((title, chapter_title, chapter_url))

        return chapter_links

    def download_chapter(self, args):
        title, chapter_title, chapter_url = args

        try:
            response = self.session.get(chapter_url, timeout=30)
            if response.status_code == 200:
                response.encoding = response.apparent_encoding
                chapter_text = response.text
                chapter_text.encode('utf-8')
                soup = BeautifulSoup(chapter_text, 'html.parser')
                text_element = soup.find('div', class_='txtnav')
                if text_element:
                    text = text_element.get_text()
                    aligned_left_text = '\n'.join(line.strip() for line in text.strip().split('\n'))
                chapter_file = f"{title}/{chapter_title}.txt"
                with open(chapter_file, 'w', encoding='utf-8') as chapter_file:
                    chapter_file.write(aligned_left_text)
                print(f'{chapter_file} - 已經寫入 - {chapter_url}')
            else:
                print(f"無法下載章節 - {chapter_title}")
        except Exception as e:
            print(f'異常狀態：{e}')

def init(session):
    global shared_session
    shared_session = session

def main(url, book_num):
    download = DownloadChapter(book_num=book_num)
    download.get_url(url)
    chapter_links = download.get_title_and_chapter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download.download_chapter, chapter_links)

if __name__ == "__main__":
    start = time.time()
    book_num = int(input("book number -> "))
    url = f'https://www.69shuba.com/book/{book_num}/'
    main(url, book_num)

    end = time.time()
    f = f"執行時間: %f 秒" %(end - start)
    print(f"{f}")