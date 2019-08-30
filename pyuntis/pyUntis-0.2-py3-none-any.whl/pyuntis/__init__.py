from bs4 import BeautifulSoup
import re

valid_class = re.compile(r"\d+.?")


class PyUntis:
    def __init__(self, data=None):
        self.data = data

    def parse(self):
        soup = BeautifulSoup(self.data, "lxml")

        stand = soup.find("table", "mon_head").find("p").text.split(": ")[1]
        date, tag = soup.find("div", "mon_title").text.split(" ")

        table = soup.find("table", "mon_list")
        info_table = soup.find("table", "info")

        plan = {
            "stand": stand,
            "date": date,
            "tag": tag,
            "informationen": [],
            "plan": []
        }

        def clean(string, info=False):
            string = string.replace("\xa0", "")
            string = string.replace("  ", "")
            if not info:
                string = string.replace("\n", " ")
            return string

        for td in table.find_all("td", "list inline_header"):
            vertretungen = {"klasse": "",
                            "vertretungen": []}
            if valid_class.match(td.text):
                vertretungen["klasse"] = td.text
                for sibling in td.parent.next_siblings:
                    if sibling != "\n":
                        if sibling.find("td", "list inline_header"):
                            break
                        cols = sibling.find_all("td")
                        if len(cols) > 1:
                            vertretungen["vertretungen"].append({
                                "stunde": clean(cols[0].text),
                                "lehrer": clean(cols[1].text),
                                "fach": clean(cols[2].text),
                                "raum": clean(cols[3].text),
                                "informationen": clean(cols[4].text),
                                "art": clean(cols[5].text)
                            })
                        else:
                            vertretungen["vertretungen"].append({
                                "special_info": True,
                                "special_info_text": clean(cols[0].text)
                            })
                plan["plan"].append(vertretungen)

        infos = info_table.find_all("td", colspan="2")

        for i in infos:
            plan["informationen"].append(clean(i.text.strip(), info=True))

        return plan
