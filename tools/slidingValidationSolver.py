import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

'''
    介绍
        解决阿里人机检测库的滑动验证模块
'''


def perfect_driver_get(driver, product_url):
    # 模拟浏览
    driver.get(product_url)
    # 识别滑块验证页面
    try:
        element = driver.find_element_by_id('PC')
    except NoSuchElementException as e:
        # 发生了NoSuchElementException异常，说明页面中未找到该元素，表示一切正常，无需异常处理
        pass
    else:
        handle = driver.current_window_handle
        js_new_window = 'window.open("{product_url}")'.format(product_url=product_url)
        # 执行js
        driver.execute_script(js_new_window)
        # 没有发生异常，在页面中找到了该元素
        # 刷新当前页面
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("r").key_up(Keys.CONTROL).perform()
        handles = driver.window_handles
        driver.close()
        for new_handle in handles:
            # 筛选新打开的窗口B
            if new_handle != handle:
                # 切换到新打开的窗口B
                driver.switch_to.window(new_handle)
        # 滑动滑块
        # 找到滑块初始位置
        time.sleep(3)
        draggier = driver.find_element_by_id('nc_1_n1z')
        action_chains = ActionChains(driver)
        action_chains.click_and_hold(draggier).perform()
        action_chains.drag_and_drop_by_offset(draggier, 258, 0).perform()
        perfect_driver_get(driver, product_url)
