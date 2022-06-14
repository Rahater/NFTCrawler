import json
from selenium import webdriver
from selenium.webdriver.common.by import By

'''
 1. 打开cmd 打开指定端口、文件夹的独立浏览器
 示例：chrome.exe --remote-debugging-port=8100 --user-data-dir="G:\42verse\selenium1"
 2. 使用ctrl+R刷新页面1次，滑动页面即可生成cookie(暂时不考虑保存cookie以进行脚本访问)
 3. 用于访问页面
 https://www.42verse.shop/product/shared/136?productId=142&marketType=0
'''


class ProductPageSelenium:
    def __init__(self, product_id):
        # 指定端口
        self.opt = webdriver.ChromeOptions()
        self.opt.add_experimental_option("debuggerAddress", "127.0.0.1:8100")
        self.driver = webdriver.Chrome(r'D:\Program Files\chromedriver\chromedriver.exe',
                                       options=self.opt)
        # 指定藏品ID
        self.product_id = product_id

    def hanging_top20_product(self):
        # 最大化窗口
        try:
            self.driver.maximize_window()
        except:
            print("wrong:最大化窗口")
            pass
        # 注入js代码反爬
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        # 生成藏品url
        product_url = "https://api.42verse.shop/api/front/sale/hangingAndShardList?limit=20&selectType=1&page=1&productId=" + str(
            self.product_id)
        # 模拟浏览
        self.driver.get(product_url)
        # 解析页面数据
        html = self.driver.execute_script("return document.documentElement.outerHTML")
        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
        data_json = json.loads(data_str)
        product_list = data_json['data']['list']
        '''
        1. product's key:
            dict_keys(['hangingId', 'hangingNo', 'shardId', 'image', 'storeName', 'salePrice', 'productId', 
            'saleStatus', 'creatorName', 'chainAccountAddress', 'createTime', 'updateTime', 'blindBoxLevelIcon'])
        '''
        for item in product_list:
            # print("藏品：{storeName}；价格：{salePrice}；作品编号：{shardId}".
            #       format(storeName=item['storeName'], salePrice=item['salePrice'], shardId=item['shardId']))
            print(item)
        self.driver.quit()
        # self.driver.close()


if __name__ == '__main__':
    productPageSelenium = ProductPageSelenium(142)
    productPageSelenium.hanging_top20_product()
