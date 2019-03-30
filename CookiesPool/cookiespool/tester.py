import json
import requests
from requests.exceptions import ConnectionError
from cookiespool.db import *


class ValidTester(object):
    def __init__(self, website='default'):
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)
    
    def test(self, username, cookies):
        raise NotImplementedError
    
    def run(self):
        cookies_groups = self.cookies_db.all()
        for username, cookies in cookies_groups.items():
            self.test(username, cookies)


# 扩展站点的Cookies的检测方法
class TaoBaoValidTester(ValidTester):
    """
    需要继承ValidTester类，并重写test()方法
    """
    def __init__(self, website='taobao'):
        ValidTester.__init__(self, website)

    def test(self, username, cookies):
        print("正在测试Cookies", cookies, '用户名', username)
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; '
                          'Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print("Cookies不合法", username)
            self.cookies_db.delete(username)
            print("删除cookies", username)
            return
        try:
            # 获取检测Cookies的URL
            test_url = TEST_URL_MAP[self.website]
            response = requests.get(test_url, timeout=20, allow_redirects=False, headers=headers, cookies=cookies)
            print("查看获取的响应：", response)
            if response.status_code == 200:
                print("Cookies有效", username)
            else:
                print(response.status_code, response.headers)
                print("Cookies失效", username)
                self.cookies_db.delete(username)
                print("删除Cookies", username)
        except ConnectionError as e:
            # 这一点也没太懂需要再次学习异常模块！！！！
            print("发生异常", e.args)


if __name__ == '__main__':
    TaoBaoValidTester().run()
