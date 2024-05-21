from user import User
from repaircontrol import RepairControl
from utils import connect_db


class Engineer(User):

    def __init__(self, engineer_id: str, password: str, role: str = 'engineer'):
        super().__init__(engineer_id, password, role)
        if not self.is_in_db():
            raise Exception(f"维修人员{self.get_id()}未注册")
        self.__role = 'engineer'
        self.__region = self.__get_region()
        self.__state = self.__get_state()

    def __get_region(self):
        """
        获取该维修人员所属片区
        :return: 片区编号
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT region FROM engineer "
                        "WHERE engineer_id = %s", self.__id)
            data = cur.fetchall()[0][0]
        return data

    def __get_state(self):
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT work_state FROM engineer "
                        "WHERE engineer_id = '%s'", self.__id)
            data = cur.fetchall()[0][0]
        return data


    def accept_repair_request(self):
        """
        接收维修请求
        :return: none
        """
        RepairControl.request_accept(self.__id, self.__region)

    def complete_repair_request(self, log: str):
        """
        进行维修记录，完成维修任务
        :return: none
        """
        RepairControl.request_complete(self.__id, log, self.__region)

    def get_repair_list(self):
        """
        查询自己的每一条维修单的 维修请求信息、维修记录、服务评价
        :return:[[维修请求信息, 维修记录, 服务评价]]
        """
        return RepairControl.engineer_get_repair(self.__id)

    def switch_state(self):
        """
        维修人员上班/请假，修改其工作状态
        :return: none
        """
        if self.__state == 0 or self.__state == 3:
            self.__state = 3 - self.__state
            with connect_db() as con:
                cur = con.cursor()
                cur.execute("UPDATE engineer SET work_state = %d WHERE engineer_id = '%s'",
                            (self.__state, self.__id))
                con.commit()
            RepairControl.change_state_engineer(self.__id, self.__region, self.__state)


if __name__ == '__main__':
    print("test Engineer")