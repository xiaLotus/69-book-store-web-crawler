from bs4 import BeautifulSoup
import requests
import threading
import time
import os
from fake_useragent import UserAgent

class Download_chapter:
    def __init__(self, book_num):
        self.book_num = book_num
        self.ua = UserAgent()
        self.public_headers = {
            'user-agent': self.ua.random,
            "Accept-Encoding": "gzip, deflate, br",
        }
        self.session = requests.Session()
        self.session.headers.update(self.public_headers)
        self.semaphore = threading.Semaphore(5) 

    # 傳遞目錄(ok)
    def get_url(self, url):
        request = requests.get(url = url, headers = self.public_headers, timeout = 5)
        if request.status_code == 200:
            request.encoding = request.apparent_encoding
            request = request.text
            request.encode('utf-8')
            print(request)
            soup = BeautifulSoup(request, 'html.parser')
            with open(f"{self.book_num}.txt", "w", encoding = "utf-8") as txt_file:
                txt_file.write(soup.prettify())
            print("網頁內容已成功寫入網頁內容.txt")
        else:
            print(f'無法下載網頁 - {url}')

    # 得到 1.第1章 楔子 - https://www.69shuba.com/txt/31585/22519550 這種txt檔案
    def get_title_and_chapter(self):
        try: 
            with open(f'{self.book_num}.txt', 'r', encoding = 'utf-8') as file:
                html_content = file.read()
                    
            soup = BeautifulSoup(html_content, 'html.parser')

            title = soup.find('title').text.strip().split("最")[0].strip()
            print(title)

            if not os.path.exists(title):
                os.makedirs(title)

                    # 找到節點
            chatpers = soup.select('.catalog li a')

            for chapter in chatpers:
                if chapter == "#":
                    continue
                chapter_url = chapter['href']
                chapter_title = chapter.text.strip()
                add_to_txt = f"{chapter_title} - {chapter_url}\n"
                print(add_to_txt)
                with open(f'{title}.txt', 'a', encoding='utf-8') as file:
                    file.write(add_to_txt)
            with open(f'{title}.txt', 'r', encoding = 'utf-8') as file:
                line = file.readlines()
                try:
                    line = line[1:]
                    f = open(f'{title}.txt', 'w', encoding = 'utf-8')
                    f.writelines(line)
                    f.close()
                except:
                    pass

            print(f'{title}.txt 已經準備好了。')
        except:
            pass
        os.remove(f"{self.book_num}.txt")
        return title

    def download_chapter(self, title):
        with open(f'{title}.txt', 'r', encoding = 'utf-8') as title_file:
            chapter_links = title_file.read().split('\n')

        for i, chapter_link in enumerate(chapter_links, start = 1):
            if chapter_link.strip():
                chapter_title, chapter_url = chapter_link.strip().split(" - ", 1)

            try:
                response = self.session.get(chapter_url, headers = self.public_headers, timeout = 30)
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    chapter_text = response.text
                    chapter_text.encode('utf-8')
                    soup = BeautifulSoup(chapter_text, 'html.parser')
                    text_element = soup.find('div', class_ = 'txtnav')
                    if text_element:
                        text = text_element.get_text()
                        aligned_left_text = '\n'.join(line.strip() for line in text.strip().split('\n'))
                    chapter_file = f"{title}/{chapter_title}.txt"    
                    with open(chapter_file, 'w', encoding = 'utf-8') as chapter_file:
                        chapter_file.write(aligned_left_text)
                else:
                    print(f"無法下載章節 - {chapter_title}")
            except:
                print('error')

# 傳遞運行
def main(url, book_num):
    ua = UserAgent()
    public_headers = {
            'user-agent' : ua.random,
            "Accept-Encoding": "gzip, deflate, br",
    }
    download = Download_chapter(book_num = book_num)
    download.get_url(url)

    title = download.get_title_and_chapter()
    threads = []
    thread = threading.Thread(target=download.download_chapter, args=(title, ))
    thread.start()
    threads.append(thread)

    for thread in threads:
        thread.join()    

if __name__ == "__main__":
    start = time.time()
    book_num = int(input())
    url = f'https://www.69shuba.com/book/{book_num}/'
    main(url, book_num)
    end = time.time()
    f = f"執行時間: %f 秒" %(end - start)
    print(f"{f}")