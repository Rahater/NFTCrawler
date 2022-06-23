import pymysql
from table.createDatabaseAndTable import *


# 查询 product_basic
def query_product_basic(product_id):
    # 建立连接，用户root 密码123456 dbname：42verse
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='42verse')
    # 获取游标
    cur = db.cursor()
    try:
        # sql查询语句 表名product_basic
        if product_id is None:
            sql = "select * from product_basic"
            cur.execute(sql)  # 执行sql语句
        else:
            sql = "select * from product_basic where productId = %s"
            cur.execute(sql, product_id)  # 执行sql语句
        desc = cur.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
        # 列表表达式把数据组装起来
        product_basic_list = [dict(zip([col[0] for col in desc], row)) for row in cur.fetchall()]
        return product_basic_list
    except Exception as e:
        print('函数query_product_basic sql执行异常：%s' % e)
    finally:
        # 关闭游标
        cur.close()
        # 关闭连接
        db.close()


# 插入 product_basic
def insert_product_basic(values):
    # 批量插入，传包含字典的list即可
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='42verse')
    cur = db.cursor()
    # 获取列名
    cols = ", ".join('`{}`'.format(k) for k in values[0].keys())
    # 将列名格式化成sql语句
    val_cols = ', '.join('%({})s'.format(k) for k in values[0].keys())
    # 组装sql
    sql = "insert ignore into product_basic(%s) values(%s)"
    res_sql = sql % (cols, val_cols)
    try:
        # 执行sql语句
        cur.executemany(res_sql, values)  # 将字典列表传入
        # 提交到数据库执行
        db.commit()
    except Exception as e:
        print('函数insert_product_basic sql执行异常：%s' % e)
        # 如果发生错误则回滚
        db.rollback()
        print('数据库插入操作错误回滚')
    finally:
        # 关闭游标
        cur.close()
        # 关闭数据库连接
        db.close()


# 删除 product_basic
def delete_product_basic(productId):
    # 建立连接，用户root 密码123456 dbname：42verse
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='42verse')
    cur = db.cursor()
    sql_delete = "delete from product_basic where productId = '%s'"
    try:
        cur.execute(sql_delete % productId)  # 向sql语句传递参数
        # 提交
        db.commit()
    except Exception as e:
        print('函数delete_product_basic sql执行异常：%s' % e)
        # 如果发生错误则回滚
        db.rollback()
        print('数据库删除操作错误回滚')
    finally:
        # 关闭游标
        cur.close()
        # 关闭数据库连接
        db.close()


if __name__ == '__main__':
    # delete_table_product_basic()
    # delete_table_today_product_detail()
    # create_table_product_basic()
    # create_table_today_product_detail()
    query_product_basic(product_id=None)
    # insert_product_basic([{'creatorId': '3', 'creatorName': '2', 'ProductId': '2', 'ProductName': '1'}])
    # query_product_basic(product_id=None)
