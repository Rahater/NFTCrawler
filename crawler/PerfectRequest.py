import json
import os
import requests


class PerfectRequest():
    def __init__(self):
        # requests' headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Cookie':
                'acw_sc__v3=62a61bb79580944ce6620fa8e4355de8213d7cb7;\
                acw_tc=0b32974e16550532295124575e01208eafb613582aaa57b96b4d8bb3f79665;\
                _uab_collina=165505322748994772455593'
        }
        self.url = "https://www.42verse.shop/index2"
        # 代理使用次数
        self.proxy_count = 0
        # 初始代理IP
        self.proxy = ''

    # 测试代理IP的request
    def proxy_test_request(self, proxy):
        proxies = {
            "http": "http://" + proxy,
            "https": "https://" + proxy,
        }
        # 设置超时时间为5s，并捕获异常
        try:
            requests.get(self.url, headers=self.headers, proxies=proxies, timeout=5)
            return True
        except Exception as e:
            # 打印报错信息
            print(e)
            return False

    # 获取可以访问网站的代理IP
    def get_proxy(self):
        while True:
            # 获取代理ip
            proxy = requests.get(
                "http://api.xiequ.cn/VAD/GetIp.aspx?act=get&uid=77093&vkey=A5C5DC250CE3A\
                27B1266435247C746C8&num=1&time=30&plat=1&re=0&type=2&so=1&ow=1&spl=3&addr=&db=1").text
            # 访问https://www.42verse.shop/index2测试是否可以正确访问
            test_response = self.proxy_test_request(proxy)
            if test_response is True:
                self.proxy_count += 1
                self.proxy = proxy
                print("第一步成功：代理ip可以访问42v，代理测试成功")
                break
            else:
                print(proxy, "第一步失败：代理ip无法使用，重新获取代理IP")

    # 使用代理IP的request
    def proxy_request(self, url):
        self.get_proxy()
        proxies = {
            "http": "http://" + self.proxy,
            "https": "https://" + self.proxy,
        }
        # 设置超时时间，若异常则重新获取代理IP并进行请求
        try:
            response = requests.get(url, headers=self.headers, proxies=proxies, timeout=3)
            return response
        except Exception as e:
            print("代理失效，重新获取代理IP.......request")
            self.get_proxy()
            return False

    # 不使用代理IP的request
    def no_proxy_request(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=3)
            return response
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    perfectRequest = PerfectRequest()
    response = perfectRequest.no_proxy_request("https://api.42verse.shop/api/front/sale/hangingAndShardList?productId=130&limit=20&selectType=1&page=1")
    print(response.text)
