"""
充电历史查询类

"""
from utils import connect_db


class ChargingHistory:
    def get_charging_history_by_user(self, charger_id):
        """
        根据用户ID查询充电历史记录
        :param
            charger_id: 充电人员ID
        ：return: 
            充电历史记录[tuple((point_id, charger_id, start_time, end_time),(),...)]    
        
        """
        query = '''SELECT * FROM charging WHERE charger_id = ?;'''
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (charger_id,))
            records = cursor.fetchall()
        return records
     
    def get_charging_history_by_charger(self, point_id):
        """
        根据充电桩ID查询充电历史记录
        ：param
            point_id: 充电桩ID
        ：return: 
            充电历史记录[tuple((point_id, charger_id, start_time, end_time),(),...)]

        """
        query = '''SELECT * FROM charging WHERE point_id = ?;'''
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (point_id,))
            records = cursor.fetchall()
        return records    
    
    def insert_charging_record(self, point_id, charger_id, start_time, end_time):
        """
        向数据库插入一条新的充电记录
        ：param
            point_id: 充电桩ID
            charger_id: 充电者ID
            start_time: 开始时间
            end_time: 结束时间
        ：return:
            无
        """
        query = '''
        INSERT INTO charging (point_id, charger_id, start_time, end_time)
        VALUES (?, ?, ?, ?);
        '''
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (point_id, charger_id, start_time, end_time))
            conn.commit()
    