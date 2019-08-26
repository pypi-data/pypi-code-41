""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 21/02/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   :

Remarks :

History : (21/02/2016) First version.
"""


from SRP.SRPCatalogue.GetVizierCat import GetVizierCat




def GetSkyBot(rad,decd,rds,time,maxerr):
    skybotaddress = "vo.imcce.fr"
    skybotquery = "/webservices/skybot/skybotconesearch_query.php?-ep=%s&-ra=%.5f&-dec=%.5f&-rs=%.1f&-mime=text&-outout=object&-filter=%.1f&-from=SRP"
    #
    sbot= []
    for r,d in zip(rad,decd):
        data = GetVizierCat(skybotaddress,skybotquery % (time,r,d,rds,maxerr))
        #
        if data != None:
            il = data[0].split('|')
            if len(il) < 7:
                sbot.append('No')
            else:
                objid = il[1].strip()
                ra = float(il[2])*15.0
                dec = float(il[3])
                objclass = il[4]
                objvmag = float(il[5])
                poserr = float(il[6])
                cdist = float(il[7])
                sbot.append("%s_%.2f" % (objid, objvmag))
        else:
            sbot.append('No')
    #
    return sbot
