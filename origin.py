from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
import io
import os
import sys
import time

ua = UserAgent()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = 'utf-8')

public_headers = {
    'user-agent' : ua.random,
    "Accept-Encoding": "gzip, deflate, br",
}

def url_get(url):
    request = requests.get(url, headers = public_headers)
    request.encoding = request.apparent_encoding
    request = request.text
    request.encode('utf-8')
    print(request)
    soup = BeautifulSoup(request, 'html.parser')
    try:
        with open("source.txt", "w", encoding = "utf-8") as txt_file:
            txt_file.write(soup.prettify())
        print("網頁內容已成功寫入網頁內容.txt")

    except Exception as e:
        print("寫入檔案時出現錯誤:", e)

def get_title_and_chatper():
    with open('source.txt', 'r', encoding = 'utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')

    title = soup.find('title').text.strip()
    title = title.split("最")[0].strip()
    # print(title)
    if os.path.exists(title):
        print(f'{title} - 資料夾已經存在。')
    else:
        os.makedirs(title)
    
    chatpers = soup.select('.catalog li a')
    for chapter in chatpers:
        if chapter == "#":
            continue
        chapter_url = chapter['href']
        chapter_title = chapter.text.strip()
        # print(f'{chapter_title}')

        chapter_file = f"{title}/{chapter_title}.txt"
        with open(chapter_file, 'w', encoding = 'utf-8') as chapter_file:
            # 下載章節，慢速
            try:
                chapter_requset_demo = requests.get(chapter_url, 
                                                    headers = public_headers,
                                                    timeout = 5)
                if chapter_requset_demo.status_code == 200:
                    chapter_requset_demo.encoding = chapter_requset_demo.apparent_encoding
                    chapter_text = chapter_requset_demo.text
                    chapter_file.write(chapter_text)
                    time.sleep(1)
                
                else:
                    print('出狀況咧')

                print(f'{chapter_title} - 已經寫入')
            except requests.ConnectionError as rc:
                print("連線出問題 - ", str(rc))
            
            except requests.Timeout as rt:
                print('請求超時 - ', str(rt))
            except requests.RequestException as rr:
                print('請求錯誤 - ', str(rr))
            except Exception as e:
                print('其他錯誤 - ', str(e))
        
    print(f"已建立{len(chatpers)}個章節檔案。")

        
        
    


if __name__ == '__main__':
    book_num = int(input())
    url = f'https://www.69shuba.com/book/{book_num}/'
    # url_get(url = url)
    get_title_and_chatper()