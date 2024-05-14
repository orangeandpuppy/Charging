from flask import Blueprint

# 创建蓝图，参数依次是：蓝图名字、蓝图所在位置、URL前缀(注意：URL前缀对该蓝图下所有route都起作用)

# 系统主页
index_blue = Blueprint('index', __name__, url_prefix='/')
# 系统登录
login_blue = Blueprint('login', __name__, url_prefix='/login')

from .index import index_blue
from .login import login_blue


def register_blueprint(app):
    # 系统主页
    app.register_blueprint(index_blue)
    # 系统登录
    app.register_blueprint(login_blue)