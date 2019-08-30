# -*- coding: utf-8 -*-


def parse_list(innert_ip_list,parse_num):
    req_instance_ip_list = []
    if len(innert_ip_list) > parse_num:
        split_num = int(len(innert_ip_list) / parse_num) + 1
        for i in range(0, split_num):
            tmp_list = []
            if int(i) == int(split_num) - 1:
                tmp_list = innert_ip_list[parse_num * i:]
            elif int(i) == 0:
                tmp_list = innert_ip_list[0:parse_num * (i + 1)]
            else:
                tmp_list = innert_ip_list[parse_num * i:parse_num * (i + 1)]
            if len(tmp_list):
                req_instance_ip_list.append(tmp_list)
    else:
        req_instance_ip_list.append(innert_ip_list)

    return req_instance_ip_list


if __name__ == "__main__":
    innert_ip_list = [
        "10.0.0.0",
        "10.0.0.1",
        "10.0.0.2",
        "10.0.0.3",
        "10.0.0.4",
        "10.0.0.5",
        "10.0.0.6",
        "10.0.0.7",
        "10.0.0.8",
        "10.0.0.9",
        "10.0.0.10",

    ]
    parse_num = 6
    req_instance_ip_list = parse_list(innert_ip_list,parse_num)
    for data in req_instance_ip_list:
        print(type(data))
        print(data)