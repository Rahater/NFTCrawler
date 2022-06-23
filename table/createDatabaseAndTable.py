import pymysql


# 创建数据库
def create_database(user='root', passwd='123456'):
    # 建库和建表
    con = pymysql.connect(host='127.0.0.1', port=3306, user=user, passwd=passwd, charset='utf8')
    cur = con.cursor()
    # 开始建库,库名:42verse
    cur.execute("create database 42verse character set utf8;")
    # 关闭游标
    cur.close()
    # 关闭连接
    con.close()


# 创建表 product_basic
def create_table_product_basic():
    # 建立连接，用户root 密码123456 dbname：42verse
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='42verse')
    # 获取游标
    cur = db.cursor()
    # 创建平台所有藏品的基础信息表product_basic(id, creatorId, creatorName, ProductId, ProductName)
    cur.execute(
        "CREATE TABLE product_basic (id INT AUTO_INCREMENT PRIMARY KEY,"
        " creatorId VARCHAR(255),creatorName VARCHAR(255),productId VARCHAR(255) UNIQUE ,productName VARCHAR(255))")
    # 关闭游标
    cur.close()
    # 关闭连接
    db.close()


# 创建表 product_basic
def create_table_today_product_detail():
    # 建立连接，用户root 密码123456 dbname：42verse
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='42verse')
    # 获取游标
    cur = db.cursor()
    # 创建平台所有藏品的当日前20个寄售藏品的详情表today_product_detail (id, productId,productName, shardId,buyPrice,
    # salePrice,transferTime, updateTime,fluctuate,transferCount, ownerNickName, fromUserName, activeCount, castQty)
    cur.execute(
        "CREATE TABLE today_product_detail ("
        "id INT AUTO_INCREMENT PRIMARY KEY, productId VARCHAR(255), productName VARCHAR(255)"
        ",shardId VARCHAR(255),  buyPrice VARCHAR(255),salePrice VARCHAR(255)"
        ",transferTime VARCHAR(255),updateTime VARCHAR(255), fluctuate VARCHAR(255), transferCount VARCHAR(255)"
        ",ownerNickName VARCHAR(255),fromUserName VARCHAR(255) "
        ", activeCount VARCHAR(255),castQty VARCHAR(255))")
    # 关闭游标
    cur.close()
    # 关闭连接
    db.close()


# 删除表 product_basic
def delete_table_product_basic():
    # 建立连接，用户root 密码123456 dbname：42verse
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='42verse')
    # 获取游标
    cur = db.cursor()
    cur.execute("drop table if exists product_basic")
    # 关闭游标
    cur.close()
    # 关闭连接
    db.close()


# 删除表 product_basic
def delete_table_today_product_detail():
    # 建立连接，用户root 密码123456 dbname：42verse
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='42verse')
    # 获取游标
    cur = db.cursor()
    cur.execute("drop table if exists today_product_detail")
    # 关闭游标
    cur.close()
    # 关闭连接
    db.close()
