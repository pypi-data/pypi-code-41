#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from xyscript.common.xylog import *
import webbrowser
from git import Repo
import re
from xyscript.common.mail import Email

class OCLint:
    def check_oclint(self):
        result = os.popen("which oclint")
        path = result.read()
        if len(path) <= 0:
            printandresult("brew tap oclint/formulae")
            printandresult("brew install oclint")
        else:
            successlog("the path of oclint is:" + path) 

    def check_xcpretty(self):
        result = os.popen("which xcpretty")
        path = result.read()
        if len(path) <= 0:
            printandresult("gem install xcpretty")
        else:
           successlog("the path of xcpretty is:" + path) 

    def run_oclint(self,git_objc=None):
        try:
            
            self.check_oclint()
            self.check_xcpretty()
            path = os.getcwd()
            path = "/Users/v-sunweiwei/Desktop/saic/ios-shell-driver"

            os.chdir(path)
            printandresult("xcodebuild clean")

            # printandresult("xcodebuild | tee xcodebuild.log")

            printandresult("xcodebuild | xcpretty -r json-compilation-database")
            printandresult("cp build/reports/compilation_db.json build/reports/compile_commands.json")
            reports_path = path + "/build/reports"
            os.chdir(reports_path)
            printandresult("oclint-json-compilation-database -e Pods \
                                                             -e DerivedSources \
                                                             -- \
                                                             -disable-rule=LongLine \
                                                             -rc=LONG_VARIABLE_NAME=30 \
                                                             -rc=NCSS_METHOD=100 \
                                                             -max-priority-1=100000 \
                                                             -max-priority-2=100000 \
                                                             -max-priority-3=100000 \
                                                             >> report.json")
            html_path = "file://" + reports_path + "/report.json"
            file_path = reports_path + "/report.json"
            print(file_path)
            # webbrowser.open_new_tab(html_path)

            if git_objc is None:
                printandresult("open " + reports_path + "/report.json")
            else:
                mail_addresses = self._get_lastest_push_user_mail(path)
                # html_path = '/Users/v-sunweiwei/Desktop/saic/ios-shell-driver/build/reports/report.json'
                push_item = self._get_push_info(path)
                diagnose_detail = self._get_diagnose_result_detail(file_path)
                diagnose = self._get_diagnose_result(diagnose_detail)

                diagnose_result = 'warning:' +  str(diagnose['warning']) + ' lines,' + 'OCLint Report:' + diagnose['report']

                content = "项目名称：%s\n提交人：%s\n提交时间：%s\n诊断结果为：%s\n详细说明见附件：" %(push_item['name'],push_item['user'],push_item['date'],diagnose_result)
                
                git_objc['project_name'] = push_item['name']
                git_objc['user_name'] = push_item['user']
                git_objc['date'] = push_item['date']
                git_objc['result'] = diagnose_result
                git_objc['result_detail'] = diagnose_detail
                git_objc['file_path'] = file_path
                
                Email(mail_addresses).send_diagnose(git_objc)

        except BaseException as error:
            faillog("run diagnose failed:" + format(error))
    
    def _get_diagnose_result_detail(self,file_path):
        with open(file_path, encoding='utf-8') as file_obj:
            contents = file_obj.read()
            return contents

    def _get_diagnose_result(self,file_obj):
        result = {}
        warnings_array = [1,1,1]
        warnings = re.findall(r'Compiler Warnings\:((?:.|\n)*?OCLint Report)',file_obj)
        if warnings and len(warnings)>0 :
            warnings_array =  warnings[0].split('\n')
        result['warning'] = len(warnings_array) -3

        oclint_report = re.findall(r'Summary\:((?:.|\n)*?)\n',file_obj)
        if oclint_report and len(oclint_report)>0:
            result['report'] = str(oclint_report[0])[1:-1]
        else:
            result['report'] = ''
        return result
    
    def _get_push_info(self,workspace):
        push_item = {}
        repo = Repo(workspace)
        result =  repo.git.show('--stat')
        # 项目名称
        project_name = (workspace.split("/")[-1]).split(".")[0]
        push_item['name'] = project_name

        # 提交人
        user = re.findall(r'Author\:((?:.|\n)*?)<',result)
        if user and len(user)>0:
            psuh_user = user[0]
            psuh_user = psuh_user.replace(' ','')
            push_item['user'] = psuh_user

        # 提交时间
        date = re.findall(r'Date:((?:.|\n)*?)\n',result)
        if date and len(date)>0:
            push_date = date[0]
            push_date = push_date.replace('   ','')
            push_item['date'] = push_date
        
        return push_item




    def _get_lastest_push_user_mail(self,workspace):
        repo = Repo(workspace)
        result =  repo.git.show('--stat')

        authors = []
        res = re.findall(r'Author\:((?:.|\n)*?>)',result)
        for author in res:
            res = re.findall(r'((?<=\<)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,8}(?=\>))',author)
            for mail_address in res:
                authors.append(mail_address)
        # print(authors)
        return authors

def main():
    OCLint().run_oclint()
    # OCLint()._get_diagnose_result('/Users/v-sunweiwei/Desktop/saic/ios-shell-driver/build/reports/report.json')

if __name__ == "__main__":
    main()
