from user import User
from repaircontrol import RepairControl
from utils import connect_db


class Engineer(User):

    def __init__(self, engineer_id: str, password: str):
        super().__init__(engineer_id, password)
        if not self.is_in_db():
            raise Exception(f"维修人员{self.get_id()}未注册")
        self.__role = 'engineer'
        self.__region = self.get_region()

    def get_region(self):
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


if __name__ == '__main__':
    print("test Engineer")