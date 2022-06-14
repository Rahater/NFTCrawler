# 这里用来获取市场实时挂出信息
# saleType=0 数字藏品
# saleType=1 数字盲盒
# orderSort=asc 价格升序
# orderSort=desc 价格降序
import requests
import json

from bean.Store import Store

class MarketList():
    market_info_api = 'https://api.42verse.shop/api/front/sale/list?creatorId=&productId=&limit=20&orderSort=&page=1&saleType=0&lastId='

    def getBasicInfo(self, shardId, productId):
        if shardId is None:
            shardId = 1
        if len(productId) < 1:
            return None
        store_map = dict()
        for i in range(len(productId)):
            url = self.detail_info_api.format(shardId, productId[i])
            response = requests.get(url)
            # 获取请求状态码 200为正常
            if (response.status_code == 200):
                # 获取相应内容
                content = response.text
                # json转数组
                json_dict = json.loads(content)

                if (json_dict['code'] == 200):
                    json_list = json_dict['data']

                    # 打印所有结果
                    store = Store('','','','','','','')
                    store.storeId = json_list.get('productId')
                    store.publishPrice = json_list.get('price')
                    store.castQty = json_list.get('castQty')
                    store.activeCount = json_list.get('activeCount')
                    store.storeName = json_list.get('storeName')
                    if(json_list['creator'] is not None):
                        store.creatorName = json_list['creator'].get('creatorName')
                        store.creatorId = json_list['creator'].get('id')
                    store_map[store.storeId] = store
                else:
                    print("请求失败!")
            else:
                print("请求失败!")
        return store_map
