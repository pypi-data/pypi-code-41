# FORMATS
#
# DELIVERER_ACTIONS = 
#   f"HREF::{URL}
#   f"GET_PARAMS::{NAME};{OPERATOR}
#   f"EVENT::{undefined}

# # {
#                 "action_type": "HREF",
#                 "rank": self.new_action_default_rank
#                 "url": entry_point,
#             }
###

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import re

chrome_options = Options()
chrome_options.add_argument("--headless")
#chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--disable-gpu")
# driver = webdriver.Chrome()

def find_all_event_listeners(preceding_xpath, element):
    elements = element.find_elements_by_xpath("./*")
    
    if len(elements) == 0:
        return [f"{preceding_xpath}-{element.tag_name}"]
    else:
        event_listeners = []
        for element in elements:
            print(f"{preceding_xpath}-{element.tag_name}")
            event_listeners =  event_listeners + find_all_event_listeners(f"{preceding_xpath}-{element.tag_name}", element)
        return event_listeners

# Finding hrefs
def find_all_hrefs(element):
    actions = []
    elements = element.find_elements_by_xpath("//a[@href]")
    for element in elements:
        href = element.get_attribute("href")
        actions.append(f"HREF::{href}")
    return actions

# Finding get parameters
def parse_get_params(url):
    get_params = {}
    for pair in url.split("?")[1].split("&"):
        get_params[pair.split("=")[0]] = pair.split("=")[1]
    return get_params

def find_get_params_candidates(url):
    actions = []
    get_params = parse_get_params(url)
    for param_name, param_value in get_params.items():
        try:
            int(value)
            actions.append(f"GET_PARAMS::++>{param_name}")
        except:
            actions.append(f"GET_PARAMS::OTHER_OPERATION>{param_name}")
    return actions


def format_url(url, action):
    operator = action.split(">")[0]
    param = action.split(">")[1]

    get_params = parse_get_params(url)
    param_value = get_params[param]
    
    if operator == "++":
        param_value = f"{int(param_value) + 1}".rjust("0", len(param_value))
    elif operator == "--":
        param_value = f"{int(param_value) - 1}".rjust("0", len(param_value))
    elif operator == "OTHER_OPERATION":
        pass    
    else:
        raise Exception("Update operation undefined")

    return re.sub(r"&" + param + r"=.+", "&", url) + f"&{param}={param_value}"

class Deliverer():
    def __init__(self, entry_point):
        super().__init__()
        
        self.new_action_default_rank = 0
        self.sum_rank = 0 # Just in case        

        # Agent        
        self.driver = webdriver.PhantomJS("./drivers/phantomjs")
        # self.driver = webdriver.Chrome("./drivers/chromedriver", chrome_options=chrome_options)
        
        # State
        self.state = {
            "actions_taken": "",
            "page": ""
        }

        # Actions, which are set of possible transitiions
        self.actions = {
            f"href::{entry_point}": {
                "action_type": "HREF",
                "rank": self.new_action_default_rank,
                "url": entry_point
            }
        }
        
    def proceed(self):
        # Randomly select action
        action = self.__randomly_select_action()

        # Execute the selected action (triggering event or sending request)
        if action["action_type"] == "HREF":
            self.driver.get(action)
        elif action["action_type"] == "GET_PARAM":
            self.url = format_url(self.url, action)
            self.driver.get(self.url)
        elif action["action_type"] == "EVENT":
            pass
            #     xpath = format_xpath(action)
            #     trigger = format_trigger(action)
            #     self.driver.find_element_by_xpath(xpath).execute(trigger)
        
        # Get the document of currently displayed page
        self.state = {
            "action_taken": action,
            "page": self.driver.execute_script("return document.documentElement.outerHTML;")
        }


    def __randomly_select_action(self):
        # Pick action in actions space weighted by rank
        # NOTE SAMPLING ACTION WILL BE IMPLEMENTED
        for _, action in self.actions.items():
            return action        

    def __sort_actions(self):
        self.actions = sorted(self.actions, key=lambda key, rank: rank)

    

    def update_action_space(self):
        print("This function will look for possible event triggers and get queries")
        
        # find all event listeners
        # find_all_event_listeners(f"{element.tag_name}", element)
        
        # find all hrefs
        for href in find_all_hrefs(self.page):
            if href not in self.actions:
                self.actions[href] = self.new_action_default_rank
        
        # find all get candidate -> i.e. next url
        for param in find_get_params_candidates(self.driver.current_url):
            if param not in self.actions:
                self.actions[param] = self.new_action_default_rank


    def update_policy(self, rank_deltas):
        for rank_delta in rank_deltas:
            # action_key = rank_delta[0]
            # action_rank = rank_delta[1]
            
            # if action_key in self.actions:
            self.actions[rank_delta[0]][1] += rank_delta[1]
            self.sum_rank += rank_delta[1]
            # else:
            #     raise Exception("This case must not exist")

        self.__sort_actions()
        # MAYBE NORMALIZE

    