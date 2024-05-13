"""
预约状态类
用于处理预约状态信息，包括充电桩预约状态(未预约，已预约，正在履约)，充电桩预约时间，充电桩预约用户信息
对外提供预约状态查询、预约状态修改、预约状态删除等接口
"""
from utils import connect_db
from datetime import datetime, timedelta
from config import config as cfg


class AppointState:
    def get_point_appoint_state(self, point_id: str, start_time: datetime, end_time: datetime):
        """
        获取充电桩从start_time到end_time内的预约状态
        :param
            point_id: 充电桩编号[str] (eg F/R-01)
            start_time: 预约开始时间[datetime]
            end_time: 预约结束时间[datetime]
        :return:
            充电桩当前预约状态[int] (0-未预约，1-已预约，未充电, 2-已预约，正在履约)
        """
        if (end_time - start_time).days > 2:
            raise ValueError("预约时间不能超过2天")
        if start_time > end_time:
            return 0
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM appoint WHERE point_id = %s", (point_id,))
            data = cur.fetchall()
        current_appoint = self.__find_appoint(data, start_time, end_time)
        if current_appoint:
            return current_appoint[-1]
        else:
            return 0

    def get_station_appoint_state(self, station_id: str, start_time: datetime, end_time: datetime):
        """
        获取指定充电站从start_time到end_time内的预约状态
        :param
            station_id: 充电站编号[str] (eg F)
            start_time: 预约开始时间[datetime]
            end_time: 预约结束时间[datetime]
        :return:
            充电站内所有充电桩当前预约状态[dict(str:int)] (0-未预约，1-已预约，未充电, 2-已预约，正在履约)
            如果开始时间大于结束时间，返回空字典
        """
        point_state = dict()
        if (end_time - start_time).days > 2:
            raise ValueError("预约时间不能超过2天")
        if start_time > end_time:
            return point_state
        for color in cfg['supported_charging_point_color']:
            for id in range(1, cfg['charging_station_point_num'][station_id] + 1):
                point_id = station_id + '/' + color + '-' + str(id).zfill(2)
                with connect_db() as con:
                    cur = con.cursor()
                    cur.execute("SELECT * FROM appoint WHERE point_id = %s", (point_id,))
                    data = cur.fetchall()
                current_appoint = self.__find_appoint(data, start_time, end_time)
                if current_appoint:
                    point_state[point_id] = current_appoint[-1]
                else:
                    point_state[point_id] = 0
        return point_state

    def get_station_current_appoint_state(self, station_id: str):
        """
        获取指定充电站当前预约状态,此处空闲定义为至少可以预约后面半个小时
        :param
            station_id: 充电站编号[str] (eg F)
        :return:
            充电站内所有充电桩当前预约状态[dict(str:int)] (0-未预约，1-已预约，未充电, 2-已预约，正在履约)
        """
        now = datetime.now()
        point_state = self.get_point_appoint_state(station_id, now, now + timedelta(hours=0.5))
        return point_state

    def handle_appoint(self, point_id: str, charger_id: str, start_time: datetime, end_time: datetime):
        """
        处理学生预约申请，修改预约状态
        :param
            point_id: 充电桩编号[str] (eg F/R-01)
            charger_id: 充电者id[str]
            start_time: 预约开始时间[datetime]
            end_time: 预约结束时间[datetime]
        :return:
            无
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM appoint WHERE point_id = %s", (point_id,))
            data = cur.fetchall()
        current_appoint = self.__find_appoint(data, start_time, end_time)
        if current_appoint:
            raise ValueError("预约失败，该时间段已有预约")
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO appoint (point_id, charger_id, start_time, end_time, state) VALUES (%s, %s, %s, %s, 1)",
                        (point_id, charger_id, start_time, end_time))
            con.commit()

    def appoint_start(self, point_id: str):
        """
        将指定充电桩的预约状态从已预约修改为正在履约
        :param
            point_id: 充电桩编号[str] (eg F/R-01)
        :return:
            无
        """
        appoint = self.get_point_appoint_state(point_id, datetime.now(), datetime.now() + timedelta(hours=0.5))
        if appoint != 1:
            raise ValueError("充电桩不是已预约状态")
        point_id, charger_id, start_time, end_time, state = appoint
        with connect_db() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE appoint SET state = 2 WHERE point_id = %s AND charger_id = %s AND start_time <= %s AND end_time >= %s AND state = 1",
                (point_id, charger_id, datetime.now(), datetime.now())
            )
            con.commit()

    def appoint_cancel(self, point_id: str):
        """
        将指定充电桩的预约状态从已预约修改为未预约
        :param
            point_id: 充电桩编号[str] (eg F/R-01)
        :return:
            无
        """
        appoint = self.get_point_appoint_state(point_id, datetime.now(), datetime.now() + timedelta(hours=0.5))
        if appoint != 1:
            raise ValueError("充电桩不是已预约状态")
        point_id, charger_id, start_time, end_time, state = appoint
        with connect_db() as con:
            cur = con.cursor()
            cur.execute(
                "DELETE FROM appoint WHERE point_id = %s AND charger_id = %s AND start_time <= %s AND end_time >= %s AND state = 1",
                (point_id, charger_id, datetime.now(), datetime.now())
            )
            con.commit()

    def appoint_finish(self, point_id: str):
        """
        将指定充电桩的预约状态从正在履约修改为未预约
        :param
            point_id: 充电桩编号[str] (eg F/R-01)
        :return:
            无
        """
        appoint = self.get_point_appoint_state(point_id, datetime.now(), datetime.now() + timedelta(hours=0.5))
        if appoint != 2:
            raise ValueError("充电桩不是正在履约状态")
        point_id, charger_id, start_time, end_time, state = appoint
        with connect_db() as con:
            cur = con.cursor()
            cur.execute(
                "DELETE FROM appoint WHERE point_id = %s AND charger_id = %s AND start_time <= %s AND end_time >= %s AND state = 2",
                (point_id, charger_id, datetime.now(), datetime.now())
            )
            con.commit()

    def block_point(self, point_id: str):
        """
        封锁指定充电桩
        :param
            point_id: 充电桩编号[str] (eg F/R-01)
        :return:
            已经预约的充电者id列表[list]
        """
        charger = list()
        # 把表中point_id为point_id的预约状态删除，把charger_id存到charger中
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT charger_id FROM appoint WHERE point_id = %s", (point_id,))
            data = cur.fetchall()
            for item in data:
                charger.append(item[0])
            cur.execute("DELETE FROM appoint WHERE point_id = %s", (point_id,))
            con.commit()

        # 封锁充电桩，加入一条预约状态为3，开始和结束时间设为无限长的记录
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO appoint (point_id, charger_id, start_time, end_time, state) VALUES (%s, %s, %s, %s, 3)",
                        (point_id, '', datetime(1970, 1, 1), datetime(9999, 12, 31)))
            con.commit()
        return charger

    def unblock_point(self, point_id: str):
        """
        解封指定充电桩
        :param
            point_id: 充电桩编号[str] (eg F/R-01)
        :return:
            无
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM appoint WHERE point_id = %s AND state = 3", (point_id,))
            con.commit()

    def __find_appoint(self, appoints: tuple, start_time: datetime, end_time: datetime):
        """
        检查start_time到end_time内是否有预约(只要时间段有交集就算有预约)
        :param
            appoints: 预约信息[tuple]
            start_time: 开始时间[datetime]
            end_time: 结束时间[datetime]
        :return:
            时间段内的预约信息[tuple]，若没有则返回None
        """
        for appoint in appoints:
            if not (appoint[3] >= end_time or appoint[4] <= start_time):
                return appoint
        return None