from datetime import datetime, timedelta
from user import User
from config import config as cfg
from utils import check_ebike_id, check_charge_time, check_point_id, connect_db
from appointstate import AppointState
from charginghistory import ChargingHistory
from charger import Charger

class Admin:
    def __init__(self, admin_id: str, password: str, role: str = 'admin'):
        super().__init__(admin_id, password, role)
        if not self.is_in_db():
            raise Exception(f"管理员{self.get_id()}未注册")
        self.__role = 'admin'
        #自己的报修服务id
        self.__repair_id = list()
        # 充电桩预约状态
        self.__appoint_state = AppointState()
        # 充电历史
        self.__charging_history = ChargingHistory()


        
    def query_charging_history_by_charger(self, point_id):
        """
        查询指定充电桩的充电历史
        :param
            point_id: 充电桩编号 [str]
        :return:
            充电历史记录[tuple((point_id, charger_id, start_time, end_time),(),...)]
        """
        return self.__charging_history.get_charging_history_by_charger(point_id)
    
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

    def lock_and_report_charger(self, charger_id):
        """将指定充电桩锁定，报修并通知预约该充电桩的学生"""
        pass

    def change_charger_status_to_charging(self, point_id):
        """
        将充电桩充电状态从“已预约”修改为“正在履约”，并将对应学生预约状态修改为“正在履约
        :param
            point_id: 充电桩编号 [str]
        :return:
            无    
        ”"""
        #查询正在使用该充电桩的学生id
        charger_id = self._find_appoint_charger(point_id)
        #将对应充电桩预约状态修改为“正在履约”
        self.__appoint_state.appoint_start(point_id)
        #将对应学生预约状态修改为“正在履约”
        with connect_db() as con:
            cur = con.cursor()
            # 将charger中已预约的状态修改为正在履约
            # 1:已预约,未充电
            cur.execute("UPDATE charger SET state = 2 WHERE charger_id = %s", (charger_id))
            con.commit()


    def change_charger_status_to_available(self, point_id):
        """
        将充电桩充电状态从“正在充电”修改为“空闲”，并加入该充电桩的充电历史
        :param
            point_id: 充电桩编号 [str]
        :return:
            无    
        """
        #在预约状态表中获取该充电桩的充电开始时间
        start_time = self._find_appoint_start(point_id, datetime.now(), datetime.now() + timedelta(hours=0.5))
        #将对应充电桩预约状态修改为“空闲”
        self.__appoint_state.appoint_finish(point_id)
        #将充电历史加入该充电桩的充电历史
        self.__charging_history.insert_charging_record(point_id, start_time, datetime.now())


    def mark_appointment_as_missed(self, point_id):
        """
        将充电桩充电状态从“已预约”修改为“空闲”，并将对应学生预约状态修改为“失约”；当失约次数达到三次时封锁该学生账号
        :param
            charger_id: 学生id [str]
        :return:
            无    
        """
        #查询正在使用该充电桩的学生id
        charger_id = self._find_appoint_charger(point_id)
        #将对应充电桩预约状态修改为“空闲”
        self.__appoint_state.appoint_cancel(point_id)
        #将对应学生预约状态修改为“失约”
        charger = Charger(charger_id)
        charger.break_appoint()


    def unlock_student_account(self, charger_id):
        """
        解锁学生账号
        ：param
            charger_id: 学生id [str]
        ：return
            无
        """
        charger = Charger(charger_id)
        #解锁学生账号
        charger._block=True
        #将学生失信次数清零
        charger.__dishonesty_time=0
        #更新数据库
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("UPDATE charger SET  dishonesty_time = %s, block = %s WHERE charger_id = %s", (charger_id))
            con.commit()


    def report_issue(self, repair_id, issue_description):
        """
        充电桩/电动车报修
        :param
            repair_id: 充电桩/电动车id [str]
            issue_description: 报修描述 [str]
        :return:
            无    
        """


    def evaluate_repair_service(self, repair_id, rating, comments):
        """报修服务评价"""

    def register_new_account(self):
        # 注册审核新账户
        pass

    def get_own_repair_records(self):
        # 获取自己的维修记录
        pass

    def review_repair_personnel(self, personnel_id):
        # 审核维修人员ID
        pass

    def _find_appoint_charger(self, point_id: str, start_time: datetime, end_time: datetime):
        """
        查询该充电桩指定时间的预约学生
        :param
            point_id: 充电桩编号 [str]
        ：return
            预约学生id [str]
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM appoint WHERE point_id = %s", (point_id,))
            data = cur.fetchall()            
        for appoint in data:
            if not (appoint[3] >= end_time or appoint[4] <= start_time):
                return appoint[2]
        return None
    
    def _find_appoint_start(self, point_id: str, start_time: datetime, end_time: datetime):
        """
        查询该充电桩的预约开始时间
        :param
            point_id: 充电桩编号 [str]
        :return
            预约开始时间 [datetime]
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM appoint WHERE point_id = %s", (point_id,))
            data = cur.fetchall()            
        for appoint in data:
            if not (appoint[3] >= end_time or appoint[4] <= start_time):
                return appoint[3]
        return None    