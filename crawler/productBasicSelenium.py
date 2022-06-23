'''
    通过API:https://api.42verse.shop/api/front/sale/queryCreatorInfoList?selectType=0获取
    product数据格式：{'productId': 118, 'productName': '小达'}
'''
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tools.slidingValidationSolver import perfect_driver_get
from table.tableProductBasic import *


class AllProduct:
    def __init__(self):
        # 配置路径
        self.driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
        self.save_path = r"C:/42verse/"
        # 设置option 防识别自动化
        self.opt = webdriver.ChromeOptions()
        self.opt.add_argument("--disable-blink-features=AutomationControlled")
        self.opt.add_experimental_option('useAutomationExtension', False)
        self.opt.add_experimental_option("excludeSwitches", ['enable-automation'])
        # 版本更新 需采用Service模块
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=self.opt)
        # 寄售藏品的列表，项是product的id和name
        self.product_basic_list = []

    # 获取所有藏品的id和name
    def get_all_product_basic(self):
        # 最大化窗口
        try:
            self.driver.maximize_window()
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
        # 生成访问url
        product_basic_url = "https://api.42verse.shop/api/front/sale/queryCreatorInfoList?selectType=0"
        perfect_driver_get(self.driver, product_basic_url)
        # 解析页面数据
        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
        data_json = json.loads(data_str)
        product_basic_list = data_json['data']

        for creator_item in product_basic_list:
            for product_item in creator_item['productList']:
                product_basic = {'creatorId': creator_item['creatorId'], 'creatorName': creator_item['creatorName'],
                                 'productId': product_item['productId'], 'productName': product_item['productName']}
                # print(product_basic)
                self.product_basic_list.append(product_basic)
        self.driver.quit()
        insert_product_basic(self.product_basic_list)

    # get方法
    def get_product_list(self):
        return self.product_basic_list


if __name__ == '__main__':
    AllProduct().get_all_product_basic()
