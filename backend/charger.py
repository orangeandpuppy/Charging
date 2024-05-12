from user import User
from config import config as cfg
from utils import check_ebike_id

class Charger(User):
    def __init__(self, id: str, password: str):
        # 电动车编号、学号、密码等个人信息
        super().__init__(id, password)
        self.__role = 'charger'
        self.__ebike_id = None

        # 维修记录
        self.__repair_id = list()

        # 失信情况
        self.__dishonesty_time = 0
        self.__block = True

    def add_electric_vehicle(self, ebike_id: str):
        if self.__ebike_id != None:
            raise Exception(f"充电桩{self.get_id()}已经绑定了电动车{self.__ebike_id}")
        if not check_ebike_id(ebike_id):
            raise Exception(f"电动车编号{ebike_id}不合法")
        self.__ebike_id = ebike_id
        self.__block = False