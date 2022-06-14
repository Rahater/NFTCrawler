# 这里用来获取作品详细信息

# shardId=9309 作品编号
# productId=51 藏品编号
# activeCount = 3078 流通量
# castQty = 10000 发行量/总量
import requests
import json

from bean.Store import Store


class ProductShardDetail():
    detail_info_api = 'https://api.42verse.shop/api/front/product/shard/detail?shardId={}&productId={}'

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
