from .deliverer import Deliverer
from .storage import Storage
from .filterer import Filterer


# def pick_influential_param(get_params):
#     param = ""
#     previous_rank = -1
#     for key, value in get_params.items():
#         current_rank = feature1(value)
#         if previous_rank < current_rank:
#             param = key
#             previous_rank = current_rank
#         elif previous_rank == current_rank:
#             # RANDOMLY SELECT ONE OF TWO
#             pass
#     return param

# def feature1(value):
#     try:
#         int(value)
#         return 1
#     except:
#         return 0




# get_params = find_get_params_candidates(TEST_URL)
# print(get_params)

# Finding event listeners
# driver = webdriver.Chrome("./chromedriver")
# driver.get(TEST_URL)
# element = driver.find_element_by_xpath("html")
# event_listeners = find_all_event_listeners(f"{element.tag_name}", element)
# print(len(event_listeners))
# driver.close()





# hrefs = find_all_hrefs(element)
# print(len(hrefs))