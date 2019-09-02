import gc
import swagger
gc.collect()


from grown import setup, run_grown
from grown.light_control import add_light_control
from grown.data_control import add_data_control
from grown.wlan import _sta_if
router = setup()
add_data_control(router, lambda: {'data': 1, 'more sensor': 2.0})

@swagger.info("My_funny summary")
@swagger.parameter('myvarname', description="", example='sdfs', required=True)
@swagger.response(200, 'smth is off')
def myrest_func(request):
    raise


@swagger.info("My_funny summary")
@swagger.body('weatherinfo', example={'tada': "examplevar",
                              "tada2": 2})
@swagger.response(200, 'smth is off')
def post_myrest_func(request):
    raise


router.add("/resturl", myrest_func, method="GET")
router.add("/resturl", post_myrest_func, method="POST")


#TODO static file
def _enable():
    print("heja enabled light")


def _disable():
    print("heja disabled light")


add_light_control(router, _enable, _disable)
# TODO better _func to get config
router.add("/swagger.json", swagger.swagger_file('my swagger api', "api title", host=_sta_if.ifconfig()[0], router_instance=router))
run_grown()
