from zlapp.cdc.api import pre_meta
from zlapp.cdc import api 

forbiden_list=["yunnan_baoshan_ggzy","yunnan_chuxiong_ggzy","yunnan_dali_ggzy","yunnan_dehong_ggzy","yunnan_honghe_ggzy","yunnan_kunming_ggzy","yunnan_lijiang_ggzy"
,"yunnan_lincang_ggzy","yunnan_puer_ggzy","yunnan_tengchong_ggzy","yunnan_wenshan_ggzy"
,"yunnan_xishuangbanna_ggzy","yunnan_yunnansheng_1_ggzy","yunnan_yunnansheng_ggzy","yunnan_yuxi_ggzy","yunnan_zhaotong_ggzy"]
from zlapp.greenplum.api import update_all

def add_quyu_app(quyu,loc="aliyun"):
    if quyu in forbiden_list:
        print("%s 已经下线"%quyu)
    else:
        api.add_quyu_app(quyu,loc)




