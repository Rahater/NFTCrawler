import json
import os
import requests

from crawler.PerfectRequest import PerfectRequest


# 单个藏品的实时数据
class ProductCrawler:
    def __init__(self, product_id):
        self.perfectRequest = PerfectRequest()
        self.product_id = product_id

    # 获取藏品前20个寄售数据
    def hanging_top20_product_crawler(self):
        base_url = "https://api.42verse.shop/api/front/sale/hangingAndShardList?limit=20&selectType=1&page=1&productId="
        # 生成访问链接
        # url = base_url + str(self.product_id)
        url="https://www.42verse.shop/index2"
        print(url)
        response = self.perfectRequest.no_proxy_request(url)
        response.encoding='utf-8'
        print(response.text)


if __name__ == '__main__':
    productCrawler = ProductCrawler(142)
    productCrawler.hanging_top20_product_crawler()
