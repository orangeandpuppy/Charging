import time
import os

config = {
    'user_db': 'data/user.db',
    'schedule.db': 'data/schedule.db',
    'RESULT_PATH': 'result'
}

exp_id = time.strftime('%Y%m%d-%H%M%S', time.localtime())
config['out_dir'] = os.path.join(config['RESULT_PATH'], exp_id)