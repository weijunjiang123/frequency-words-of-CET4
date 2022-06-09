import asyncio
import json
import re
from random import choice

import aiohttp
from bs4 import BeautifulSoup
from requests import request


class CET4_spider:
    
    base_url = "https://m.kekenet.com/cet4/r/ydzt/"

    @staticmethod
    async def getheaders():
        headers_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36", ]
        headers = {'User-Agent': choice(headers_list)}
        return headers

    async def requests_url(self, url: str) -> str:
        hds = await self.getheaders()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=hds) as response:
                    return await response.text(encoding='utf-8')
        except:
            print("error connect")

    def parse_index(self, index_html: str) -> list:
        """解析出索引页面中的所有链接和标题

        Args:
            index_html (str): 解析索引页面html

        Returns:
            list: 返回历届四级阅读真题链接列表  [(title, link),]
        """
        soup = BeautifulSoup(index_html, "lxml")
        urls = []
        listItem = soup.find_all(class_='listItem')
        for item in listItem:
            link = 'https://m.kekenet.com' + item.find("a").get("href")
            title = item.find("dt").get_text()
            urls.append((title, link))
        return urls

    async def get_url_list(self, page: int) -> list:
        """异步爬取指定页数的索引页面，并返回页面中所有链接列表
        Args:
            page (int): 要爬取的页数
        Returns:
            list:返回所有页中链接列表  [(title, link),]
        """
        url_list = []
        for i in range(1, page+1):
            if i == 1:
                url = self.base_url + 'index.shtml'
                index_html = await self.requests_url(url)
                print(f'已经爬取第{i}页链接')
                url_list.extend(self.parse_index(index_html))
            else:
                url = self.base_url + 'List_' + str(i) + '.shtml'
                index_html = await self.requests_url(url)
                print(f'已经爬取第{i}页链接')
                url_list.extend(self.parse_index(index_html))
        return url_list

    def select_url_list(self, link_list: list) -> list:
        """在link_list中通过title索引， 选出所有选词填空的元素

        Args:
            link_list (list): 爬取到的所有链接及标题列表  [(title), (link), ]

        Returns:
            list: 返回选词填空链接列表
        """
        # \d{4}年\d{1,2}月英语四级阅读真题及答案 第\d套 选词填空
        new_link_list = []
        for data in link_list:
            if re.match('^\d.*?选词填空$', data[0]) != None:
                new_link_list.append(data[1])
        return new_link_list

    def save_word_list(self, content):
        """将列表保存到本地

        Args:
            content (_type_):要保存的内容
        """
        with open('./word_list.txt', 'a', encoding='utf-8') as f:
            for word in content:  
                f.write(word + '\n')
            

    def parse_content(self, html) -> list:
        soup = BeautifulSoup(html, 'lxml')
        content_text = soup.find(class_="f-y").get_text()
        content_text = content_text.replace(' ', '')
        words = re.findall('[A-O][\)|\.][a-z]+', content_text)
        return words

    async def get_link_content(self, urls: list) -> list:
        all_words = []
        for url in urls:
            html = await self.requests_url(url)
            print(f"解析:  {url}")
            words = self.parse_content(html)
            # print(words)
            all_words.extend(words)
        all_words = list(map(lambda x: re.sub(
            '[A-O][\.|\)]', '', x), all_words))
        return all_words

    def main_get_link_content(self, url_list: list):
        loop = asyncio.get_event_loop()
        all_words = loop.run_until_complete(self.get_link_content(url_list))
        all_words = set(all_words)
        self.save_word_list(list(all_words))
        print(all_words)

    def main(self):
        loop = asyncio.get_event_loop()
        link_list = loop.run_until_complete(self.get_url_list(16))
        # self.save_url_list(link_list)
        new_link_list = self.select_url_list(link_list)
        self.main_get_link_content(new_link_list)


if __name__ == "__main__":
    spider = CET4_spider()
    spider.main()
