import allProduct

import productSelenium


class AllProductSelenium:
    def __init__(self):
        self.id_list = []
        self.product_list = []

    # 全平台数据获取
    def get_list_of_product(self):
        all_product = allProduct.AllProduct()
        all_product.get_all_product_id_and_name()
        id_name_list = all_product.get_product_list()
        for product in id_name_list:
            if id_name_list.index(product)+1 > 6:
                id = int(product['productId'])
                product_selenium = productSelenium.ProductSelenium(id)
                product_selenium.complete_steps_of_get_product()
                print(product_selenium.product_name, "：爬取结束")


if __name__ == '__main__':
    all_product_selenium = AllProductSelenium()
    all_product_selenium.get_list_of_product()
