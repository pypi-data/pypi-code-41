from . import addressResource as rs
#coding:utf-8
#import addressIsStandard.jmaddress.addressResource as rs
import jieba
import jieba.analyse
import re


def addCutWord():
    for tmpword in rs.VILLAGE:
        jieba.add_word(tmpword)
    for tmpword in rs.SHORT_VILLAGE:
        jieba.add_word(tmpword)
    for tmpword in rs.ROAD_NAME:
        jieba.add_word(tmpword)
    for tmpword in rs.UNIT_NAME:
        jieba.add_word(tmpword)


MATCH1 = u'江门'
MATCH2 = u'(江门市)+'
MATCH_DIST_SHORT=u'(蓬江)|(江海)|(新会)|(台山)|(鹤山)|(开平)|(恩平)'
MATCH_DIST_WHOLE=u'(蓬江区)|(江海区)|(新会区)|(台山市)|(鹤山市)|(开平市)|(恩平市)'
MATCH_TOWN_SHORT = u'(荷塘)|(棠下)|(杜阮)|(仓后)|(堤东)|(沙尾仔)|(北街)|(环市)|(潮连)|(外海)|(礼乐)|(江南)|(滘头)|(滘北)|(大泽)|(司前)|(沙堆)|(古井)|(三江)|(崖门)|(双水)|(罗坑)|(大鳌)|(睦州)|(会城)|(雅瑶)|(古劳)|(龙口)|(桃源)|(共和)|(鹤城)|(址山)|(云乡)|(宅梧)|(双合)|(沙坪)|(大江)|(水步)|(端芬)|(四九)|(三合)|(白沙)|(冲蒌)|(斗山)|(都斛)|(赤溪)|(川岛)|(广海)|(海宴)|(汶村)|(北陡)|(深井)|(台城)|(金鸡)|(月山)|(水口)|(沙塘)|(百合)|(苍城)|(龙胜)|(马冈)|(塘口)|(赤坎)|(蚬冈)|(赤水)|(大沙)|(长沙)|(三埠)|(那吉)|(大田)|(圣堂)|(牛江)|(沙湖)|(君堂)|(大槐)|(横陂)|(良西)|(东成)|(恩城)|(东安)|(平石)'
MATCH_TOWN_IN_ROAD=u'(荷塘圩)|(棠下大道)|(杜阮北二路)|(杜阮北三路)|(杜阮北一路)|(杜阮枌榆里)|(杜阮居晏里)|(杜阮南路)|(杜阮西路)|(仓后路)|(堤东路)|(环市东路)|(环市二路)|(环市路)|(环市三路)|(环市西路)|(环市一路)|(环市中路)|(潮连大道)|(礼乐二路)|(礼乐三路)|(礼乐一路)|(江南大道)|(江南路)|(江南四路)|(古井街)|(三江大道)|(三江海峰大道)|(三江路)|(双水迎宾大道西)|(双水振兴大道)|(会城大道)|(古劳街)|(龙口大道)|(龙口里大道)|(桃源大道北)|(桃源大道南)|(桃源街)|(共和路)|(址山线)|(水步大道)|(白沙大道)|(白沙大道东)|(白沙大道西)|(白沙路)|(龙胜路)|(长沙东路)|(长沙金章大道)|(长沙西路)|(长沙中路)|(牛江江洲大道)|(牛江街)|(牛江江洲大道)|(牛江街)|(沙湖大道)|(君堂街)|(东成村)|(东成街)|(东安村大道)|(东安街)'


match1 = re.compile(MATCH1)
match2 = re.compile(MATCH2)
match_dist_short = re.compile(MATCH_DIST_SHORT)
match_dist_whole = re.compile(MATCH_DIST_WHOLE)
match_town_short = re.compile(MATCH_TOWN_SHORT)
match_town_in_road = re.compile(MATCH_TOWN_IN_ROAD)


def jugStr(source_string):
    """
    :param string: str
    :return: (tag,split_list)   return is a tuple
    @tag is 0 ,this str is standard address ,tag is -1 this str is not standard address
    @ split_list ,the origin stirng's infomations
    """
    tmp_p = None
    tmp_c = None
    tmp_d = None
    tmp_t = None
    tmp_v = None
    tmp_r = None
    tmp_u = None
    tmpstr = source_string
    if re.match(u'广东',tmpstr) is not None:
        tmp_p = '广东省'
        if len(tmpstr)>2:
            if tmpstr[2] == '省':
                tmpstr = tmpstr[3:]
            else:
                tmpstr = tmpstr[2:]
        else:
            tmpstr = ''

    # 处理江门市的信息
    if re.match(match1, tmpstr) is not None:
        tmp_c = '江门市'
        group = re.match(MATCH2, tmpstr)  # 匹配表达式匹配多个，可以剔除重复的江门市
        if group is not None:
            tmpstr = tmpstr.replace(group[0], '', 1)
    elif tmpstr != '' and tmpstr[0] == '市':  # 95
        tmpstr = tmpstr[1:]

    # 处理区的相关信息
    dist = re.match(match_dist_short, tmpstr)
    if dist is not None:
        dist_all = re.match(match_dist_whole, tmpstr)
        if dist_all is not None:  # 完整的区
            tmpstr = tmpstr[3:]
            tmp_d = dist_all[0]

    # 处理镇的相关信息
    dist = re.match(match_town_short, tmpstr)
    if dist is not None:
        if dist[0] in rs.JM_JIEDAO:
            if dist[0] in rs.JM_JIEDAO_TO_BAISHA:  # 堤东   仓后   北街 都换成了白沙街道
                tmp_t = '白沙街道'
            else:
                tmp_t = dist[0] + '街道'
        elif dist[0] != '白沙':  # 白沙在台山也存在，所以先把白沙区分开
            tmp_t = dist[0] + '镇'
        else:
            if tmp_d == '蓬江区':
                tmp_t = dist[0] + '街道'
            elif tmp_d == '台山市':
                tmp_t = dist[0] + '镇'
            else:
                tmp_t = dist[0] + '街道'

        town_name_len = len(dist[0])
        if re.match(match_town_in_road, tmpstr) is not None:  # 包含镇名字的街和路  1790
            pass
        else:
            if len(tmpstr) > 2:  # 有的名字只是镇的缩写
                if tmpstr[town_name_len] == '镇' or tmpstr[town_name_len] == '区':  # 剔除 镇   并且纠错  区
                    tmpstr = tmpstr[town_name_len + 1:]
                elif tmpstr[town_name_len] == '村':
                    if tmpstr[:town_name_len + 1] in rs.TOWN_NAME_IN_VILLAGE:
                        pass
                    else:  # 这里面是把镇写成了村的错误信息
                        tmpstr = tmpstr[town_name_len + 1:]

                elif tmpstr[town_name_len:town_name_len + 2] == '街道':  # 剔除街道  112398
                    if tmpstr[town_name_len:town_name_len + 5] == '街道办事处':  # 1623
                        tmpstr = tmpstr[town_name_len + 5:]
                    elif tmpstr[town_name_len:town_name_len + 3] == '街道办':  # 45
                        tmpstr = tmpstr[town_name_len + 3:]
                    else:  #
                        tmpstr = tmpstr[town_name_len + 2:]

                elif tmpstr[town_name_len:town_name_len + 2] != '社区':
                    tmpdist = re.match(rs.MATCH_TOWN_IN_VILLAGE, tmpstr)
                    if tmpdist is not None:  # 镇的名字在村中
                        if len(tmpstr) > 3:
                            if tmpstr[3] == '镇' or tmpstr[3] == '里':
                                if re.match(u'镇中街', tmpstr[3:]) is not None:
                                    tmpstr = tmpstr[3:]
                                else:
                                    tmpstr = tmpstr[4:]
                            else:
                                pass
                                # 如果有是村级别的 ， 留着给村来处理
                                # tmpstr = tmpstr[3:]
                        else:  # 7个 ，单独村的名字
                            pass
                            # tmpstr = tmpstr[town_name_len:]
                    else:  # 都是镇的缩写
                        if tmpstr[town_name_len] == '圩':  # 77
                            if (len(tmpstr) > town_name_len + 1):
                                if tmpstr[town_name_len + 1] == '镇':
                                    tmpstr = tmpstr[town_name_len + 2:]
                            else:
                                tmpstr = tmpstr[town_name_len + 1:]
                        elif tmpstr[town_name_len] == '路' or tmpstr[
                            town_name_len] == '街':  # 418 可能的错误信息，也有很多把街道缩写成街
                            tmpstr = tmpstr[3:]
                        else:
                            tmpstr = tmpstr[town_name_len:]
                else:  # 存在有社区和社区居委会     1
                    if tmpstr[:town_name_len + 2] in rs.TOWN_NAME_IN_VILLAGE:
                        # 是村的信息，保留给村来处理
                        pass
                    else:
                        if tmpstr[town_name_len + 2:town_name_len + 5] == '居委会':
                            tmpstr = tmpstr[town_name_len + 5:]
                        else:
                            tmpstr = tmpstr[town_name_len + 2:]

    # 开始分词处理

    if tmpstr:
        seg_list = jieba.cut(tmpstr, cut_all=False, HMM=True)
        for seg in seg_list:
            if seg in rs.VILLAGE:
                tmp_v = seg
                continue
            if seg in rs.ROAD_NAME:
                tmp_r = seg
                continue
            if seg in rs.UNIT_NAME:
                tmp_u = seg
                break

    return_list = list((tmp_p,tmp_c,tmp_d,tmp_t,tmp_v,tmp_r,tmp_u))

    if tmp_d is not None and tmp_t is not None and tmp_v is not None and tmp_r is None:
        return (0 ,return_list)
    elif tmp_d is not None and tmp_t is not None and tmp_v is not None and tmp_u is None:
        return (0, return_list)
    else :
        return (-1, return_list)

if __name__ == '__main__':
    addCutWord()
    str1 = "广东省江门市蓬江区白沙街道丰乐路"
    tmp = jugStr(str1)
    print(tmp)