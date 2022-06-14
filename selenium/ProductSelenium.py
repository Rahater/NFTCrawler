# coding=utf-8
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import xlsxwriter

'''
 1. 打开cmd 打开指定端口、文件夹的独立浏览器
 示例：chrome.exe --remote-debugging-port=8100 --user-data-dir="G:\42verse\selenium1"
 2. 使用ctrl+R刷新页面1次，滑动页面即可生成cookie(暂时不考虑保存cookie以进行脚本访问)
 3. get_product_shardid_first_child
 作用：用于访问api接口 只能访问前20个
 最新上架链接：https://api.42verse.shop/api/front/sale/list?creatorId=35&productId=142&saleType=0 可获取寄售时间
 价格升序链接：https://api.42verse.shop/api/front/sale/hangingAndShardList?selectType=1&productId=142 可获取寄售总数
 价格升序链接2：https://api.42verse.shop/api/front/sale/list?creatorId=35&productId=142&orderSort=asc&saleType=0 可获取寄售时间
 价格降序链接：https://api.42verse.shop/api/front/sale/list?creatorId=35&productId=142&orderSort=desc&saleType=0
 4. 
 未寄售藏品全体访问：
    没有必要，数据暂无参考性 lastId=用于加载下一部分
    链接：https://api.42verse.shop/api/front/sale/hangingAndShardList?productId=142&selectType=2&lastId=27
 寄售藏品全体访问：
    selectType=1表示寄售，lastSalePrice=&lastId=用于加载下一部分
    链接：https://api.42verse.shop/api/front/sale/hangingAndShardList?productId=142&selectType=1&lastSalePrice=3488.00&lastId=1182
    代码步骤：首先调用get_product_shardid_first_child获取前20个，再依次根据前一次的最末尾的lastSalePric和lastId来生成访问链接，依次类推循环
'''


class ProductSelenium:
    def __init__(self, product_id):
        # 配置路径
        self.driver_path = r"D:\Program Files\chromedriver\chromedriver.exe"
        self.save_path = "G:/42verse/"
        # 指定端口
        self.opt = webdriver.ChromeOptions()
        self.opt.add_experimental_option("debuggerAddress", "127.0.0.1:8100")
        self.driver = webdriver.Chrome(self.driver_path,
                                       options=self.opt)
        # 藏品ID
        self.product_id = product_id
        # 藏品名称
        self.product_name = ""
        # 藏品寄售总数量
        self.product_total = 0
        # 藏品寄售页面总数量
        self.product_totalPage = 0
        # 三次访问api的计数器
        self.first_count = 1
        self.second_count = 1
        self.third_count = 1

    # 第一步：爬取数据阶段
    # 子函数：用于第一次爬取，只获取寄售藏品前20个数据
    def get_product_shardid_first_child(self):
        # 最大化窗口
        try:
            self.driver.maximize_window()
        except:
            print("get_product_shardid_first_child：最大化窗口失败，无影响")
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
        1. 藏品数据data部分的key:
            dict_keys(['hangingId', 'hangingNo', 'shardId', 'image', 'storeName', 'salePrice', 'productId', 
            'saleStatus', 'creatorName', 'chainAccountAddress', 'createTime', 'updateTime', 'blindBoxLevelIcon'])
        '''
        # 获取藏品总数、页面总数、藏品名称
        self.product_total = data_json['data']['total']
        self.product_totalPage = data_json['data']['totalPage']
        self.product_name = product_list[0]['storeName']
        # 打印藏品数据
        for item in product_list:
            print("第一步：寄售藏品总数：{product_total}；寄售藏品序号：{index}；寄售藏品名称：{storeName}；寄售藏品编号：{shardId};寄售藏品价格：{salePrice}".
                  format(product_total=self.product_total, index=self.first_count, storeName=item['storeName'],
                         salePrice=item['salePrice'], shardId=item['shardId']))
            self.first_count += 1
        # 保存藏品数据
        self.first_save_product_shardid_to_txt(product_list)
        # 获取最末尾数据
        sale_price, shard_id = product_list[19]['salePrice'], product_list[19]['shardId']
        return self.product_total, self.product_totalPage, sale_price, shard_id

    # 第一步：爬取数据阶段
    # 子函数：用于第二次之后的每次爬取，每次获取20个寄售藏品数据
    def get_product_shardid_second_child(self, lastSalePrice, lastId, flag):
        # 生成藏品url
        product_url = "https://api.42verse.shop/api/front/sale/hangingAndShardList?productId={" \
                      "productId}&selectType=1&lastSalePrice={lastSalePrice}&lastId={lastId}". \
            format(productId=str(self.product_id), lastSalePrice=lastSalePrice, lastId=lastId)
        # 模拟浏览（未作异常处理：出现滑块验证页面情况）
        self.driver.get(product_url)
        # 解析页面数据
        html = self.driver.execute_script("return document.documentElement.outerHTML")
        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
        data_json = json.loads(data_str)
        product_list = data_json['data']['list']
        # 打印藏品数据
        for item in product_list:
            print("第一步：寄售藏品总数：{product_total}；寄售藏品序号：{index}；寄售藏品名称：{storeName}；寄售藏品编号：{shardId};寄售藏品价格：{salePrice}".
                  format(product_total=self.product_total, index=self.first_count, storeName=item['storeName'],
                         salePrice=item['salePrice'], shardId=item['shardId']))
            self.first_count += 1
        # 保存藏品数据
        self.save_product_shardid_to_txt(product_list)
        # flag为True表示当前访问的链接是第一步的最后一次
        # 当前访问页面不是第一步的最后一个页面，获取20个数据中最末尾寄售价格和shardId，用于第一步的下一次访问
        if flag is False:
            sale_price, shard_id = product_list[19]['salePrice'], product_list[19]['shardId']
            return sale_price, shard_id

    # 第一步：爬取数据阶段
    # 父函数：获取寄售藏品的基础数据，主要用于获取shardid
    def get_product_shardid(self):
        # 必须使用get_product_shardid_first_child访问藏品前20个数据以获取总数，原因：由于两个子函数的访问api不一致导致，只有第一次访问才能获取到寄售藏品总数、寄售藏品页面总数
        product_total, product_totalPage, sale_price, shard_id = self.get_product_shardid_first_child()
        for index in range(0, product_totalPage - 1):
            # 判断是否是该寄售藏品的最后一次访问页面
            if index == product_totalPage - 2:
                # flag为True表示当前访问的链接是第一步的最后一个页面
                flag = True
                self.get_product_shardid_second_child(sale_price, shard_id, flag)
                # 最后一次访问结束关闭driver进程
                # self.driver.quit()
            else:
                flag = False
                sale_price, shard_id = self.get_product_shardid_second_child(sale_price, shard_id, flag)
                # 睡眠0.2s
                time.sleep(0.2)

    # 第一步：存储数据阶段：覆盖模式
    # 第一次访问时保存寄售藏品数据
    def first_save_product_shardid_to_txt(self, product_list):
        with open(self.save_path + str(self.product_id) + '-第一步.txt', 'w',
                  encoding='utf-8') as f:
            for item in product_list:
                # 使用json的dumps方法将字典数据转成json数据，方便后续读取数据
                item_json = json.dumps(item)
                f.write(item_json + '\n')

    # 第一步：存储数据阶段：追加模式
    # 非第一次访问时保存寄售藏品数据
    def save_product_shardid_to_txt(self, product_list):
        with open(self.save_path + str(self.product_id) + '-第一步.txt', 'a+',
                  encoding='utf-8') as f:
            for item in product_list:
                # 使用json的dumps方法将字典数据转成json数据，方便后续读取数据
                item_json = json.dumps(item)
                f.write(item_json + '\n')

    # 第一步：读取数据阶段
    # 获取寄售藏品数据，返回字典格式数据，用于获取shardid
    def read_product_shardid_from_txt(self):
        with open(self.save_path + str(self.product_id) + '-第一步.txt', 'r',
                  encoding='utf-8') as f:
            product_list_str = f.readlines()
            # 存储字典数据的列表
            product_list = []
            for item in product_list_str:
                product_json = json.loads(item)
                product_list.append(product_json)
        return product_list

    # 第二步：爬取数据阶段
    # 获取所有寄售藏品的salePrice和buyPrice
    def get_product_price(self):
        # 读取第一步的txt数据
        product_list = self.read_product_shardid_from_txt()
        # 带寄售价格和购买价格的藏品列表
        product_price_list = []
        for item in product_list:
            # 获取作品编号
            shardId = item['shardId']
            # 生成含有价格的寄售作品api链接
            product_price_url = "https://api.42verse.shop/api/front/sale/dynamicInfo?productId={productId}&shardId={shardId}".format(
                productId=self.product_id, shardId=shardId)
            # 访问api并进行解析
            self.driver.get(product_price_url)
            html = self.driver.execute_script("return document.documentElement.outerHTML")
            data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
            data_json = json.loads(data_str)
            # 获取salePrice和buyPrice
            sale_price = data_json['data']['salePrice']
            buy_price = data_json['data']['buyPrice']
            item['salePrice'] = sale_price
            item['buyPrice'] = buy_price
            product_price_list.append(item)
            # 打印藏品数据
            print(
                "第二步：寄售藏品总数：{product_total}；寄售藏品序号：{index}；寄售藏品名称：{storeName}；寄售藏品编号：{shardId};寄售藏品价格：{salePrice}；上次购买价格：{buyPrice}".
                    format(product_total=self.product_total, index=self.second_count,
                           storeName=item['storeName'],
                           salePrice=item['salePrice'], shardId=item['shardId'], buyPrice=item['buyPrice']))
            self.second_count += 1
            # 最后一次循环关闭chromedriver进程
            # if product_list.index(item) == len(product_list) - 1:
            #     self.driver.quit()
            # 睡眠0.2s
            time.sleep(0.2)
        # 存储第二步的数据
        self.save_product_price_to_txt(product_price_list)

    # 第二步:存储数据阶段
    # 保存寄售藏品的购买价格和寄售价格
    def save_product_price_to_txt(self, product_price_list):
        with open(self.save_path + str(self.product_id) + '-第二步.txt', 'w',
                  encoding='utf-8') as f:
            for item in product_price_list:
                # 使用json的dumps方法将字典数据转成json数据，方便后续读取数据
                item_json = json.dumps(item)
                f.write(item_json + '\n')

    # 第二步：读取数据阶段
    # 获取寄售藏品的购买价格和寄售价格
    def read_product_price_from_txt(self):
        with open(self.save_path + str(self.product_id) + '-第二步.txt', 'r',
                  encoding='utf-8') as f:
            product_list_str = f.readlines()
            # 存储字典数据的列表
            product_list = []
            for item in product_list_str:
                product_json = json.loads(item)
                product_list.append(product_json)
        return product_list

    # 第三步：爬取数据阶段
    # 利用第一步的shardid去遍历所有寄售藏品，得到藏品细节信息
    def get_product_all(self):
        # 从带寄售价格和购买价格的txt文件读取数据
        product_list = self.read_product_price_from_txt()
        product_all_list = []
        for item in product_list:
            # 获取作品编号
            shardId = item['shardId']
            # 生成寄售作品api链接
            product_url = "https://api.42verse.shop/api/front/product/shard/detail?shardId={shardId}&productId={productId}".format(
                productId=self.product_id, shardId=shardId)
            # 访问api并解析数据
            self.driver.get(product_url)
            html = self.driver.execute_script("return document.documentElement.outerHTML")
            data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
            data_json = json.loads(data_str)
            # 获取所有数据
            # 持有者昵称
            ownerNickName = data_json['data']['ownerNickName']
            # 一次都没有交易过的藏品此项默认长度为2
            if len(data_json['data']['shardTransferRecordList']) != 2:
                # 上次交易时间
                transferTime = data_json['data']['shardTransferRecordList'][0]['transferTime']
                # 上个卖家ID
                fromUserName = data_json['data']['shardTransferRecordList'][0]['fromUserName']
                # 转手次数
                transferCount = len(data_json['data']['shardTransferRecordList']) - 1
            else:
                # 上次交易时间
                transferTime = data_json['data']['shardTransferRecordList'][1]['transferTime']
                # 上个卖家ID
                fromUserName = '铸造发行'
                # 转手次数
                transferCount = 0
            # 发行量和流通量
            castQty = data_json['data']['castQty']
            activeCount = data_json['data']['activeCount']
            # 藏品名称
            storeName = data_json['data']['storeName']
            # 生成字典
            product_dic = {}
            product_dic['storeName'] = storeName
            product_dic['salePrice'] = item['salePrice']
            product_dic['buyPrice'] = item['buyPrice']
            product_dic['shardId'] = item['shardId']
            if product_dic['salePrice'] == None:
                product_dic['fluctuate'] = "取消寄售"
            else:
                product_dic['fluctuate'] = format(
                    (float(product_dic['salePrice']) - float(product_dic['buyPrice'])) / float(product_dic['buyPrice']),
                    '.2%')
            product_dic['ownerNickName'] = ownerNickName
            product_dic['fromUserName'] = fromUserName
            product_dic['transferTime'] = transferTime
            product_dic['transferCount'] = transferCount
            product_dic['activeCount'] = activeCount
            product_dic['castQty'] = castQty
            product_all_list.append(product_dic)
            print(
                "第三步：寄售藏品总数：{product_total}；寄售藏品序号：{index}；寄售藏品名称：{storeName}；寄售藏品编号：{shardId};寄售藏品价格：{salePrice}；上次购买价格：{buyPrice}；波动：\
                {fluctuate}；当前持有者昵称：{ownerNickName}；上个卖家昵称：{fromUserName}；上次交易时间：{transferTime}；转手次数:{transferCount}；流通量：{activeCount}；发行量：{castQty}；".
                    format(product_total=self.product_total, index=self.third_count,
                           storeName=product_dic['storeName'],
                           shardId=product_dic['shardId'], salePrice=product_dic['salePrice'],
                           buyPrice=product_dic['buyPrice'], fluctuate=product_dic['fluctuate'],
                           ownerNickName=product_dic['ownerNickName'],
                           fromUserName=product_dic['fromUserName'],
                           transferTime=product_dic['transferTime'], transferCount=product_dic['transferCount'],
                           activeCount=product_dic['activeCount'], castQty=product_dic['castQty']))
            self.third_count += 1
            if product_list.index(item) == len(product_list) - 1:
                self.driver.quit()
            time.sleep(0.2)
        # 第三步：存储数据
        self.save_product_all_data_to_csv(product_all_list)

    # 第三步：存储数据阶段
    # 以csv格式保存含有价格的寄售藏品数据
    def save_product_all_data_to_csv(self, product_list):
        col = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1', 'K1']
        title = ["藏品名称", "藏品编号", "寄售价格", "上次交易价格", "波动", "当前持有者昵称", "上个卖家昵称", "上次交易时间", "转手次数", "流通量", "发行量"]
        workbook = xlsxwriter.Workbook(
            self.save_path + str(self.product_id) + '-第三步.xlsx')  # 建立文件
        worksheet = workbook.add_worksheet()
        worksheet.write_row(col[0], title)
        for index in range(len(product_list)):
            worksheet.write(index + 1, 0, product_list[index]['storeName'])
            worksheet.write(index + 1, 1, product_list[index]['shardId'])
            worksheet.write(index + 1, 2, product_list[index]['salePrice'])
            worksheet.write(index + 1, 3, product_list[index]['buyPrice'])
            worksheet.write(index + 1, 4, product_list[index]['fluctuate'])
            worksheet.write(index + 1, 5, product_list[index]['ownerNickName'])
            worksheet.write(index + 1, 6, product_list[index]['fromUserName'])
            worksheet.write(index + 1, 7, product_list[index]['transferTime'])
            worksheet.write(index + 1, 8, product_list[index]['transferCount'])
            worksheet.write(index + 1, 9, product_list[index]['activeCount'])
            worksheet.write(index + 1, 10, product_list[index]['castQty'])
        workbook.close()


if __name__ == '__main__':
    # 计时：开始
    start = time.time()
    # 初始化，使用productId
    productSelenium = ProductSelenium(155)
    # 第一步
    productSelenium.get_product_shardid()
    time.sleep(1)
    # 第二步
    productSelenium.get_product_price()
    time.sleep(1)
    # 第三步
    productSelenium.get_product_all()
    # 计时：结束
    end = time.time()

    print(end - start)
