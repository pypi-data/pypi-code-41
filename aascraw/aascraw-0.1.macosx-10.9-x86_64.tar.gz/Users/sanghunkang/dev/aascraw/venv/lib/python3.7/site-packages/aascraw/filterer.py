from lxml import etree, html
import numpy as np
from io import StringIO
import re

def build_xpath(prefix, element, child_index):
    selector = f"[{child_index}]"
    for attrib_name, attrib_value in element.attrib.items():
        selector = selector + f"[@{attrib_name}='{attrib_value}']"
    return f"{prefix}/{element.tag}{selector}"

def update_prev_tag_counts(tag_name, prev_tag_counts):
    if tag_name in prev_tag_counts:
        prev_tag_counts[tag_name] += 1
    else:
        prev_tag_counts[tag_name] = 1
    return prev_tag_counts

def find_all_xpaths(preceding_xpath, element, child_index):
    prefix_xpath = build_xpath(preceding_xpath, element, child_index)
    xpaths = [prefix_xpath]
    children = element.getchildren()

    if len(children) > 0:
        prev_tag_counts = {}
        for child in children:
            prev_tag_counts = update_prev_tag_counts(child.tag, prev_tag_counts)
            xpaths = xpaths + find_all_xpaths(prefix_xpath, child, prev_tag_counts[child.tag])
    return xpaths

def cleanse_content(content):
    content = re.sub(r"<(script).*?</\1>(?s)", "", content)
    content = re.sub(r"<(style).*?</\1>(?s)", "", content)
    content = re.sub(r"<.+>", "", content)
    content = re.sub(r"[\n|\t]", "", content)
    content = content.strip()
    return content

class Filterer():
    def __init__(self):
        super().__init__()

        self.new_action_default_rank = 0
        self.sum_rank = 0
        
        self.actions = {
            #XPath to locate an element: [rank, array_id]
            #XPath to locate an element: id at array
        }

        self.vector_alpha = [] 

        self.results = [

        ]


    def __sort_actions(self):
        pass

    def __sample_action(self):
        # The probability to sample actions follow Dirichlet distribution
        sample_size = 10
        vector_alpha = # Array of ranks at associated positions
        np.random.dirichlet(vector_alpha, sample_size).transpose()
        # np.random.dirichlet((10, 5, 3), 20).transpose()

        return self.actions.keys()

    def load_page(self, action_taken, page):
        self.deliverer_action = action_taken
        self.page = page
        self.tree = html.fromstring(self.page)

    def run_page(self):
        
        actions_to_execute = self.__sample_action()
        
        
        results = []
        for action_to_execute in actions_to_execute:
            try:
                # Locate element
                elements = self.tree.xpath(action_to_execute)
                
                # Parse its content
                content = etree.tostring(elements[0], pretty_print=True, encoding="UTF-8").decode("utf-8")
                content = cleanse_content(content)
                
                # The method doesn't care about schema until this step
                # results.append(
                #     [self.deliverer_action, action_to_execute, content]
                # )

                results.append({
                    "deliverer_action": self.deliverer_action,
                    "filterer_action": action_to_execute,
                    "crawled_data": content,
                    "index": None,          # NOTE MAYBE SOMETHING ELSE INDICATING IT WILL BE IMPLEMENTED LATER ON
                    "rank_delta": None,     # NOTE MAYBE SOMETHING ELSE INDICATING IT WILL BE IMPLEMENTED LATER ON
                })
                # print(content)
            except etree.XPathEvalError:
                pass
                # print("Invalid xpath")
        return results
    
    def update_action_space(self):
        print("This function will look for selector sequences")

        xpaths = find_all_xpaths("", self.tree, 1)
        for xpath in xpaths:
            if xpath not in self.actions:
                self.actions[xpath] = self.new_action_default_rank
        
        
        


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