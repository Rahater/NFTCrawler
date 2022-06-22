import pymysql


def createDBAndTable(user='root', passwd='123456'):
    # 建库和建表
    con = pymysql.connect(host='127.0.0.1', port=3306, user=user, passwd=passwd, charset='utf8')
    cur = con.cursor()
    # 开始建库,库名:42verse
    cur.execute("create database 42verse character set utf8;")
    # 使用42verse
    cur.execute("use 42verse;")
    # 创建平台所有藏品的基础信息表product_basic(id, creatorId, creatorName, ProductId, ProductName)
    cur.execute(
        "CREATE TABLE product_basic (id INT AUTO_INCREMENT PRIMARY KEY,"
        " creatorId VARCHAR(255),creatorName VARCHAR(255),ProductId VARCHAR(255),ProductName VARCHAR(255))")
    # 创建平台所有藏品的当日前20个寄售藏品的详情表today_product_detail (id, productId, shardId, salePrice, updateTime,buyPrice,
    # fluctuate, ownerNickName, fromUserName, transferTime, transferCount, activeCount, castQty)
    cur.execute(
        "CREATE TABLE today_product_detail (id INT AUTO_INCREMENT PRIMARY KEY, productId VARCHAR(255), shardId VARCHAR(255)"
        ", salePrice VARCHAR(255), buyPrice VARCHAR(255), ownerNickName VARCHAR(255), fromUserName VARCHAR(255)"
        ", transferTime VARCHAR(255), updateTime VARCHAR(255), transferCount VARCHAR(255)"
        ", castQty VARCHAR(255),chainAccountAddress VARCHAR(255))")


def query_basic(product_id):
    # 建立连接，用户root 密码root dbname：nft
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', db='nft')
    # 获取游标
    cur = db.cursor()
    try:
        # sql查询语句 表名product_basic
        if product_id is None:
            sql = "select * from product_basic"
            cur.execute(sql)  # 执行sql语句
        else:
            sql = "select * from product_basic where productId in (%s)"
            cur.execute(sql, product_id)  # 执行sql语句
        desc = cur.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
        data_dict = [dict(zip([col[0] for col in desc], row)) for row in cur.fetchall()]  # 列表表达式把数据组装起来
        return data_dict
    except Exception as e:
        print('函数【query_basic】sql执行异常：%s' % e)
    finally:
        # 关闭游标
        cur.close()
        # 关闭连接
        db.close()


def query_detail(product_id, shard_id):
    # 建立连接，用户root 密码root dbname：nft
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', db='nft')
    # 获取游标
    cur = db.cursor()
    try:
        # sql查询语句 表名product_basic
        if product_id is None:
            sql = "select * from product_detail"
            cur.execute(sql)  # 执行sql语句
        elif product_id is not None and shard_id is not None:
            sql = "select * from product_detail where productId = %(productId)s and shardId = %(shardId)s"
            values = {"productId": product_id, "shardId": shard_id}
            cur.execute(sql, values)
        elif product_id is not None and shard_id is None:
            sql = "select * from product_basic where productId in (%s)"
            cur.execute(sql, product_id)  # 执行sql语句

        desc = cur.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
        data_dict = [dict(zip([col[0] for col in desc], row)) for row in cur.fetchall()]  # 列表表达式把数据组装起来
        return data_dict
    except Exception as e:
        print('函数【query_basic】sql执行异常：%s' % e)
    finally:
        # 关闭游标
        cur.close()
        # 关闭连接
        db.close()


def insert_basic(values):
    # 可以批量插入，传包含字典的list即可
    # 插入操作
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', db='nft')
    cur = db.cursor()

    # 获取列名
    cols = ", ".join('`{}`'.format(k) for k in values[0].keys())
    # 将列名格式化成sql语句
    val_cols = ', '.join('%({})s'.format(k) for k in values[0].keys())
    # 组装sql
    sql = "insert into product_basic(%s) values(%s)"
    res_sql = sql % (cols, val_cols)
    try:
        # 执行sql语句
        cur.executemany(res_sql, values)  # 将字典列表传入
        # 提交到数据库执行
        db.commit()
        print('开始数据库插入操作')
    except Exception as e:
        print('函数【insert_basic】sql执行异常：%s' % e)
        # 如果发生错误则回滚
        db.rollback()
        print('数据库插入操作错误回滚')
    finally:
        # 关闭游标
        cur.close()
        # 关闭数据库连接
        db.close()


def insert_deatil(values):
    # 可以批量插入，传包含字典的list即可
    # 插入操作
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', db='nft')
    cur = db.cursor()

    # 获取列名
    cols = ", ".join('`{}`'.format(k) for k in values[0].keys())
    # 将列名格式化成sql语句
    val_cols = ', '.join('%({})s'.format(k) for k in values[0].keys())
    # 组装sql
    sql = "insert into product_detail(%s) values(%s)"
    res_sql = sql % (cols, val_cols)
    try:
        # 执行sql语句
        cur.executemany(res_sql, values)  # 将字典列表传入
        # 提交到数据库执行
        db.commit()
        print('开始数据库插入操作')
    except Exception as e:
        print('函数【insert_detail】sql执行异常：%s' % e)
        # 如果发生错误则回滚
        db.rollback()
        print('数据库插入操作错误回滚')
    finally:
        # 关闭游标
        cur.close()
        # 关闭数据库连接
        db.close()


def update_basic(values):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', db='nft')
    cur = db.cursor()
    # 获取列名
    cols = ", ".join('{} = %({})s'.format(k, k) for k in values[0].keys())
    # 将列名格式化成sql语句
    val_cols = 'productId = %(productId)s'
    # 组装sql
    sql = "update product_basic set (%s) where (%s)"
    res_sql = sql % (cols, val_cols)

    try:
        # 执行sql语句
        cur.executemany(res_sql, values)  # 将字典列表传入
        # 提交到数据库执行
        db.commit()
        print('开始数据库更新操作')
    except Exception as e:
        print('函数【update_basic】sql执行异常：%s' % e)
        # 如果发生错误则回滚
        db.rollback()
        print('数据库更新操作错误回滚')
    finally:
        # 关闭游标
        cur.close()
        # 关闭数据库连接
        db.close()


def update_detail(values):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', db='nft')
    cur = db.cursor()
    # 获取列名
    cols = ", ".join('{} = %({})s'.format(k, k) for k in values[0].keys())
    # 将列名格式化成sql语句
    val_cols = 'productId = %(productId)s and shardId = %(shardId)s'
    # 组装sql
    sql = "update product_detail set (%s) where (%s)"
    res_sql = sql % (cols, val_cols)

    try:
        # 执行sql语句
        cur.executemany(res_sql, values)  # 将字典列表传入
        # 提交到数据库执行
        db.commit()
        print('开始数据库更新操作')
    except Exception as e:
        print('函数【update_detail】sql执行异常：%s' % e)
        # 如果发生错误则回滚
        db.rollback()
        print('数据库更新操作错误回滚')
    finally:
        # 关闭游标
        cur.close()
        # 关闭数据库连接
        db.close()


def delete_basic(productId):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', db='nft')
    cur = db.cursor()

    sql_delete = "delete from product_basic where productId = '%s'"
    try:
        cur.execute(sql_delete % productId)  # 像sql语句传递参数
        # 提交
        db.commit()
        print('开始数据库删除操作')
    except Exception as e:
        print('函数【delete_basic】sql执行异常：%s' % e)
        # 如果发生错误则回滚
        db.rollback()
        print('数据库删除操作错误回滚')
    finally:
        # 关闭游标
        cur.close()
        # 关闭数据库连接
        db.close()


def delete_detail(productId, shardId):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', db='nft')
    cur = db.cursor()

    sql_delete = "delete from product_detail where productId = '%s'"

    try:
        if shardId is not None:
            sql_delete = sql_delete + " and shardId = '%s'" % (productId, shardId)
            cur.execute(sql_delete)  # 向sql语句传递参数
        else:
            cur.execute(sql_delete % productId)  # 向sql语句传递参数
        # 提交
        db.commit()
        print('开始数据库删除操作')
    except Exception as e:
        print('函数【delete_basic】sql执行异常：%s' % e)
        # 如果发生错误则回滚
        db.rollback()
        print('数据库删除操作错误回滚')
    finally:
        # 关闭游标
        cur.close()
        # 关闭数据库连接
        db.close()


if __name__ == '__main__':
    createDBAndTable()
