from config import config as cfg
from datetime import timedelta, datetime
import pymysql as py


CHARGER_LIST = cfg['supported_charging_station']

def connect_db():
    """
    连接数据库
    :return:
        数据库连接对象
    """
    conn = py.connect(host=cfg['host'],
                      user=cfg['user'],
                      password=cfg['password'],
                      port=cfg['port'],
                      database=cfg['database'],
                      charset=cfg['charset'])
    return conn


def check_ebike_id(ebike_id: str):
    """
    检查电动车编号是否为合法编号
    :param
        ebike_id: 电动车编号 (eg G1234)
    :return:
        True/False
    """
    if len(ebike_id) != 5:
        return False
    if ebike_id[0] not in cfg['supported_charging_station']:
        return False
    if not ebike_id[1:].isdigit():
        return False
    return True


def check_point_id(point_id: str):
    """
    检查充电桩编号是否为合法编号
    :param
        point_id: 充电桩编号
    :return:
        True/False
    """
    # 充电桩编号格式为: 充电站字母/充电口颜色（R或B）-两位数字 例如: F/R-01
    if len(point_id) != 6:
        return False
    if point_id[0] not in cfg['supported_charging_station']:
        return False
    if point_id[2] not in CHARGER_LIST:
        return False
    if point_id[1] != '/' or point_id[3] != '-':
        return False
    if not point_id[4:].isdigit():
        return False
    return True


def check_charge_time(start_time: datetime, end_time: datetime):
    """
    检查充电开始和结束时间是否合法
    :param
        start_time: 充电开始时间 [datetime]
        end_time: 充电结束时间 [datetime]
    :return:
        True/False
    """
    if start_time > end_time:
        return False
    if end_time - start_time > timedelta(hours=10):
        raise Exception("充电时间不得超过10小时")
    # 充电开始和结束时间之差为半小时的整数倍
    if (end_time - start_time).seconds % 1800 != 0:
        return False
    return True


def str_to_datetime(time_str: str):
    """
    把str类型的时间转为datetime类型
    :param
        time_str: str类型的时间
    :return:
        datetime类型的时间
    """
    # str类型格式:2021-01-01 00:00
    return datetime.strptime(time_str, '%Y-%m-%d %H:%M')


def str_to_timedelta(time_str: str):
    """
    把str类型的时间转为timedelta类型
    :param
        time_str: str类型的时间
    :return:
        timedelta类型的时间
    """
    # str类型格式:00:00
    return timedelta(hours=int(time_str.split(':')[0]), minutes=int(time_str.split(':')[1]))


def count_engineer():
    """
    计算每个片区中维修人员的数量
    :return: dict('片区字母':[维修人员id, 工作状态])，工作状态为0(空闲)1(分配工作中)2(工作中)3(放假中)
    """
    cnt_list = {i:[] for i in CHARGER_LIST}
    for region in CHARGER_LIST:
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT engineer_id FROM engineer WHERE region = %s", region)
            data = cur.fetchall()
        cnt_list[region] = [[i, 0] for i in data]
    return cnt_list

if __name__ == "__main__":
    print(check_point_id("F/R-01"))