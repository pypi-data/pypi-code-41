from zltask.route import task_quyu

#
# from zltask.hawq import add_quyu ,restart_quyu

# from zlhawq.data import zhulong_diqu_dict

#
# from zlhawq.data import zl_diqu_dict
#
# from zlhawq.data import zlest1_diqu_dict
#
# from zlhawq.data import zl_shenpi_dict
#
# from zlhawq.data import zlsys_diqu_dict
#
# from zlhawq.data import zlest_diqu_dict
#
# import traceback
#
#
#
# def add_sheng(sheng):
#     if sheng=='zfcg':
#         quyus=zl_diqu_dict['zfcg']
#         quyus.sort()
#     elif sheng=='gcjs':
#         quyus=zl_diqu_dict['gcjs']
#         quyus.sort()
#
#     elif sheng=='qycg':
#         quyus=zl_diqu_dict['qycg']
#         quyus.sort()
#
#     elif sheng=='zlsys':
#         quyus=zlsys_diqu_dict['zlsys']
#         quyus.sort()
#
#     elif sheng=='zlest':
#         quyus=zlest_diqu_dict['zlest']
#         quyus.sort()
#
#     elif sheng=='zlest1':
#         quyus=zlest1_diqu_dict['zlest1']
#         quyus.sort()
#
#     elif sheng=='zlshenpi':
#         quyus=zl_shenpi_dict['zlshenpi']
#         quyus.sort()
#
#     else:
#         quyus=zhulong_diqu_dict[sheng]
#     length=len(quyus)
#     i=0
#     for quyu in quyus:
#         try:
#             print(quyu)
#             add_quyu(quyu)
#             i+=1
#         except:
#             traceback.print_exc()
#     if i!=length:
#         raise Exception("i<length,%s-更新失败"%sheng)
#
#
#
# def add_quyu_all():
#     shengs1=list(zhulong_diqu_dict.keys())
#
#     shengs1.sort()
#
#     shengs2=['zfcg','gcjs','qycg','zlest','zlest1','zlsys']
#
#     shengs1.extend(shengs2)
#
#     for sheng in shengs1:
#
#         add_sheng(sheng)
#
#
#
#
#
#
#
#
#
#
#
