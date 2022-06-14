class Store():

    #允许绑定的对象
    __slots__ = ('__storeName', '__storeId','__creatorId','__creatorName','__activeCount','__castQty','__publishPrice')

    #构造函数
    def __init__(self, storeName, storeId,creatorId,creatorName,activeCount,castQty,publishPrice):
        '''用双下划线开头的变量，表示私有变量，外部程序不可直接访问'''
        self.__storeName = storeName
        self.__storeId = storeId
        self.__creatorId = creatorId
        self.__creatorName = creatorName
        self.__activeCount = activeCount
        self.__castQty = castQty
        self.__publishPrice = publishPrice

    #getter
    @property
    def storeName(self):
        return self.__storeName

    #settter
    @storeName.setter
    def storeName(self, storeName):
        self.__storeName = storeName

    #getter
    @property
    def storeId(self):
        return self.__storeId

    @storeId.setter
    def storeId(self, storeId):
        self.__storeId = storeId

    #getter
    @property
    def creatorId(self):
        return self.__creatorId

    @creatorId.setter
    def creatorId(self, creatorId):
        self.__creatorId = creatorId

    #getter
    @property
    def creatorName(self):
        return self.__creatorName

    @creatorName.setter
    def creatorName(self, creatorName):
        self.__creatorName= creatorName

    #getter
    @property
    def activeCount(self):
        return self.__activeCount

    @activeCount.setter
    def activeCount(self, activeCount):
        self.__activeCount = activeCount

    #getter
    @property
    def castQty(self):
        return self.__castQty

    @castQty.setter
    def castQty(self, castQty):
        self.__castQty = castQty

    #getter
    @property
    def publishPrice(self):
        return self.__publishPrice

    @publishPrice.setter
    def publishPrice(self, publishPrice):
        self.__publishPrice = publishPrice

    #相当于java的toString方法
    def __str__(self):
        return "藏品id：%s 藏品名称：%s 作者id：%s 作者名称：%s 发行量：%s 发行价：%s 流通量：%s" % (self.__storeId, self.__storeName,self.__creatorId,self.__creatorName,self.__castQty,self.__publishPrice,self.__activeCount)

    # 相当于java的toString方法
    def __repr__(self):
        return "藏品id：%s 藏品名称：%s 作者id：%s 作者名称：%s 发行量：%s 发行价：%s 流通量：%s" % (self.__storeId, self.__storeName,self.__creatorId,self.__creatorName,self.__castQty,self.__publishPrice,self.__activeCount)

    #相当于java的equals方法
    def __eq__(self, other):
        if self.__storeId == other.storeId:
            return True
        else:
            return False
