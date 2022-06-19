'''
    通过API:https://api.42verse.shop/api/front/sale/queryCreatorInfoList?selectType=0获取
    product数据格式：{'productId': 118, 'productName': '小达'}
'''
import json

from selenium import webdriver
from selenium.webdriver.common.by import By

from tools.slidingValidationSolver import perfect_driver_get


class AllProduct:
    def __init__(self):
        # 配置路径
        self.driver_path = r"D:\chromedriver\chromedriver.exe"
        self.save_path = "d:/42v/"
        # 指定端口
        self.opt = webdriver.ChromeOptions()
        self.opt.add_experimental_option("debuggerAddress", "127.0.0.1:8100")
        self.driver = webdriver.Chrome(self.driver_path,
                                       options=self.opt)
        # 寄售藏品的列表，项是product的id和name
        self.product_list = []

    # 获取所有藏品的id和name
    def get_all_product_id_and_name(self):
        # 最大化窗口
        try:
            self.driver.maximize_window()
        except:
            print("第一步第一次访问：最大化窗口失败，无影响")
            pass
        # 注入js代码反爬
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                            Object.defineProperty(navigator, 'webdriver', {
                              get: () => True
                            })
                          """
        })
        # 生成访问url
        product_url = "https://api.42verse.shop/api/front/sale/queryCreatorInfoList?selectType=0"
        perfect_driver_get(self.driver, product_url)
        # 解析页面数据
        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
        data_json = json.loads(data_str)
        list = data_json['data']
        for item in list:
            creator_product_list = item['productList']
            for product in creator_product_list:
                self.product_list.append(product)
        for item in self.product_list:
            print(item)

    # get方法
    def get_product_list(self):
        return self.product_list


if __name__ == '__main__':
    all_product = AllProduct()
    all_product.get_all_product_id_and_name()
