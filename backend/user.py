"""
用户类
对外提供用户的基本信息，包括用户的id，密码信息，查询用户信息是否在数据库中，保存用户信息到数据库中
"""
from config import config as cfg
import duckdb


class User:
    def __init__(self, id: str, password: str, db_path=None):
        self.__id = id
        self.__password = password
        if db_path:
            self.__db_path = db_path
        else:
            self.__db_path = cfg['user_db']

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
        con = duckdb.connect(self.__db_path)
        cur = con.cursor()
        cur.execute(f"SELECT * FROM user WHERE id = '{self.__id}'")
        result = cur.fetchdf()
        con.close()
        return not result.empty

    def save_to_db(self):
        """
        保存用户信息到数据库中,如果用户已经存在，则报错
        :return: 无
        """
        con = duckdb.connect(self.__db_path)
        cur = con.cursor()
        if self.is_in_db():
            raise Exception(f"用户{self.__id}已经存在")
        cur.execute(f"INSERT INTO user VALUES ('{self.__id}', '{self.__password}')")
        con.close()


if __name__ == '__main__':
    user = User('admin', 'admin')
    print(user.get_password())