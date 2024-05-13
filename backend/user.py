"""
用户类
对外提供用户的基本信息，包括用户的id，密码信息，查询用户信息是否在数据库中，保存用户信息到数据库中
"""
from config import config as cfg
from utils import connect_db


class User:
    def __init__(self, id: str, password: str):
        self.__id = id
        if not self.__check_password(password):
            raise Exception("密码不合法")
        self.__password = password

    def get_id(self):
        """
        获取用户的id
        :return: 用户的id
        """
        return self.__id

    def get_password(self):
        """
        获取用户的密码
        :return: 用户的密码
        """
        return self.__password

    def is_in_db(self):
        """
        查询用户信息是否在数据库中
        :return: True/False
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE id = %s", (self.__id,))
            data = cur.fetchone()
        return data is not None

    def save_to_db(self):
        """
        保存用户信息到数据库中,如果用户已经存在，则报错
        :return: 无
        """
        if self.is_in_db():
            raise Exception(f"用户{self.__id}已经存在")
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO user VALUES (%s, %s)", (self.__id, self.__password))
            con.commit()

    def __check_password(self, password):
        """
        检查密码是否合法
        :param
            password: 密码
        :return: True/False
        """
        # 检查是否每个字符都在cfg['supported_password_char']中,且长度在[6, 20]之间
        if len(password) < 6 or len(password) > 20:
            return False
        for c in password:
            if c not in cfg['supported_password_char']:
                return False
        return True


if __name__ == '__main__':
    user = User('admin', 'admin')
    print(user.get_password())