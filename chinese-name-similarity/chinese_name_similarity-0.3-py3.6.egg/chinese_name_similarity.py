import pandas as pd
import numpy as np
import Levenshtein  #pip install python-Levenshtein
import opencc  #pip install opencc-python-reimplemented

# 異體字
variant_mapping = {'啓':'啟','爲':'為','艷':'豔','裡':'裏','沉':'沈','晒':'曬','灑':'洒','祕':'秘','臺':'台','抬':'擡','檯':'台','梁':'樑','溼':'濕','汙':'污','闊':'濶','敘':'敍','峰':'峯','群':'羣','遍':'徧','匯':'滙','床':'牀','鋪':'舖','脣':'唇','蹤':'踪','蔥':'葱','憩':'憇','舉':'擧','鬥':'鬪','朵':'朶','卻':'却','腳':'脚','飆':'飇','秌':'秋','晳':'晰','咊':'和','飃':'飄','嶋':'島','𣑯':'桃','够':'夠','畧':'略','鵞':'鵝','讐':'讎','庵':'菴','霸':'覇','柏':'栢','背':'揹','杯':'盃','并':'併','鉢':'缽','布':'佈','册':'冊','厠':'廁','鏟':'剷','嘗':'嚐','場':'塲','耻':'恥','厨':'廚','糍':'餈','村':'邨','吊':'弔','叠':'疊','妒':'妬','珐':'琺','鰐':'鱷','况':'況','斂':'歛','渺':'淼','昵':'暱','娘':'孃','咽':'嚥','肴':'餚','鷄':'雞','捆':'綑','删':'刪','姗':'姍','栅':'柵','膳':'饍','膻':'羶','尸':'屍','謚':'諡','竪':'豎','嘆':'歎','掏':'搯','鑒':'鑑','奸':'姦','减':'減','杆':'桿','秆':'稈','雇':'僱','挂':'掛','鈎':'鉤','館':'舘','涌':'湧','恿':'慂','韵':'韻','衆':'眾','凶':'兇','綉':'繡','銹':'鏽','踪':'蹤','泄':'洩','糕':'餻','琅':'瑯','汚':'污','馱':'䭾','托':'託','潜':'潛','强':'強','棱':'稜','剋':'尅','届':'屆','灾':'災','蝎':'蠍','嫻':'嫺','綫':'線','厢':'廂','彦':'彥'}

# 相似字
similar_mapping = {'珮佩姵','偉瑋煒暐緯','祐佑','宥侑','庭廷','柏伯','宸辰','弘泓宏','紘竑','均鈞','璇嫙旋','琬婉','宛菀','螢瑩','翰瀚漢','亦羿奕弈','珊姍','俊峻竣駿','茿筑','臻蓁','諺彥','琪淇','建健','峰鋒','皓浩晧','萱宣','瑄暄煊','瑤媱','涵函','惠蕙','瑜愉媮渝','瑀禹','于予'}

# 簡轉繁
def cc_convert(string):
    cc = opencc.OpenCC('s2t')
    return cc.convert(string)

# 取代異體字
def replace_variants(string):
    '''Replace the variant words in Chinese according to input dictionary'''
    for v_word1, v_word2 in variant_mapping.items():
        if v_word1 in string:
            string = string.replace(v_word1, v_word2)
    return string

# 比對相似字 
def similar_name(string1,string2):
    '''If input name and target name have similar word, return 1 '''
    for i in similar_mapping:    
        for index, j  in enumerate(string1):
            if j in i:
                if string2[index] in i and string2[index] != j:
                    return 1

def chinese_name_similarity(string1, string2):
    string1 = cc_convert(string1)
    string2 = cc_convert(string2)

    string1 = replace_variants(string1)
    string2 = replace_variants(string2)
    
    jaro = Levenshtein.jaro_winkler(string1, string2)
    ratio = Levenshtein.ratio(string1, string2) 
    score = (jaro + ratio) /2
    
    if similar_name(string1,string2):
        score = score + (1-score)*0.7
    return score