from repairrequest import RepairRequest
from utils import CHARGER_LIST, connect_db, count_engineer
import queue


class RepairControl:
    """
    静态方法类，通过类名直接调用
    """
    repair_request_process_list = {i:[] for i in CHARGER_LIST}   # 每个地区中正在进行的维修列表
    repair_request_wait_queue = {i:queue.Queue() for i in CHARGER_LIST}
    region_engineer = count_engineer()

    @staticmethod
    def position_classify(position: str):
        """
        根据地址划分片区，暂时默认前端已经处理成对应片区的编号
        :param position: 用户所在地址
        :return: 片区编号
        """
        return position

    @staticmethod
    def repair_request(user_id: str, position_api: str, request_info: str):
        """
        用户调用此函数申请维修
        :param user_id: 用户id
        :param position_api: 用户地址，前端调用api获取 or 自行填写
        :param request_info: 维修信息
        :return: none
        """
        region = RepairControl.position_classify(position_api)
        new_repair_request = RepairRequest(user_id, region, request_info)
        new_repair_request.distribute_engineer()
        found = False
        for (index,engineer) in enumerate(RepairControl.region_engineer[region]):
            if engineer[1] == 0:    # 找到该片区第一个空闲的人，分配任务
                new_repair_request.distribute_engineer(engineer[0])     # 分配
                RepairControl.region_engineer[region][index].append(new_repair_request)
                RepairControl.region_engineer[region][index][1] = 1
                found = True

        if not found:   # 暂无空闲维修人员，加入等待列表
            RepairControl.repair_request_wait_queue[region].put(new_repair_request)

    @staticmethod
    def request_accept(engineer_id: str, region: str):
        """
        维修人员接受请求后调用该函数
        :param engineer_id: 维修人员id
        :param region: 维修人员所属片区编号
        :return: none
        """
        for (index,engineer) in enumerate(RepairControl.region_engineer[region]):
            if engineer[0] == engineer_id:    # 找到该维修人员
                RepairControl.region_engineer[region][index][2].request_accept()
                RepairControl.region_engineer[region][index][1] = 2

    @staticmethod
    def request_complete(engineer_id: str, log: str, region: str):
        """
        维修人员完成任务后调用该函数
        :param engineer_id: 维修人员id
        :param log: 维修记录
        :param region: 维修人员所属片区编号
        :return: none
        """
        for (index,engineer) in enumerate(RepairControl.region_engineer[region]):
            if engineer[0] == engineer_id:    # 找到该维修人员，状态改为空闲，弹出任务
                RepairControl.region_engineer[region][index][2].request_complete(log)
                RepairControl.region_engineer[region][index][1] = 0
                RepairControl.region_engineer[region][index].pop()
                if not RepairControl.repair_request_wait_queue[region].empty():     # 还有任务需要分配
                    new_repair_request = RepairControl.repair_request_wait_queue[region].pop()
                    new_repair_request.distribute_engineer(engineer[0])     # 分配给该维修人员
                    RepairControl.region_engineer[region][index].append(new_repair_request)
                    RepairControl.region_engineer[region][index][1] = 1

    @staticmethod
    def request_evaluate(repair_id: int, comment: str):
        """
        用户调用该函数，对维修进行评价
        :param repair_id: 维修单id
        :param comment: 评价内容
        :return: none
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("UPDATE charger_repair_id SET service_evaluate = '%s' WHERE repair_id = %d",
                        (comment, repair_id))
            con.commit()

    @staticmethod
    def user_get_repair(user_id: str):
        """
        用户调用，查询自己的报修记录
        :param user_id: 用户id
        :return: [维修单编号(用于调用填写评价函数), 维修请求信息, 维修人员的维修记录, 用户自己的评价]
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT repair_id,repair_request,repair_log,service_evaluate FROM charger_repair_id "
                        "WHERE user_id = %s", user_id)
            data = cur.fetchall()
        return data

    @staticmethod
    def engineer_get_repair(engineer_id: str):
        """
        维修人员调用，查询自己的报修记录
        :param engineer_id: 用户id
        :return: [维修请求信息, 维修人员自己的维修记录, 用户评价]
        """
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("SELECT repair_request,repair_log,service_evaluate FROM charger_repair_id "
                        "WHERE engineer_id = %s", engineer_id)
            data = cur.fetchall()
        return data


if __name__ == '__main__':
    print("test RepairControl")