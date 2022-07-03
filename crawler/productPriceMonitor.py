# coding=utf-8
import json
import time

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
    def __init__(self):
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
        self.product_basic_list = []

    # 获取所有藏品的id和name
    def get_all_product_basic(self):
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
                print(product_basic)
                self.product_basic_list.append(product_basic)

    # 获取单个藏品的最低价与次低价格
    def get_product_price(self, product_id):
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
            product_id)
        # 模拟浏览
        perfect_driver_get(self.driver, product_url)
        # 解析页面数据
        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
        data_json = json.loads(data_str)
        product_list = data_json['data']['list']
        # 用于判断藏品是否存在寄售，不存在寄售返回False
        if len(product_list) == 0:
            return -1, -1, -1
        # 获取当前最低价与次低价格
        return product_list[0]['salePrice'], product_list[1]['salePrice'], product_list[0]['shardId']

    # 单个藏品指定价格监控
    def product_loop_monitor(self, product_id, product_goal_price, goal_fluctuate):
        self.get_all_product_basic()
        first_product_price, second_product_price, first_product_shard_id = self.get_product_price(product_id)
        if first_product_price == -1:
            return '藏品无寄售'
        else:
            while float(first_product_price) > product_goal_price and float(
                    float(second_product_price) - float(first_product_price)) / float(
                first_product_price) < goal_fluctuate:
                print(first_product_price, second_product_price, str(round(float(
                        float(second_product_price) - float(first_product_price)) / float(
                        first_product_price), 2)))
                # 满足其中一个条件时，进行公众号消息推送
                if float(first_product_price) <= product_goal_price or float(
                        float(second_product_price) - float(first_product_price)) / float(
                    first_product_price) >= goal_fluctuate:
                    title = str(product_id) + "-" + str(
                        first_product_price) + "-" + str(second_product_price) + "-" + str(round(float(
                        float(second_product_price) - float(first_product_price)) / float(
                        first_product_price), 2))
                    desp = "https://www.42verse.shop/product/shared/{shard_id}?productId={product_id}&marketType=0".format(
                        shard_id=first_product_shard_id, product_id=product_id)
                    url = "http://wx.xtuis.cn/WposFNHMIgv1hkjkoa2awaEGx.send?text={title}&&desp={desp}".format(
                        title=title, desp=desp)
                    requests.get(url)
                # 价格高于目标价格 睡眠一分钟后再执行函数
                time.sleep(3)
                first_product_price, second_product_price, first_product_shard_id = self.get_product_price(product_id)
            self.driver.quit()

    # 所有藏品监控，以最低两个藏品价格差距作为判断条件,fluctuate是波动
    def all_product_loop_monitor(self, goal_fluctuate):
        self.get_all_product_basic()
        while True:
            for product in self.product_basic_list:
                first_product_price, second_product_price, first_product_shard_id = self.get_product_price(
                    product['productId'])
                if first_product_price == -1:
                    print("藏品无寄售")
                    continue
                fluctuate = round(
                    float(float(second_product_price) - float(first_product_price)) / float(first_product_price), 2)
                if fluctuate >= goal_fluctuate:
                    title = str(product['productName']) + "-" + str(
                        first_product_price) + "-" + str(second_product_price) + "-" + str(fluctuate)
                    desp = "https://www.42verse.shop/product/shared/{shard_id}?productId={product_id}&marketType=0".format(
                        shard_id=first_product_shard_id, product_id=product['productId'])
                    url = "http://wx.xtuis.cn/WposFNHMIgv1hkjkoa2awaEGx.send?text={title}&&desp={desp}".format(
                        title=title, desp=desp)
                    requests.get(url)
                print(str(product['productName']), first_product_price, second_product_price,
                      float(float(second_product_price) - float(first_product_price)) / float(first_product_price),
                      fluctuate)
            time.sleep(60)
            print("新一轮循环")
        self.driver.quit()


if __name__ == '__main__':
    productPriceMonitor = ProductPriceMonitor()
    productPriceMonitor.product_loop_monitor(59, 1750, 0.10)
    # productPriceMonitor.all_product_loop_monitor(0.28)
