from crawler.productBasicSelenium import AllProduct


class Config(object):
    JOBS = [
        {
            'id': 'job-1',
            'func': 'flaskScheduler:product_basic_scheduler',
            'trigger': 'interval',
            'seconds': 1
        }
    ]
    SCHEDULER_API_ENABLED = True


# 定时任务 product_basic
def product_basic_scheduler():
    # 执行爬虫
    # AllProduct().get_all_product_basic()
    print('123')