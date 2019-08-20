#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR: XYCoder
# FILE: /Users/v-sunweiwei/Desktop/saic/xyscript/xyscript/ios/gitandjira.py
# DATE: 2019/08/16 Fri
# TIME: 17:33:35

# DESCRIPTION:gitlab相关操作与jira相关操作

import os,sys,re,json
from xyscript.common.xylog import *
from xyscript.common.mail import Email

LOGNUM = 10
LASTSUCCESS = None
CURRENTSUCCESS = None

class GitLab:
    def get_all_commit_between_push(self,code_branch,package_branch,workspace,mail):
        commit_result = {}
        os.chdir(workspace)
        commit_content = "merge " + code_branch + " into " + package_branch
        log_num = self.get_num_of_need_commit(commit_content,workspace)

        result = os.popen('git log -' + str(log_num) + ' --pretty=format:"%cn<%ce>ce%cd%s" --date=iso')
        all_lines = result.readlines()
        all_commits = []
        for line in all_lines:
            info = line.split('')
            commit_info = {}
            commit_info['user'] = info[0]
            commit_info['date'] = info[2]
            commit_info['info'] = info[3].split('\n')[0]
            commit_info['email'] = info[1]
            all_commits.append(commit_info)
        
        last_commit_date = all_commits[0]['date']
        old_commit_date = all_commits[-1]['date']
        cc = all_commits[0]['email']
        # print(last_commit_date)
        # print(old_commit_date)
        submodule_commit_list = []
        submodule_list = self._get_current_config_file()
        for moduleConfig in submodule_list:
            module_path = workspace + "/" + moduleConfig["module"]
            commit_array = self.get_submodule_changes_during(module_path,old_commit_date,last_commit_date)
            if len(commit_array) > 0:
                # print(moduleConfig["module"])
                # print(commit_array)
                submodule_commit_list.append({'name':moduleConfig["module"],'commit_log':commit_array})
        
        
        commit_result['cc'] = cc
        commit_result['project_name'] = workspace.split('/')[-1]
        commit_result['start_time'] = last_commit_date
        commit_result['end_time'] = old_commit_date
        commit_result['code_branch'] = code_branch
        commit_result['package_branch'] = package_branch
        commit_result['shell'] = all_commits
        commit_result['submodule'] = submodule_commit_list
        print(commit_result)
        Email([mail]).send_merge_result(commit_result)

    
    def get_submodule_changes_during(self,workspace,start_time,end_time):
        os.chdir(workspace)
        # print(workspace)
        result = os.popen('git log --date=iso --before="'+ end_time +'" --after="' + start_time + '" --pretty=format:"%cn<%ce>%cd%s"')
        all_lines = result.readlines()
        # print(all_lines)
        all_commits = []
        for line in all_lines:
            info = line.split('')
            commit_info = {}
            commit_info['user'] = info[0]
            commit_info['date'] = info[1]
            commit_info['info'] = info[2].split('\n')[0]
            all_commits.append(commit_info)
        return all_commits

    def _get_current_config_file(self):
        file = open("ProjConfig.json")
        moduleConfigList = json.load(file)
        return moduleConfigList
    
    def get_jira_url_with_commit(self,commit_info):
        pass

    def get_num_of_need_commit(self,content,workspace):
        global LOGNUM
        global LASTSUCCESS
        global CURRENTSUCCESS
        os.chdir(workspace)
        result = os.popen('git log -' + str(LOGNUM) + ' --pretty=format:"%cn<%ce>%cd%s"')
        all_lines = result.read()

        content_num = all_lines.count(content)
        # print(LOGNUM)
        # print(content_num)

        # merge = re.compile('Merge\: ([a-z0-9]{7,})+([\t ]*)+([a-z0-9]{7,})')
        # merge_result = merge.findall(all_lines)
        # merge_num = len(merge_result)
        if content_num >=2:
            CURRENTSUCCESS = True
        else:
            CURRENTSUCCESS = False

        if LASTSUCCESS == True and CURRENTSUCCESS:
            LOGNUM = LOGNUM - 1
        elif LASTSUCCESS == False and CURRENTSUCCESS:
            return LOGNUM
        elif LASTSUCCESS == True and not CURRENTSUCCESS:
            return LOGNUM + 1
        elif LASTSUCCESS == False and not CURRENTSUCCESS:
            LOGNUM = LOGNUM + 1
        elif LASTSUCCESS is None and CURRENTSUCCESS:
            LOGNUM = LOGNUM - 1
        elif LASTSUCCESS is None and not CURRENTSUCCESS:
            LOGNUM = LOGNUM + 1

        LASTSUCCESS = CURRENTSUCCESS
        return self.get_num_of_need_commit(content,workspace)


    def printf(self,num):
        print (" " + str(num) + " ")


if __name__ == "__main__":
    GitLab().get_all_commit_between_push(code_branch='Develop',package_branch='zuche-test',workspace='/Users/v-sunweiwei/Desktop/saic/ios-shell-passenger',mail='m187221031340@163.com')
    # test = None
    # print(test == False)
    # print('--pretty=format:\"\%cn<\%ce>\%cd\%s\"')