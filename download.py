import aiohttp
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import asyncio
import os
import sys
import io
import time

async def url_get(url, public_headers):
    session = aiohttp.ClientSession()
    try:
        async with session.get(url, headers = public_headers, timeout = 5) as res:
            if res.status == 200:
                page_content = await res.text()
                soup = BeautifulSoup(page_content, 'html.parser')
                with open("source.txt", "w", encoding = "utf-8") as txt_file:
                    txt_file.write(soup.prettify())
                print("網頁內容已成功寫入網頁內容.txt")
            else:
                print(f'無法下載網頁 - {url}')
    except aiohttp.ClientError as ce:
        print(f"異常 - {ce}")
    
    finally:
        await session.close()

async def download_chapter(session, chapter_url, chapter_title, title, public_headers):
    try:
        async with session.get(chapter_url, headers = public_headers, timeout = 8) as res:
            if res.status == 200:
                chapter_text = await res.text()
                soup = BeautifulSoup(chapter_text, 'html.parser')
                text_element = soup.find('div', class_ = 'txtnav')

                if text_element:
                    text = text_element.get_text()
                    aligned_left_text = '\n'.join(line.strip() for line in text.strip().split('\n'))
                chapter_file = f"{title}/{chapter_title}.txt"
                with open(chapter_file, 'w', encoding = 'utf-8') as chapter_file:
                    chapter_file.write(aligned_left_text)
                print(f'{chapter_file} - 已經寫入')
            else:
                print(f'無法下載 - {chapter_title}.txt')
    except aiohttp.ClientError as ce:
        print(f'異常狀態：{ce}')


async def get_title_and_chapter(public_headers, url):
    await url_get(url, public_headers)
    session = aiohttp.ClientSession()
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

    # 找到節點
    chatpers = soup.select('.catalog li a')
    tasks = []

    for chapter in chatpers:
        if chapter == "#":
            continue
        chapter_url = chapter['href']
        chapter_title = chapter.text.strip()
        tasks.append(download_chapter(session, 
                                          chapter_url,
                                          chapter_title,
                                          title,
                                          public_headers
                                          ))
    await asyncio.gather(*tasks)  
    await session.close()

async def main(url):
    try:
        ua = UserAgent()
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = 'utf-8')
        public_headers = {
            'user-agent' : ua.random,
            "Accept-Encoding": "gzip, deflate, br",
        }
        await get_title_and_chapter(public_headers, url)
    except asyncio.CancelledError as ce:
        print(f"問題 - {ce}")

if __name__ == '__main__':
    start = time.time()
    book_num = int(input())
    url = f'https://www.69shuba.com/book/{book_num}/'
    loop = asyncio.get_event_loop()

    asyncio.run(main(url))

    end = time.time()
    f = f"執行時間: %f 秒" %(end - start)
    print(f"{f}")
    os.remove("source.txt")

