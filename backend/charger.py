import duckdb

from user import User
from config import config as cfg
from utils import check_ebike_id, check_charge_time, check_point_id
from appointstate import AppointState


class Charger(User):
    def __init__(self, id: str, password: str):
        # 电动车编号、学号、密码等个人信息
        super().__init__(id, password)
        self.__role = 'charger'
        self.__ebike_id = None
        self.__appoint_state = 0  # 0:未预约 1:已预约,未充电 2:已预约,正在履约

        # 维修记录
        self.__repair_id = list()

        # 失信情况
        self.__dishonesty_time = 0
        self.__block = True

        # 充电桩预约状态
        self.__appoint_state = AppointState()

    def add_electric_vehicle(self, ebike_id: str):
        """
        绑定电动车
        :param
            ebike_id:想要绑定上去的电动车编号
        :return: 无
        """
        if self.__ebike_id != None:
            raise Exception(f"充电桩{self.get_id()}已经绑定了电动车{self.__ebike_id}")
        if not check_ebike_id(ebike_id):
            raise Exception(f"电动车编号{ebike_id}不合法")
        self.__ebike_id = ebike_id
        self.__block = False

    def keep_appoint(self):
        """
        充电者开始履约
        :return: 无
        """
        if self.__appoint_state != 1:
            raise Exception(f"充电者{self.get_id()}未预约")
        with duckdb.connect(cfg['appint.db']) as conn:
            cur = conn.cursor()
            # 将预约信息表中已预约的状态改为正在履约
            # 1:已预约,未充电 -> 2:已预约,正在履约
            cur.execute(f'''UPDATE appoint
                            SET state = 2
                            WHERE charger_id = {self.get_id()} and state = 1;''')
        self.__appoint_state = 2

    def finish_appoint(self):
        """
        充电者结束履约
        :return: 无
        """
        if self.__appoint_state != 2:
            raise Exception(f"充电者{self.get_id()}未在履约中")
        with duckdb.connect(cfg['appint.db']) as conn:
            cur = conn.cursor()
            # 将预约信息表中正在履约的状态删除
            # 2:已预约,正在履约
            cur.execute(f'''DELETE FROM appoint
                            WHERE charger_id = {self.get_id()} and state = 2;''')
        self.__appoint_state = 0

    # 充电者失约
    def break_appoint(self):
        """
        充电者失约
        :return: 无
        """
        if self.__appoint_state != 1:
            raise Exception(f"充电者{self.get_id()}未预约")
        with duckdb.connect(cfg['appint.db']) as conn:
            cur = conn.cursor()
            # 将预约信息表中已预约的状态删除
            # 1:已预约,未充电
            cur.execute(f'''DELETE FROM appoint
                            WHERE charger_id = {self.get_id()} and state = 1;''')
        self.__appoint_state = 0
        self.report_dishonesty()

    def report_dishonesty(self):
        """
        管理员举报充电者失信
        :return: 无
        """
        if self.__block:
            raise Exception(f"充电者{self.get_id()}已被封禁")
        self.__dishonesty_time += 1
        if self.__dishonesty_time >= 3:
            self.__block = True

    # 预约指定充电桩某一时间段
    def appoint(self, charging_point_id: str, start_time: str, end_time: str):
        """
        预约指定充电桩某一时间段
        :param
            charging_point_id: 充电桩编号
            start_time: 开始时间
            end_time: 结束时间
        :return: 无
        """
        if self.__block:
            raise Exception(f"充电者{self.get_id()}已被封禁")
        if self.__appoint_state != 0:
            raise Exception(f"充电者{self.get_id()}已经预约了")
        if not check_charge_time(start_time, end_time):
            raise Exception("充电时间不合法")
        if not check_point_id(charging_point_id):
            raise Exception(f"充电桩编号{charging_point_id}不合法")
        if self.__appoint_state.get_appoint_state(charging_point_id) != 0:
            raise Exception(f"充电桩{charging_point_id}已经被预约")
        with duckdb.connect(cfg['appint.db']) as conn:
            cur = conn.cursor()
            # 插入预约信息表
            cur.execute(f'''INSERT INTO appoint
                            VALUES ({charging_point_id}, {self.get_id()}, {start_time}, {end_time}, 1);''')
        self.__appoint_state = 1