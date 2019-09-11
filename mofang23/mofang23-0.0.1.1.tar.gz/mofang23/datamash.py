# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ss
   Description :
   Author :        Asdil
   date：          2019/8/16
-------------------------------------------------
   Change Activity:
                   2019/8/16:
-------------------------------------------------
"""
__author__ = 'Asdil'
import os
from Asdil import tool
from multiprocessing import Pool


# 获取染色体数目
def get_chroms(path):
    """
    :param path:  vcf文件 eg: /data7/xxx/abc.vcf 或者/data7/xxx/abc.vcf.gz
    :return:      染色体列表['1', '2', '3', ....]
    """
    suff = tool.splitPath(path)[-2]
    if suff == '.gz':
        # 第一步读取染色体数据
        cmd = f"""gzip -dc {path} """ + """| awk '{print $1}' | grep -v '#' | uniq"""
    else:
        cmd = """awk '{print $1}' """ + f"""{path} |grep -v '#'|uniq"""
    chroms = tool.subprocessPopen(cmd)
    return chroms


# 获取染色体数目，针对已经分染色体的数据
def get_chroms2(path):
    """
    :param path:  已经分过染色体的vcf/vcf.gz文件    eg: /data7/xxx/abc.1.vcf /data7/xxx/abc.2.vcf path=/data7/xxx
    :return: 染色体列表, 分染色体的每个文件路径
    """
    files = tool.getFiles(path, 'vcf')
    chroms = [each.split('.')[-2] for each in files]
    if len(files) == 0:
        files = tool.getFiles(path, 'gz')
        chroms = [each.split('.')[-3] for each in files]
    return chroms, files


# 分割染色体
def split_chroms(path, chroms, out_path, core=8):
    """
    :param path:     vcf路径
    :param chroms:   染色体列表
    :param out_path: 输出文件夹
    :param core:     进程数
    :return:         分染色体的数据，后缀matirx
    """
    name = tool.splitPath(path)[1].split('.')[0]
    cmds = []
    data_list = []
    for chrom in chroms:
        save_path = tool.pathJoin(out_path, f'{name}.{chrom}.matirx')
        data_list.append(save_path)
        suff = tool.splitPath(path)[-2]
        if suff == '.gz':
            cmd = f"""gzip -dc {path} """ + f"""| grep -w '^#CHROM\|^{chrom}' > {save_path}"""
        else:
            cmd = f"""grep -w '^#CHROM\|^{chrom}' {path} > {save_path}"""
        cmds.append(cmd)
    pool = Pool(core)
    pool.map(tool.subprocessCall, cmds)
    pool.close()
    pool.join()
    return data_list


# 分割染色体，已经分染色体的数据
def split_chroms2(paths, out_path, core=8):
    """
    :param paths:     已经分离染色体的文件夹
    :param out_path:  输出文件夹目录
    :param core:      并行核数
    :return:
    """
    data_list = []
    cmds = []
    for path in paths:
        name = tool.splitPath(path)[1]
        suff = tool.splitPath(path)[-2]
        if suff == '.gz':
            chrom = name.split('.')[-2]
            name = name.split('.')[0]
            save_path = tool.pathJoin(out_path, f'{name}.{chrom}.matirx')
            data_list.append(save_path)
            cmd = f"""gzip -dc {path} """ + f"""| grep -w '^#CHROM\|^{chrom}' > {save_path}"""
        else:
            chrom = name.split('.')[-1]
            name = name.split('.')[0]
            save_path = tool.pathJoin(out_path, f'{name}.{chrom}.matirx')
            data_list.append(save_path)
            cmd = f"""grep -w '^#CHROM\|^{chrom}' {path} > {save_path}"""
        cmds.append(cmd)
    pool = Pool(core)
    pool.map(tool.subprocessCall, cmds)
    pool.close()
    pool.join()
    return data_list


# 获取map文件
def get_cpra(paths, out_path, core=8):
    """
    :param paths:     获取染色体 chrom pos ref alt列表
    :param out_path:  输出文件夹
    :param core:      并行核数
    :return:          chrom pos ref alt 文件 .map结尾
    """
    cmds = []
    for path in paths:
        suff = tool.splitPath(path)[-2]
        if suff == '.gz':
            name = tool.splitPath(path)[1].split('.')[0]
            chrom = path.split('.')[-3]
            save_path = tool.pathJoin(out_path, f'{name}.{chrom}.map')
            cmd = f"""gzip -dc {path} | grep -w '^{chrom}' |awk """ + """'{print $1, $2, $4, $5}' >""" + f""" {save_path}"""
        else:
            name = tool.splitPath(path)[1].split('.')[0]
            chrom = path.split('.')[-2]
            save_path = tool.pathJoin(out_path, f'{name}.{chrom}.map')
            cmd = f"""grep -w '^{chrom}' {path}|awk """ + """'{print $1, $2, $4, $5}' >""" + f""" {save_path}"""
        cmds.append(cmd)
    pool = Pool(core)
    pool.map(tool.subprocessCheckAll, cmds)
    pool.close()
    pool.join()


# 转置文件
def trans(params):
    """
    :param params:  文件路径, 输出文件路径
    :return:
    """
    path, out_path = params
    name = tool.splitPath(path)[1]
    save_path = tool.pathJoin(out_path, f'{name}.aped')
    cmd = """awk '{for (i=1; i<=NF; i++) {a[NR,i] = $i}} NF>p { p = NF } END {for(j=1; j<=p; j++) {str=a[1,j]; for(i=2; i<=NR; i++){str=str" "a[i,j];} print str }}' """ + f"{path} > {save_path}"
    tool.subprocessCheckAll(cmd)
    os.remove(path)
    cmd = f"""sed -i '1,9d' {save_path}"""
    tool.subprocessCheckAll(cmd)
    cmd = f"""sed -i 's/0|0/2 2/g' {save_path}"""
    tool.subprocessCheckAll(cmd)
    cmd = f"""sed -i 's/0|1/2 1/g' {save_path}"""
    tool.subprocessCheckAll(cmd)
    cmd = f"""sed -i 's/1|0/1 2/g' {save_path}"""
    tool.subprocessCheckAll(cmd)
    cmd = f"""sed -i 's/1|1/1 1/g' {save_path}"""
    tool.subprocessCheckAll(cmd)
    cmd = f"""sed -i 's/.|./0 0/g' {save_path}"""
    tool.subprocessCheckAll(cmd)
    cmd = f"""sed -i 's/.\/./0 0/g' {save_path}"""
    tool.subprocessCheckAll(cmd)


# 主转置文件
def transpose(paths, out_path, core=8):
    """
    :param paths:     matrix文件路径列表
    :param out_path:  输出文件夹
    :param core:      并行核数
    :return:
    """
    params = [[path, out_path] for path in paths]
    pool = Pool(core)
    pool.map(trans, params)
    pool.close()
    pool.join()


def makeaped(path, out_path, cores=8):
    """
       :path
    """
    chroms = get_chroms(path)
    print('拆分文件...')
    paths = split_chroms(path, chroms, out_path)
    print('拆分文件结束')
    print('生成map文件...')
    get_cpra(paths, out_path, cores)
    print('map文件生成完毕')
    print('转置文件...')
    transpose(paths, out_path, cores)
    print('所有处理完毕')


def makeaped_splited(path, out_path, cores=8):
    chroms, paths = get_chroms2(path)
    print('拆分文件...')
    paths = split_chroms2(paths, out_path, cores)
    print('拆分文件结束')
    print('生成map文件...')
    get_cpra(paths, out_path, cores)
    print('map文件生成完毕')
    print('转置文件...')
    transpose(paths, out_path, cores)
    print('所有处理完毕')


def hp():
    print('1.第一种针对于文件 名称固定 文件名.vcf.gz 或者 文件名.vcf')
    print("path = '/home/jiapeiling/tmp/aa.1.vcf.gz'\nout_path = '/home/jiapeiling/tmp'\nmakeaped(path, out_path)")
    print()
    print('2.第一种针对于已经分染色体的文件 文件夹下包含 文件名.1.vcf.gz 或者 文件名.1.vcf')
    print("path = '/home/jiapeiling/tmp'\nout_path = '/home/jiapeiling/tmp'\nmakeaped_splited(path, out_path)")
    print()
    print('输出文件: 文件名.染色体.map   文件名.染色体.aped')