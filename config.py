import time
import os


# =============================================== 后端配置 =================================================

config = {
    # MySQL
    'host': '115.236.153.172',
    'user': "remote_connect",
    'password': "123456",
    'port': 22434,  # 26505
    'database': 'charging_db',
    'charset': 'utf8',

    # 输出路径
    'RESULT_PATH': 'result',

    # 电动车充电
    'supported_charging_station': ['G', 'X', 'F'],  # 支持的充电站
    'supported_charging_point_color': ['R', 'B'],  # 支持的充电口颜色
    'charging_station_point_num': {'G': 30, 'X': 30, 'F': 30},  # 充电站内每种颜色的充电桩数量，编号从1开始

    # 支持的密码字符（为了防止加入数据库时有转义符）
    'supported_password_char': [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + ['-', '+', '*', '@'],
}

exp_id = time.strftime('%Y%m%d-%H%M%S', time.localtime())
config['out_dir'] = os.path.join(config['RESULT_PATH'], exp_id)


# =============================================== 前后端连接配置 =================================================

# 应用运行地址
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
# 应用运行端口
FLASK_PORT = os.getenv('FLASK_PORT', 8021)
# 是否调试模式：是-True,否-False
FLASK_DEBUG = True