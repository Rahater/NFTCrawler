# 这里用来获取作者的数字藏品信息
# selectType=0 数字藏品
# selectType=1 数字盲盒
import json


from api.productShardDetail import ProductShardDetail
from crawler.PerfectRequest import PerfectRequest


class QueryCreatorInfoList():
    basic_info_api = 'https://api.42verse.shop/api/front/sale/queryCreatorInfoList?selectType={}'

    def getAllProductInfo(self, selectType):
        if selectType is not None:
            if selectType != 1 and selectType != 0:
                selectType = 0
        else:
            selectType = 0
        url = self.basic_info_api.format(selectType)
        response = PerfectRequest(url)
        store_map = dict()
        productId = []
        # 获取请求状态码 200为正常
        if (response.status_code == 200):
            # 获取相应内容
            content = response.text
            # json转数组
            json_dict = json.loads(content)

            if (json_dict['code'] == 200):
                json_list = json_dict['data']
                # 打印所有结果
                for i in range(len(json_list)):
                    product_list = json_list[i]['productList']
                    for j in range(len(product_list)):
                        productId.append(product_list[j]['productId'])

                productShardDetail = ProductShardDetail()
                store_map = productShardDetail.getBasicInfo(None,productId)
            else:
                print("请求失败!")
        else:
            print("请求失败!")

        return store_map

