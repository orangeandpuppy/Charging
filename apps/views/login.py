from apps.views import login_blue
from flask import render_template, request
from backend.user import User


# 系统登录
@login_blue.route('/')
def login():
    return render_template("login.html")


# 登陆结果
@login_blue.route('/loginResult', methods=['POST', 'GET'])
def loginResult():
    if request.method == 'POST':
        nm = request.form['nm']
        pwd = request.form['pwd']
        user = User(nm, pwd)
        if user.is_in_db():
            return render_template('loginResult.html', data='succeed')
        else:
            return render_template('loginResult.html', data='failed')
