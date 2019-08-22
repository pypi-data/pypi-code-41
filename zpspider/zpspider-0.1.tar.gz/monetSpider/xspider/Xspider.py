# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

from monetSpider.utils.xml import *


class Head:

    def __init__(self,xsid,name,description):
        self.xsid=xsid
        self.name=name
        self.description=description

class Param:

    def __init__(self,name="",label="",type="string",format=None,size=None,value=None,defaultValue=None,notNull=True,begin=None,end=None,step=None):
        self.name=name
        self.label=label
        self.type=type
        self.format=format
        self.value=value
        self.defaultValue=defaultValue
        self.notNull=notNull
        self.begin=begin
        self.end=end
        self.step=step



class DataCol:
    def __init__(self,name="",label="",type="string",defaultValue=None,size=None,format=None,notNull=True):
        self.name=name
        self.label=label
        self.type=type
        self.defaultValue=defaultValue
        self.size=size
        self.format=format
        self.notNull=notNull
    pass

class Pageextractor:
    def __init__(self,name="",dataStored=True,jsonRegex=None,sampleUrl=None,type="html",urlRegex=None,links=None,setcols=None,regions=None):
        self.name=name
        self.dataStored=dataStored
        self.jsonRegex=jsonRegex
        self.sampleUrl=sampleUrl
        self.type=type
        self.urlRegex=urlRegex
        self.link=links
        self.setcol=setcols
        self.region=regions


class Region:
    def __init__(self,name,label,xpath,regex,setcols,links):
        self.name=name
        self.label=label
        self.xpath=xpath
        self.regex=regex
        self.setcols=setcols
        self.links=links


class Node:
    def __init__(self, xpath,regex, format ):
        self.xpath=xpath
        self.regex=regex
        self.format=format


class SetCol(Node):
    def __init__(self,ref,xpath,regex,format):
        super(SetCol,self).__init__(xpath,regex,format)
        self.ref=ref


class Link(Node):
    def __init__(self,name,label,xpath,regex,format):
        super(Link,self).__init__(xpath,regex,format)
        self.name=name
        self.label=label



class Config:
    def __init__(self,agent=0,cookie="",urlcharset="utf-8",charset="utf-8",sleepInterval="1000",antiVerfiedCodeType="auto",poolSize=2,threadNum=5,timeOut=10000,retryTimes=2,cycleRetryTimes=2,incrementParam=None):
        self.agent=agent
        self.cookie=cookie
        self.urlcharset=urlcharset
        self.charset=charset
        self.sleepInterval=sleepInterval
        self.antiVerfiedCodeType=antiVerfiedCodeType
        self.poolSize=poolSize
        self.threadNum=threadNum
        self.retryTimes=retryTimes
        self.cycleRetryTimes=cycleRetryTimes
        self.incrementParam=incrementParam
    # def __setattr__(self, key, value):
    #
    #     self.__dict__[key] = value
    #     print("k:"+key  )


class IncrementParam:
    def __init__(self,key=None,value=None):
        self.key=key
        self.value=value

class Xspider():

    # def __init__(self, root):
    #     self.root = root
    #     self.__head()
    #     self.__params()
    #     self.__entryUrls()
    #     self.__datastructures()
    #     self.__pageextractors()
    #     self.__config()

        # TODO 从xspider解析得到scrapy spider所需的参数

    def __init__(self, path):
        self.str=read_file_as_str(path)
        tree=readfromxml(path)
        self.root = tree.getroot()
        self.__head()
        self.__params()
        self.__entryUrls()
        self.__datastructures()
        self.__pageextractors()
        self.__config()
        self.dict=xmlstrtodict(self.str)
        self.makeurl_settings = self.dict["xspider"]["body"]["entry"]
        self.parse_settings = self.dict["xspider"]["body"]["pageextractors"]
        self.datastructure=self.dict["xspider"]["body"]["datastructure"]
        # self.notNullColNameList=self.getNotNullColName()
        #TODO 解析获取start_url的功能
    '''
    head 
    '''
    def __findhead(self):
        return find_node(self.root, "head")

    def __head(self):
        self.head=Head(self.__xsid(),self.__name(),self.__description())

    def __xsid(self):
        return find_node(self.__findhead(), "xsid")

    def __name(self):
        return find_node(self.__findhead(), "name")

    def __description(self):
        return find_node(self.__findhead(), "description")

    '''
    body
    '''
    def __findbody(self):
        return find_node(self.root, "body")
    '''
    entry
    '''
    def __findentry(self):
        return find_node(self.root, "body/entry")

    def __entryUrls(self):
        self.entryUrls=[]
        for entry in find_nodes(self.__findentry(),"entryUrls/entryUrl"):
            self.entryUrls.append(entry.text)

    def __params(self):
        self.params=[]
        for node in find_nodes(self.__findentry(), "params/param"):
            self.params.append(Param(node.attrib.get("name",""),label=node.attrib.get("label",None)))


    '''
    datastructure
    '''
    def __datastructures(self):
        self.datacol=[]
        for node in find_nodes(self.__findbody(), "datastructure/col"):
            self.datacol.append(DataCol(node.attrib.get("name",""),label=node.attrib.get("label",None)))

    def getNotNullColName(self):
        list=[]
        for col in self.datastructure.get("col"):
            if str(col.get("@notNull",False)).__eq__("true"):
                list.append(col.get("@name"))
        return list
    '''
    pageextractors
    '''
    def __findpageextractors(self):
        return find_node(self.root, "body/pageextractors")

    def __pageextractors(self):
        self.pageextractors=[]
        for node in  find_nodes(self.__findpageextractors(), "pageextractor"):
            regions=self.__regions(node)
            setcols=self.__setcols(node)
            links=self.__links(node)
            self.pageextractors.append(Pageextractor(name=node.attrib.get("name",""),dataStored=node.attrib.get("dataStored",True),
                                                     jsonRegex=node.attrib.get("jsonRegex",None),sampleUrl=node.attrib.get("sampleUrl",None),
                                                     type=node.attrib.get("type","html"),urlRegex=node.attrib.get("urlRegex",None),
                                                     links=links,setcols=setcols,regions=regions))
    '''
    
    '''
    def __regions(self,element):
        regions=[]
        for node in find_nodes(element, "region"):
            setcols = self.__setcols(node)
            links = self.__links(node)
            regions.append(Region(node.attrib.get("name",None),node.attrib.get("label",None),node.attrib.get("xpath",None),node.attrib.get("regex",None),setcols=setcols,links=links))
        return regions

    def __setcols(self,element):
        setcols = []
        for node in find_nodes(element, "setcol"):
            setcols.append(SetCol(node.attrib.get("ref",None),node.attrib.get("xpath",None),node.attrib.get("regex",None),node.attrib.get("format",None)))
        return setcols

    def __links(self,element):
        links = []
        for node in find_nodes(element, "link"):
            links.append(Link(node.attrib.get("name",""),node.attrib.get("label",""), node.attrib.get("xpath",""), node.attrib.get("regex",""), node.attrib.get("format","")))
        return links

    '''
    config
    '''
    def __config(self):
        node=find_node(self.root, "body/config")
        self.config=Config(agent=node.find("agent").text,urlcharset=node.find("urlcharset").text,
                           charset=node.find("charset").text,sleepInterval=node.find("sleep").text,antiVerfiedCodeType=node.attrib.get("anti-verified-code","auto"),
                           poolSize=node.find("poolSize").text,threadNum=node.find("threadNum").text,timeOut=node.find("timeOut").text,
                           retryTimes=node.find("retryTimes").text,cycleRetryTimes=node.find("cycleRetryTimes").text,
                           incrementParam=IncrementParam(node.attrib.get("key",None),node.attrib.get("value",None)))

    # def __setattr__(self, key, value):
    #
    #     self.__dict__[key] = value
    #     print("k:"+key  )
    #     pass
    def elementstr(self):
        return str(ET.tostring(self.root, encoding='utf-8', method='xml'), "utf-8")

    # def json(self):
    #     return xmltojson(self.elementstr())




if __name__ == "__main__":
    # tree = readfromxml("./a.xml")
    # root = tree.getroot()
    # treestr=tostring(tree, encoding='utf8', method='xml')
    # print(str(ET.tostring(root, encoding='utf-8', method='xml'), "utf-8"))

    xspider=Xspider("../../xml/a.xml")
    # print(xspider.xsid())
    # print(xspider.entryUrls())
    print(xspider.entryUrls)
    print(xspider.params[1].name)
    print(xspider.params[1].label)
    print(xspider.datacol)
    print(xspider.pageextractors[0].name)
    print(xspider.pageextractors[0].link)
    print(xspider.pageextractors[0].region)
    print(xspider.pageextractors[0].region[0].setcols[0].ref)

    print(xspider.config.poolSize)
    xspider.config.poolSize = 100
    print(xspider.config.poolSize)

    # print(xspider.elementstr())








