#-*- coding: utf-8 -*-
__author__  = "8034.com"
__date__    = "2018-10-22"

import xmind
import os

class Parse(object):
    def parse_xmind(self, xmind_file):
        w = xmind.load(xmind_file)
        s1=w.getPrimarySheet() # get the first sheet
        # print(s1.getTitle())
        r1=s1.getRootTopic() # get the root topic of this sheet
        topics_l01 = r1.getSubTopics() 

        case=dict(group="",title="",priority="",pestep="",step="",expect="",remarks="",upload=u"是")
        # print("\t%(group)s, %(title)s, %(priority)s, %(pestep)s, %(step)s, %(expect)s, %(remarks)s, %(upload)s"% case)
        
        for topic_case_group in topics_l01:
            topic_case_group_name = topic_case_group.getTitle()# case group 
            case["group"]=topic_case_group_name
            # print(topic_case_group_name)
            topics_case_title = topic_case_group.getSubTopics()
            if (not topics_case_title ):break
            for topic_case_title in topics_case_title:
                topic_case_title_name=topic_case_title.getTitle()  # case title
                case["title"]=topic_case_title_name
                count_case_num = 1
                topics_case_mainstep = topic_case_title.getSubTopics() 
                if (not topics_case_mainstep ):break
                for topic_case_mainstep in topics_case_mainstep:
                    topic_case_mainstep_name=topic_case_mainstep.getTitle() # case mainstep 
                    topic_case_pestep_name = u""
                    if topic_case_mainstep.getNotes():
                        topic_case_pestep_name=topic_case_mainstep.getNotes().getContent() # case pestep 
                    case["pestep"]=topic_case_pestep_name
                    topics_case_substep = topic_case_mainstep.getSubTopics() 
                    if (not topics_case_substep ):break
                    for topic_case_substep in topics_case_substep:
                        topic_case_substep_name = topic_case_substep.getTitle() # case substep
                        topic_case_priority_name = u"中"
                        if topic_case_substep.getMarkers():
                            topic_case_priority_name = topic_case_substep.getMarkers()[0].getMarkerId() # # case priority
                            if topic_case_priority_name: 
                                print(type(topic_case_priority_name))
                                topic_case_priority_name = self.switch_priority(topic_case_priority_name)
                                pass 
                        case["priority"]= topic_case_priority_name
                        case["step"]= self.fit_step(topic_case_mainstep_name,topic_case_substep_name)
                        topics_case_expect = topic_case_substep.getSubTopics() 
                        if (not topics_case_expect ):break
                        for topic_case_expect in topics_case_expect:
                            topic_case_expect_name=topic_case_expect.getTitle() # case expect 
                            case["expect"]=topic_case_expect_name
                            topics_case_remarks_name = u""
                            if topic_case_expect.getNotes():
                                topics_case_remarks_name = topic_case_expect.getNotes().getContent()
                            case["remarks"] = topics_case_remarks_name
                            topics_case_upload = topic_case_expect.getSubTopics()
                            if (topics_case_upload and topics_case_upload[0].getTitle()==u"不上传"): # case upload  
                                case["upload"]=u"否"
                            else:
                                case["upload"]=u"是"
                            entity_case=case.copy()
                            if (count_case_num > 1):
                                entity_case["title"] ="%s: %s"%(self.fit_title(entity_case["title"], count_case_num), topic_case_substep_name) 
                                pass
                            count_case_num = count_case_num+1
                            yield entity_case
                            # print(json.dumps(entity_case).decode('unicode-escape'))

    def switch_priority(self,xmind_priority):
        if (xmind_priority == "priority-1"):
            return u"高"
        elif (xmind_priority == "priority-2"): 
            return u"中"
        elif (xmind_priority == "priority-3"): 
            return u"低"
        else:
            return  u"中"
    
    def fit_step(self, mainstep,substep):
        separator = "\n"+ "="*10+ "\n"
        full_step = mainstep + separator + substep
        return full_step

    def fit_title(self, title, num):
        return title + u" 组用例-%d"%(num)
    def file_extension(self, path): 
        return os.path.splitext(path)[1] 

    pass
    