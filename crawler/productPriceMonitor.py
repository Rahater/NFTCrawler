# coding=utf-8
import json
import time
import xlsxwriter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tools.slidingValidationSolver import perfect_driver_get
import requests

'''
    介绍
        实现对单一藏品价格的实时监控
    使用流程
        设置谷歌浏览器的环境变量-设置目标浏览器的重定向
    相关接口
    参数：藏品ID、藏品当前价格、藏品目标价格
     1. 每隔一段时间获取某个藏品升序的第一个页面
     2. 与藏品目标价格进行比对
     3. 低于藏品目标价格通过虾推啥公众号发送消息提醒购买
'''


class ProductPriceMonitor:
    def __init__(self, product_id, product_goal_price):
        # 配置路径
        self.driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
        # 设置option 防识别自动化
        self.opt = webdriver.ChromeOptions()
        self.opt.add_argument("--disable-blink-features=AutomationControlled")
        self.opt.add_experimental_option('useAutomationExtension', False)
        self.opt.add_experimental_option("excludeSwitches", ['enable-automation'])
        # 版本更新 需采用Service模块
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=self.opt)
        # 藏品ID、藏品目标价格
        self.product_id = product_id
        self.product_goal_price = product_goal_price

    def get_product_price(self):
        # 最大化窗口
        try:
            self.driver.maximize_window()
        except:
            print('max exception')
            pass
        finally:
            pass
        # 注入js代码
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => True
                    })
                  """
        })
        # 生成藏品url
        product_url = "https://api.42verse.shop/api/front/sale/hangingAndShardList?limit=20&selectType=1&page=1&productId=" + str(
            self.product_id)
        # 模拟浏览
        perfect_driver_get(self.driver, product_url)
        # 解析页面数据
        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
        data_json = json.loads(data_str)
        product_list = data_json['data']['list']
        # 用于判断藏品是否存在寄售，不存在寄售返回False
        if len(product_list) == 0:
            return False
        # 存在时判断价格是否低于目标价格
        # 获取当前最低价格
        return product_list[0]['salePrice']
        # self.driver.quit()

    def loop_monitor(self):
        flag = self.get_product_price()
        if flag is False:

            return '藏品无寄售'
        else:
            while float(flag) >= self.product_goal_price:
                print(float(flag))
                # 价格高于目标价格 睡眠一分钟后再执行函数
                time.sleep(60)
                flag = self.get_product_price()
            self.driver.quit()
            # 价格低于目标价格时，进行公众号消息推送
            requests.get(
                "http://wx.xtuis.cn/WposFNHMIgv1hkjkoa2awaEGx.send?text=" + str(self.product_id) + "最新价格是" + str(
                    flag) + "&desp=Go!")



if __name__ == '__main__':
    productPriceMonitor = ProductPriceMonitor(59, 1800)
    productPriceMonitor.loop_monitor()
