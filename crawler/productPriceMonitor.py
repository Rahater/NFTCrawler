# coding=utf-8
import datetime
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from tools.purchaseSolver import ProductSolver
from tools.slidingValidationSolver import perfect_driver_get
import requests


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
                self.product_basic_list.append(product_basic)

    # 获取单个藏品的最低价格、次低价格、编号
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

    # 单个藏品监控，指定价格+差价比（次低价-最低价/次低价）；参数：藏品ID、目标锁单价格、锁单差价比、循环时间间隔
    def single_product_loop_monitor(self, product_id, product_goal_price, goal_fluctuate, loop_time):
        self.get_all_product_basic()
        first_product_price, second_product_price, first_product_shard_id = self.get_product_price(product_id)
        if first_product_price == -1:
            return '藏品暂无寄售数据'
            # 两个条件符合其一则进行公众号消息推送
        try:
            while True:
                first_product_price, second_product_price, first_product_shard_id = self.get_product_price(product_id)
                fluctuate = round(
                    float(float(second_product_price) - float(first_product_price)) / float(first_product_price), 2)
                print("程序执行常规数据打印-", str(product_id), first_product_price, second_product_price, fluctuate)
                # 满足其中一个条件时，进行公众号消息推送
                if float(first_product_price) <= product_goal_price or fluctuate >= goal_fluctuate:
                    title = str(product_id) + "-" + str(
                        first_product_price) + "-" + str(second_product_price) + "-" + str(round(float(
                        float(second_product_price) - float(first_product_price)) / float(
                        first_product_price), 2))
                    desp = "https://www.42verse.shop/product/shared/{shard_id}?productId={product_id}&marketType=0".format(
                        shard_id=first_product_shard_id, product_id=product_id)
                    url = "http://wx.xtuis.cn/WposFNHMIgv1hkjkoa2awaEGx.send?text={title}&&desp={desp}".format(
                        title=title, desp=desp)
                    # 锁单
                    purchase_solver = ProductSolver(desp)
                    purchase_solver.purchase_lowest_product()
                    # 公众号消息推送
                    requests.get(url)
                    print(title, "已锁单请尽快支付，即将睡眠180s")
                    time.sleep(180)
                time.sleep(loop_time)
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        except:
            print("single_product_loop_monitor终止")
            self.driver.quit()

    # 42Verse多个藏品监控，指定差价比+藏品ID列表；参数：锁单差价比、藏品ID列表
    def multi_product_loop_monitor_fluctuate(self, goal_fluctuate, product_id_list, loop_time):
        self.get_all_product_basic()
        try:
            while True:
                for product_id in product_id_list:
                    first_product_price, second_product_price, first_product_shard_id = self.get_product_price(
                        product_id)
                    if first_product_price == -1:
                        print("藏品无寄售")
                        continue
                    fluctuate = round(
                        float(float(second_product_price) - float(first_product_price)) / float(first_product_price), 2)
                    print(str(product_id), first_product_price, second_product_price, fluctuate)
                    if fluctuate >= goal_fluctuate:
                        title = str(first_product_price) + "-" + str(second_product_price) + "-" + str(fluctuate)
                        desp = "https://www.42verse.shop/product/shared/{shard_id}?productId={product_id}&marketType=0".format(
                            shard_id=first_product_shard_id, product_id=product_id)
                        url = "http://wx.xtuis.cn/WposFNHMIgv1hkjkoa2awaEGx.send?text={title}&&desp={desp}".format(
                            title=title, desp=desp)
                        # 抢购
                        purchase_solver = ProductSolver(desp)
                        purchase_solver.purchase_lowest_product()
                        # 公众号消息推送
                        requests.get(url)
                        print("程序锁单成功，即将睡眠180s")
                        time.sleep(180)
                time.sleep(loop_time)
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        except:
            print("multi_product_loop_monitor_fluctuate终止")
            self.driver.quit()

    # 42Verse多个藏品监控，指定价格+藏品ID列表；参数：藏品ID+价格的列表、循环间隔
    def multi_product_loop_monitor_price(self, product_id_price_list, loop_time):
        self.get_all_product_basic()
        try:
            while True:
                for product in product_id_price_list:
                    first_product_price, second_product_price, first_product_shard_id = self.get_product_price(
                        product['id'])
                    if first_product_price == -1:
                        print("藏品无寄售")
                        continue
                    print(str(product['id']), first_product_price, second_product_price)
                    if product['price'] >= first_product_price:
                        title = str(product['id']) + '-' + str(first_product_price) + "-" + str(second_product_price)
                        desp = "https://www.42verse.shop/product/shared/{shard_id}?productId={product_id}&marketType=0".format(
                            shard_id=first_product_shard_id, product_id=product['id'])
                        url = "http://wx.xtuis.cn/WposFNHMIgv1hkjkoa2awaEGx.send?text={title}&&desp={desp}".format(
                            title=title, desp=desp)
                        # 抢购
                        purchase_solver = ProductSolver(desp)
                        purchase_solver.purchase_lowest_product()
                        # 公众号消息推送
                        requests.get(url)
                        print("程序锁单成功，即将睡眠180s")
                        time.sleep(180)
                time.sleep(loop_time)
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        except:
            print("multi_product_loop_monitor_price终止")
            self.driver.quit()

    # 42Verse全平台藏品监控，指定差价比+余额+流通量；参数：锁单差价比、余额、流通量、循环时间间隔
    def all_product_loop_monitor(self, goal_fluctuate, goal_price, goal_active_count, loop_time):
        self.get_all_product_basic()
        try:
            while True:
                for product in self.product_basic_list:
                    first_product_price, second_product_price, first_product_shard_id = self.get_product_price(
                        product['productId'])
                    if first_product_price == -1:
                        print("藏品暂无寄售数据")
                        continue
                    fluctuate = round(
                        float(float(second_product_price) - float(first_product_price)) / float(first_product_price), 2)
                    print("程序常规数据打印：", product['productName'], product['productId'], first_product_price,
                          second_product_price, fluctuate)
                    if fluctuate >= goal_fluctuate and float(first_product_price) <= goal_price:
                        # 获取流通量
                        active_count_url = "https://api.42verse.shop/api/front/product/shard/detail?shardId={shard_id}&productId={product_id}".format(
                            shard_id=first_product_shard_id, product_id=product['productId'])
                        # 模拟浏览
                        perfect_driver_get(self.driver, active_count_url)
                        # 解析页面数据
                        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
                        data_json = json.loads(data_str)
                        active_count = data_json['data']['activeCount']
                        # 藏品流通量符合条件
                        if int(active_count) > goal_active_count:
                            title = str(product['productName']) + "-" + str(
                                first_product_price) + "-" + str(second_product_price) + "-" + str(fluctuate)
                            desp = "https://www.42verse.shop/product/shared/{shard_id}?productId={product_id}&marketType=0".format(
                                shard_id=first_product_shard_id, product_id=product['productId'])
                            url = "http://wx.xtuis.cn/WposFNHMIgv1hkjkoa2awaEGx.send?text={title}&&desp={desp}".format(
                                title=title, desp=desp)
                            # 抢购
                            purchase_solver = ProductSolver(desp)
                            purchase_solver.purchase_lowest_product()
                            # 公众号消息推送
                            requests.get(url)
                            print(product['productName'], product['productId'], first_product_price,
                                  second_product_price,
                                  fluctuate, "即将睡眠180s，等待锁单时间")
                            time.sleep(180)
                            continue
                        print(product['productName'], product['productId'], first_product_price, second_product_price,
                              fluctuate, active_count)
                    time.sleep(loop_time)
        except:
            print("all_product_loop_monitor终止")
            self.driver.quit()

    # 所有藏品波动监控 价格低于指定余额 抄底用
    def all_product_loop_monitor_balance(self, goal_price, loop_time):
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
        try:
            while True:
                # 生成藏品url
                product_url = "https://api.42verse.shop/api/front/sale/list?creatorId=26&productId=&lastSalePrice=&orderSort=asc&saleType=0&lastId="
                # 模拟浏览
                perfect_driver_get(self.driver, product_url)
                # 解析页面数据
                data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
                data_json = json.loads(data_str)
                product_list = data_json['data']['list']
                print(product_list[0]['productId'], product_list[0]['salePrice'])
                if float(product_list[0]['salePrice']) <= goal_price:
                    title = str(product_list[0]['productId']) + "-" + str(product_list[0]['salePrice'])
                    desp = "https://www.42verse.shop/product/shared/{shard_id}?productId={product_id}&marketType=0".format(
                        shard_id=product_list[0]['shardId'], product_id=product_list[0]['productId'])
                    url = "http://wx.xtuis.cn/WposFNHMIgv1hkjkoa2awaEGx.send?text={title}&&desp={desp}".format(
                        title=title, desp=desp)
                    # 抢购
                    purchase_solver = ProductSolver(desp)
                    purchase_solver.purchase_lowest_product()
                    # 公众号消息推送
                    requests.get(url)
                    print("程序锁单成功，即将睡眠180s")
                    time.sleep(60)
                time.sleep(loop_time)
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        except:
            print("all_product_loop_monitor_balance终止")
            self.driver.quit()


if __name__ == '__main__':
    productPriceMonitor = ProductPriceMonitor()
    # 单个藏品监控，指定价格/差价比（次低价-最低价/次低价）；参数：藏品ID、目标锁单价格、锁单差价比、循环时间间隔
    # productPriceMonitor.single_product_loop_monitor(158, 1000, 0.08, 1)
    # 42Verse全平台藏品监控，指定差价比/余额/流通量；参数：锁单差价比、余额、流通量、循环时间间隔
    # productPriceMonitor.all_product_loop_monitor(0.06, 900, 1000, 0.8)
    # 42Verse全平台藏品最低价监控，指定价格进行锁单；参数：藏品最低价 抄底用
    # productPriceMonitor.all_product_loop_monitor_balance(1700, 0.8)
    # 42Verse多个藏品监控，指定差价比/藏品ID列表；参数：锁单差价比、藏品ID列表
    goal_product_list = [79, 80, 81, 82, 83, 84]
    productPriceMonitor.multi_product_loop_monitor_fluctuate(0.08, goal_product_list, 1)
