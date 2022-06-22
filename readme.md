## 开发文档
### 需求
1. 获取所有藏品的name和id并一一对应显示到前端
2. 获取所有藏品的每日价格图（20个）并展示到前端


4. 代理更换
5. https://api.42verse.shop/api/front/sale/list 获取指定时间内交易的藏品数据
6. 按照一定的策略修改显示的数据样式，比如持有者最多的人，最近交易时间，割肉的人（负波动全标出来），山顶买入的人（购入价格最高）
7. 增加获取藏品数量的可扩展性，获取所有藏品的数据
### API
1. https://api.42verse.shop/api/front/sale/queryCreatorInfoList?selectType=0 获取所有藏品id name  

### Web页面需求
1. 单个藏品寄售趋势图
2. 所有藏品最低价对比图
3. 单个藏品寄售信息详情
### 更新日志
1. 为第三步生成的excel表格添加序号
2. 三步生成的文件添加product_name(需保证每次执行三步)
3. 修复漏洞：藏品数量少于20个的情况
4. 添加第四步：寄售藏品的寄售时间
5. 删去前两步的保存文件步骤；重构代码以减少内存使用量
### 技术难点解决方案：
1. 固定时间间隔爬取全平台数据用于更新数据库  
解决方案：项目设置在深夜首次上线，迅速爬取全平台数据存入数据库，并记录当前时刻后所有的最新上架数据直至平台数据爬取结束后更新数据库，持续获取最新上架数据用于更新数据库，可以有效避免数据不一致情况，更有可行性；
2. 选择先做单一藏品数据爬取的原因  
全平台的数据都是由单一藏品组成而成的，先做一个便能推广到所有藏品；  
3. 第四步不选择边爬取边匹配数据更新寄售时间而选择合并所有数据然后进行排序再采用双指针方法进行一一匹配的原因  
基于时间复杂度，选择消耗时间更短的情况；
4. 采用固定缓存文件的方式在一定时间内延缓滑动验证模块出现
5. 破解阿里人机检测库的滑动验证模块
解决教程示例：https://blog.csdn.net/sayyy/article/details/99649372
务必手动打开重定向、指定已存在的浏览器
6. 解决藏品寄售但数量为0的情况
在进行第一步的时候进行数量判断再确定是否进行后续数据爬取阶段
### 备注
* 表格属性：序号 藏品名称 藏品编号 寄售价格 购入价格 波动 持有者昵称 卖家昵称 交易时间 转手次数 流通量 发行量寄售时间
### Tips
1. 浏览器重定向路径：chrome://settings/content/popups
2. 隧道代理：阿布云，迅代理，蚂蚁，微秒云