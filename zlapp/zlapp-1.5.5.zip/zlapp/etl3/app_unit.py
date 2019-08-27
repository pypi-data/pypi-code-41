from zlapp.etl3 import app_bd 
from zlapp.etl3 import app_bd_dt
from zlapp.etl3 import app_t_gg_ent_bridge
from zlapp.etl3 import app_gg_zhongbiao
from zlapp.etl3 import app_qy_zhongbiao 
from zlapp.etl3 import app_app_qy_zz
from zlapp.etl3 import app_app_qy_zcry

from zlapp.etl3 import app_app_gg_zhongbiao
from zlapp.etl3 import app_app_qy_query 
from zlapp.etl3 import app_t_bd_xflv 


print("一、bd")
app_bd.est()
print("二、bd_dt")
app_bd_dt.est()
print("三、t_gg_ent_bridge")
app_t_gg_ent_bridge.est()
print("四、gg_zhongbiao")
app_gg_zhongbiao.est()

print("五、qy_zhongbiao")
app_qy_zhongbiao.est()
print("六、app_qy_zz")
app_app_qy_zz.est()
print("七、app_qy_zcry")
app_app_qy_zcry.est()
print("八、app_gg_zhongbiao")
app_app_gg_zhongbiao.est()
print("九、t_bd_xflv")
app_t_bd_xflv.est()





