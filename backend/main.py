import sys
sys.path.append('e:/学校用/大三/软件工程/Charging')
from utils import connect_db
from user import User
from appointstate import AppointState
from datetime import datetime

def create_db(delete=False):
    """
    创建数据库
    :param
        delete: 是否删除已有数据库
    :return: 无
    """
    con = connect_db()
    if delete:
        con.cursor().execute("DROP DATABASE IF EXISTS charging_db;")

    con.cursor().execute("CREATE DATABASE IF NOT EXISTS charging_db;")
    con.cursor().execute("USE charging_db;")
    # 创建用户表, 用户id为主键, 密码为非空
    con.cursor().execute("CREATE TABLE IF NOT EXISTS user ("
                         "`id`          VARCHAR(255) PRIMARY KEY,"
                         "`password`    VARCHAR(255) NOT NULL"
                         ");")

    # 创建预约状态表, 预约id为主键，充电者id为外键，开始时间和结束时间为非空，状态为非空
    con.cursor().execute("CREATE TABLE IF NOT EXISTS appoint (" 
                         "`id`          INT PRIMARY KEY AUTO_INCREMENT,"
                         "`point_id`    VARCHAR(255) NOT NULL,"
                         "`charger_id`  VARCHAR(255) NOT NULL,"
                         "`start_time`  DATETIME NOT NULL,"
                         "`end_time`    DATETIME NOT NULL,"
                         "`state`       INT NOT NULL,"
                         "FOREIGN KEY (`charger_id`) REFERENCES user(`id`)"
                         ");")
    # state: 1-已预约，未充电, 2-已预约，正在履约 3-上锁

    # 创建充电记录表, 充电id为主键，充电者id为外键，开始时间和结束时间为非空
    con.cursor().execute("CREATE TABLE IF NOT EXISTS charging (" 
                         "`id`          INT PRIMARY KEY AUTO_INCREMENT,"
                         "`point_id`    VARCHAR(255) NOT NULL,"
                         "`charger_id`  VARCHAR(255) NOT NULL,"
                         "`start_time`  DATETIME NOT NULL,"
                         "`end_time`    DATETIME NOT NULL,"
                         "FOREIGN KEY (`charger_id`) REFERENCES user(`id`)"
                         ");")
    con.close()
    print("数据库创建成功")


if __name__ == '__main__':
    create_db()
    """
    # Test user
    user = User('admin', '123456')
    user.save_to_db()
    # 因为没有清空数据库，所以会报错，改一下id就行
    """

    # Test appoint
    with connect_db() as con:
        con.cursor().execute("INSERT INTO appoint (point_id, charger_id, start_time, end_time, state) VALUES ('F/R-01', 'admin', '2021-07-01 12:00:00', '2021-07-01 13:00:00', 1);")
        con.commit()
    appoint_state = AppointState()
    a = appoint_state.get_station_appoint_state('F', datetime(2021, 7, 1, 12, 0, 0), datetime(2021, 7, 1, 13, 0, 0))
    print(a)