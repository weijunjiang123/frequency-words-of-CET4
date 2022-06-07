from bs4 import BeautifulSoup
import json
import asyncio
import aiohttp
import re


class CET4_spider:
    hds = {
        "user-agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"
    }
    base_url = "https://m.kekenet.com/cet4/r/ydzt/"

    async def requests_url(self, url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.hds) as response:
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
        # \d{4}年\d{1,2}月英语四级阅读真题及答案 第\d套 选词填空
        new_link_list = []
        for data in link_list:
            if re.match('^\d.*?选词填空$', data[0]) != None:
                new_link_list.append(data)
                print(data)
        return new_link_list

    def save_url_list(self, content):
        with open('./link_list.txt', 'w', encoding='utf-8') as f:
            json.dump(content, f)

    def main(self):
        loop = asyncio.get_event_loop()
        link_list = loop.run_until_complete(self.get_url_list(16))
        # self.save_url_list(link_list)
        self.select_url_list(link_list)


if __name__ == "__main__":
    spider = CET4_spider()
    spider.main()
