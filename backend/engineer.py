from user import User
from repaircontrol import RepairControl
from utils import connect_db
from main import create_db
import random


class Engineer(User):

    def __init__(self, engineer_id: str, password: str, region = "G"):
        super().__init__(engineer_id, password)
        self.__role = 'engineer'
        self.__region = region
        self.__state = 0
        if self.is_in_db():
            self.__region, self.__state = self.__get_info()
        else:
            self.save_to_db(region)
            RepairControl.change_for_new_engineer(engineer_id, region)

    def __get_info(self):
        """
        获取该维修人员所属片区
        :return: 片区编号, 工作状态
        """
        print("获取信息",end=' ')
        print(self._User__id)
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT region, work_state FROM engineer "
                        "WHERE engineer_id = %s", self._User__id)
            data = cur.fetchall()[0]
        return data[0], data[1]

    def refresh(self):
        """
        前台定期刷新自己的工作状态
        :return:
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT work_state FROM engineer "
                        "WHERE engineer_id = %s", self._User__id)
            data = cur.fetchall()
            self.__state = data[0][0]

    def save_to_db(self, region):
        """
        保存用户信息到数据库中，即注册,如果用户已经存在，则报错
        :return: 无
        """
        if self.is_in_db():
            raise Exception(f"用户{self._User__id}已经存在")
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO user VALUES (%s, %s)", (self._User__id, self._User__password))
            con.commit()
            cur.execute("INSERT INTO engineer(`engineer_id`, `region`) VALUES (%s, %s)", (self._User__id, region))
            con.commit()

    def get_region(self):
        """
        获取该维修人员所属片区
        :return: 片区编号
        """
        return self.__region

    def get_state(self):
        if self.__state == 0:
            return 0,"空闲"
        elif self.__state == 1:
            return 1,"有新的任务"
        elif self.__state == 2:
            return 2,"工作中"
        else:
            return 3,"请假"

    def accept_repair_request(self):
        """
        接收维修请求
        :return: none
        """
        RepairControl.request_accept(self._User__id, self.__region)

    def complete_repair_request(self, log: str):
        """
        进行维修记录，完成维修任务
        :return: none
        """
        RepairControl.request_complete(self._User__id, log, self.__region)

    def get_current_repair(self):
        """
        查看当前被分配/正在进行的维修单
        :return: 报修信息
        """
        if self.__state == 1 or self.__state == 2:
            return RepairControl.current_request(self._User__id, self.__region).get_request()
        return 0

    def get_repair_list(self):
        """
        查询自己的每一条维修单的 维修请求信息、维修记录、服务评价
        :return:[[维修请求信息, 维修记录, 服务评价]]
        """
        return RepairControl.engineer_get_repair(self._User__id)

    def switch_state(self):
        """
        维修人员上班/请假，修改其工作状态
        :return: none
        """
        if self.__state == 0 or self.__state == 3:
            self.__state = 3 - self.__state
            RepairControl.change_state_engineer(self._User__id, self.__region, self.__state)


if __name__ == '__main__':

    create_db(delete=True)

    user = User('user1', '123456')
    user.save_to_db()

    while True:
        print("1. 登录\n2. 注册")
        choice = int(input())
        print("id:", end='')
        id_login = input()
        print("password:", end='')
        psw_login = input()
        region = 'G'
        if choice == 2:
            print("所属地区:", end='')
            region = input()
        e1 = Engineer(id_login, psw_login, region)
        # if not e1.is_in_db():
        #     if choice == 1:
        #         print("该id尚未注册")
        #         continue
        #     else:
        #         e1.save_to_db()
        # else:
        #     if choice == 2:
        #         print("该id已被注册")
        #         continue
        if not e1.is_in_db():
            e1.save_to_db()

        RepairControl.repair_request(user.get_id(), 'G', '车坏了修一下' + str(random.random()))   # 模拟用户报修

        while True:
            e1.refresh()
            state, state_name = e1.get_state()
            print("------------------------------")
            print("地区:{0}  {1}".format(e1.get_region(), state_name))
            if state == 0:
                print("1. 请假")
            elif state == 1 or state == 2:
                print("1. 查看当前维修单")
            else:
                print("1. 开始工作")
            print("2. 查看历史维修信息")
            print("3. 刷新状态")
            print("4. 退出登录")

            choice = int(input())

            if choice == 1:
                if state == 0 or state == 3:
                    e1.switch_state()
                elif state == 1 or state == 2:
                    print(e1.get_current_repair())
                    if state == 1:
                        print("1. 接受报修申请")
                    else:
                        print("1. 完成此次维修")
                    print("2. 返回")
                    choice = int(input())
                    if choice == 1:
                        if state == 1:
                            e1.accept_repair_request()
                            print("已接受")
                        else:
                            print("维修日志:", end='')
                            log = input()
                            e1.complete_repair_request(log)
                            print("完成维修")

                            rid = RepairControl.user_get_repair(user.get_id())[0][0]  # 模拟用户评价
                            RepairControl.request_evaluate(rid, '非常好维修')

            elif choice == 2:
                rlist = e1.get_repair_list()
                print(rlist)
                print("任意键返回上一级")
                input()

            elif choice == 4:
                break
