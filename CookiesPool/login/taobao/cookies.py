from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time


class TaoBaoCookies(object):
    def __init__(self, username, password, browser):
        # 手动输入账号密码的登陆界面
        self.url = "https://login.taobao.com/member/login.jhtml"
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password
    # def load_js(self):
    #     """
    #     执行js代码，修改浏览器属性，对于一些简单的网站此方法奏效，但对于复杂的问题需要利用抓包工具替换
    #     :return:
    #     """
    #     self.browser.execute_script("Object.defineProperties(navigator,{webdriver:{get:() => false}})")
    #     print("执行脚本")

    def open(self):
        """
        打开网页输入用户名，密码，并点击
        :return: None
        """
        # self.load_js()
        self.browser.delete_all_cookies()
        self.browser.get(self.url)
        # 获取登陆界面
        """
        有时界面会发生变化，直接进入的就是用户名密码登陆界面，此时就不再需要此步骤
        """
        password_login = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'login-switch')))
        if password_login:
            password_login.click()
            time.sleep(1)
        # 获取用户名的输入框
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'TPL_username_1')))
        print(username)
        # 获取账号的输入框
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'TPL_password_1')))
        print(password)
        # 获取输入框
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'J_SubmitStatic')))
        print(submit)
        # 填写表单内容
        username.send_keys(self.username)
        password.send_keys(self.password)
        time.sleep(1)
        ##############################################################################################
        """
        此处需要滑动验证的原因为淘宝检测出来是程序在进行发送请求，经过对其检测的js文件进行修改，
        淘宝使用的探测并反selenium-webdriver的方法，正是通过判断 window.navigator.webdriver 是否为true
        在相应的报错的Js文件之中添加一段代码进行修改，并利用抓包工具进行替换
        """
        # 此处需要做是否有滑动验证

        # if self.browser.find_element_by_xpath("//*[@id='nc_1_n1t']/span"):
        #     action = ActionChains(self.browser)
        #     action.click_and_hold(self.browser.find_element_by_xpath("//*[@id='nc_1_n1t']/span")).perform()
        #     action.move_by_offset(298,0)
        #     action.release().perform()
        ##############################################################################################
        # 提交表单
        submit.click()
        # time.sleep(60)

    def password_error(self):
        """
        判断是否密码错误
        :return:
        """
        try:
            return WebDriverWait(self.browser, 5).until(EC.text_to_be_present_in_element_value((By.CLASS_NAME, 'error'), '你输入的密码和账户名不匹配'))
        except TimeoutException:
            return False

    def login_successfully(self):
        """
        判断是否登陆成功
        :return:
        """
        try:
            return bool(WebDriverWait(self.browser, 5).until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'site-nav-login-info-nick '))))
        except TimeoutException:
            return False

    def get_cookies(self):
        """
        登陆成功获取Cookies
        :return:
        """
        return self.browser.get_cookies()

    def main(self):
        """
        登陆获取Cookies如入口
        :return:
        """
        self.open()
        # 如果用户名或者密码错误
        if self.password_error():
            return {
                'status': 2,
                'content': '你输入的账号和密码不匹配'
            }
        # 如果登陆成功
        if self.login_successfully():
            # 获取登陆后的Cookies
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        else:
            return {
                'status': 3,
                'content': '登陆失败'
            }


if __name__ == "__main__":
    result = TaoBaoCookies('your account', 'your password').main()
    print(result)
