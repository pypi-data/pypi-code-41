# encoding:utf8
''' 2017-8-24 pylint fix '''
import os
import sys
import json
import shutil
import logging
import plistlib


def path_fmt(path):
    ''' 路径兼容 '''
    path = path.replace("\n", "")
    return path.replace("/", os.sep)


class BatchPackimg(object):
    ''' 文件打包工具 '''
    _basepath = None   # 打包路径
    _tarpath = None   # 目标路径
    _pconfs = []     # 打包配置

    RESCONFIG_FILENAME = "resconf.data"  # 打包文件配置文件名

    @classmethod
    def _handle_etc1cmd_316(cls, pconf):
        ''' 
        这里是兼容316的官方etc1的
        打包方法独立的打包命令

        '''
        # pardir
        pardir = os.path.join(
            cls._tarpath, pconf["pardir"].replace("/", os.sep))
        if not os.path.isdir(pardir):
            os.makedirs(pardir)
        cmdrgb_str = "TexturePacker --sheet {out_file} --data {plist_name} \
                    --texture-format pkm --format {fmt_type} \
                    --opt ETC1 --size-constraints POT --disable-auto-alias \
                    --max-width 2048 --max-height 2048 {dir_name}"
        cmda_str = "TexturePacker --sheet {out_file} --data {plist_name} \
                    --texture-format pkm --format {fmt_type} --opt ETC1_A \
                    --size-constraints POT --disable-auto-alias \
                    --max-width 2048 --max-height 2048 {dir_name}"
        fmtrgb_str = dict(
            out_file=os.path.join(cls._tarpath, pconf["tarfile"] + ".pkm"),
            plist_name=os.path.join(cls._tarpath, pconf["tarfile"] + ".plist"),
            fmt_type="cocos2d",
            dir_name=os.path.join(cls._basepath, pconf["packpath"])
        )
        fmta_str = dict(
            out_file=os.path.join(
                cls._tarpath, pconf["tarfile"] + ".pkm@alpha"),
            plist_name=os.path.join(
                cls._tarpath, pconf["tarfile"] + ".plist@alpha"),
            fmt_type="cocos2d",
            dir_name=os.path.join(cls._basepath, pconf["packpath"])
        )
        ret = cmdrgb_str.format(out_file=fmtrgb_str["out_file"],
                                plist_name=fmtrgb_str["plist_name"],
                                fmt_type=fmtrgb_str["fmt_type"],
                                dir_name=fmtrgb_str["dir_name"])
        os.system(ret)
        ret = cmda_str.format(out_file=fmta_str["out_file"],
                              plist_name=fmta_str["plist_name"],
                              fmt_type=fmta_str["fmt_type"],
                              dir_name=fmta_str["dir_name"])
        os.system(ret)

    @classmethod
    def _handle_etc1cmd(cls, pconf):
        ''' 
        pconf是单条配置
        *兼容pvr 用类似工具
        '''
        # no-use files
        noulist = []
        # pardir
        pardir = os.path.join(
            cls._tarpath, pconf["pardir"].replace("/", os.sep))
        if not os.path.isdir(pardir):
            os.makedirs(pardir)

        # pack rgb + alpha
        cmdrgb_str = "TexturePacker --sheet {out_file} --data {plist_name} \
                    --texture-format pkm --format {fmt_type} --opt ETC1 \
                    --size-constraints POT --disable-auto-alias \
                    --max-width 2048 --max-height 2048 {dir_name}"
        cmda_str = "TexturePacker --sheet {out_file} --data {plist_name} \
                    --texture-format pkm --format {fmt_type} --opt ETC1_A \
                    --size-constraints POT --disable-auto-alias \
                    --max-width 2048 --max-height 2048 {dir_name}"
        fmtrgb_str = dict(
            out_file=os.path.join(cls._tarpath, pconf["tarfile"] + ".pkm"),
            plist_name=os.path.join(cls._tarpath, pconf["tarfile"] + ".plist"),
            fmt_type="cocos2d-v2",
            dir_name=os.path.join(cls._basepath, pconf["packpath"])
        )
        fmta_str = dict(
            out_file=os.path.join(
                cls._tarpath, pconf["tarfile"] + "_alpha.pkm"),
            plist_name=os.path.join(
                cls._tarpath, pconf["tarfile"] + "_alpha.plist"),
            fmt_type="cocos2d-v2",
            dir_name=os.path.join(cls._basepath, pconf["packpath"])
        )
        ret = cmdrgb_str.format(out_file=fmtrgb_str["out_file"],
                                plist_name=fmtrgb_str["plist_name"],
                                fmt_type=fmtrgb_str["fmt_type"],
                                dir_name=fmtrgb_str["dir_name"])
        print ret
        os.system(ret)
        ret = cmda_str.format(out_file=fmta_str["out_file"],
                              plist_name=fmta_str["plist_name"],
                              fmt_type=fmta_str["fmt_type"],
                              dir_name=fmta_str["dir_name"])
        os.system(ret)
        noulist.append(fmtrgb_str["out_file"])
        noulist.append(fmta_str["out_file"])
        noulist.append(fmta_str["plist_name"])

        # etc1_packdir
        outdir = cls._tarpath
        fname = pconf["tarfile"].split(os.sep)[-1]
        fnamehalf = pconf["tarfile"]
        tmpp = os.path.join(outdir, fnamehalf)
        tmpall = os.path.join(outdir, fnamehalf) + os.sep + fname + "_all.png"
        tmprgb = os.path.join(outdir, fnamehalf) + os.sep + fname + ".png"
        tmpa = os.path.join(outdir, fnamehalf) + os.sep + fname + "_alpha.png"

        # pkm 转 png
        binpath = os.environ["texturetool"]
        etcbin = os.path.join(binpath, "etcpack")
        convertbin = os.path.join(binpath, "convert")
        gzipbin = os.path.join(binpath, "gzip")

        cmdrgb_str = "cd {binpath} && {etcpack} {bfile} {ofile} \
                -ext PNG".format(binpath=binpath, etcpack=etcbin,
                                 bfile=fmtrgb_str["out_file"], ofile=tmpp)
        cmda_str = "cd {binpath} && {etcpack} {bfile} {ofile} \
                -ext PNG".format(binpath=binpath, etcpack=etcbin,
                                 bfile=fmta_str["out_file"], ofile=tmpp)
        print cmdrgb_str
        os.system(cmdrgb_str)
        os.system(cmda_str)

        # convert a+rgb
        cmdconv_str = "cd {binpath} && {convert} -append {rgb} {a}\
                     {all}".format(binpath=binpath, convert=convertbin,
                                   rgb=tmprgb, a=tmpa, all=tmpall)
        print cmdconv_str
        logging.info('cmdconv_str--->>>%s', cmdconv_str)
        os.system(cmdconv_str)

        # final 转etcpack
        cmdetc_str = "cd {binpath} && {etcpack} {all} {tar} -c etc1".format(
            binpath=binpath, etcpack=etcbin, all=tmpall, tar=tmpp)
        os.system(cmdetc_str)

        # gzip all pkm
        nosuffix = os.path.join(outdir, fnamehalf) + os.sep + fname
        retpkm = os.path.join(outdir, fnamehalf) + os.sep + fname + "_all.pkm"
        os.renames(retpkm, nosuffix)
        cmdgzip_str = "{gzipbin} {tarfile} -f".format(
            gzipbin=gzipbin, tarfile=nosuffix)
        print cmdgzip_str
        os.system(cmdgzip_str)

        # move and remove
        gzret = nosuffix + ".gz"
        ret = fmtrgb_str["out_file"].replace('.pkm', '.png')
        if os.path.isfile(ret):
            os.remove(ret)
        print(gzret, "--->>gzret")
        print(fmtrgb_str["out_file"].replace(".pkm", ".png"), "fmtrgb")
        os.rename(gzret, fmtrgb_str["out_file"].replace(".pkm", ".png"))

        # os.rename(tarpng + ".zip", tarpng + ".png")

        # remove unuse
        noulist.append(tmpp)
        for fobj in noulist:
            if os.path.isdir(fobj):
                shutil.rmtree(fobj)
            else:
                os.remove(fobj)
        # sys.exit()

    @classmethod
    def _handle_pvrcmd(cls, pconf):
        '''
        pconf是单条配置
        *pvr 一定是pot
        '''
        cmd_str = "TexturePacker --sheet {out_file} --data {plist_name} \
                --texture-format pvr3 --force-squared --format {fmt_type} \
                --opt PVRTC4 --disable-auto-alias --max-width 2048 \
                --max-height 2048 {dir_name}"
        fmtdic = dict(
            out_file=os.path.join(cls._tarpath, pconf["tarfile"] + ".pvr"),
            plist_name=os.path.join(cls._tarpath, pconf["tarfile"] + ".plist"),
            fmt_type="cocos2d-v2",
            dir_name=os.path.join(cls._basepath, pconf["packpath"])
        )
        pardir = os.path.join(
            cls._tarpath, pconf["pardir"].replace("/", os.sep))
        if not os.path.isdir(pardir):
            os.makedirs(pardir)

        ret = cmd_str.format(out_file=fmtdic["out_file"],
                             plist_name=fmtdic["plist_name"],
                             fmt_type=fmtdic["fmt_type"],
                             dir_name=fmtdic["dir_name"])

        logging.info(ret)
        if (os.path.isfile(fmtdic["out_file"])):
            os.remove(fmtdic["out_file"])
            os.remove(fmtdic["plist_name"])
        os.system(ret)
        if (os.path.isfile(fmtdic["out_file"])):
            if fmtdic["out_file"].endswith(".pvr"):
                os.rename(fmtdic["out_file"],
                          fmtdic["out_file"].replace(".pvr", ".png"))
        if (os.path.isfile(fmtdic["plist_name"])):
            if fmtdic["plist_name"].endswith(".plist"):
                plistdic = plistlib.readPlist(fmtdic["plist_name"])
                plistdic["metadata"]["realTextureFileName"] = \
                    plistdic["metadata"]["realTextureFileName"].replace(
                    ".pvr", ".png")
                plistdic["metadata"]["textureFileName"] = \
                    plistdic["metadata"]["textureFileName"].replace(
                    ".pvr", ".png")
                plistdic["metadata"].pop("smartupdate")
                plistlib.writePlist(plistdic, fmtdic["plist_name"])

    @classmethod
    def _handle_pngcmd(cls, pconf, extparam):
        '''pconf是单条配置'''

        cmd_str = "{TexturePacker} --sheet {out_file} --data {plist_name} \
                    --texture-format png8 --force-squared \
                    --format {fmt_type} --size-constraints NPOT \
                    --disable-auto-alias --max-width 2048 \
                    --multipack \
                    --max-height 2048  %s {dir_name}" % extparam
        cmd_str = "{TexturePacker} --sheet {out_file} --data {plist_name} \
                    --texture-format png8 --force-squared \
                    --format {fmt_type} --size-constraints NPOT \
                    --disable-auto-alias --max-width 2048 \
                    --max-height 2048  %s {dir_name}" % extparam

        fmtdic = dict(
            out_file=os.path.join(cls._tarpath, pconf["tarfile"] + ".png"),
            plist_name=os.path.join(cls._tarpath, pconf["tarfile"] + ".plist"),
            fmt_type="cocos2d",
            # fmt_type="cocos2d-v2",
            dir_name=os.path.join(cls._basepath, pconf["packpath"])
        )
        # chk pardir
        if pconf["pardir"]:
            pardir = os.path.join(
                cls._tarpath, pconf["pardir"].replace("/", os.sep))
            if not os.path.isdir(pardir):
                os.makedirs(pardir)

        ret = cmd_str.format(TexturePacker="/usr/local/bin/TexturePacker",
                             out_file=fmtdic["out_file"],
                             plist_name=fmtdic["plist_name"],
                             fmt_type=fmtdic["fmt_type"],
                             dir_name=fmtdic["dir_name"])
        logging.info(ret)
        os.system(ret)
        if (os.path.isfile(fmtdic["out_file"])):
            if fmtdic["out_file"].endswith(".pvr"):
                os.rename(fmtdic["out_file"],
                          fmtdic["out_file"].replace(".pvr", ".png"))

        cls.del_smartudpate(fmtdic["plist_name"])
        cls.add_dirname(fmtdic["plist_name"], "xl")

    @classmethod
    def _do_packlist(cls, extparam):
        '''遍历配置来打包'''
        if cls._packtype == "png":
            for pconf in cls._pconfs:
                cls._handle_pngcmd(pconf, extparam)
        elif cls._packtype == "pvr":
            for pconf in cls._pconfs:
                cls._handle_pvrcmd(pconf)
        elif cls._packtype == "etc1":
            for pconf in cls._pconfs:
                cls._handle_etc1cmd_316(pconf)
        else:
            logging.error(
                "Chk the pack type first!\
                 It's not support <{}> yet".format(cls._packtype))
            sys.exit()

    @classmethod
    def chk_packconf(cls, key):
        '''获取资源打包配置'''
        print(cls._resconf, "--->>cls.resconf")
        if not cls._resconf.has_key(key):
            logging.error("There is no config for pack <%s>", key)
            logging.error("Sys out!")
            sys.exit()
        resconf = cls._resconf[key]
        pconf = {}
        pconf["packpath"] = resconf["from"]
        pconf["tarfile"] = resconf["to"]
        pconf["pardir"] = resconf["to"].split("/")[0] if \
            len(resconf["to"].split("/")) > 1 else None

        logging.debug("out logging pconf is %s", pconf)
        return pconf

    @classmethod
    def get_resconfig(cls):
        '''获取资源打包配置'''
        jfile = os.path.join(cls._basepath, cls.RESCONFIG_FILENAME)
        fobj = open(jfile, "r")
        fcont = fobj.read().decode('utf-8')
        fobj.close()
        return json.loads(fcont)

    @classmethod
    def del_smartudpate(cls, plistfile):
        pdic = plistlib.readPlist(plistfile)
        # smart
        if pdic.has_key("metadata"):
            if pdic["metadata"].has_key("smartupdate"):
                pdic["metadata"].pop("smartupdate")
        plistlib.writePlist(pdic, plistfile)

    @classmethod
    def add_dirname(cls, plistfile, dirname):
        pdic = plistlib.readPlist(plistfile)
        for k, v in (pdic["frames"].items()):
            if k.find('/') == -1:
                item = pdic["frames"].pop(k)
                pdic["frames"][dirname + '/' + k] = v
        plistlib.writePlist(pdic, plistfile)

    @classmethod
    def excute(cls, packpath, tarpath, confkey, packtype="png", extparam=""):
        ''' 执行 '''
        cls._pconfs = []

        cls._basepath = packpath
        cls._tarpath = tarpath
        cls._resconf = cls.get_resconfig()

        conftmp = cls.chk_packconf(confkey)
        cls._pconfs.append(conftmp)
        cls._packtype = packtype
        cls._do_packlist(extparam)


if __name__ == "__main__":
    DEBUG = True
    if not DEBUG:
        sys.exit()

    b = "/data0/public_work/yn/share/resource/"
    t = "/data0/public_work/yn/client/trunk/"
    l = "common_1"
    # BatchPackimg.excute(b, t, l)
