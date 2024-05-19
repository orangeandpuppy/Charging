from utils import connect_db


class RepairRequest:
    def __init__(self, user_id:str, position:str, request:str):
        """
        特定维修申请的类
        :param user_id: 用户的维修id
        :param position: 维修地址
        :param request: 维修请求信息
        """
        self.__user_id = user_id
        self.__region = position
        self.__repair_request = request
        self.__engineer_id = ''
        self.__repair_log = ''
        self.__service_evaluate = ''

    def distribute_engineer(self, engineer_id:str):
        """
        把维修请求单分配给维修人员，状态改变为1(分配工作中)
        :param engineer_id: 维修人员id
        :return: none
        """
        self.__engineer_id = engineer_id
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("UPDATE engineer SET work_state = 1 WHERE engineer_id = %s", self.__engineer_id)
            con.commit()

    def request_accept(self):
        """
        维修人员接受请求后，状态改变为2(工作中)
        :return:none
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("UPDATE engineer SET work_state = 2 WHERE engineer_id = %s", self.__engineer_id)
            con.commit()

    def request_complete(self, log:str):
        """
        维修人员记录维修信息后完成维修，信息记录到数据库中，状态改变为0(空闲)
        :param log:维修记录
        :return: none
        """
        self.__repair_log = log
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO charger_repair_id VALUES (NULL, '%s', '%s', '%s', '%s', '%s')",
                        (self.__user_id, self.__engineer_id, self.__repair_request, self.__repair_log,
                         self.__service_evaluate))
            con.commit()

            cur.execute("UPDATE engineer SET work_state = 0 WHERE engineer_id = %s", self.__engineer_id)
            con.commit()


if __name__ == '__main__':
    print("test RepairRequest")