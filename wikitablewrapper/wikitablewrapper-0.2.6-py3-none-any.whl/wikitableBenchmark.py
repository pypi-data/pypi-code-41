# -*- coding: utf-8 -*-

import os.path
from os import listdir
from .wikitableWrapper import WikitableWrapper


class WikitableBenchmark:  
    
    def __init__(self):
        self.createHtmlFile = True
        self.outputFolder = ""
        self.currentHead = []
        self.currentTitle = ""
        self.wikiPrefix = "https://en.wikipedia.org/wiki/"
        
        self.wt = WikitableWrapper()
        self.listComparison = []
        
        
        self.removeFromSysNotInGold = True # As in Gerbil
        
        self.sys2sufix = {"Babelfy":"_babelfy", "TagME":"_tagme", "FremeNER":"_fremener", "DBpedia Spotlight":"_dbpst"}
    
    
    def isSpace(self,ch_):
        return (ch_ in set([" ","\t","\r","\n"]))
    
    #I'm not using this right now
    # the diference with WikitableWrapper.parserHtmlATag is that, in this case, I keep all the html tags
    # e.g., [{'ini': 0, 'fin': 12, 'url': 'Barack_Obama'}, ...]
    def getAtag(self,cell_):
        state = 0
        p = -1
        tempPos = -1
        tempLink = ""
        tempLabel = ""
        R = []
        while (p+1 < len(cell_)):
            p = p + 1
            ch = cell_[p]            
            #print(p,ch,"state:",state,tempState)
            if state == 0: # 
                if ch == "<":
                    state = 1
            
            elif state == 1:
                if ch == "a":
                    tempPos = p
                    tempLink = ""
                    tempLabel = ""
                    state = 2                    
                elif not self.isSpace(ch):
                    #another HTML tag
                    state = 100 # wait to close this non-href tag
            
            elif state == 2:
                if ch == ">":
                    state = 1    
                elif ch == "h":
                    state = 3
                    
            elif state == 3:
                if ch == ">":
                    state = 1    
                elif ch == "r":
                    state = 4
                else:
                    state = 2
                    
            elif state == 4:
                if ch == ">":
                    state = 1    
                elif ch == "e":
                    state = 5
                else: state = 2
                    
            elif state == 5:
                if ch == ">":
                    state = 1    
                elif ch == "f":
                    state = 6
                else: state = 2
            
            elif state == 6:
                if ch == ">":
                    state = 1    
                elif ch == "=":
                    state = 7
                elif not self.isSpace(ch):
                    state = 2
                    
            elif state == 7:
                if ch == ">":
                    state = 1    
                elif ch == '"':
                    state = 8
                elif not self.isSpace(ch):
                    state = 2
                
            elif state == 8:
                if ch == '"':
                    state = 9
                else:
                    tempLink = tempLink + ch
                    
            elif state == 9:
                if ch==">":
                    state = 10                    
                    
            elif state == 10:# store label
                if ch == "<":
                    state = 100
                    R.append({'ini': tempPos, 'fin': tempPos+len(tempLabel), 'url': tempLink})
                else:
                    tempLabel = tempLabel + ch
                    
            elif state == 100:
                if ch == ">":
                    state = 0
        
        return R

                
                    
    #                                                 
    # this return a table in a list of tuples  (#row, #column, ini, fin, url) 
    # e.g., [(1, 0, 1, 13, 'Donald_Trump', 'Donald Trump'), (1, 1, 1, 4, 'United_States', 'USA')]
    def getTableFromFile(self,filename):
        T_ = []
        if os.path.isfile(filename):
            finput = open(filename,mode="r")
            content = "".join(finput.readlines())
            tab = eval(content)
            
            self.currentHead = tab["htmlMatrix"][0]
            self.currentTitle = tab["articleTitle"]
            
            for row_i in range(len(tab["htmlMatrix"])):
                if row_i == 0: 
                    continue # skipping heading
                row = tab["htmlMatrix"][row_i]
                for cell_i in range(len(row)):
                    cell = row[cell_i]
                    for r in self.wt.parserHtmlATagWithLabel(cell):
                        if len(r["label"].strip(" \t\n\r")) > 0 and len(r["url"].strip(" \t\n\r")) > 0:
                            T_.append(tuple([row_i, cell_i, r["ini"], r["fin"], r["url"], r["label"]]))

        else:
            print("[Error] file <%s> is not found")
        return T_
    
    
    def filename2name(self, fil_, outF = None):
        if outF== None and self.outputFolder!= None:
            return self.outputFolder.rstrip(" \t\r\n"+os.sep) + os.sep + fil_.split(os.sep)[-1]
        if outF!=None:
            return outF.rstrip(" \t\r\n"+os.sep) + os.sep + fil_.split(os.sep)[-1]
        return fil_


    
    
    def createMatchingTable(self, filename, _gl, prefix):
        newTab = dict([])
        newTab["htmlMatrix"] = []
        newTab["articleTitle"] = self.currentTitle

        ## adding heading
        head = []
        for column in self.currentHead:
             head.append(self.wt.title(column))
        newTab["htmlMatrix"].append(head)
        cantColumn = len(head)
        cantRow = 0
        
        ## body
        cat2labelcolor = {"tp":"blueLabel","fp":"redLabel","fn":"redLabel"}
        for _it in _gl:
            [row,col,ini,fin,url,label,cat] = _it # e.g., (1, 0, 1, 13, 'Donald_Trump', 'Donald Trump', 'tp')
            while row>=len(newTab["htmlMatrix"]):
                newTab["htmlMatrix"].append(["<td></td>"]*cantColumn)
            ann = '<span class="label"><span class="'+cat2labelcolor[cat]+'">'+cat+'</span><a target="_blank" href="'+self.wikiPrefix+url+'">'+label+'</a></span>'
            newTab["htmlMatrix"][row][col]= "<td>"+ newTab["htmlMatrix"][row][col][4:-5] + ann + "</td>"
        

        fhtml = open(self.filename2name(filename.replace(".json",prefix+".html")), "w")
        html = self.wt.getTableHTML(newTab)
        fhtml.write(html)
        fhtml.close()

        
    
        
        
    #
    # e.g., 
    # Input-> folderGold = "../in_", folderSys= "../out_"
    # Output-> [('../in_/493677_3.json', '../out_/493677_3.json'), ('../in_/495418_9.json', '../out_/495418_9.json')]
    def MeasureF1FolderOfJson(self, folderGold, folderSys, folderOut=None):

        if folderOut!=None and not os.path.isdir(folderOut):
            self.outputFolder = folderOut
        else:
            self.outputFolder = folderSys
        
        if not os.path.isdir(folderGold):
            print("[Error] The is not folder <%s>"%(folderGold))
            return None
        
        if not os.path.isdir(folderSys):
            print("[Error] The is not folder <%s>"%(folderSys))
            return None
        
        # -- Searching by all the json files with the same name in both folders: folderGold and folderSys
        sSet = set([])
        Pairs = []
        for gfilename in listdir(folderGold):
            if gfilename[-5:] == ".json":
                sSet.add(gfilename)
            else: print("[Warngin] file <%s> from the folder <%s> is not a jsons"%(gfilename, folderGold))
        
        for sfilename in listdir(folderSys):
            if sfilename[-5:] == ".json":
                if sfilename in sSet:
                    Pairs.append((folderGold.strip(" \r\t\n"+os.sep) + os.sep +sfilename,folderSys.strip(" \r\t\n"+os.sep) + os.sep +sfilename))
            else: print("[Warngin] file <%s> from the folder <%s> is not a jsons"%(sfilename, folderSys))
        
        return self.MeasureF1(Pairs)
    
    
    
    def P(self,tp,fp,fn):
        if tp + fp == 0: return 0
        return (tp/(tp + fp))
        
    def R(self,tp,fp,fn):
        if tp + fn == 0: return 0
        return (tp/(tp + fn))
    
    def F1(self,p,r):
        if p + r == 0: return 0.0
        return 2*p*r/(p + r)



    # For a given list of pair of json, compute the F1.
    # e.g., [('../in_/493677_3.json', '../out_/493677_3.json'), ('../in_/495418_9.json', '../out_/495418_9.json')]
    def MeasureF1(self, Pairs, folderOut=None, sys_sufix=None):
        if sys_sufix == None:
            sys_sufix = ""
        
        if folderOut!=None and os.path.isdir(folderOut):
            self.outputFolder = folderOut
            
        if self.createHtmlFile and folderOut!=None:
            self.wt.createCSS(self.outputFolder)
            
        
        [overalltp,overallfp,overallfn] = [0,0,0]
        for pair in Pairs:
            gl = self.getTableFromFile(pair[0])
            sy = self.getTableFromFile(pair[1])

            gl_ = []
            sy_ = []
            
            
            sSet = set(sy)
            tempSy = [x for x in sy]
            if self.removeFromSysNotInGold:
                gSet = set([(x[0],x[1],x[2],x[3]) for x in gl])
                sSet = [x for x in sy if (x[0],x[1],x[2],x[3]) in gSet]
            
            [tp,fp,fn] = [0,0,0]
            for g in gl:
                if g in sSet:
                    tp = tp + 1
                    sSet.remove(g)
                    
                    gl_.append(tuple(list(g)+["tp"]))
                    sy_.append(tuple(list(g)+["tp"]))
                else:
                    fn = fn + 1
                    gl_.append(tuple(list(g)+["fn"]))
                    
            fp = len(sSet)  
            for s_ in sSet:
                sy_.append(tuple(list(s_)+["fp"]))
            
            if self.createHtmlFile:
                self.createMatchingTable(self.filename2name(pair[0]),gl_,sys_sufix+"_gold")
                self.createMatchingTable(self.filename2name(pair[1]),sy_,sys_sufix+"_sys")
                
                final_loc_gold = self.filename2name(pair[0]).replace(".json",sys_sufix+"_gold.html")
                final_loc_sys  = self.filename2name(pair[0]).replace(".json",sys_sufix+"_sys.html")
                self.listComparison.append({
                       "gold":pair[0],
                       "sys":pair[1],
                       "contigency_gold":final_loc_gold,
                       "contigency_sys":final_loc_sys,
                       "tp":tp,
                       "fp":fp,
                       "fn":fn
                    })
            overalltp = overalltp + tp
            overallfp = overallfp + fp
            overallfn = overallfn + fn
            
        p = self.P(overalltp,overallfp,overallfn)
        r = self.R(overalltp,overallfp,overallfn)
        f = self.F1(p,r)
        return {"precision":p, "recall":r, "f1":f}
        
        
        
    def MeasureF1_and_Summarize(self,folderGold, folderSys, dSystems, folderOut):
        if folderOut!=None and not os.path.isdir(folderOut):
            self.outputFolder = folderOut
        else:
            self.outputFolder = folderSys
        
        if not os.path.isdir(folderGold):
            print("[Error] The is not folder <%s>"%(folderGold))
            return None
        
        if not os.path.isdir(folderSys):
            print("[Error] The is not folder <%s>"%(folderSys))
            return None
        
        
        L_label_systems = list(dSystems.values())
        
        # -- Searching by all the json files with the same name in both folders: folderGold and folderSys
        sSet = set([])

        T = {}
        for k in dSystems:
            sufix = dSystems[k]
            Pairs = []
            self.listComparison = []
            LL = sorted(listdir(folderSys))
            for sfilename in LL:
                if sfilename[-5:] == ".json" and sfilename.find(sufix)!=-1:
                    _fg = folderGold.rstrip(" \r\t\n"+os.sep) + os.sep +sfilename.replace(sufix+".json",".json")
                    _fs = folderSys.rstrip(" \r\t\n"+os.sep) + os.sep +sfilename

                    if not os.path.isfile(_fg):
                        print("[WARNING] file <%s> does not exist"%(_fg))
                        self.listComparison.append({"gold":None, "sys":None})
                        continue
                    
                    if not os.path.isfile(_fs):
                        print("[WARNING] file <%s> does not exist"%(_fs))
                        self.listComparison.append({"gold":None, "sys":None})
                        continue
                    
                    Pairs.append((_fg,_fs))
            
            T[k] = {"score":self.MeasureF1(Pairs,folderOut,self.sys2sufix[k]), "comparison":[x for x in self.listComparison]}
        
        
        # --- write Summary
        
        html_page = """<html>\n<head>\n   <meta charset="utf-8" />\n   <title>Benchmark</title>\n   <style>        
        th {
            padding-top: 11px;
            padding-bottom: 11px;
            color: black;
        }


        td, th{
            border: 1px solid #ddd;
            text-align: left;
            padding: 8px;
            position: relative;
        }

        table{
            font-size: 16px;
            font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            border-spacing: 0;
            overflow: hidden;
            
        }\n   </style>\n<body>\n  <h3>Benchmark</h3>\n  <table>\n    <tr>\n"""
        
        html_page = html_page + "      <th><i>System</th>\n"
        html_page = html_page + "      <th>Precision</th>\n"
        html_page = html_page + "      <th>Recall</th>\n"
        html_page = html_page + "      <th>F1</th>\n"
        html_page = html_page + "    </tr>\n"
        
        
        for k in T:
            html_page = html_page + "    <tr>\n"
            html_page = html_page + "      <td>"+k+"</td>\n"
            html_page = html_page + "      <td>"+str(round(T[k]["score"]["precision"],3))+"</td>\n"
            html_page = html_page + "      <td>"+str(round(T[k]["score"]["recall"],3))+"</td>\n"
            html_page = html_page + "      <td>"+str(round(T[k]["score"]["f1"],3))+"</td>\n"
            html_page = html_page + "    </tr>\n"
        html_page = html_page +"  </table><br>"
        
        
        #---- Details 
        # - head
        html_page = html_page + "<br><h3>Detailed Results</h3>\n"
        html_page = html_page + "  <table>\n    <tr>\n"
        html_page = html_page + "      <th></th>\n"
        html_page = html_page + "      <th><i>tables</i></th>\n"
        for k in T:
            html_page = html_page + "      <th>"+k+"</th>\n"
        html_page = html_page + "      </tr>\n"
        
        # - cells
        k_ = list(T.keys())[0]
        for i in range(len(T[k_]["comparison"])):
            html_page = html_page + "      <tr>\n"
            html_page = html_page + "        <td>"+str(i+1)+"</td>\n"
            html_page = html_page + '        <td><a target="_blank" href="'+T[k_]["comparison"][i]["gold"].split(os.sep)[-1].replace(".json",".html")+'">'+T[k_]["comparison"][i]["gold"].split(os.sep)[-1].replace(".json",".html")+'</a></td>\n'
            for k in T:
                html_page = html_page + "      <td>tp:"+str(T[k]["comparison"][i]["tp"])+" fp:"+str(T[k]["comparison"][i]["fp"])+" fn:"+str(T[k]["comparison"][i]["fn"])+"<br>"
                html_page = html_page + 'Original System Output:[<a target="_blank" href="'+T[k]["comparison"][i]["sys"].split(os.sep)[-1].replace(".json",".html")+'">'+T[k]["comparison"][i]["sys"].split(os.sep)[-1].replace(".json","")+'</a>]<br>\n'
                html_page = html_page + 'Contingency Gold:[<a target="_blank" href="'+T[k]["comparison"][i]["contigency_gold"].split(os.sep)[-1]+'">g</a>]<br>'
                html_page = html_page + 'Contingency Sys:[<a target="_blank" href="'+T[k]["comparison"][i]["contigency_sys"].split(os.sep)[-1].replace("_sys",self.sys2sufix[k]+"_sys")+'">s</a>]</td>\n'
            html_page = html_page + "      </tr>\n"
        
        
        
        html_page = html_page + "  </table>"
        
        
        html_page = html_page + "  </table>\n</body></html>"
        fpage = open(os.path.join(folderOut, "Benchmark.html"), "w")
        fpage.write(html_page)
        fpage.close()
        

