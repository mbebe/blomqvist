# -*- coding: UTF-8 -*-
import sys,re,os

try:
    # For Python 3.0 and later
   import urllib.parse as urlparse
except ImportError:
    # Fall back to Python 2's urllib2
    import urlparse


import requests
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc, xbmcvfs

try:
    import http.cookiejar as cookielib
except ImportError:
    import  cookielib

try:
    from urllib.parse import urlencode, quote_plus, quote
except ImportError:
    from urllib import urlencode, quote_plus, quote

import random
import time

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.polsatgo')

PATH            = addon.getAddonInfo('path')
if sys.version_info >= (3,0,0):
    DATAPATH        = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
else:
    DATAPATH        = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
RESOURCES       = PATH+'/resources/'
FANART=RESOURCES+'fanart.jpg'
ikona = RESOURCES+'../icon.png'


sys.path.append( os.path.join( RESOURCES, "lib" ) )

exlink = params.get('url', None)
name= params.get('title', None)
opisy= params.get('plot', None)
offse= params.get('page', None)
rys=params.get('image', None)

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
osinfo = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"

uapg = "pg_pc_windows_firefox_html/1 (Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0)"
uapgwidevine = "pg_pc_windows_firefox_html/1 (Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0) (Windows 7; widevine=true)"
auth_url='https://b2c-www.redefine.pl/rpc/auth/'
navigate_url='https://b2c-www.redefine.pl/rpc/navigation/'
system_url = 'https://b2c-www.redefine.pl/rpc/system/'
user_url = 'https://b2c-www.redefine.pl/rpc/user_content/'
host = 'b2c-www.redefine.pl'
origin = 'https://polsatgo.pl'

clid = addon.getSetting('clientId')
devid = addon.getSetting('devid')

stoken = addon.getSetting('sesstoken')
sexpir = addon.getSetting('sessexpir')
skey = addon.getSetting('sesskey')





def build_url(query):
    return base_url + '?' + urlencode(query)


def add_item(url, name, image, folder, mode,  isPlayable=True, infoLabels=False, FANART=None, contextmenu=None, itemcount=1, page=0):

    list_item = xbmcgui.ListItem(label=name)    
        
    if isPlayable:
        list_item.setProperty("IsPlayable", 'true')
        contextMenuItems = []
        contextMenuItems.append(('Informacja', 'XBMC.Action(Info)'))
        list_item.addContextMenuItems(contextMenuItems, replaceItems=False)
    if contextmenu:
        out=contextmenu
        list_item.addContextMenuItems(out, replaceItems=True)

    if not infoLabels:
        infoLabels={'title': name,'plot':name}
    
    list_item.setInfo(type="video", infoLabels=infoLabels)
    
    FANART = FANART if FANART else image
    list_item.setArt({'thumb': image, 'poster': image, 'banner': image, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(
        handle=addon_handle,    
        url = build_url({'title':name,'mode': mode, 'url' : url, 'page' : page,'plot':infoLabels,'image':image}),    
        listitem=list_item,
        isFolder=folder)


def PlayPolsat(stream_url,data):
    import inputstreamhelper

    PROTOCOL = 'mpd'
    DRM = 'com.widevine.alpha'
    LICENSE_URL = 'https://b2c-www.redefine.pl/rpc/drm/'
    is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    
    UAcp=  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36'
    
    dane=eval(opisy)
    if is_helper.check_inputstream():
        play_item = xbmcgui.ListItem(path=stream_url)#
        play_item.setInfo(type="Video", infoLabels={"title": dane['title'],'plot':dane['plot']})
        
        play_item.setArt({'thumb': rys, 'poster': rys, 'banner': rys, 'fanart': FANART})
        
        play_item.setMimeType('application/xml+dash')
        play_item.setContentLookup(False)
        if sys.version_info >= (3,0,0):
            play_item.setProperty('inputstream', is_helper.inputstream_addon)
        else:
            play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
        play_item.setProperty("IsPlayable", "true")
        play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        play_item.setProperty('inputstream.adaptive.license_type', DRM)

        play_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
        play_item.setProperty('inputstream.adaptive.stream_headers', 'Referer: %s'%(origin))
        play_item.setProperty('inputstream.adaptive.license_key',
                            LICENSE_URL + '|Content-Type=application%2Fjson&Referer=https://polsatgo.pl/&User-Agent=' + quote(UA) +
                            '|'+data+'|JBlicense')        

            
        play_item.setProperty('inputstream.adaptive.license_flags', "persistent_storage")

    Player = xbmc.Player()
    Player.play(stream_url, play_item)

def checkAccess(id):
    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json; utf-8',
        'Origin': 'https://go.cyfrowypolsat.pl',
        'Connection': 'keep-alive',
    }
    
    dane =stoken+'|'+sexpir+'|navigation|getMedia'
    authdata=getHmac(dane)
    
    data={"jsonrpc":"2.0","method":"getMedia","id":1,"params":{"cpid":1,"mediaId":id,"ua":"cpgo_www/2015","authData":{"sessionToken":authdata}}}

    response = requests.post(navigate_url, headers=headers, json=data,timeout=15, verify=False).json()
    prod=response['result']['product']
    prodid=prod['id']
    prodtype=prod['type']
    prodstype=prod['subType']
    
    dane =stoken+'|'+sexpir+'|payments|checkProductsAccess'
    authdata=getHmac(dane)
    
    
    
    data={"jsonrpc":"2.0","method":"checkProductsAccess","id":1,"params":{"products":[{"id":prodid,"type":prodtype,"subType":prodstype}],"ua":"cpgo_www/2015","authData":{"sessionToken":authdata}}}
    response = requests.post('https://b2c-www.redefine.pl/rpc/payments/', headers=headers, json=data,timeout=15, verify=False).json()
    dostep=response['result'][-1]['access']['statusDescription']
    if 'no access' in dostep:
        return False
    else:
        return True

def playVOD(id):

    playCPGO(id,cpid=1)

def playCPGO(id,cpid=0):
    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')

    dane =stoken+'|'+sexpir+'|auth|getSession'

    headers = {
        'Host': host,
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }

    authdata=getHmac(dane)
    
    data = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "getSession",
            "params": {
                "ua": uapg,
                "deviceId": {
                    "type": "other",
                    "value": devid
                },
                "userAgentData": {
                    "portal": "pg",
                    "deviceType": "pc",
                    "application": "firefox",
                    "player": "html",
                    "build": 1,
                    "os": "windows",
                    "osInfo": osinfo
                },
                "authData": {
                    "sessionToken": authdata
                },
                "clientId": ""}}
    
    
    response = requests.post(auth_url, headers=headers, json=data,timeout=15, verify=False).json()
    sesja=response['result']['session']
    
    sesstoken=sesja['id']
    sessexpir=str(sesja['keyExpirationTime'])
    sesskey=sesja['key']
    
    
    
    
    
    
    
    
    
    addon.setSetting('sesstoken', sesstoken)
    addon.setSetting('sessexpir', str(sessexpir))
    addon.setSetting('sesskey', sesskey)
    
    
    
    response = requests.post(auth_url, headers=headers, json=data,timeout=15, verify=False).json()
    sesja=response['result']['session']
    
    sesstoken=sesja['id']
    sessexpir=str(sesja['keyExpirationTime'])
    sesskey=sesja['key']
    
    addon.setSetting('sesstoken', sesstoken)
    addon.setSetting('sessexpir', str(sessexpir))
    addon.setSetting('sesskey', sesskey)
    
    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')

    dane =stoken+'|'+sexpir+'|navigation|prePlayData'
    authdata=getHmac(dane)

    data = {"jsonrpc":"2.0","id":1,"method":"prePlayData","params":{"ua":uapgwidevine,"userAgentData":{"deviceType":"pc","application":"firefox","os":"windows","build":2150100,"portal":"pg","player":"html","widevine":True},"cpid":cpid,"mediaId":id,"authData":{"sessionToken":authdata},"clientId":clid}}

    response = requests.post(navigate_url, headers=headers, json=data,timeout=15, verify=False).json()
    playback = response['result']['mediaItem']['playback']
    mediaid = playback['mediaId']['id']
    mediaSources = playback['mediaSources'][0]
    keyid = mediaSources['keyId']
    sourceid = mediaSources['id']

    try:
        cc=mediaSources['authorizationServices']['pseudo']
        dane =stoken+'|'+sexpir+'|drm|getPseudoLicense'
        authdata=getHmac(dane)
        devcid=devid.replace('-','')
        
    
        data={"jsonrpc":"2.0","id":1,"method":"getPseudoLicense","params":{"ua":"cpgo_www_html5/2","cpid":1,"mediaId":mediaid,"sourceId":sourceid,"deviceId":{"type":"other","value":devcid},"authData":{"sessionToken":authdata}}}
        response = requests.post('https://b2c-www.redefine.pl/rpc/drm/', headers=headers, json=data,timeout=15, verify=False).json()
        str_url=response['result']['url']

        PlayPolsatPseudo(str_url)
    except:

        stream_url = mediaSources['url']
        
        dane =stoken+'|'+sexpir+'|drm|getWidevineLicense'
        authdata=getHmac(dane)
        devcid=devid.replace('-','')

        data=quote('{"jsonrpc":"2.0","id":1,"method":"getWidevineLicense","params":{"cpid":%d,"mediaId":"'%cpid+mediaid+'","sourceId":"'+sourceid+'","keyId":"'+keyid+'","object":"b{SSM}","deviceId":{"type":"other","value":"'+devid+'"},"ua":"pg_pc_windows_firefox_html/2150100","authData":{"sessionToken":"'+authdata+'"}}}')

        PlayPolsat(stream_url,data)
    return
        
def PlayPolsatPseudo(str_url):
    dane=eval(opisy)
    play_item = xbmcgui.ListItem(path=str_url)#
    play_item.setInfo(type="Video", infoLabels={"title": dane['title'],'plot':dane['plot']})
    
    play_item.setArt({'thumb': rys, 'poster': rys, 'banner': rys, 'fanart': FANART})

    play_item.setContentLookup(False)
    play_item.setProperty("IsPlayable", "true")
    Player = xbmc.Player()
    Player.play(str_url, play_item)
    
def loginCPgo():

    headers = {
        'Host': host,
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }


    clid = addon.getSetting('clientId')
    devid = addon.getSetting('devid')
    
    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')
    skey = addon.getSetting('sesskey')
    
    def gen_hex_code(myrange=6):
        return ''.join([random.choice('0123456789ABCDEF') for x in range(myrange)])
    
    def ipla_system_id():
        myrand = gen_hex_code(10) + '-' + gen_hex_code(4) + '-' + gen_hex_code(4) + '-' + gen_hex_code(4) + '-' + gen_hex_code(12)
    
        return myrand
    if not clid and not devid:
    
        clientid=ipla_system_id()
        deviceid=ipla_system_id()
        
        addon.setSetting('clientId', clientid)
        addon.setSetting('devid', deviceid)
        return loginCPgo()
        
    else:

        usernameCP = addon.getSetting('usernameCP')
        passwordCP = addon.getSetting('passwordCP')    
        if usernameCP and passwordCP:
        
            data = {"id":1,"jsonrpc":"2.0","method":"login","params":{"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"clientId":"","authData":{"login":usernameCP,"password":passwordCP,"deviceId":{"type":"other","value":devid}}}}

            data = {
                    "id": 1,
                    "jsonrpc": "2.0",
                    "method": "login",
                    "params": {
                        "ua": uapg,
                        "deviceId": {
                            "type": "other",
                            "value": devid
                        },
                        "userAgentData": {
                            "portal": "pg",
                            "deviceType": "pc",
                            "application": "firefox",
                            "player": "html",
                            "build": 1,
                            "os": "windows",
                            "osInfo": osinfo
                        },
                        "clientId": "",
                        "authData": {
                            "login": usernameCP,
                            "password": passwordCP,
                            "deviceId": {
                                "type": "other",
                                "value": devid}}}
                    }
                            

            response = requests.post(auth_url, headers=headers, json=data,timeout=15, verify=False).json()
            try:
                blad=response['error']
                if blad:
                    message=blad['message']
                    xbmcgui.Dialog().notification('[B]Logowanie[/B]', message,xbmcgui.NOTIFICATION_INFO, 6000)
                return False,False

            except:

                sesja=response['result']['session']

                sesstoken=sesja['id']
                sessexpir=str(sesja['keyExpirationTime'])
                sesskey=sesja['key']

                addon.setSetting('sesstoken', sesstoken)
                addon.setSetting('sessexpir', str(sessexpir))
                addon.setSetting('sesskey', sesskey)
                
                
                
                
                
                
                
                
                dane =sesstoken+'|'+sessexpir+'|auth|getSession'
                authdata=getHmac(dane)
    
                data = {
                        "id": 1,
                        "jsonrpc": "2.0",
                        "method": "getSession",
                        "params": {
                            "ua": uapg,
                            "deviceId": {
                                "type": "other",
                                "value": devid
                            },
                            "userAgentData": {
                                "portal": "pg",
                                "deviceType": "pc",
                                "application": "firefox",
                                "player": "html",
                                "build": 1,
                                "os": "windows",
                                "osInfo": osinfo
                            },
                            "authData": {
                                "sessionToken": authdata
                            },
                            "clientId": ""}}


                response = requests.post(auth_url, headers=headers, json=data,timeout=15, verify=False).json()
                sesja=response['result']['session']

                sesstoken=sesja['id']
                sessexpir=str(sesja['keyExpirationTime'])
                sesskey=sesja['key']
                
                
                
                
                
                
                
                
                
                addon.setSetting('sesstoken', sesstoken)
                addon.setSetting('sessexpir', str(sessexpir))
                addon.setSetting('sesskey', sesskey)
                accesgroup = response['result']['accessGroups']

                addon.setSetting('accgroups', str(accesgroup))
                
                dane =sesstoken+'|'+sessexpir+'|auth|getProfiles'
                authdata=getHmac(dane)
                data = {"id":1,"jsonrpc":"2.0","method":"getProfiles","params":{"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":""}}
                response = requests.post(auth_url, headers=headers, json=data,timeout=15, verify=False).json()
                nids = []
                for result in response['result']:
                    nids.append({'id':result['id'],'nazwa':result["name"],'img':result["avatarId"]})    
                if len(nids)>1:
                    profile = [x.get('nazwa') for x in nids]
                    sel = xbmcgui.Dialog().select('Wybierz profil',profile)    
                    if sel>-1:
                        id = nids[sel].get('id')
                        nazwa = nids[sel].get('nazwa')
                        avt = nids[sel].get('img')
                        profil = nazwa+'|'+id
                    else:
                        id = str(nids[0].get('id'))
                        nazwa = nids[0].get('nazwa')
                        avt = nids[sel].get('img')
                        profil = nazwa+'|'+id

                else:
                    id = str(nids[0].get('id'))
                    nazwa = nids[0].get('nazwa')
                    avt = nids[0].get('img')
                    profil = nazwa+'|'+id

                dane =sesstoken+'|'+sessexpir+'|auth|setSessionProfile'
                authdata=getHmac(dane)
                data = {"id":1,"jsonrpc":"2.0","method":"setSessionProfile","params":{"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":"","profileId":id}}
                response = requests.post(auth_url, headers=headers, json=data,timeout=15, verify=False).json()
                dane =sesstoken+'|'+sessexpir+'|auth|getSession'
                authdata=getHmac(dane)
    
                data = {"id":1,"jsonrpc":"2.0","method":"getSession","params":{"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":""}}
    

                response = requests.post(auth_url, headers=headers, json=data,timeout=15, verify=False).json()
                sesja=response['result']['session']

                sesstoken=sesja['id']
                sessexpir=str(sesja['keyExpirationTime'])
                sesskey=sesja['key']
                

                
                addon.setSetting('sesstoken', sesstoken)
                addon.setSetting('sessexpir', str(sessexpir))
                addon.setSetting('sesskey', sesskey)
                accesgroup = response['result']['accessGroups']

                addon.setSetting('accgroups', str(accesgroup))
                
                return True,profil

    
        else:
            xbmcgui.Dialog().notification('[B]Logowanie[/B]', 'Błędne dane logowania.',xbmcgui.NOTIFICATION_INFO, 6000)
            return False,False

def home():
    logged,profil=loginCPgo()
    if logged:
        add_item(name='Zalogowany - %s'%(profil.split('|')[0]), url='', mode=' ', image='DefaultUser.png', folder=False, isPlayable=False,FANART=FANART)
        add_item(name='LIVE', url='', mode='live', image=ikona, folder=True, isPlayable=False,FANART=FANART)
        add_item(name='Telewizja', url='', mode='tvcpgo', image=ikona, folder=True, isPlayable=False,FANART=FANART)
        add_item(name='VOD', url='', mode='vodmain', image=ikona, folder=True, isPlayable=False,FANART=FANART)
        add_item(name='Moja lista', url='', mode='mojalista', image=ikona, folder=True, isPlayable=False,FANART=FANART)
    else:
        add_item('', '[B]Zaloguj[/B]','DefaultAddonService.png',False,'settings',False,FANART=FANART)
    xbmcplugin.endOfDirectory(addon_handle)    

def newtime(self,ff):
    ff=re.sub(':\d+Z','',ff)

    import time
    import calendar
    dd=int(calendar.timegm(time.strptime(ff, '%Y-%m-%dT%H:%M')))
    format_date=datetime.datetime(*(time.localtime(dd)[0:6]))

    return dd,format_date   

def live():
    headers = {
        'Host': host,
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }


    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')


    items = []
    myperms = []
    ff = addon.getSetting('accgroups')
    lista=eval(ff)
    
    for l in lista:
        if 'sc:' in l or 'loc:' in l:
            myperms.append(l)

    dane =stoken+'|'+sexpir+'|navigation|getLiveChannels'
    authdata=getHmac(dane)
    

    data = {"id":1,"jsonrpc":"2.0","method":"getLiveChannels","params":{"filters":[],"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":clid}}
    

    response = requests.post(navigate_url, headers=headers, json=data,timeout=15, verify=False).json()
    aa=response['result']['results']
    for i in aa:
        item = {}
        
        channelperms = i['grantExpression'].split('+')
        channelperms = [w.replace('+plat:all', '') for w in channelperms]    

        for j in myperms:

            if j in channelperms or 'transmisja bezpłatna' in i['title']:
                item['img'] = i['thumbnails'][-1]['src'].encode('utf-8')
                item['id'] = i['id']
    
                z,data = newtime(i["publicationDate"]) 
                item['title'] = '%s - %s'%(data,i['title'].upper().encode('utf-8'))
                item['plot'] = i['category']['description'].encode('utf-8')
                items.append(item)
    dupes = []
    filter = []
    for entry in items:

        if not entry['id'] in dupes:
            filter.append(entry)
            dupes.append(entry['id'])

    items = filter
    items.sort(key=lambda x: x['title'])
    itemz= len(items)
    for item in items:
        opis=''
        add_item(name=item.get('title'), url=item.get('id'), mode='playCPGO', image=item.get('img'), folder=False, isPlayable=False, infoLabels={'title':item.get('title'),'plot':opis}, itemcount=itemz,FANART=FANART)


    xbmcplugin.endOfDirectory(addon_handle)

    
def tvmain():
    headers = {
        'Host': host,
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }


    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')


    items = []
    myperms = []
    ff = addon.getSetting('accgroups')
    lista=eval(ff)
    
    for l in lista:
        if 'sc:' in l or 'loc:' in l:
            myperms.append(l)

    dane =stoken+'|'+sexpir+'|navigation|getTvChannels'
    authdata=getHmac(dane)
    

    data = {"id":1,"jsonrpc":"2.0","method":"getTvChannels","params":{"filters":[],"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":clid}}
    

    response = requests.post(navigate_url, headers=headers, json=data,timeout=15, verify=False).json()
    aa=response['result']['results']
    for i in aa:
        item = {}
        
        channelperms = i['grantExpression'].split('+')
        channelperms = [w.replace('+plat:all', '') for w in channelperms]    

        for j in myperms:
            
            if j in channelperms or i['title']=='Polsat' or i['title']=='TV4':
                item['img'] = i['thumbnails'][-1]['src'].encode('utf-8')
                item['id'] = i['id']
    
                item['title'] = i['title'].upper().encode('utf-8')
                item['plot'] = i['category']['description'].encode('utf-8')
                items.append(item)
    dupes = []
    filter = []
    for entry in items:

        if not entry['id'] in dupes:
            filter.append(entry)
            dupes.append(entry['id'])
    
    addon.setSetting('kanaly', str(dupes))

    dups=getEpgs()
    items = filter
    itemz= len(items)
    for item in items:
        try:
            opis=dups[0][item.get('id')]
        except:
            opis=''
        add_item(name=item.get('title'), url=item.get('id'), mode='playCPGO', image=item.get('img'), folder=False, isPlayable=False, infoLabels={'title':item.get('title'),'plot':opis}, itemcount=itemz,FANART=FANART)


    xbmcplugin.endOfDirectory(addon_handle)

    
def newtime(ff):
    from datetime import datetime
    ff=re.sub(':\d+Z','',ff)
    dd=re.findall('T(\d+)',ff)[0]
    dzien=re.findall('(\d+)T',ff)[0]
    dd='{:>02d}'.format(int(dd)+2)
    if dd=='24':
        dd='00'
        dzien='{:>02d}'.format(int(dzien)+1)
    if dd=='25':
        dd='01'
        dzien='{:>02d}'.format(int(dzien)+1)
    ff=re.sub('(\d+)T(\d+)','%sT%s'%(dzien,int(dd)),ff)
    
    import time
    try:
        format_date=datetime.strptime(ff, '%Y-%m-%dT%H:%M')
    except TypeError:
        format_date=datetime(*(time.strptime(ff, '%Y-%m-%dT%H:%M')[0:6]))
    dd= int('{:0}'.format(int(time.mktime(format_date.timetuple()))))

    return dd,format_date    
    
def getEpgs():
    kanaly = addon.getSetting('kanaly')
    kanaly=eval(kanaly)
    
    import datetime 
    now = datetime.datetime.now()
    now2 = datetime.datetime.now()+ datetime.timedelta(days=1)
    aa1=now.strftime('%Y-%m-%dT%H:%M:%S') + ('.%03dZ' % (now.microsecond / 10000))
    aa=now2.strftime('%Y-%m-%dT%H:%M:%S') + ('.%03dZ' % (now.microsecond / 10000))
    
    headers = {
        'Host': host,
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }
    
    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')
    
    dane =stoken+'|'+sexpir+'|navigation|getChannelsProgram'
    authdata=getHmac(dane)

    data={"jsonrpc":"2.0","method":"getChannelsProgram","id":1,"params":{"channelIds":kanaly,"fromDate":aa1,"toDate":aa,"ua":uapg,"authData":{"sessionToken":authdata}}}

    
    response = requests.post(navigate_url, headers=headers, json=data,timeout=15, verify=False).json()

    dupek=[]
    import datetime 
    now = datetime.datetime.now()
    ab=now.strftime('%Y-%m-%dT%H:%M:%SZ')

    from datetime import datetime
    import time
    try:
        format_date=datetime.strptime(ab, '%Y-%m-%dT%H:%M:%SZ')
    except TypeError:
        format_date=datetime(*(time.strptime(ab, '%Y-%m-%dT%H:%M:%SZ')[0:6]))
    zz= int('{:0}'.format(int(time.mktime(format_date.timetuple()))))
    
    items={}
    for kanal in kanaly:
        
        el1=''
        if kanal in response['result']:
            dane=response['result'][kanal]
            for i in range(len(dane)):
                try:
                    nowy,format_date=newtime(dane[i]["startTime"])
                    nowy2,format_date2=newtime(dane[i+1]["startTime"])
                    trwa=nowy2-nowy
                    if nowy<zz and nowy+trwa>zz:
                        tyt=dane[i]["title"]
                        tyt2=dane[i]["genre"]
                        cc=re.sub(':\d+$','',str(format_date))
                        el1+='[COLOR khaki]'+cc+'[/COLOR] - '+tyt+' [COLOR violet]('+tyt2+')[/COLOR][CR]'
                    elif nowy>zz:
                        tyt=dane[i]["title"]
                        tyt2=dane[i]["genre"]
                        cc=re.sub(':\d+$','',str(format_date))
                        el1+='[COLOR khaki]'+cc+'[/COLOR] - '+tyt+' [COLOR violet]('+tyt2+')[/COLOR][CR]'
                    
                except:
                    pass
                
        else:
            continue
        items[kanal]=el1
    dupek.append(items)

    return dupek
    
    
    
def vodmain():
    add_item(name='Szukaj', url='', mode='vodszukaj', image=RESOURCES+'search.png', folder=True, isPlayable=False,FANART=FANART)


    add_item(name='SERIALE', url='5024024', mode='vodlist', image='https://redirector.redefine.pl/iplatv/menu_icon_seriale.png', folder=True, isPlayable=False,FANART=FANART)
    add_item(name='SPORT', url='5024074', mode='vodlist', image='https://redirector.redefine.pl/iplatv/menu_icon_sport.png', folder=True, isPlayable=False,FANART=FANART)
    add_item(name='FILM', url='5024058', mode='vodlist', image='https://ipla-e3-18.pluscdn.pl/p/iplatv/gf/gfarpsbbncitbcsxze1artm3uf3i3jh8/film.png', folder=True, isPlayable=False,FANART=FANART)
    add_item(name='PROGRAMY', url='5024073', mode='vodlist', image='https://redirector.redefine.pl/iplatv/menu_icon_programy.png', folder=True, isPlayable=False,FANART=FANART)
    xbmcplugin.endOfDirectory(addon_handle)

    
def vodSzukaj(query):
    headers = {
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Connection': 'keep-alive',
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }
    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')
    
    items = []
    myperms = []
    
    ff = addon.getSetting('accgroups')
    lista=eval(ff)
    
    for l in lista:
        if 'sc:' in l:
            myperms.append(l)
        if 'oth:' in l:
            myperms.append(l)
        if 'loc:' in l:
            myperms.append(l)


    dane =stoken+'|'+sexpir+'|navigation|searchContent'
    authdata=getHmac(dane)


    data={"jsonrpc":"2.0","method":"searchContent","id":1,"params":{"query":query,"limit":50,"ua":uapg,"authData":{"sessionToken":authdata}}}

    
    data={
            "id": 1,
            "jsonrpc": "2.0",
            "method": "searchContent",
            "params": {
                "query": query,
                "limit": 50,
                "ua": uapg,
                "deviceId": {
                    "type": "other",
                    "value": devid
                },
                "userAgentData": {
                    "portal": "pg",
                    "deviceType": "pc",
                    "application": "firefox",
                    "player": "html",
                    "build": 1,
                    "os": "windows",
                    "osInfo": osinfo
                },
                "authData": {
                    "sessionToken": authdata
                },
                "clientId": clid
            }
        }
    
    response = requests.post(navigate_url, headers=headers, json=data,timeout=15, verify=False).json()
    
    mud='playVOD'
    folder=False
    isplay=False
    ss='0'

    try:
        aa = response['result']['results']
    except:
        aa = response['result']

    if not aa:
       return vodSzukaj(id)

    if 'keyCategoryId' in aa[0]:
        mud='vodlist'
        folder=True
        isplay=False
    try:
        otal = response['result']['total']
    except:
        otal = 0

    for i in aa:
        if 'keyCategoryId' in i:
            #mud='vodlist'
            #folder=True
            #isplay=False
            
            if i['keyCategoryId'] == i['id']:
                ss='1'

        else:
            mud='playVOD'
            folder=False
            isplay=False

        item = {}
        for j in myperms:
            if i.get('thumbnails',None):
                item['img'] = i['thumbnails'][-1]['src'].encode('utf-8')
            else:
                item['img'] = None

            item['id'] = str(i['id'])+'|ss' if (ss == '1' )  else str(i['id'])  
            if (mud == 'vodlist'):
                item['id'] = item['id']+'|dod'                  
        
            try:
                item['title'] = i['title'].upper().encode('utf-8')
            except:
                item['title'] = i['name'].upper().encode('utf-8')
            item['plot'] = i['description'].encode('utf-8')
            items.append(item)

    dupes = []
    filter = []
    for entry in items:
        if not entry['id'] in dupes:
            filter.append(entry)
            dupes.append(entry['id'])
    items = filter
    itemz= len(items)
    
    for item in items:
        idc = item.get('id')
        if 'dod' in idc:
            mud='vodlist'
            folder=True
            isplay=False
            
            #idc = idc.split('|')[0]+'|getSubCategories'
            if 'ss' in idc:       
                idc = idc.split('|')[0]+'|getSubCategories'
            else:
                idc = idc.split('|')[0]
        else:
            mud = 'playVOD'
            folder=False
            isplay=False


        contextmenu = []
        if mud =='playVOD':
            contextmenu.append(('[B][COLOR lightgreen]Dodaj do MOJEJ LISTY[/B][/COLOR]', 'RunPlugin(plugin://plugin.video.polsatgo?mode=DodajUsun&url=%s)'%str('vod_'+idc)))

        else:

            contextmenu.append(('[B][COLOR lightgreen]Dodaj do MOJEJ LISTY[/B][/COLOR]', 'RunPlugin(plugin://plugin.video.polsatgo?mode=DodajUsun&url=%s)'%str(idc)))
        
        
        add_item(name=item.get('title'), url=idc, mode=mud, image=item.get('img'), folder=folder, isPlayable=isplay, infoLabels=item, contextmenu=contextmenu, itemcount=itemz,FANART=FANART)    
    xbmcplugin.endOfDirectory(addon_handle)    
    
def MojaLista():
    headers = {
        'Host': host,
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }
    
    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')
    dane =stoken+'|'+sexpir+'|navigation|getFavoritesWithFlatNavigation'
    authdata=getHmac(dane)
    data = {"id":1,"jsonrpc":"2.0","method":"getFavoritesWithFlatNavigation","params":{"offset":0,"limit":50,"filters":[],"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":clid}}
    response = requests.post(navigate_url, headers=headers, json=data,timeout=15, verify=False).json()
    results = response.get('result',None).get('results',None)
    
    for r in results:
        object = r.get('object',None)
        try:
            tyt = (object.get('title',None)).upper().encode('utf-8')
        except:
            tyt = (object.get('name',None)).upper().encode('utf-8')

        description = (object.get('description',None)).encode('utf-8')
        imag = (object.get('thumbnails',None)[-1].get('src',None)).encode('utf-8')

        id = r.get('value',None)
        contextmenu = []

        if r.get('type',None) == 'category':
            mud = 'vodlist'
            folder = True
            isplay = False
            contextmenu.append(('[B][COLOR red]Usuń z MOJEJ LISTY[/B][/COLOR]', 'RunPlugin(plugin://plugin.video.polsatgo?mode=Usun&url=category_%s)'%str(id)))
        else:
            mud = 'playVOD'
            folder=False
            isplay=False
            contextmenu.append(('[B][COLOR red]Usuń z MOJEJ LISTY[/B][/COLOR]', 'RunPlugin(plugin://plugin.video.polsatgo?mode=Usun&url=vod_%s)'%str(id)))
        add_item(name=tyt, url=id, mode=mud, image=imag, folder=folder, isPlayable=isplay, infoLabels={"title": tyt,'plot':description}, contextmenu=contextmenu,FANART=FANART)    
    xbmcplugin.endOfDirectory(addon_handle)
        
    
def vodList(id):
    
    headers = {
        'Host': host,
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }
    
    stoken = addon.getSetting('sesstoken')
    sexpir = addon.getSetting('sessexpir')

    items = []
    myperms = []
    ff = addon.getSetting('accgroups')
    lista=eval(ff)
    
    for l in lista:
        if 'sc:' in l:
            myperms.append(l)
        if 'oth:' in l:
            myperms.append(l)
        if 'loc:' in l:
            myperms.append(l)
    
    if 'getSubCategories' in id:
        id = id.split('|')[0]
        dane =stoken+'|'+sexpir+'|navigation|getSubCategories'
        authdata=getHmac(dane)
        
        data = {"id":1,"jsonrpc":"2.0","method":"getSubCategories","params":{"catid":int(id),"filters":[],"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":""}}
        
    else:
        dane =stoken+'|'+sexpir+'|navigation|getCategoryContentWithFlatNavigation'
        authdata=getHmac(dane)

        try:
            idc = int(id)
        except:
            idc = id
        data = {"id":1,"jsonrpc":"2.0","method":"getCategoryContentWithFlatNavigation","params":{"catid":idc,"offset":int(offse),"limit":50,"filters":[],"collection":{"type":"sortedby","name":"Alfabetycznie","default":True,"value":"13"},"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":""}}
    

    response = requests.post(navigate_url, headers=headers, json=data,timeout=15, verify=False).json()

    mud='playVOD'
    folder=False
    isplay=False

    try:
    
        aa = response['result']['results']
    except:
        aa = response['result']
    if 'keyCategoryId' in aa[0]:
        mud='vodlist'
        folder=True
        isplay=False
    try:
        otal = response['result']['total']
    except:
        otal = 0

    for i in aa:
        item = {}

        for j in myperms:

            if i.get('thumbnails',None):
                item['img'] = i['thumbnails'][-1]['src'].encode('utf-8')
            else:
                item['img'] = None
            item['id'] = i['id']
            try:
                item['title'] = i['title'].upper().encode('utf-8')
            except:
                item['title'] = i['name'].upper().encode('utf-8')
            item['plot'] = i['description'].encode('utf-8')
            items.append(item)

    dupes = []
    filter = []

    for entry in items:
        if not entry['id'] in dupes:
            filter.append(entry)
            dupes.append(entry['id'])
    items = filter
    itemz= len(items)

    for item in items:

        getid = item.get('id')


        contextmenu = []
        if mud =='playVOD':
            contextmenu.append(('[B][COLOR lightgreen]Dodaj do MOJEJ LISTY[/B][/COLOR]', 'RunPlugin(plugin://plugin.video.polsatgo?mode=DodajUsun&url=%s)'%str('vod_'+getid)))

        else:

            contextmenu.append(('[B][COLOR lightgreen]Dodaj do MOJEJ LISTY[/B][/COLOR]', 'RunPlugin(plugin://plugin.video.polsatgo?mode=DodajUsun&url=%s)'%str(getid)))
        
        add_item(name=item.get('title'), url=getid, mode=mud, image=item.get('img'), folder=folder, isPlayable=isplay, infoLabels={'plot':item.get('plot'),"title": item.get('title')}, contextmenu=contextmenu    , itemcount=itemz,FANART=FANART)
    
    if int(offse)+50<otal:
        add_item(name='Następna strona', url=id, mode='vodlist', image=RESOURCES+'nextpage.png', folder=True, isPlayable=False, infoLabels=None, contextmenu=None, itemcount=itemz,page=int(offse)+50,FANART=FANART)    

    xbmcplugin.endOfDirectory(addon_handle)
    
    
def getHmac(dane):
    skey = addon.getSetting('sesskey')
    import hmac
    import hashlib 
    import binascii
    import base64
    from hashlib import sha256
    ssdalej=dane
    import base64

    def base64_decode(s):
        """Add missing padding to string and return the decoded base64 string."""
        #log = logging.getLogger()
        s = str(s).strip()
        try:
            return base64.b64decode(s)
        except TypeError:
            padding = len(s) % 4
            if padding == 1:
                #log.error("Invalid base64 string: {}".format(s))
                return ''
            elif padding == 2:
                s += b'=='
            elif padding == 3:
                s += b'='
            return base64.b64decode(s)
    secretAccessKey = base64_decode(skey.replace('-','+').replace('_','/'))
    
    auth = hmac.new(secretAccessKey, ssdalej.encode("ascii"), sha256)
    vv= base64.b64encode(bytes(auth.digest())).decode("ascii")

    aa=vv
    bb=ssdalej+'|'+aa.replace('+','-').replace('/','_')
    return bb


def Usun(id):

    kateg,id = id.split('_')
    typ = {"type":kateg,"value":id}

    headers = {
        'Host': host,
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }

    dane =stoken+'|'+sexpir+'|user_content|deleteFromFavorites'
    authdata=getHmac(dane)
    
    
    
    
    data = {"id":1,"jsonrpc":"2.0","method":"deleteFromFavorites","params":{"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":clid,"favorite":typ}}

    
    
    
    
    
    
    
    response = requests.post(user_url, headers=headers, json=data,timeout=15, verify=False).json()
    xbmcgui.Dialog().notification('[B]Info[/B]', 'Usunięto z MOJEJ LISTY' ,xbmcgui.NOTIFICATION_INFO, 6000)        
    xbmc.executebuiltin("Container.Update({0}?mode=mojalista,replace)".format(sys.argv[0]))
    
def dodajusun(id):

    kateg = 'category'

    if 'vod' in id:
        kateg,id = id.split('_')
    typ = {"type":kateg,"value":id}

    headers = {
        'Host': host,
        'User-Agent': UA,
        'Accept': 'application/json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': origin,
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }

    dane =stoken+'|'+sexpir+'|user_content|addToFavorites'
    authdata=getHmac(dane)
    
    
    
    
    data = {"id":1,"jsonrpc":"2.0","method":"addToFavorites","params":{"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":clid,"favorite":typ}}

    
    
    
    
    
    
    
    response = requests.post(user_url, headers=headers, json=data,timeout=15, verify=False).json()
    dane =stoken+'|'+sexpir+'|navigation|getFavoritesWithFlatNavigation'
    authdata=getHmac(dane)
    data = {"id":1,"jsonrpc":"2.0","method":"getFavoritesWithFlatNavigation","params":{"offset":0,"limit":40,"filters":[],"ua":uapg,"deviceId":{"type":"other","value":devid},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":osinfo},"authData":{"sessionToken":authdata},"clientId":clid}}
    response = requests.post(navigate_url, headers=headers, json=data,timeout=15, verify=False).json()

    results = response.get('result',None).get('results',None)
    for r in results:
        if r.get('value',None) == id:
            komunikat = 'DODANE DO LISTY'
            break
        else:
            continue
    xbmcgui.Dialog().notification('[B]Info[/B]', komunikat,xbmcgui.NOTIFICATION_INFO, 6000)        

    
    return

    
def router(paramstring):
    args = dict(urlparse.parse_qsl(paramstring))
    
    if args:
        mode = args.get('mode', None)

        if mode == 'playCPGO':
            playCPGO(exlink)
        elif mode == 'live':
            live()    
        elif mode == 'tvcpgo':
            tvmain()    
        elif mode == 'vodmain':
            vodmain()
        elif mode == 'vodlist':
            vodList(exlink)
        
        elif mode == 'playVOD':
            playVOD(exlink)
        
        elif mode == 'vodszukaj':
            query = xbmcgui.Dialog().input(u'Szukaj, Podaj tytuł...', type=xbmcgui.INPUT_ALPHANUM)
            if query:          
                vodSzukaj(query)
            
        elif mode == 'settings':
            addon.openSettings()
            xbmc.executebuiltin('Container.Refresh()')
        elif mode =='DodajUsun':
            dodajusun(exlink)
        elif mode =='Usun':
            Usun(exlink)
        elif mode == 'mojalista':
            MojaLista()
            
    else:
        home()     
        
        
if __name__ == '__main__':
    router(sys.argv[2][1:])