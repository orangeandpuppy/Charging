import time
import os

config = {
    # 数据库路径
    'user_db': 'data/user.db',
    'schedule.db': 'data/schedule.db',
    'charging.db': 'data/charging.db',

    # 输出路径
    'RESULT_PATH': 'result',

    # 电动车充电
    'supported_charging_station': ['G', 'X', 'F'],  # 支持的充电站
}

exp_id = time.strftime('%Y%m%d-%H%M%S', time.localtime())
config['out_dir'] = os.path.join(config['RESULT_PATH'], exp_id)