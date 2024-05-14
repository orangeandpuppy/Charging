import flask
from flask_cors import CORS
from apps.views import register_blueprint


def create_app():
    app = flask.Flask(__name__, template_folder='../templates', static_folder='../static')
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # 注册蓝图
    register_blueprint(app)
    return app
