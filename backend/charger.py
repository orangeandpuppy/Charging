from datetime import datetime, timedelta
from user import User
from config import config as cfg
from utils import check_ebike_id, check_charge_time, check_point_id, connect_db
from appointstate import AppointState


class Charger(User):
    def __init__(self, id: str, password: str):
        # 电动车编号、学号、密码等个人信息
        super().__init__(id, password)
        # 使用充电服务前必须注册,init则代表登陆
        if not self.is_in_db():
            raise Exception(f"充电者{self.get_id()}未注册")
        # 如果charger中没有charger_id为id的记录，则插入一条记录，表示给该用户充电者的身份
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM charger WHERE charger_id = %s", (self.get_id(),))
            res = cur.fetchone()
            if not res:
                cur.execute("INSERT INTO charger VALUES (%s, %s, %s, %s, %s)", (self.get_id(), "0", 0, 0, True))
                con.commit()

        self.__role = 'charger'
        self.__ebike_id = "0"
        self.__state = 0  # 0:未预约 1:已预约,未充电 2:已预约,正在履约

        # 维修记录
        self.__repair_id = list()

        # 失信情况
        self.__dishonesty_time = 0
        self.__block = True

        # 充电桩预约状态
        self.__appoint_state = AppointState()

        # 从数据库中读取该用户已有的信息
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT ebike_id, state, dishonesty_time, block FROM charger WHERE charger_id = %s", (self.get_id(),))
            res = cur.fetchone()
            if res:
                self.__ebike_id, self.__state, self.__dishonesty_time, self.__block = res

    def add_electric_vehicle(self, ebike_id: str):
        """
        绑定电动车
        :param
            ebike_id:想要绑定上去的电动车编号 [str]
        :return: 无
        """
        if self.__ebike_id != "0":
            raise Exception(f"充电桩{self.get_id()}已经绑定了电动车{self.__ebike_id}")
        if not check_ebike_id(ebike_id):
            raise Exception(f"电动车编号{ebike_id}不合法")

        # 检查电动车是否已经被绑定
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM ebike WHERE ebike_id = %s", (ebike_id,))
            res = cur.fetchone()
        if res:
            raise Exception(f"电动车{ebike_id}已经被绑定到其他充电者账户上")

        # 更新数据库
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("UPDATE charger SET ebike_id = %s, block = %s WHERE charger_id = %s", (ebike_id, False, self.get_id()))
            cur.execute("INSERT INTO ebike VALUES (%s, %s)", (ebike_id, self.get_id()))
            con.commit()
        self.__ebike_id = ebike_id
        self.__block = False

    def keep_appoint(self):
        """
        充电者开始履约
        :return: 无
        """
        if self.__state != 1:
            raise Exception(f"充电者{self.get_id()}未预约")
        with connect_db() as con:
            cur = con.cursor()
            # 将charger中已预约的状态修改为正在履约
            # 1:已预约,未充电
            cur.execute("UPDATE charger SET state = 2 WHERE charger_id = %s", (self.get_id(),))
            con.commit()
        self.__state = 2

    def finish_appoint(self):
        """
        充电者结束履约
        :return: 无
        """
        if self.__state != 2:
            raise Exception(f"充电者{self.get_id()}未在履约中")
        with connect_db() as con:
            cur = con.cursor()
            # 将charger中正在履约的状态修改为未预约
            # 2:已预约,正在履约
            cur.execute("UPDATE charger SET state = 0 WHERE charger_id = %s", (self.get_id(),))
            con.commit()
        self.__state = 0

    # 充电者失约
    def break_appoint(self):
        """
        充电者失约
        :return: 无
        """
        if self.__state != 1:
            raise Exception(f"充电者{self.get_id()}未预约")
        with connect_db() as con:
            cur = con.cursor()
            # 将charger中已预约的状态修改为未预约
            # 1:已预约,未充电
            cur.execute("UPDATE charger SET state = 0 WHERE charger_id = %s", (self.get_id(),))
            con.commit()
        self.__state = 0
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
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("UPDATE charger SET dishonesty_time = %s, block = %s WHERE charger_id = %s", (self.__dishonesty_time, self.__block, self.get_id()))
            con.commit()

    def appoint(self, point_id: str, start_time: datetime, end_time: datetime):
        """
        预约指定充电桩某一时间段
        :param
            point_id: 充电桩编号 [str]
            start_time: 开始时间 [datatime]
            end_time: 结束时间 [datatime]
        :return: 无
        """
        # 处理不合法情况
        if self.__block:
            raise Exception(f"充电者{self.get_id()}已被封禁")
        if self.__state != 0:
            raise Exception(f"充电者{self.get_id()}已经预约了")
        if not check_charge_time(start_time, end_time):
            raise Exception("充电时间不合法")
        if not check_point_id(point_id):
            raise Exception(f"充电桩编号{point_id}不合法")
        if self.__appoint_state.get_point_appoint_state(point_id, start_time, end_time) != 0:
            raise Exception(f"充电桩{point_id}已经被预约")

        # 开始预约
        self.__appoint_state.handle_appoint(point_id, self.get_id(), start_time, end_time)

        # 更新用户数据库
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("UPDATE charger SET state = 1 WHERE charger_id = %s", (self.get_id(),))
            con.commit()
        self.__state = 1

    def get_point_appoint_state(self, point_id: str, start_time: datetime, end_time: datetime):
        """
        查询指定充电桩从start_time到end_time的预约状态
        :param
            point_id: 充电桩编号 [str]
            start_time: 开始时间 [datatime]
            end_time: 结束时间 [datatime]
        :return:
            预约状态 [int]
        """
        return self.__appoint_state.get_point_appoint_state(point_id, start_time, end_time)

    def get_charging_history(self):
        """
        查询自己已经完成的充电历史
        :return:
            充电历史 [tuple((point_id, charger_id, start_time, end_time),(),...)]
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM charging WHERE charger_id = %s", (self.get_id(),))
            res = cur.fetchall()
        return res