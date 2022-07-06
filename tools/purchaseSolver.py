import json
import subprocess
import time

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tools.slidingValidationSolver import perfect_driver_get

'''
 1. 打开cmd 打开指定端口、文件夹的独立浏览器
 示例：chrome.exe --remote-debugging-port=8100 --user-data-dir="C:\42verse\Chrome-data-42verse"
 2. 使用ctrl+R刷新页面1次，滑动页面即可生成cookie(暂时不考虑保存cookie以进行脚本访问)
 3. 用于访问页面
 https://www.42verse.shop/product/shared/136?productId=142&marketType=0
'''


class ProductSolver:
    def __init__(self, product_url):
        # 打开cmd执行命令
        # command = 'chrome.exe --remote-debugging-port=8100 --user-data-dir=\"C:\\42verse\\\Chrome-data-42verse\"'
        # subprocess.Popen(command)
        # 配置路径
        self.driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
        # 设置option 防识别自动化
        self.opt = webdriver.ChromeOptions()
        self.opt.add_experimental_option("debuggerAddress", "127.0.0.1:8100")
        # 版本更新 需采用Service模块
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=self.opt)
        # 指定藏品链接
        self.product_url = product_url

    def purchase_lowest_product(self):
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
        # 模拟浏览
        self.driver.get(self.product_url)
        try:
            try:
                element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class='button sale']"))
                )
            except:
                self.driver.quit()
            finally:
                draggier = self.driver.find_element(by=By.CSS_SELECTOR, value="[class='button sale']")
                action_chains = ActionChains(self.driver)
                action_chains.click(draggier).perform()
                action_chains.click(draggier).perform()
                try:
                    element1 = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class='icon nc-iconfont icon-slide-arrow']"))
                    )
                except:
                    self.driver.quit()
                finally:
                    draggier1 = self.driver.find_element(by=By.CSS_SELECTOR,
                                                         value="[class='icon nc-iconfont icon-slide-arrow']")
                action_chains.click_and_hold(draggier1).perform()
                action_chains.drag_and_drop_by_offset(draggier1, 1680, 0).perform()
                # self.driver.quit()
        except:
            print("Purchase Fail")
            self.driver.quit()

if __name__ == '__main__':
    productSolver = ProductSolver("https://www.42verse.shop/product/shared/2776?productId=47&marketType=0")
    productSolver.purchase_lowest_product()
