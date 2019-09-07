# -*- coding: utf-8 -*-

import os.path
from os import listdir

import simplejson as json
import subprocess

from .tagme import Tagme
from .babelfy import Babelfy
from .freme_ner import Freme_NER
from .aida import Aida

null = None

class WikitableWrapper:  
    
    def __init__(self, max_r = None):
        if max_r == None:
            self.maxRows = 1
        else:
            self.maxRows = max_r
        
        self.includeBabelfy = True
        self.includeTagme = True
        self.includeFremeNer = True
        self.includeAida = False
        self.includeDBpediaSpotlightLocal = False
        
        self.createHtmlFile = False
        
        self.tagme = Tagme("EN")
        self.babelfy = Babelfy("EN")
        self.freme = Freme_NER("EN")
        self.aida = Aida("EN")
        
        self.outputFolder = None # path to store the html
        self.AnnotateSameNoAnnotatedMentions = True # Annotate those surface forms in the same work that have not been annotated in some cases.
        self.KeepCurrentAnnotations = True  # Create an aditional JsonTable, keeping the current annotations from the Json and adding the annotations of the systems that do not introduce inconsisteces with them.
        self.showProgress = True
        
        
    def cleanHeader(self, txt):
        return txt.split("@")[0].strip(" \t\n\r").lower()
    
    def parserHtml(self,text_):
        text = text_.replace("<br>"," ")
        text = text.replace("<br/>"," ")
        state = 0
        t = ""        
        p = -1
        while (p+1 < len(text)):
            p = p + 1
            ch = text[p]
            
            if state == 0:
                if ch == "<":
                    state = 1
                else:
                    t = t + ch
                    
            elif state == 1:
                if ch == ">":
                    state = 0
        t = t.replace(";",",")
        return t
    
    
    #for each html tag <a href="..">..</a> return a dict with the ini,fin and uri of it
    def parserHtmlATag(self,text):
        text = text.replace("<br>"," ")
        text = text.replace("<br/>"," ")
        
        state = 0
        R = []
        t = ""
        t_ini = 0
        l = 0
        
        p = -1
        while (p+1 < len(text)):
            p = p + 1
            ch = text[p]
            #print("----- >("+ch+")","p:",p,"state:",state,"t:",t,"  t_ini:",t_ini,"  l:",l)
            if state == 0: # fw html tags
                if ch == "<":
                    state = 1
                    t = ""
                else:
                    #t = t + ch
                    t_ini = t_ini + 1
            
            
            elif state == 1: # <a href???
                if (ch == "a") and ( p+2<len(text) ) and (text[p+1] in [" ","\r", "\n", "\t"]):
                    state = 2
                else: state = 10
                
            
            elif state == 2: # href??
                if ch == "h" and text[p:p+4] == "href":
                    p = p+3
                    state = 3
                elif ch==">":
                    state = 0
                elif ch=="'":
                    state = 100
                elif ch=='"':
                    state = 102
            
            elif state == 3: # init of url in href?
                if ch=='"':
                    state = 4                    
                    
                
            elif state == 4: # url
                if ch=='"':
                    state = 5 
                else:
                    t = t + ch
                    
            elif state == 5: # fw end of <a..'>'
                if ch==">":
                    state = 6
                    l = 0
                    
            elif state == 6: # counting length of mention
                          
                if ch == "<":
                    state = 10 
                    R.append({"ini":t_ini-l, "fin":t_ini, "url":t.strip("/. \t\r\n").split("/")[-1]})
                else:
                    l = l + 1      
                    t_ini = t_ini+1
                    
            
            elif state == 10:
                if ch == ">":
                    state = 0
                    
            elif state == 100:
                if ch == "'":
                    state = 2
                elif ch=="\\":
                    state = 1000
            elif state == 102:
                if ch == '"':
                    state = 2
                elif ch=="\\":
                    state = 1002
            elif state == 1000:
                state = 100
            elif state == 1002:
                state = 102
        return R



    
    #for each html tag <a href="..">..</a> return a dict with the ini,fin and uri of it
    def parserHtmlATagWithLabel(self,text):
        text = text.replace("<br>"," ")
        text = text.replace("<br/>"," ")
        state = 0
        R = []
        t = ""
        t_ini = 0
        l = 0
        label = ""
        
        p = -1
        while (p+1 < len(text)):
            p = p + 1
            ch = text[p]
            #print(p,ch,"state:",state,t)
            if state == 0: # fw html tags
                if ch == "<":
                    state = 1
                    t = ""
                else:
                    #t = t + ch
                    t_ini = t_ini + 1
            
            
            elif state == 1: # <a href???
                if (ch == "a") and ( p+2<len(text) ) and (text[p+1] in [" ","\r", "\n", "\t"]):
                    state = 2
                else: state = 10
                
            
            elif state == 2: # href??
                if ch == "h" and text[p:p+4] == "href":
                    p = p+3
                    state = 3
                elif ch==">":
                    state = 0
                elif ch=="'":
                    state = 100
                elif ch=='"':
                    state = 102
            
            elif state == 3: # init of url in href?
                if ch=='"':
                    state = 4                    
                    
                
            elif state == 4: # url
                if ch=='"':
                    state = 5 
                else:
                    t = t + ch
                    
            elif state == 5: # fw end of <a..'>'
                if ch==">":
                    state = 6
                    l = 0
                    label = ""
                    
            elif state == 6: # counting length of mention
                          
                if ch == "<":
                    state = 10 
                    R.append({"ini":t_ini-l, "fin":t_ini, "url":t.strip("/. \t\r\n").split("/")[-1], "label":label})
                else:
                    l = l + 1      
                    t_ini = t_ini+1
                    label = label + ch
                    
            
            elif state == 10:
                if ch == ">":
                    state = 0
                    
            elif state == 100:
                if ch == "'":
                    state = 2
                elif ch=="\\":
                    state = 1000
            elif state == 102:
                if ch == '"':
                    state = 2
                elif ch=="\\":
                    state = 1002
            elif state == 1000:
                state = 100
            elif state == 1002:
                state = 102
        return R
    
    #parsing a cell result: The <a href="./Social_status">status</a> is <a href="./Same-sex_marriage">Marriage</a>
    def parserResult(self,text):
        state = 0
        tempState = -1
        p = -1
        while (p+1 < len(text)):
            p = p + 1
            ch = text[p]            
            #print(p,ch,"state:",state,tempState)
            if state == 0: # 
                if ch == "T":
                    state = 1
                elif ch == "<":
                    state = 101
                    tempState = 0
            
            elif state == 101:
                if ch == ">":
                    state = tempState
            
            elif state == 1:
                if ch == "h":
                    state = 2
                elif ch == "<":
                    state = 101
                    tempState = 1
                else: state = 0
                
            elif state == 2:
                if ch == "e":
                    state = 3
                elif ch == "<":
                    state = 101
                    tempState = 2
                else: state = 0
                
            elif state == 3:
                if ch == " " or ch == "\r" or ch == "\t" or ch == "\n":
                    state = 4
                elif ch == "<":
                    state = 101
                    tempState = 3
                else: state = 0
                
            elif state == 4:
                if ch == " " or ch == "\r" or ch == "\t" or ch == "\n":
                    pass
                elif ch == "<":
                    state = 5
                else: state = 10
                
            elif state == 5:
                if ch == ">":
                    state = 51

            elif state == 51:
                if ch == ">":
                    state = 6
            
            elif state == 6:
                if ch == " " or ch == "\r" or ch == "\t" or ch == "\n":
                    pass
                elif ch == "i":
                    state = 7
                else: 
                    #No es seguido por 'is'
                    return text[p:].split(" is ")[-1].rstrip(" \t\r\n")
                
            elif state == 7:
                if ch == "s":
                    state = 8
                else: state = 0
                
            elif state == 8:
                if ch == " " or ch == "\r" or ch == "\t" or ch == "\n":
                    pass
                else:
                    return text[p:].rstrip(" \t\r\n")
                
            elif state == 10:
                if ch == " " or ch == "\r" or ch == "\t" or ch == "\n":
                    state = 6
        return ""
                
        
    
    def html2plain(self, txt):
        return txt.split("@")[0]
    
    
    
    def title(self,t):
        if len(t)>=1:
            return t[0].upper() + t[1:]
        return ""
    
    
    def createCSS(self,_outputFolder):
        path = _outputFolder.rstrip(" \t\r\n"+os.sep) + os.sep + "css"
        if not os.path.isdir(path):
            try:  
                os.mkdir(path)
            except OSError:  
                print ("Creation of the directory %s failed" % path)
            else:  
                print ("Successfully created the directory %s " % path)
            
            fhtml = open(_outputFolder.rstrip(" \t\r\n"+os.sep) + os.sep + "css"+ os.sep+"tabl.css", mode="w")
            fhtml.write(self.css())           
            fhtml.close()
    

    def processJson(self,filename):
        #print("--> self.maxRows:",self.maxRows)
        if os.path.isfile(filename):
            finput = open(filename,mode="r")
            content = "".join(finput.readlines())
            tab = eval(content)

            if tab["htmlMatrix"]  == None:
                os.system("echo "+filename+" >> errors.log")
                return
            
            #writting input table in html format if it is required
            if self.createHtmlFile:
                fhtml = open(self.filename2standard(filename.replace(".json",".html")), mode="w")
                #
                tab_ = dict([it for it in tab.items()])
                tab_["htmlMatrix"] = []
                
                isHead = True
                for row in tab["htmlMatrix"]:
                    row_ = []
                    for cell in row:
                        Tags = self.parserHtmlATagWithLabel(cell)
                        cell_ = self.parserHtml(cell)
                        
                        T_sorted = sorted(Tags, key=lambda x:x["ini"], reverse=True)
                        for r in T_sorted:
                            n = 17 + len(r["url"])
                            cell_ = cell_[:r["ini"]] + '<a href="./'+r["url"]+'">'+cell_[r["ini"]:r["fin"]]+'</a>' + cell_[r["fin"]:]
                        if isHead:
                            row_.append("<th>"+cell_+"</th>")
                        else:
                            row_.append("<td>"+cell_+"</td>")

                    isHead = False
                    tab_["htmlMatrix"].append(row_)
                
                #
                html = self.getTableHTML(tab_)
                fhtml.write(html)           
                fhtml.close()
                
                #--     
                if self.outputFolder != None:                  
                    self.createCSS(self.outputFolder)

            if tab["tableType"] == "WELL_FORMED":
                # -- title
                article_title = tab["articleTitle"].strip("  \t\n\r.")
                table_title = tab["title"].strip("  \t\n\r.")
                
                if len(table_title) == 0:
                    table_title = article_title
                
                if len(article_title) == 0:
                    article_title = table_title
                
                # -- headers
                #colHeaders = [self.cleanHeader(x) for x in tab["colHeaders"]]
                colHeaders = [self.parserHtml(x) for x in tab["htmlMatrix"][0]]

                # -- rows
                rows = tab["htmlMatrix"][1:]
                #rows = tab["htmlMatrix"][27:] ##---------------- ojoooooooooooo
                
                
                max_r = int(len(rows)/self.maxRows)
                if (len(rows)%self.maxRows>0):
                    max_r = max_r + 1
                
                Sentences = {}
                RTable = {}
                #self.chunch2RawSentence = {}
                RTagme = {}                
                RBabelfy = {}
                RFreme = {}
                RAida = {}
                
                RDBpediaSpotlightLocal = {}
                self.OffsetCellsValues = {}
                self.OffsetCellsEnds = {}
                self.OffsetSentenceDelimiter = {}
                
                jump_first = False
                for chunck_i in range(max_r): 
                    sentence = article_title + ". "+ table_title + ". "
                    sentence_with_tags = article_title + ". "+ table_title + ". "
                    self.OffsetCellsValues[chunck_i] = []
                    self.OffsetCellsEnds[chunck_i] = []
                    self.OffsetSentenceDelimiter[chunck_i] = [len(sentence)]
                    
                    for row_i in range(chunck_i*self.maxRows, (chunck_i+1)*self.maxRows):
                        
                        if row_i >= len(rows): 
                            break
                        row = rows[row_i]
                        for cell_i in range(len(row)):
                            cell = row[cell_i].strip(" \t\n\r")
                            parcedCell = self.title(self.parserHtml(cell))
                            
                            columnHeader = colHeaders[cell_i]
                            if (len(columnHeader)==0):
                                columnHeader = "entity"
                            
                            if len(parcedCell) != 0:
                                sentence = sentence + "The "+columnHeader+" is "
                                self.OffsetCellsValues[chunck_i].append(len(sentence))
                                sentence = sentence + parcedCell
                                self.OffsetCellsEnds[chunck_i].append(len(sentence))
                                sentence = sentence + "; "
                                sentence_with_tags = sentence_with_tags + "The "+columnHeader+" is "+cell+"; "
                            else:
                                self.OffsetCellsValues[chunck_i].append(len(sentence))
                                self.OffsetCellsEnds[chunck_i].append(len(sentence))
                                sentence = sentence + "; "
                                sentence_with_tags = sentence_with_tags +"; "
                        
                        self.OffsetSentenceDelimiter[chunck_i].append(len(sentence))
                        sentence = sentence[:-2] + ". "
                        sentence_with_tags = sentence_with_tags[:-2] + ". "
                        
                    # --
                    Sentences[chunck_i] = sentence
                    #self.chunch2RawSentence[chunck_i] = sentence_with_tags
                    
                    # -- anchor texts  -- a href tags
                    if self.KeepCurrentAnnotations:
                        RTable[chunck_i] = self.parserHtmlATag(sentence_with_tags)  
                        sentTEst = self.parserHtml(sentence_with_tags)
                    
                    #-- Systems
                    if (self.includeTagme):
                        #print("-> tagme")
                        rtagme = self.tagme.annotate(sentence)
                        RTagme[chunck_i] = rtagme
                    
                    if (self.includeBabelfy):
                        #print("-> babelfy")
                        rbabelfy = self.babelfy.annotate(sentence)
                        RBabelfy[chunck_i] = rbabelfy
                        
                    if (self.includeFremeNer):
                        #print("-> freme")
                        rfreme = self.freme.annotate(sentence)
                        RFreme[chunck_i] = rfreme
                        
                    if (self.includeAida):
                        #print("aida")
                        raida = self.aida.annotate(sentence)
                        RAida[chunck_i] = raida

                    if (self.includeDBpediaSpotlightLocal):
                        #print("-----db")
                        rdbspotl = self.DBpediaSpotlightLocal(sentence)
                        RDBpediaSpotlightLocal[chunck_i] = rdbspotl
                
                
                # Writting tables with new annotations
                if (self.includeTagme):
                    #print("=> tagme")
                    try:
                        self.writeNewJson(filename.replace(".json","_tagme.json"), tab, RTagme, Sentences)
                        if self.KeepCurrentAnnotations:
                            self.writeNewJson(filename.replace(".json","_tagm_keeping_annotations.json"), tab, RTagme, Sentences,RTable)
                    except:
                        print("[ERROR] TagME got an error processing %s"%(filename))
                      
                if (self.includeBabelfy):
                    #print("=> babelfy")
                    try:
                        self.writeNewJson(filename.replace(".json","_babelfy.json"), tab, RBabelfy, Sentences)
                        if self.KeepCurrentAnnotations:
                            self.writeNewJson(filename.replace(".json","_babelf_keeping_annotations.json"), tab, RBabelfy, Sentences,RTable)
                    except:
                        print("[ERROR] Babelfy got an error processing %s"%(filename))
                    
                if (self.includeFremeNer):
                    #print("=> freme")
                    try:
                        self.writeNewJson(filename.replace(".json","_fremener.json"), tab, RFreme, Sentences)
                        if self.KeepCurrentAnnotations:
                            self.writeNewJson(filename.replace(".json","_freme_keeping_annotations.json"), tab, RFreme, Sentences,RTable)
                    except:
                        print("[ERROR] FremeNER got an error processing %s"%(filename))
                    
                if (self.includeAida):
                    try:
                        self.writeNewJson(filename.replace(".json","_aida.json"), tab, RAida, Sentences)
                        if self.KeepCurrentAnnotations:
                            self.writeNewJson(filename.replace(".json","_aid_annotations.json"), tab, RAida, Sentences,RTable)
                    except:
                        print("[ERROR] AIDA got an error processing %s"%(filename))
                
                if (self.includeDBpediaSpotlightLocal):
                    try:
                        self.writeNewJson(filename.replace(".json","_dbpst.json"), tab, RDBpediaSpotlightLocal, Sentences)
                        if self.KeepCurrentAnnotations:
                            self.writeNewJson(filename.replace(".json","_dbps_keeping_annotations.json"), tab, RDBpediaSpotlightLocal, Sentences,RTable)
                    except:
                        print("[ERROR] DBpedia Spotlight got an error processing %s"%(filename))

                
            finput.close()
        else:
            print("[Warning] '%s' file does not exist"%filename)
    
    
    # return if annotation "a_" is in the sentences number "i__" of "offSetS_"
    def sameRow(self, i__, offsetS_, a_):
        return (i__ == len(offsetS_)-1  and  offsetS_[i__]<=a_["ini"]) or (i__ < len(offsetS_)-1  and  offsetS_[i__]<=a_["ini"] and a_["ini"]  <= offsetS_[i__+1])
    
    # Here I check if the annotation '_a' include text from the text used to build the sentence and the cell of the table.
    # For example, the sentence "The No. is 1.; The Title is "Amala and Kamala" (instrumental);" could be annotated as 
    # ---he No. <a href="./IS_tank_family">is 1</a>.; The <a href="./Arabic_name">Title</a> is "<a href="./Amala_and_Kamala">Amala and Kamala</a>" (<a href="./Instrumentalism">instrumental</a>); The <a href="./Vowel_length">Length</a> is 1:56.---
    #
    # In this case, "is" is a text included in the sentence, and 1 is part of the content of the table. So, this function detetct if the current annotation have this problem
    def isThereConflict(self,_a,_offsetC,_offsetE,_offsetS,_cantColumn):
        for _i_ in range(len(_offsetS)):
            if self.sameRow(_i_,_offsetS,_a):
                for _j_ in range(_cantColumn):
                    pj = _i_*_cantColumn + _j_
                    if (_offsetC[pj]<=_a["ini"] and _a["ini"]  <= _offsetE[pj]) and (_offsetC[pj]<=_a["fin"] and _a["fin"]  <= _offsetE[pj]):  
                        return False
        return True
    
    
    # if ann overlaps with any of the annotations of _R. 
    # ej, ann = {'ini': 18, 'fin': 41, 'url': 'United_States'}
    def existOverlapping(self,_ann,_R,sent_=None):
        ini = _ann["ini"]
        fin = _ann["fin"]
        for _r in _R:
            if (not (    ( (_r["ini"]<ini and _r["ini"]<fin) and (_r["fin"]<ini and _r["fin"]<fin) )   or   
                        ( (ini<_r["ini"] and ini<_r["fin"]) and (fin<_r["ini"] and fin<_r["fin"]) )  )):
                return True;
        return False
    
    
    # if ann overlaps with any of the annotations of _R. 
    # ej, ann = {'ini': 18, 'fin': 41, 'url': 'United_States'}
    # if number_row!= None, then check this contrain in this row
    def existOverlappingSameRow(self,_ann,_R, number_row_, offsetS_):
        ini = _ann["ini"]
        fin = _ann["fin"]
        for _r in _R:
            if number_row_ == None or self.sameRow(number_row_, offsetS_, _r):
                if (not (    ( (_r["ini"]<ini and _r["ini"]<fin) and (_r["fin"]<ini and _r["fin"]<fin) )   or   
                            ( (ini<_r["ini"] and ini<_r["fin"]) and (fin<_r["ini"] and fin<_r["fin"]) )  )):
                    return True;
        return False
    #
    def writeNewJson(self, filename, tab, RSystem, Sentences, RTable=None):
        ## --
        newTab = dict([it for it in tab.items()])
        newTab["htmlMatrix"] = []
        
        ## adding heading
        head = []
        for x in [self.parserHtml(x) for x in tab["htmlMatrix"][0]]:#tab["colHeaders"]:
             column = self.cleanHeader(x)
             head.append('<th>'+self.title(column)+'</th>')
        newTab["htmlMatrix"].append(head)
        cantColumn = len(head)
        
        ## rows
        for chunck_i in RSystem:
            if RSystem[chunck_i] == None:
                print("[WARNING] file %s was not stored"%(filename))
                return False
            sent = Sentences[chunck_i]
            offsetC = [x for x in self.OffsetCellsValues[chunck_i]]
            offsetE = [x for x in self.OffsetCellsEnds[chunck_i]]
            offsetS = [x for x in self.OffsetSentenceDelimiter[chunck_i]]
            
            ## -- Prioritizing annotations form RTable
            R = []
            if self.KeepCurrentAnnotations == True and RTable!=None:                
                R = [x for x in RTable[chunck_i]]# if self.OffsetCellsValues[chunck_i][0]<x["ini"]]
                for rr in R:
                    rr["label"] = sent[rr["ini"]:rr["fin"]]

                for r in RSystem[chunck_i]:
                    if not self.existOverlapping(r,R,sent):
                        R.append(r)
            else:
                R = [x for x in RSystem[chunck_i]]            
            R_ = self.onlyMaximalAnnotations([x for x in R if x["ini"]!=x["fin"]])
            
            # --
            if self.AnnotateSameNoAnnotatedMentions:
                R_sorted = sorted(R_, key=lambda x:x["ini"], reverse=False)
                _R = []
                for _r in R_sorted:
                    if not self.isThereConflict(_r,offsetC,offsetE,offsetS,cantColumn): 
                        #e.g., an annotation that starts in one sentence and ends in the next one.
                        _R.append(_r)
                
                # Finding if there is any word no annotated, but which was annotated in other position in the same row
                R_ex = []
                R_news = []
                current_s = 0
                Set_ = set([tuple([x["ini"],x["fin"]]) for x in _R])
                for _r in _R:
                    # -- search only in its sentence, poping until arrive to the current row
                    while (not self.sameRow(current_s,offsetS,_r)) and (current_s+1 < len(offsetS)) :
                        current_s = current_s + 1
                    
                    if current_s+1 == len(offsetS):
                        break
                    
                    this_sent = sent[offsetS[current_s]:offsetS[current_s+1]]                    
                    label = sent[_r["ini"]:_r["fin"]]
                    
                    
                    pnew = this_sent.find(label)
                    bbb = True
                    u  = 0
                    while (pnew != -1):
                        
                        u = u +1
                        i_ = offsetS[current_s] + pnew
                        j_ = offsetS[current_s] + pnew+len(label)
                        
                        if not (i_,j_) in Set_:
                            if not self.existOverlappingSameRow({"ini":i_,"fin":j_},_R + R_news,current_s,offsetS):
                                R_news.append({"ini":i_, "fin":j_,"url":_r["url"]})
                                Set_.add((i_, j_))
                            
                        old_pnew = pnew + len(label)
                        pnew = this_sent[old_pnew:].find(label) + old_pnew
                        if old_pnew-1 == pnew:
                            break
                R_ = _R + R_news
            
            # Generating sentence with annotations
            R_sorted = sorted(R_, key=lambda x:x["ini"], reverse=True)
            for r in R_sorted:
                #if self.isThereConflict(r,offsetC,offsetE,offsetS,cantColumn): 
                #    #e.g., an annotation that starts in one sentence and ends in the next one.
                #    continue
                n = 17 + len(r["url"])
                sent = sent[:r["ini"]] + '<a href="./'+r["url"]+'">'+sent[r["ini"]:r["fin"]]+'</a>' + sent[r["fin"]:]
                offsetC = [((x+n) if x>r["ini"] else x) for x in offsetC]
                offsetE = [((x+n) if x>r["ini"] else x) for x in offsetE]
                offsetS = [((x+n) if x>r["ini"] else x) for x in offsetS]

            for r_i in range(len(offsetS)):
                if r_i+1 == len(offsetS): 
                    continue

                final_row = []
                for c_i in range(cantColumn):#range(len(offsetC)):
                    p_val_ini = offsetC.pop(0)
                    p_val_fin = offsetE.pop(0)
                    new_cell = sent[p_val_ini:p_val_fin]
                    final_row.append("<td>" + new_cell + "</td>")

                newTab["htmlMatrix"].append(final_row)

        ftemp = open(self.filename2standard(filename), "w")
        ftemp.write(json.dumps(newTab, separators=(',', ':'), sort_keys=False))
        ftemp.close()
        
        # creating html if required
        if self.createHtmlFile:
            fhtml = open(self.filename2standard(filename.replace(".json",".html")), "w")
            html = self.getTableHTML(newTab)
            fhtml.write(html)
            fhtml.close()
        return True
            
    def filename2standard(self, fil_):
        if self.outputFolder != None:
            return self.outputFolder.rstrip(" \t\r\n"+os.sep) + os.sep + fil_.split(os.sep)[-1]
        return fil_
        
    
    def getTableHTML(self,tab_):
        cssfile = '<link href="css/tabl.css" rel="stylesheet"/>'
        html_ = '<html>\n<head>\n<title>'+tab_["articleTitle"].strip("  \t\n\r.")+'</title>\n'+cssfile+'\n<meta charset="utf-8" />\n</head>\n<body>\n<table>\n'
        for rr in tab_["htmlMatrix"]:
            html_ = html_ + '  <tr>\n'
            for td in rr:
                html_ = html_ + '    '+td.replace("./","https://en.wikipedia.org/wiki/").replace("href=",'target="_blank" href=')+"\n"
            html_ = html_ + '  </tr>\n'
        html_ = html_ + '</table>\n</body>\n</html>'
        return html_

  
    def getSamePosition(self,tag,v,A):
        L_ = []
        for a in A:
            if a[tag] == v:
                L_.append(a)
        return L_

    def onlyMaximalAnnotations(self, R_): # non-overlapping
        final = []
        
        oldpos = -1
        _R = sorted(R_, key=lambda x:x["ini"], reverse=False)
        for i in range(len(_R)):
            r = _R[i]
            if r["ini"] > oldpos:
                L = self.getSamePosition("ini", r["ini"],_R)
                L_s = sorted(L, key=lambda x:x["fin"], reverse=True)
                final.append(L_s[0])
                oldpos = r["fin"]            
        
        return final
    
    def DBpediaSpotlightLocal(self,text):
        try:
            self.param_confidence = 0.3
            self.param_support = 20
            p = subprocess.Popen(
                ['curl', '-H', 
                 'Accept: application/json',
                 #'Accept: text/html', 
                 'http://localhost:2222/rest/annotate', 
                 '--data-urlencode', 'text=%s' % text, 
                 '--data', 'confidence='+str(self.param_confidence), '--data', 'support='+str(self.param_support)
                 ], 
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                                    
            stdout, stderr = p.communicate()

            if stdout:
                list_response = eval(stdout)
                R_out = []
                for entity in list_response['Resources']:
                    if "@URI" in entity:
                        last_part_url = entity["@URI"].split("/")[-1]
                        label = entity["@surfaceForm"]  
                        ini = int(entity["@offset"])
                        fin = ini + len(label)
                        R_out.append({"ini":ini, "fin":fin, "url":last_part_url})
                return R_out
        except Exception as err:
            print(err)
            return None
        return None
    
    # Here, I search all the files in a folder and apply the function ProcessJson.
    # Additionally, I generate a html page with the summary
    def ProcessFolderOfJson(self, folderIn, folderOut, skipUntilThisFile=None):
        tempOut = self.outputFolder
        self.outputFolder = folderOut
        html_page = """<html>
<head>
   <meta charset="utf-8" />
   <title>Summary</title>
   
   <style>
        
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
            
        }
        
        .redLabel {
            display: inline;
            padding: .2em .4em .2em;
            line-height: 1;
            background-color: #dc3545;
            color: #fff;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: .90em;
            cursor:pointer;
        }
        
            
        /* The Modal (background) */
        .modal {
            display: none; /* Hidden by default */
            position: fixed; /* Stay in place */
            z-index: 1; /* Sit on top */
            padding-top: 100px; /* Location of the box */
            left: 0;
            top: 0;
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            overflow: auto; /* Enable scroll if needed */
            background-color: rgb(0,0,0); /* Fallback color */
            background-color: rgba(0,0,0,0.4); /* Black w/ opacity */
        }

        /* Modal Content */
        .modal-content {
            background-color: #fefefe;
            margin: auto;
            padding: 20px;
            border: 1px solid #888;
            width: 80%;
        }

        /* The Close Button */
        .close {
            color: #aaaaaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
        }

        .close:hover,
        .close:focus {
            color: #000;
            text-decoration: none;
            cursor: pointer;
        }
        
        .hide{
            display:none;
        }
   </style>
   
    <script>
        startF = function(){
            var modal = document.getElementById('myModal');
            var span = document.getElementsByClassName("close")[0];
            var list = document.getElementsByClassName("redLabel");
            for (var i = 0; i < list.length; i++) {
                var btn = list[i];
                btn.onclick = function() {
                    modal.style.display = "block";
                    var content = document.getElementById('modal_content');
                    var sys = this.getAttribute("sys"); 
                    content.innerHTML = echoError(sys);
                }                
            }

            document.onkeydown = function(evt) {
                evt = evt || window.event;
                var isEscape = false;
                if ("key" in evt) {
                    isEscape = (evt.key === "Escape" || evt.key === "Esc");
                } else {
                    isEscape = (evt.keyCode === 27);
                }
                if (isEscape) {
                    modal.style.display = "none";
                }
            };
                
            span.onclick = function() {
                modal.style.display = "none";
            }

            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }
        }
    </script>
</head>


<body onload="startF();">

        """
        if not os.path.isdir(folderIn):
            print("[Error] The is not folder <%s>"%(folderIn))
            return
        
        if not os.path.isdir(folderOut):
            print("[Error] The is not folder <%s>"%(folderOut))
            return
        
        sys2errors = {}
        
        html_page = html_page + "<table>\n"
        
        
        #-- Header
        html_page = html_page + "    <tr>\n"
        html_page = html_page + "      <th></th>\n"
        html_page = html_page + "      <th> <i>table</i> </th>\n"
        if (self.includeTagme):
            html_page = html_page + '      <th id="headTagME"> TagME <span id="headTagME_label"  sys="TagME" class="redLabel">0</span></th>\n'
        sys2errors["TagME"] = []
        
        if (self.includeBabelfy):
            html_page = html_page + '      <th id="headBabelfy"> Babelfy <span id="headBabelfy_label" sys="Babelfy" class="redLabel">0</span></th>\n'
        sys2errors["Babelfy"] = []
            
        if (self.includeFremeNer):
            html_page = html_page + '      <th id="headFremeNER"> FremeNER <span id="headFremeNER_label" sys="FremeNER" class="redLabel">0</span></th>\n'
        sys2errors["FremeNER"] = []
            
        if (self.includeAida):
            html_page = html_page + '      <th id="headAIDA"> AIDA <span id="headAIDA_label" sys="AIDA" class="redLabel">0</span></th>\n'
        sys2errors["AIDA"] = []
        
        if (self.includeDBpediaSpotlightLocal):
            html_page = html_page + '      <th id="headDBpediaSp"> DBpediaSp <span id="headDBpediaSp_label" sys="DBpediaSp" class="redLabel">0</span></th>\n'
        sys2errors["DBpediaSp"] = []
        
        html_page = html_page + "    </tr>\n"
        
        #-- 
        Nbr = 0
        ListOfFiles = listdir(folderIn)
        nListOfFiles = len(ListOfFiles)
        for filename_ in ListOfFiles:                
            if filename_[-5:] != ".json": 
                continue
            
            Nbr = Nbr +1
            
            if skipUntilThisFile != None:
                if filename_ == skipUntilThisFile:
                    skipUntilThisFile = None
                if self.showProgress:
                    print(Nbr,"/",nListOfFiles,"---->",filename_,"(skipped)")
                continue
            if self.showProgress:
                print(Nbr,"/",nListOfFiles,"---->",filename_)
            filepath = os.path.join(folderIn.rstrip(" \t\r\n"+os.sep), filename_)
            
            _filename_ = filename_.split(os.sep)[-1]
            td_html = ''
            
            if self.createHtmlFile:
                finput = open(folderIn.rstrip(" \r\n\t"+os.sep)+os.sep+filename_,mode="r")
                content = "".join(finput.readlines())
                tab = eval(content)

                if tab["htmlMatrix"]  == None:
                    os.system("echo "+filename_+" >> errors.log")
                    continue
            
                fhtml = open(self.filename2standard(filename_.replace(".json",".html")), mode="w")
                html = self.getTableHTML(tab)
                try:
                   fhtml.write(html)           
                except:
                    os.system("echo "+filename_+" >> errors.log")
                    continue
                fhtml.close()

            if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json",".html")):
                td_html = '&nbsp;[<a target="_blank" href="'+filename_.replace(".json",".html")+'">html</a>]'
            
            html_page = html_page + "    <tr>\n"
            html_page = html_page + "      <td>"+str(Nbr)+"</td>\n"
            html_page = html_page + "      <td>"+_filename_+td_html+"</td>\n"
            
            #try:
            self.processJson(filepath)
            #except:
            #    pass
            
            #---
            if (self.includeTagme):
                td_json = ''
                if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_tagme.html")):
                    td_json = '[<a target="_blank" href="'+filename_.replace(".json","_tagme.html")+'">html</a>]'
                td_html = ''
                if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_tagme.json")):
                    td_html = '[<a target="_blank" href="'+filename_.replace(".json","_tagme.json")+'">json</a>]'     
                else:
                    sys2errors["TagME"].append(filename_)
                
                if self.KeepCurrentAnnotations:
                    td_json_k = ''
                    if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_tagm_keeping_annotations.html")):
                        td_json_k = '[<a target="_blank" href="'+filename_.replace(".json","_tagm_keeping_annotations.html")+'">k_html</a>]'
                    td_html_k = ''
                    if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_tagm_keeping_annotations.json")):
                        td_html_k = '[<a target="_blank" href="'+filename_.replace(".json","_tagm_keeping_annotations.json")+'">k_json</a>]'
                    
                    html_page = html_page + '      <td>'+td_json+td_html+td_json_k+td_html_k+'</td>\n'
                else:
                    html_page = html_page + '      <td>'+td_json+td_html+'</td>\n'
            
            #---
            if (self.includeBabelfy):
                td_json = ''
                if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_babelfy.html")):
                    td_json = '[<a target="_blank" href="'+ filename_.replace(".json","_babelfy.html")+'">html</a>]'
                td_html = ''
                if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_babelfy.json")):
                    td_html = '[<a target="_blank" href="'+filename_.replace(".json","_babelfy.json")+'">json</a>]'
                else:
                    sys2errors["Babelfy"].append(filename_)
                
                if self.KeepCurrentAnnotations:
                    td_json_k = ''
                    if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_babelf_keeping_annotations.html")):
                        td_json_k = '[<a target="_blank" href="'+ filename_.replace(".json","_babelf_keeping_annotations.html")+'">k_html</a>]'
                    td_html_k = ''
                    if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_babelf_keeping_annotations.json")):
                        td_html_k = '[<a target="_blank" href="'+filename_.replace(".json","_babelf_keeping_annotations.json")+'">k_json</a>]'
                    html_page = html_page + '      <td>'+td_json+td_html+td_json_k+td_html_k+'</td>\n'
                else:
                    html_page = html_page + '      <td>'+td_json+td_html+'</td>\n'
            
            #---
            if (self.includeFremeNer):
                td_json = ''
                if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_fremener.html")):
                    td_json = '[<a target="_blank" href="'+filename_.replace(".json","_fremener.html")+'">html</a>]'
                td_html = ''
                if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_fremener.json")):
                    td_html = '[<a target="_blank" href="'+filename_.replace(".json","_fremener.json")+'">json</a>]'     
                else:
                    sys2errors["FremeNER"].append(filename_)
                
                if self.KeepCurrentAnnotations:
                    td_json_k = ''
                    if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_freme_keeping_annotations.html")):
                        td_json_k = '[<a target="_blank" href="'+filename_.replace(".json","_freme_keeping_annotations.html")+'">k_html</a>]'
                    td_html_k = ''
                    if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_freme_keeping_annotations.json")):
                        td_html_k = '[<a target="_blank" href="'+filename_.replace(".json","_freme_keeping_annotations.json")+'">k_json</a>]'  
                    html_page = html_page + '      <td>'+td_json+td_html+td_json_k+td_html_k+'</td>\n'
                else:
                    html_page = html_page + '      <td>'+td_json+td_html+'</td>\n'
            
            
            #---
            if (self.includeAida):
                td_json = ''
                if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_aida.html")):
                    td_json = '[<a target="_blank" href="'+filename_.replace(".json","_aida.html")+'">html</a>]'
                td_html = ''
                if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep)+os.sep+filename_.replace(".json","_aida.json")):
                    td_html = '[<a target="_blank" href="'+filename_.replace(".json","_aida.json")+'">json</a>]'
                else:
                    sys2errors["AIDA"].append(filename_)
                
                if self.KeepCurrentAnnotations:
                    td_json_k = ''
                    if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_freme_aid_annotations.html")):
                        td_json_k = '[<a target="_blank" href="'+filename_.replace(".json","_freme_aid_annotations.html")+'">k_html</a>]'
                    td_html_k = ''
                    if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep)+os.sep+filename_.replace(".json","_freme_aid_annotations.json")):
                        td_html_k = '[<a target="_blank" href="'+filename_.replace(".json","_freme_aid_annotations.json")+'">k_json</a>]'
                    html_page = html_page + '      <td>'+td_json+td_html+td_json_k+td_html_k+'</td>\n'
                else:
                    html_page = html_page + '      <td>'+td_json+td_html+'</td>\n'
            
            
            #---
            if (self.includeDBpediaSpotlightLocal):
                td_json = ''
                if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_dbpst.html")):
                    td_json = '[<a target="_blank" href="'+filename_.replace(".json","_dbpst.html")+'">html</a>]'
                    
                td_html = ''
                if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_dbpst.json")):
                    td_html = '[<a target="_blank" href="'+filename_.replace(".json","_dbpst.json")+'">json</a>]'  
                else:
                    sys2errors["DBpediaSp"].append(filename_)

                if self.KeepCurrentAnnotations:
                    td_json_k = ''
                    if os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_dbps_keeping_annotations.html")):
                        td_json_k = '[<a target="_blank" href="'+filename_.replace(".json","_dbps_keeping_annotations.html")+'">k_html</a>]'
                        
                    td_html_k = ''
                    if self.createHtmlFile and os.path.isfile(folderOut.rstrip(" \t\r\n"+os.sep) +os.sep+filename_.replace(".json","_dbps_keeping_annotations.json")):
                        td_html_k = '[<a target="_blank" href="'+filename_.replace(".json","_dbps_keeping_annotations.json")+'">k_json</a>]'  
                    html_page = html_page + '      <td>'+td_json+td_html+td_json_k+td_html_k+'</td>\n'
                else:
                    html_page = html_page + '      <td>'+td_json+td_html+'</td>\n'
                
            html_page = html_page + "    </tr>\n"
            

        html_page = html_page + "</table>\n\n";
        
        html_page = html_page + "<script>\n";
        
        sys2included = {
            "TagME": self.includeTagme,
            "Babelfy": self.includeBabelfy,
            "FremeNER": self.includeFremeNer,
            "AIDA": self.includeAida,
            "DBpediaSp": self.includeDBpediaSpotlightLocal
        }
        
        for k in sys2errors:
            if sys2included[k]:
                cantErrors = len(sys2errors[k])
                if cantErrors == 0:
                    html_page = html_page +'    document.getElementById("head'+k+'_label").classList.add("hide");\n';
                else:
                    html_page = html_page +'    document.getElementById("head'+k+'").innerHTML = \''+k+' <span id="head'+k+'_label"  sys="'+k+'" class="redLabel">'+str(cantErrors)+'</span>\';\n';

        html_page = html_page + "\n    echoError = function(sys){\n";
        
        for k in sys2errors:
            cantErrors = len(sys2errors[k])
            if cantErrors != 0:
                html_page = html_page + '        if (sys=="'+k+'"){\n';
                html_page = html_page + '            return "<h3>"+sys+" fails for the next tables</h3>"';
                
                for err in sys2errors[k]:
                    html_page = html_page + '+\'&nbsp;&nbsp;<a target="_blank" href="'+err.replace(".json",".html")+'">'+err.replace(".json","")+'</a>\'';
                html_page = html_page + ";\n        }\n"                
            
        html_page = html_page +"""    
        return '<i>No error found</i>';
    }
</script>

<!-- The Modal -->
<div id="myModal" class="modal">

    <!-- Modal content -->
    <div class="modal-content" style="overflow:auto">
        <span class="close">&times;</span>
        <div id="modal_content">
            <p>Some text in the Modal..</p>
        </div>
    </div>

</div>
"""
            
        
        html_page = html_page + "</body></html>"
        fpage = open(os.path.join(folderOut, "Summary.html"), "w")
        fpage.write(html_page)
        fpage.close()
        
        self.outputFolder = tempOut
        
    
    def css(self):
        return """
th {
    padding-top: 11px;
    padding-bottom: 11px;
    background-color: #4CAF50;
    color: white;
}

tr:hover {
  background-color: lightblue!important;
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
    
}

td:hover::after,
th:hover::after {
  content: "";
  position: absolute;
  background-color: lightblue!important;
  left: 0;
  top: -5000px;
  height: 10000px;
  width: 100%;
  z-index: -1;
}


tr:nth-child(odd){ 
  background: #ddd;
}




blockquote {
  background: #f9f9f9;
  border-left: 10px solid #ccc;
  margin: 1.5em 10px;
  padding: 0.5em 10px;
}

blockquote p {
}

.redLabel {
            display: inline;
            padding: .2em .4em .2em;
            line-height: 1;
            background-color: #dc3545;
            color: #fff;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: .90em;
            cursor:pointer;
        }
.blueLabel {
            display: inline;
            padding: .2em .4em .2em;
            line-height: 1;
            background-color: #0058da;
            color: #fff;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: .90em;
            cursor:pointer;
        }
        
.label {
            display: inline;
            padding: .2em .4em .2em;
            line-height: 1;
            background-color: #aaa;
            color: #fff;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: .90em;
            cursor:pointer;
        }
"""
