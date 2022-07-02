# coding=utf-8
import json
import time
import xlsxwriter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tools.slidingValidationSolver import perfect_driver_get
from tools.xlsxSaver import set_style_of_excel

'''
    介绍
        实现对单一藏品的数据监控，生成Excel表格，表格包含一下数据：序号 藏品名称 藏品编号 寄售价格 寄售时间 购入价格 涨幅 持有者昵称 卖家昵称 购入时间 转手次数 流通量 发行量
    使用流程
        设置谷歌浏览器的环境变量-设置目标浏览器的重定向
    相关接口
     1. 最新上架链接：https://api.42verse.shop/api/front/sale/list?creatorId=35&productId=142&saleType=0 可获取寄售时间
     2. 价格升序链接：https://api.42verse.shop/api/front/sale/hangingAndShardList?selectType=1&productId=142 可获取寄售总数
     3. 价格升序链接2：https://api.42verse.shop/api/front/sale/list?creatorId=35&productId=142&orderSort=asc&saleType=0 可获取寄售时间
     4. 价格降序链接：https://api.42verse.shop/api/front/sale/list?creatorId=35&productId=142&orderSort=desc&saleType=0
     5. 未寄售藏品全体访问链接：https://api.42verse.shop/api/front/sale/hangingAndShardList?productId=142&selectType=2&lastId=27 数据暂无参考性
     6. 寄售藏品全体访问链接：https://api.42verse.shop/api/front/sale/hangingAndShardList?productId=142&selectType=1&lastSalePrice=3488.00&lastId=1182 \
     selectType=1表示寄售，lastSalePrice=&lastId=用于加载下一部分
'''


class ProductSelenium:
    def __init__(self, product_id):
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
        # 藏品ID
        self.product_id = product_id
        # 藏品名称
        self.product_name = ""
        # 藏品寄售总数量
        self.product_total = 0
        # 藏品寄售页面总数量
        self.product_totalPage = 0
        # 寄售藏品的列表
        self.product_list = []
        # 第一步在>=20个及藏品的情况下获取的寄售价格和购买价格
        self.sale_price = -1
        self.shard_id = -1

    # 第零步：用于判断藏品是否存在寄售
    def is_product_sale(self):
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
        # 生成藏品url
        product_url = "https://api.42verse.shop/api/front/sale/hangingAndShardList?limit=20&selectType=1&page=1&productId=" + str(
            self.product_id)
        # 模拟浏览
        perfect_driver_get(self.driver, product_url)
        # 解析页面数据
        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
        data_json = json.loads(data_str)
        first_product_list = data_json['data']['list']
        if len(first_product_list) == 0:
            return False
        return True

    # 第一步：爬取数据阶段
    # 子函数：用于第一次爬取，只获取寄售藏品前20个数据
    def get_product_shardid_first_child(self):
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
        # 生成藏品url
        product_url = "https://api.42verse.shop/api/front/sale/hangingAndShardList?limit=20&selectType=1&page=1&productId=" + str(
            self.product_id)
        # 模拟浏览
        perfect_driver_get(self.driver, product_url)
        # 解析页面数据
        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
        data_json = json.loads(data_str)
        first_product_list = data_json['data']['list']
        '''
        1. 藏品数据data部分的key:
            dict_keys(['hangingId', 'hangingNo', 'shardId', 'image', 'storeName', 'salePrice', 'productId', 
            'saleStatus', 'creatorName', 'chainAccountAddress', 'createTime', 'updateTime', 'blindBoxLevelIcon'])
        '''
        # 获取藏品总数、页面总数、藏品名称
        self.product_total = data_json['data']['total']
        self.product_totalPage = data_json['data']['totalPage']
        self.product_name = first_product_list[0]['storeName']
        # 打印藏品数据
        # for item in first_product_list:
        #     print("第一步：寄售总数：{product_total}；寄售序号：{index}；寄售名称：{storeName}；寄售编号：{shardId};寄售价格：{salePrice}".
        #           format(product_total=self.product_total, index=first_product_list.index(item), storeName=item['storeName'],
        #                  salePrice=item['salePrice'], shardId=item['shardId']))
        # 保存藏品数据
        # self.first_save_product_shardid_to_txt(first_product_list)
        # 保存藏品数据至self.product_list
        for item in first_product_list:
            self.product_list.append(item)
        # 寄售藏品数量>=20个，获取最末尾数据
        if self.product_total >= 20:
            self.sale_price, self.shard_id = first_product_list[19]['salePrice'], first_product_list[19]['shardId']

    # 第一步：爬取数据阶段
    # 子函数：用于第二次之后的每次爬取，每次获取20个寄售藏品数据
    def get_product_shardid_second_child(self, lastSalePrice, lastId, flag):
        # 生成藏品url
        product_url = "https://api.42verse.shop/api/front/sale/hangingAndShardList?productId={" \
                      "productId}&selectType=1&lastSalePrice={lastSalePrice}&lastId={lastId}". \
            format(productId=str(self.product_id), lastSalePrice=lastSalePrice, lastId=lastId)
        perfect_driver_get(self.driver, product_url)
        # 解析页面数据
        data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
        data_json = json.loads(data_str)
        first_product_list = data_json['data']['list']
        # 打印藏品数据
        # for item in first_product_list:
        #     print("第一步：寄售总数：{product_total}；寄售序号：{index}；寄售名称：{storeName}；寄售编号：{shardId};寄售价格：{salePrice}".
        #           format(product_total=self.product_total, index=first_product_list.index(item),
        #                  storeName=item['storeName'],
        #                  salePrice=item['salePrice'], shardId=item['shardId']))
        # 保存藏品数据
        # self.save_product_shardid_to_txt(first_product_list)
        # 保存藏品数据至self.product_list
        for item in first_product_list:
            self.product_list.append(item)
        # flag为True表示当前访问的链接是第一步的最后一次
        # 当前访问页面不是第一步的最后一个页面，获取20个数据中最末尾寄售价格和shardId，用于第一步的下一次访问
        if flag is False:
            self.sale_price, self.shard_id = first_product_list[19]['salePrice'], first_product_list[19]['shardId']

    # 第一步：爬取数据阶段
    # 父函数：获取寄售藏品的基础数据，主要用于获取shardid
    def get_product_shardid(self):
        # 必须使用get_product_shardid_first_child访问藏品前20个数据以获取总数，原因：由于两个子函数的访问api不一致导致，只有第一次访问才能获取到寄售藏品总数、寄售藏品页面总数
        self.get_product_shardid_first_child()
        # 排除藏品寄售总数量少于20个的情况
        if self.product_totalPage > 1:
            for index in range(0, self.product_totalPage - 1):
                # 判断是否是该寄售藏品的最后一次访问页面
                if index == self.product_totalPage - 2:
                    # flag为True表示当前访问的链接是第一步的最后一个页面
                    flag = True
                    self.get_product_shardid_second_child(self.sale_price, self.shard_id, flag)
                    # 第一步：最后一次访问结束关闭driver进程
                    # self.driver.quit()
                else:
                    flag = False
                    self.get_product_shardid_second_child(self.sale_price, self.shard_id, flag)
        print(len(self.product_list))

    # 已取消使用：第一步：存储数据阶段：覆盖模式
    # 第一次访问时保存寄售藏品数据
    def first_save_product_shardid_to_txt(self, product_list):
        with open(self.save_path + str(self.product_id) + '-' + str(self.product_name) + '-第一步.txt', 'w',
                  encoding='utf-8') as f:
            for item in product_list:
                # 使用json的dumps方法将字典数据转成json数据，方便后续读取数据
                item_json = json.dumps(item)
                f.write(item_json + '\n')

    # 已取消使用：第一步：存储数据阶段：追加模式
    # 非第一次访问时保存寄售藏品数据
    def save_product_shardid_to_txt(self, product_list):
        with open(self.save_path + str(self.product_id) + '-' + str(self.product_name) + '-第一步.txt', 'a+',
                  encoding='utf-8') as f:
            for item in product_list:
                # 使用json的dumps方法将字典数据转成json数据，方便后续读取数据
                item_json = json.dumps(item)
                f.write(item_json + '\n')

    # 已取消使用：第一步：读取数据阶段
    # 获取寄售藏品数据，返回字典格式数据，用于获取shardid
    def read_product_shardid_from_txt(self):
        with open(self.save_path + str(self.product_id) + '-' + str(self.product_name) + '-第一步.txt', 'r',
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
        # 带寄售价格和购买价格的藏品列表
        product_price_list = []
        for item in self.product_list:
            # 获取作品编号
            shardId = item['shardId']
            # 生成含有价格的寄售作品api链接
            product_price_url = "https://api.42verse.shop/api/front/sale/dynamicInfo?productId={productId}&shardId={shardId}".format(
                productId=self.product_id, shardId=shardId)
            # 访问api并进行解析
            perfect_driver_get(self.driver, product_price_url)
            data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
            data_json = json.loads(data_str)
            # 获取salePrice和buyPrice
            sale_price = data_json['data']['salePrice']
            buy_price = data_json['data']['buyPrice']
            item['salePrice'] = sale_price
            item['buyPrice'] = buy_price
            item['number'] = self.product_list.index(item) + 1
            product_price_list.append(item)
            # 打印藏品数据
            # print(
            #     "第二步：寄售总数：{product_total}；寄售序号：{index}；寄售名称：{storeName}；寄售编号：{shardId};寄售价格：{salePrice}；购入价格：{buyPrice}".
            #         format(product_total=self.product_total, index=self.product_list.index(item),
            #                storeName=item['storeName'],
            #                salePrice=item['salePrice'], shardId=item['shardId'], buyPrice=item['buyPrice']))
            # 第二步：最后一次循环关闭chromedriver进程
            # if product_list.index(item) == len(product_list) - 1:
            #     self.driver.quit()
        # 存储第二步的数据
        # self.save_product_price_to_txt(product_price_list)

    # 暂不使用：第二步:存储数据阶段
    # 保存寄售藏品的购买价格和寄售价格
    def save_product_price_to_txt(self, product_price_list):
        with open(self.save_path + str(self.product_id) + '-' + str(self.product_name) + '-第二步.txt', 'w',
                  encoding='utf-8') as f:
            for item in product_price_list:
                # 使用json的dumps方法将字典数据转成json数据，方便后续读取数据
                item_json = json.dumps(item)
                f.write(item_json + '\n')

    # 暂不使用：第二步：读取数据阶段
    # 获取寄售藏品的购买价格和寄售价格
    def read_product_price_from_txt(self):
        with open(self.save_path + str(self.product_id) + '-' + str(self.product_name) + '-第二步.txt', 'r',
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
    def get_product_details(self):
        for item in self.product_list:
            # 获取作品编号
            shardId = item['shardId']
            # 生成寄售作品api链接
            product_url = "https://api.42verse.shop/api/front/product/shard/detail?shardId={shardId}&productId={" \
                          "productId}".format(
                productId=self.product_id, shardId=shardId)
            perfect_driver_get(self.driver, product_url)
            # 解析数据
            data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
            data_json = json.loads(data_str)
            # 持有者昵称
            ownerNickName = data_json['data']['ownerNickName']
            # 一次都没有交易过的藏品此项默认长度为2
            if len(data_json['data']['shardTransferRecordList']) != 2:
                # 上次购入时间
                transferTime = data_json['data']['shardTransferRecordList'][0]['transferTime']
                # 上个卖家ID
                fromUserName = data_json['data']['shardTransferRecordList'][0]['fromUserName']
                # 转手次数
                transferCount = len(data_json['data']['shardTransferRecordList']) - 1
            else:
                # 上次购入时间
                transferTime = data_json['data']['shardTransferRecordList'][1]['transferTime']
                # 上个卖家ID
                fromUserName = '42Verse官方'
                # 转手次数
                transferCount = 0
            # 发行量和流通量
            castQty = data_json['data']['castQty']
            activeCount = data_json['data']['activeCount']
            # 保存第二步self.product_list没有的项
            item['storeName'] = self.product_name
            # 在第三步运行阶段撤销寄售
            if item['salePrice'] is None:
                item['fluctuate'] = "数据丢失（已撤销寄售）"
            else:
                item['fluctuate'] = (float(item['salePrice']) - float(item['buyPrice'])) / float(item['buyPrice'])
            item['ownerNickName'] = ownerNickName
            item['fromUserName'] = fromUserName
            item['transferTime'] = transferTime
            item['transferCount'] = transferCount
            item['activeCount'] = activeCount
            item['castQty'] = castQty
            # print(
            #     "第三步：寄售总数：{product_total}；寄售序号：{index}；寄售名称：{storeName}；寄售编号：{shardId};寄售价格：{salePrice}；购入价格：{buyPrice}；涨幅：\
            #     {fluctuate}；持有者昵称：{ownerNickName}；卖家昵称：{fromUserName}；购入时间：{transferTime}；转手次数:{transferCount}；流通量：{activeCount}；发行量：{castQty}；".
            #         format(product_total=self.product_total, index=self.product_list.index(item),
            #                storeName=item['storeName'],
            #                shardId=item['shardId'], salePrice=item['salePrice'],
            #                buyPrice=item['buyPrice'], fluctuate=item['fluctuate'],
            #                ownerNickName=item['ownerNickName'],
            #                fromUserName=item['fromUserName'],
            #                transferTime=item['transferTime'], transferCount=item['transferCount'],
            #                activeCount=item['activeCount'], castQty=item['castQty']))
            # self.third_count += 1
            # if self.product_list.index(item) == len(self.product_list) - 1:
            #     self.driver.quit()
        # 第三步：存储数据
        # self.save_product_details_to_csv(self.product_list)

    # 暂不使用：第三步：存储数据阶段
    # 以xlsx格式保存含有价格的寄售藏品数据
    def save_product_details_to_csv(self, product_list):
        col = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1', 'K1']
        title = ["序号", "藏品名称", "藏品编号", "寄售价格", "购入价格", "涨幅", "持有者昵称", "卖家昵称", "购入时间", "转手次数", "流通量", "发行量"]
        workbook = xlsxwriter.Workbook(
            self.save_path + str(self.product_id) + '-' + str(self.product_name) + '-第三步.xlsx')  # 建立文件
        worksheet = workbook.add_worksheet()
        worksheet.write_row(col[0], title)
        for index in range(len(product_list)):
            worksheet.write(index + 1, 0, product_list[index]['number'])
            worksheet.write(index + 1, 1, product_list[index]['storeName'])
            worksheet.write(index + 1, 2, product_list[index]['shardId'])
            worksheet.write(index + 1, 3, product_list[index]['salePrice'])
            worksheet.write(index + 1, 4, product_list[index]['buyPrice'])
            worksheet.write(index + 1, 5, product_list[index]['fluctuate'])
            worksheet.write(index + 1, 6, product_list[index]['ownerNickName'])
            worksheet.write(index + 1, 7, product_list[index]['fromUserName'])
            worksheet.write(index + 1, 8, product_list[index]['transferTime'])
            worksheet.write(index + 1, 9, product_list[index]['transferCount'])
            worksheet.write(index + 1, 10, product_list[index]['activeCount'])
            worksheet.write(index + 1, 11, product_list[index]['castQty'])
        workbook.close()

    # 第四步：爬取数据阶段，带保存excel表的函数
    # 利用第一步的shardid去遍历所有寄售藏品，得到藏品寄售时间
    def get_product_sale_time(self):
        '''
            第一步：直接调用接口https://api.42verse.shop/api/front/sale/list?productId=142进行访问，获取lastSalePrice（寄售价格）和lastId（寄售ID）
            第二步：通过第一步获取的两个参数进行后续访问
            第三步：利用shardId进行藏品数据一一匹配，更新self.product_list数据
            第四步：保存数据
        '''
        base_url = "https://api.42verse.shop/api/front/sale/list?productId=" + str(self.product_id)
        # 通过self.product_Totalpage数量控制访问次数
        # 不足20个寄售藏品的情况
        if self.product_totalPage == 1:
            # 访问api并解析数据
            perfect_driver_get(self.driver, base_url)
            data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
            data_json = json.loads(data_str)
            fourth_product_list = data_json['data']['list']
        # 寄售藏品数量大于20个
        elif self.product_totalPage > 1:
            fourth_product_list = []
            # 进行第一次访问以获取两个参数
            # 访问api并解析数据
            perfect_driver_get(self.driver, base_url)
            data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
            data_json = json.loads(data_str)
            fourth_product_list_first = data_json['data']['list']
            lastSalePrice, lastId = fourth_product_list_first[19]['salePrice'], fourth_product_list_first[19][
                'hangingId']
            # 将fourth_product_list_first存入fourth_product_list
            for item in fourth_product_list_first:
                fourth_product_list.append(item)
            for index in range(0, self.product_totalPage - 1):
                # 寄售页面不是最后一个的情况
                if index == self.product_totalPage - 2:
                    # flag为True表示当前访问的链接是第一步的最后一个页面
                    url = "https://api.42verse.shop/api/front/sale/list?productId={productId}&lastSalePrice={lastSalePrice}&lastId={lastId}".format(
                        productId=self.product_id, lastSalePrice=lastSalePrice, lastId=lastId)
                    # 访问api并解析数据
                    perfect_driver_get(self.driver, url)
                    data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
                    data_json = json.loads(data_str)
                    fourth_product_list_second = data_json['data']['list']
                    # 将fourth_product_list_second存入fourth_product_list
                    for item in fourth_product_list_second:
                        fourth_product_list.append(item)
                # 寄售页面是最后一个的情况
                else:
                    # 获取数据并更新两个参数
                    url = "https://api.42verse.shop/api/front/sale/list?productId={productId}&lastSalePrice={lastSalePrice}&lastId={lastId}".format(
                        productId=str(self.product_id), lastSalePrice=str(lastSalePrice), lastId=str(lastId))
                    # 访问api并解析数据
                    perfect_driver_get(self.driver, url)
                    data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
                    data_json = json.loads(data_str)
                    fourth_product_list_second = data_json['data']['list']
                    lastSalePrice, lastId = fourth_product_list_second[19]['salePrice'], fourth_product_list_second[19][
                        'hangingId']
                    # 将fourth_product_list_second存入fourth_product_list
                    for item in fourth_product_list_second:
                        fourth_product_list.append(item)
                    # time.sleep(0.1)
        # 对fourth_product_list按照价格进行升序排序，然后采用双指针方法进行一一匹配
        fourth_product_list_sorted = sorted(fourth_product_list, key=lambda x: float(x.get("salePrice")))
        for item2 in self.product_list:
            item2['updateTime'] = "数据丢失（已取消寄售）"
        for item1 in fourth_product_list_sorted:
            for item2 in self.product_list:
                if item1['shardId'] == item2['shardId']:
                    item2['updateTime'] = item1['updateTime']
                    break
        self.driver.quit()
        # for item in self.product_list:
        #     print(
        #         "第四步：寄售总数：{product_total}；寄售序号：{index}；寄售名称：{storeName}；寄售编号：{shardId};寄售价格：{salePrice}；寄售时间：{updateTime}；购入价格：{buyPrice}；涨幅：\
        #         {fluctuate}；持有者昵称：{ownerNickName}；卖家昵称：{fromUserName}；购入时间：{transferTime}；转手次数:{transferCount}；流通量：{activeCount}；发行量：{castQty}；".
        #             format(product_total=self.product_total, index=self.product_list.index(item),
        #                    storeName=item['storeName'],
        #                    shardId=item['shardId'], salePrice=item['salePrice'], updateTime=item['updateTime'],
        #                    buyPrice=item['buyPrice'], fluctuate=item['fluctuate'],
        #                    ownerNickName=item['ownerNickName'],
        #                    fromUserName=item['fromUserName'],
        #                    transferTime=item['transferTime'], transferCount=item['transferCount'],
        #                    activeCount=item['activeCount'], castQty=item['castQty']))
        # 第四步：存储数据
        self.save_product_sale_time_to_excel_with_style(self.product_list)

    # 第四步：爬取数据阶段
    # 利用第一步的shardid去遍历所有寄售藏品，得到藏品寄售时间
    def get_product_sale_time_without_excel(self):
        '''
            第一步：直接调用接口https://api.42verse.shop/api/front/sale/list?productId=142进行访问，获取lastSalePrice（寄售价格）和lastId（寄售ID）
            第二步：通过第一步获取的两个参数进行后续访问
            第三步：利用shardId进行藏品数据一一匹配，更新self.product_list数据
            第四步：保存数据
        '''
        base_url = "https://api.42verse.shop/api/front/sale/list?productId=" + str(self.product_id)
        # 通过self.product_Totalpage数量控制访问次数
        # 不足20个寄售藏品的情况
        if self.product_totalPage == 1:
            # 访问api并解析数据
            perfect_driver_get(self.driver, base_url)
            data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
            data_json = json.loads(data_str)
            fourth_product_list = data_json['data']['list']
        # 寄售藏品数量大于20个
        elif self.product_totalPage > 1:
            fourth_product_list = []
            # 进行第一次访问以获取两个参数
            # 访问api并解析数据
            perfect_driver_get(self.driver, base_url)
            data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
            data_json = json.loads(data_str)
            fourth_product_list_first = data_json['data']['list']
            lastSalePrice, lastId = fourth_product_list_first[19]['salePrice'], fourth_product_list_first[19][
                'hangingId']
            # 将fourth_product_list_first存入fourth_product_list
            for item in fourth_product_list_first:
                fourth_product_list.append(item)
            for index in range(0, self.product_totalPage - 1):
                # 寄售页面不是最后一个的情况
                if index == self.product_totalPage - 2:
                    # flag为True表示当前访问的链接是第一步的最后一个页面
                    url = "https://api.42verse.shop/api/front/sale/list?productId={productId}&lastSalePrice={lastSalePrice}&lastId={lastId}".format(
                        productId=self.product_id, lastSalePrice=lastSalePrice, lastId=lastId)
                    # 访问api并解析数据
                    perfect_driver_get(self.driver, url)
                    data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
                    data_json = json.loads(data_str)
                    fourth_product_list_second = data_json['data']['list']
                    # 将fourth_product_list_second存入fourth_product_list
                    for item in fourth_product_list_second:
                        fourth_product_list.append(item)
                # 寄售页面是最后一个的情况
                else:
                    # 获取数据并更新两个参数
                    url = "https://api.42verse.shop/api/front/sale/list?productId={productId}&lastSalePrice={lastSalePrice}&lastId={lastId}".format(
                        productId=str(self.product_id), lastSalePrice=str(lastSalePrice), lastId=str(lastId))
                    # 访问api并解析数据
                    perfect_driver_get(self.driver, url)
                    data_str = self.driver.find_element(By.TAG_NAME, 'pre').text
                    data_json = json.loads(data_str)
                    fourth_product_list_second = data_json['data']['list']
                    lastSalePrice, lastId = fourth_product_list_second[19]['salePrice'], fourth_product_list_second[19][
                        'hangingId']
                    # 将fourth_product_list_second存入fourth_product_list
                    for item in fourth_product_list_second:
                        fourth_product_list.append(item)
                    # time.sleep(0.1)
        # 对fourth_product_list按照价格进行升序排序，然后采用双指针方法进行一一匹配
        fourth_product_list_sorted = sorted(fourth_product_list, key=lambda x: float(x.get("salePrice")))
        for item2 in self.product_list:
            item2['updateTime'] = "未获取"
        for item1 in fourth_product_list_sorted:
            for item2 in self.product_list:
                if item1['shardId'] == item2['shardId']:
                    item2['updateTime'] = item1['updateTime']
                    break
        # 关闭chromedriver
        self.driver.quit()
        # for item in self.product_list:
        #     print(
        #         "第四步：寄售总数：{product_total}；寄售序号：{index}；寄售名称：{storeName}；寄售编号：{shardId};寄售价格：{salePrice}；寄售时间：{updateTime}；购入价格：{buyPrice}；涨幅：\
        #         {fluctuate}；持有者昵称：{ownerNickName}；卖家昵称：{fromUserName}；购入时间：{transferTime}；转手次数:{transferCount}；流通量：{activeCount}；发行量：{castQty}；".
        #         format(product_total=self.product_total, index=self.product_list.index(item),
        #                storeName=item['storeName'],
        #                shardId=item['shardId'], salePrice=item['salePrice'], updateTime=item['updateTime'],
        #                buyPrice=item['buyPrice'], fluctuate=item['fluctuate'],
        #                ownerNickName=item['ownerNickName'],
        #                fromUserName=item['fromUserName'],
        #                transferTime=item['transferTime'], transferCount=item['transferCount'],
        #                activeCount=item['activeCount'], castQty=item['castQty']))

    # 暂不使用：第四步：不带样式的列表
    def save_product_sale_time_to_excel(self, product_list):
        col = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1', 'K1', 'L1']
        title = ["序号", "藏品名称", "藏品编号", "寄售价格", "寄售时间", "购入价格", "涨幅", "持有者昵称", "卖家昵称", "购入时间", "转手次数", "流通量", "发行量"]
        workbook = xlsxwriter.Workbook(
            self.save_path + str(self.product_id) + '-' + str(self.product_name) + '-第四步.xlsx')  # 建立文件
        worksheet = workbook.add_worksheet()
        worksheet.write_row(col[0], title)
        for index in range(len(product_list)):
            worksheet.write(index + 1, 0, product_list[index]['number'])
            worksheet.write(index + 1, 1, product_list[index]['storeName'])
            worksheet.write(index + 1, 2, product_list[index]['shardId'])
            worksheet.write(index + 1, 3, product_list[index]['salePrice'])
            worksheet.write(index + 1, 4, product_list[index]['updateTime'])
            worksheet.write(index + 1, 5, product_list[index]['buyPrice'])
            worksheet.write(index + 1, 6, product_list[index]['fluctuate'])
            worksheet.write(index + 1, 7, product_list[index]['ownerNickName'])
            worksheet.write(index + 1, 8, product_list[index]['fromUserName'])
            worksheet.write(index + 1, 9, product_list[index]['transferTime'])
            worksheet.write(index + 1, 10, product_list[index]['transferCount'])
            worksheet.write(index + 1, 11, product_list[index]['activeCount'])
            worksheet.write(index + 1, 12, product_list[index]['castQty'])
        workbook.close()

    # 第四步：带样式的列表
    def save_product_sale_time_to_excel_with_style(self, product_list):
        file_name = self.save_path + str(self.product_id) + '-' + str(self.product_name) + '.xlsx'
        set_style_of_excel(product_list, file_name, self.product_name)

    # 数据爬取全过程，输出excel表
    def complete_steps_of_get_product(self):
        flag = self.is_product_sale()
        if flag == False:
            print('该藏品寄售数量为0')
        else:
            # 第一步
            self.get_product_shardid()
            print(self.product_name, ':第1步完成')
            # 第二步
            self.get_product_price()
            print(self.product_name, ':第2步完成')
            # 第三步
            self.get_product_details()
            print(self.product_name, ':第3步完成')
            # 第四步
            self.get_product_sale_time()
            print(self.product_name, ':第4步完成')

    # get方法 获取self.product_list
    def get_self_product_list(self):
        return self.product_list


if __name__ == '__main__':
    # 计时：开始
    start = time.time()
    # 祈雨舞-157 Day1-44 不信谣-106 少女绿-71 少女蓝-86
    productSelenium = ProductSelenium(59)
    productSelenium.complete_steps_of_get_product()
    # 计时：结束
    end = time.time()
    print(end - start)
