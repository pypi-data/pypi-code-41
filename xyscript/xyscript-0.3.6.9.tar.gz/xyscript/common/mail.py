#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from email.mime.image import MIMEImage 
from email.header import Header
from email.mime.base import MIMEBase
from email.utils import parseaddr,formataddr
from xyscript.source.html import diagnosemail_body, diagnosemail_header,mergemail_body
from xyscript.source.image import jsonfileicon
import base64,os

mail_host = "smtp.163.com"  # 设置服务器
mail_user = "idouko@163.com"  # 用户名
mail_pass = "XYCoder02"  # 三方邮箱口令
sender = 'idouko@163.com'# 发送者邮箱
receivers = ['m18221031340@163.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

class Email():
    def __init__(self,receiver=None):
        global receivers
        # print(receiver)
        if receiver is not None and len(receiver) > 0:
            receivers = receiver
        # print (receivers)
        # print(receivers)

    def send_package_email(self,success,url=None,image=None):
        global receivers
        string = ""
        if success:
            string = "您好！\n      项目打包成功，详情如下：\n 项目地址：%s\n打包分支：%s\n打包平台：%s\n打包网络环境：%s\n版本号：%s\n编译号：%s\n" %(address,branch,platform,env,version,build)
        else:
            string = "您好！\n      项目打包失败，请注意查看错误日志！信息如下：\n项目地址：%s\n打包分支：%s\n打包平台：%s\n打包网络环境：%s\n版本号：%s\n编译号：%s\n" %(address,branch,platform,env,version,build)
        Email(receivers).sendemail(string,"此邮件来自自动化打包","iOS项目组",image='/Users/v-sunweiwei/Downloads/timg.jpeg')

    def send_diagnose(self,git_objc=None):
        global receivers
        
        content_string = diagnosemail_body.format(project_url=git_objc['project_url']
                                                ,project_name=git_objc['project_name']
                                                ,user_name=git_objc['user_name']
                                                ,branch_name=git_objc['branch_name']
                                                ,commit_content=git_objc['commit_content']
                                                ,commit_url=git_objc['commit_url']
                                                ,commit_id=git_objc['commit_id']
                                                ,date=git_objc['date']
                                                ,result=git_objc['result']
                                                ,result_detail=git_objc['result_detail'])
        content = "<!DOCTYPE html><html lang=\"en\">" +  diagnosemail_header + content_string + "</html>"
        content = content.replace('\n','').encode("utf-8")

        image_name = 'jsonfileicon' + '.png'
        tmp = open(image_name, 'wb')
        tmp.write(base64.b64decode(jsonfileicon))
        tmp.close()
# 抄送人
        cc = None
        if git_objc['cc'] is not None:
            cc = git_objc['cc']

        Email(receivers).sendemail(None,"此邮件来自代码自动诊断","iOS项目组",cc=cc,htmltext=content,image=image_name,filepath=git_objc['file_path'])
        os.remove(image_name)

    def send_merge_result(self,merge_result):
        global receivers
        
        content_string = mergemail_body.format(project_name=merge_result['project_name']
                                                ,package_branch=merge_result['package_branch']
                                                ,end_time=merge_result['end_time']
                                                ,start_time=merge_result['start_time'])

        shell_array = merge_result['shell']
        submodule_array = merge_result['submodule']
        shell_dom = ''
        for shell in shell_array:
            shell_dom = shell_dom + '<tr><td>'+ shell['user'] +'</td><td>'+ shell['date'] +'</td><td>'+ shell['info'] +'</td><td>&nbsp;</td></tr>'
            content_string.replace('<&shell_list&>',shell_dom)

        sub_dom = ''
        for sub in submodule_array:
            sub_dom = sub_dom + '<H3>' + sub['name'] + '</H3>'
            sub_commit_dom = '<tr class="table-header" style="background-color: gray"><td>提交人</td><td>提交时间</td><td>提交内容</td><td>备注</td></tr>'
            for sub_commit in sub['commit_log']:
                sub_commit_dom = sub_commit_dom + '<tr><td>'+ sub_commit['user'] +'</td><td>'+ sub_commit['date'] +'</td><td>'+ sub_commit['info'] +'</td><td>&nbsp;</td></tr>'
            sub_commit_dom = '<table class="result_table_shell" >' + sub_commit_dom + '</table>'
            sub_dom = sub_dom + sub_commit_dom
            content_string.replace('<&submodule_list&>',shell_dom)
        
        content = "<!DOCTYPE html><html lang=\"en\">" +  diagnosemail_header + content_string + "</html>"
        content = content.replace('\n','').encode("utf-8")

        cc = None
        if merge_result['cc'] is not None:
            cc = merge_result['cc']

        Email(receivers).sendemail(None,"此邮件来自代码自动诊断","iOS项目组",cc=cc,htmltext=content)

    def get_html_text(self,html_path):
        with open(html_path,'r') as f:
            # print(f.read())
            content = f.read()
            self.sendemail(None,"此邮件来自代码自动诊断","iOS项目组",htmltext=content,image='/Users/v-sunweiwei/Desktop/saic/xyscript/xyscript/source/img/jsonfileicon.png',filepath='/Users/v-sunweiwei/Desktop/extension/人力图.jpg')


    def sendemail(self, content ,subject, form_name, cc=None ,htmltext=None ,image=None , filepath=None):
        """
        发送邮件
        content 正文文本
        subject 副标题
        form_name 邮件来源文本
        cc
        htmltext 网页
        image 图片
        filepath 附件
        """
        global receivers
        
        subject = subject#邮件来源
        #构建信息体
        message = MIMEMultipart('alternative') 
        
        #下面的主题，发件人，收件人，日期是显示在邮件页面上的。
        message['From'] = formataddr([form_name, sender])
        message['To'] = ";".join(receivers)
        message['Subject'] = Header(subject, 'utf-8')#编码方式
        if cc != None:
            message["Cc"] = ";".join(cc.split(','))
            receivers = receivers + cc.split(',')
            print(receivers)

        #构造文字内容   
        text = content    
        text_plain = MIMEText(text,'plain', 'utf-8')    
        message.attach(text_plain)    

        if image != None:
            #构造图片链接
            sendimagefile=open(image,'rb').read()
            image = MIMEImage(sendimagefile)
            image.add_header('Content-ID','<image1>')
            image["Content-Disposition"] = 'attachment; filename="testimage.png"'
            message.attach(image)

        if htmltext != None:
            #构造html
            #发送正文中的图片:由于包含未被许可的信息，网易邮箱定义为垃圾邮件，报554 DT:SPM ：<p><img src="cid:image1"></p>
            message.attach(MIMEText(htmltext,'html','utf-8')) 


        if filepath != None:
            #构造附件
            sendfile=open(filepath,'rb').read()
            text_att = MIMEText(sendfile, 'base64', 'utf-8') 
            text_att["Content-Type"] = 'application/octet-stream'  
            #以下附件可以重命名成aaa.txt  
            file_name = (filepath.split("/")[-1])
            text_att["Content-Disposition"] = 'attachment; filename="%s"' %(file_name)
            text_att.add_header('Content-ID','<file1>')
            #另一种实现方式
            # text_att.add_header('Content-Disposition', 'attachment', filename='aaa.txt')
            #以下中文测试不ok
            #text_att["Content-Disposition"] = u'attachment; filename="中文附件.txt"'.decode('utf-8')
            message.attach(text_att)  

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
            smtpObj.quit()
        except smtplib.SMTPException as e:
            print("Error: 无法发送邮件" + str(e))

if __name__ == "__main__":
    # Email('m18221031340@163.com').send_package_email(False)
    # Email('m18221031340@163.com').send_diagnose('/Users/v-sunweiwei/Desktop/saic/iosTestDemo/build/reports/report.json','content')
    # Email(['m18221031340@163.com'])
    # Email().get_html_text('/Users/v-sunweiwei/Desktop/saic/xyscript/xyscript/source/htmlx/diagnosemail.html')
    Email().sendemail('这是一封来自财务的报表邮件','你','财务部',cc='m13451923928@163.com,786857294@qq.com',htmltext="<h1>test</h1>")
    # Email().send_diagnose()
