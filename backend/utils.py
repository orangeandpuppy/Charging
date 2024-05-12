from config import config as cfg


def check_ebike_id(ebike_id: str):
    """
    检查电动车编号是否为合法编号
    :param
        ebike_id: 电动车编号
    :return:
        True/False
    """
    if len(ebike_id) != 5:
        return False
    if ebike_id[0] not in cfg['supported_charging_station']:
        return False
    if not ebike_id[1:].isdigit():
        return False
    return True


if __name__ == "__main__":
    print(check_ebike_id('G1234'))
    print(check_ebike_id('X1X34'))