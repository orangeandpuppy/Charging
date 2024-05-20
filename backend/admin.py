from datetime import datetime, timedelta
from user import User
from config import config as cfg
from utils import check_ebike_id, check_charge_time, check_point_id, connect_db
from appointstate import AppointState
from charginghistory import ChargingHistory
from charger import Charger
from repaircontrol import RepairControl

class Admin:
    def __init__(self, admin_id: str, password: str,role:str='admin'):
        super().__init__(admin_id, password, role)
        if not self.is_in_db():
            raise Exception(f"管理员{self.get_id()}未注册")
        self.__role = 'admin'
        #自己的报修服务id
        self.__repair_id = self.get_id()
        # 充电桩预约状态
        self.__appoint_state = AppointState()
        # 充电历史
        self.__charging_history = ChargingHistory()
        #维修服务
        self.__repair_control = RepairControl()


        
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


    def lock_and_report_charger(self, point_id):
        """将指定充电桩锁定，报修并通知预约该充电桩的学生"""
        self._appoint_state.block_point(point_id)


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
        #在数据库中查询该学生id的密码
        password = self._find_charger_password(charger_id)
        charger=Charger(charger_id, password)
        #将对应充电桩预约状态修改为“正在履约”
        self.__appoint_state.appoint_start(point_id)
        #将对应学生预约状态修改为“正在履约”
        charger.keep_appoint()


    def change_charger_status_to_available(self, point_id: str):
        """
        将充电桩充电状态从“正在充电”修改为“空闲”，并加入该充电桩的充电历史
        :param
            point_id: 充电桩编号 [str]
        :return:
            无    
        """
        #在预约状态表中获取该充电桩的充电开始时间
        start_time = self._find_appoint_start(point_id)
        #将对应充电桩预约状态修改为“空闲”
        self.__appoint_state.appoint_finish(point_id)
        #将充电历史加入该充电桩的充电历史
        self.__charging_history.insert_charging_record(point_id, start_time, datetime.now())


    def mark_appointment_as_missed(self, point_id: str):
        """
        将充电桩充电状态从“已预约”修改为“空闲”，并将对应学生预约状态修改为“失约”；当失约次数达到三次时封锁该学生账号
        :param
            charger_id: 学生id [str]
        :return:
            无    
        """
        #查询正在使用该充电桩的学生id
        charger_id = self._find_appoint_charger(point_id)
        #在数据库中查询该学生id的密码
        password = self._find_charger_password(charger_id)
        #将对应充电桩预约状态修改为“空闲”
        self.__appoint_state.appoint_cancel(point_id)
        #将对应学生预约状态修改为“失约”
        charger = Charger(charger_id,password)
        charger.break_appoint()


    def unlock_student_account(self, charger_id : str):
        """
        解锁学生账号
        ：param
            charger_id: 学生id [str]
        ：return
            无
        """
        password=self._find_charger_password(charger_id)
        charger = Charger(charger_id,password)
        #解锁学生账号
        charger.unlock()
    

    def report_issue(self, issue_description: str):
        """
        充电桩/电动车报修
        :param
            issue_description: 报修描述 [str]
        :return:
            无    
        """
        id=self.get_id()
        self.__repair_control.report_issue(id,issue_description)


    def evaluate_repair_service(self,repair_id:int, comments: str):
        """报修服务评价"""
        self.__repair_control.request_evaluate(repair_id, comments)

    def register_new_account(self,user_id:str):
        # 注册审核新账户
        pass

    def get_own_repair_records(self):
        # 获取自己的维修记录
        return self.__repair_control.user_get_repair(self.get_id())

    def review_repair_personnel(self, engineer_id: str):
        # 审核维修人员ID

        pass

    def _find_appoint_charger(self, point_id: str):
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
            if (appoint[3] <= datetime.now() or appoint[4] >= datetime.now()-timedelta(hours=0.5)):
                return appoint[2]
        return None
    
    def _find_appoint_start(self, point_id: str):
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
            if not (appoint[3] >= datetime.now() or appoint[4] <= datetime.now()-timedelta(hours=0.5)):
                return appoint[3]
        return None    
    
    def _find_charger_password(self, charger_id: str):
        """
        查询学生密码
        :param
            charger_id: 学生id [str]
        :return
            学生密码 [str]
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT password FROM user WHERE id = %s", (charger_id,))
            password = cur.fetchone()
        return password