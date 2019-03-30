import json
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from cookiespool.config import *
from cookiespool.db import RedisClient
from login.taobao.cookies import TaoBaoCookies
from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options


class CookiesGenerator(object):
    def __init__(self, website='default'):
        """
        父类, 初始化一些对象
        :param website: 名称
        :param browser: 浏览器, 若不使用浏览器则可设置为 None
        """
        # 浏览器对象
        self.website = website
        # Redis 数据库连接对象---cookies 池
        self.cookies_db = RedisClient('cookies', self.website)
        # Redis 数据库连接对象--- 用户池
        self.accounts_db = RedisClient('accounts', self.website)
        # 初始化浏览器设置
        self.init_browser()

    def __del__(self):
        """
        不论是手动关闭浏览器还是python自动回收都会触发这个方法
        :return:
        """
        self.close()
    
    def init_browser(self):
        """
        通过browser参数初始化全局浏览器供模拟登录使用
        :return:
        """
        if BROWSER_TYPE == 'PhantomJS':
            caps = DesiredCapabilities.PHANTOMJS
            caps[
                "phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Macintosh; ' \
                                                       'Intel Mac OS X 10_12_3) AppleWebKit/537.36 ' \
                                                       '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
            self.browser = webdriver.PhantomJS(desired_capabilities=caps)
            self.browser.set_window_size(1400, 500)
        elif BROWSER_TYPE == 'Chrome':
            # 为满足在Linux下达到无界面的效果而增加代码
            # self.display = Display(visible=0, size=(1920, 1080))
            # self.display.start()
            # self.options = Options()
            # self.options.add_argument('--headless')
            # self.options.add_argument('--no-sandbox')
            # self.browser = webdriver.Chrome(chrome_options=self.options)
            self.browser = webdriver.Chrome()
    
    def new_cookies(self, username, password):
        """
        新生成Cookies，子类需要重写
        :param username: 用户名
        :param password: 密码
        :return:
        """
        raise NotImplementedError
    
    def process_cookies(self, cookies):
        """
        处理Cookies
        :param cookies:
        :return:
        """
        dict = {}
        for cookie in cookies:
            dict[cookie['name']] = cookie['value']
        return dict
    
    def run(self):
        """
        运行, 得到所有账户, 然后顺次模拟登录
        :return:
        """
        accounts_usernames = self.accounts_db.usernames()
        cookies_usernames = self.cookies_db.usernames()
        
        for username in accounts_usernames:
            if not username in cookies_usernames:
                password = self.accounts_db.get(username)
                print('正在生成Cookies', '账号', username, '密码', password)
                result = self.new_cookies(username, password)
                # 成功获取
                if result.get('status') == 1:
                    cookies = self.process_cookies(result.get('content'))
                    print('成功获取到Cookies', cookies)
                    if self.cookies_db.set(username, json.dumps(cookies, ensure_ascii=False)):
                        print('成功保存Cookies')
                # 密码错误，移除账号
                elif result.get('status') == 2:
                    print(result.get('content'))
                    if self.accounts_db.delete(username):
                        print('成功删除账号')
                else:
                    print(result.get('content'))
        else:
            print('所有账号都已经成功获取Cookies')
    
    def close(self):
        """
        关闭
        :return:
        """
        try:
            print('Closing Browser')
            self.browser.close()
            del self.browser
        except TypeError:
            print('Browser not opened')


# 在此处写扩展站点的Cookies生成类
class TaoBaoCookiesGenerator(CookiesGenerator):
    def __init__(self, website='taobao'):
        """
        初始化操作
        :param website: 站点名称
        :param browser: 使用的浏览器
        """
        CookiesGenerator.__init__(self, website)
        self.website = website
    
    def new_cookies(self, username, password):
        """
        生成Cookies
        :param username: 用户名
        :param password: 密码
        :return: 用户名和Cookies
        """
        # 将自己扩展站点Cookies生成函数导入进来，将结果返回
        return TaoBaoCookies(username, password, self.browser).main()


if __name__ == '__main__':
    generator = TaoBaoCookiesGenerator()
    generator.run()
