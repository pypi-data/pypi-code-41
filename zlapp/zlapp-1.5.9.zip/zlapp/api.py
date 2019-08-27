from zlapp.cdc.api import add_quyu_app 

from zlgp.api import add_quyu_union 

def src_dst_app(quyu,tag,loc='aliyun'):

    add_quyu_union(quyu,tag,loc)

    add_quyu_app(quyu)