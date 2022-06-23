import datetime

from flask import Flask, redirect, url_for, render_template

from flaskScheduler import Config
from table.tableProductBasic import *
from crawler.productBasicSelenium import *
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config.from_object(Config())
aps = APScheduler()
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@app.route('/')
@app.route('/index')
def index():
    # 查询数据库
    product_basic_list = query_product_basic(None)
    return render_template('index.html', product_basic_list=product_basic_list)


@app.route('/productBasic')
def product_basic_function():
    # 查询数据库
    product_basic_list = query_product_basic(None)
    return render_template('productBasic.html', product_basic_list=product_basic_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
