# -*- coding: UTF-8 -*-

import sys, os, re, json, base64, math, random

PY3 = sys.version_info >= (3,0,0)
if PY3:
# for Python 3
    to_unicode = str

    from urllib.parse import unquote, parse_qs, parse_qsl, quote, urlencode, quote_plus
    from resources.lib.cmf3 import parseDOM
    
else:
    # for Python 2
    to_unicode = unicode

    from urllib import unquote, quote, urlencode, quote_plus
    from urlparse import parse_qsl, parse_qs
    from resources.lib.cmf2 import parseDOM


import xbmc, xbmcvfs

import requests
import xbmcgui
import xbmcplugin
import xbmcaddon

import inputstreamhelper



#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.cdaplMB')

PATH            = addon.getAddonInfo('path')
try:
    DATAPATH        = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
except:
    DATAPATH    = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
    
if not os.path.exists(DATAPATH):
    os.makedirs(DATAPATH)


RESOURCES       = PATH+'/resources/'
ikona = RESOURCES+'../icon.png'
FANART=RESOURCES+'../fanart.jpg'

exlink = params.get('url', None)
nazwa= params.get('title', None)
rys = params.get('image', None)
page = params.get('page',[1])[0]


refr_token = addon.getSetting('refr_token')
login_id = addon.getSetting('login_id')
wybormax = int(addon.getSetting('wybormax'))

squalv = addon.getSetting('szukqualV')
squaln = addon.getSetting('szukqualN') if squalv else 'każda'
sduratv = addon.getSetting('szukduratV')
sduratn = addon.getSetting('szukduratN') if sduratv else 'każda'
szuksortv = addon.getSetting('szuksortV')
szuksortv = '&sort=date' if not szuksortv else szuksortv
szuksortn = addon.getSetting('szuksortN') if szuksortv else 'najnowsze'
if not szuksortn:
    szuksortn = 'najnowsze'

fsortv = addon.getSetting('fsortV')
fsortn = addon.getSetting('fsortN') if fsortv else 'popularne w ciągu ostatnich 30 dni'
ssortv = addon.getSetting('ssortV')
ssortn = addon.getSetting('ssortN') if ssortv else 'popularne w ciągu ostatnich 30 dni'
dsortv = addon.getSetting('dsortV')
dsortn = addon.getSetting('dsortN') if dsortv else 'popularne w ciągu ostatnich 30 dni'


fkatv = addon.getSetting('fkatV')
fkatn = addon.getSetting('fkatN') if fkatv else 'wszystkie'

fwerv = addon.getSetting('fwerV')
fwern = addon.getSetting('fwerN') if fwerv else 'wszystkie'
swerv = addon.getSetting('swerV')
swern = addon.getSetting('swerN') if swerv else 'wszystkie'
dwerv = addon.getSetting('dwerV')
dwern = addon.getSetting('dwerN') if dwerv else 'wszystkie'

ftypv = addon.getSetting('ftypV')
ftypn = addon.getSetting('ftypN') if ftypv else 'premium'
stypv = addon.getSetting('stypV')
stypn = addon.getSetting('stypN') if stypv else 'premium'
dtypv = addon.getSetting('dtypV')
dtypn = addon.getSetting('dtypN') if dtypv else 'premium'



dataf =  addon.getSetting('fdata')    
datas =  addon.getSetting('sdata')    
datad =  addon.getSetting('ddata')  
dataszukaj =  addon.getSetting('szukajdata') 

dataszukaj = dataszukaj if dataszukaj else szuksortv
wybornapisow = True




sess = requests.Session()
def build_url(query):
    return base_url + '?' + urlencode(query)

def add_item(url, name, image, mode, folder=False, IsPlayable=True, infoLabels=False, contextmenu=None,itemcount=1, page=1,fanart=FANART,moviescount=0):
    list_item = xbmcgui.ListItem(label=name)

    if IsPlayable:
        list_item.setProperty("IsPlayable", 'True')
    if not infoLabels:
        infoLabels={'title': name,'plot':name}
    if contextmenu:
        out=contextmenu
        list_item.addContextMenuItems(out, replaceItems=True)
    list_item.setInfo(type="video", infoLabels=infoLabels)    
    list_item.setArt({'thumb': image, 'poster': image, 'banner': image, 'icon': image, 'fanart': FANART})
    ok=xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url = build_url({'mode': mode, 'url' : url, 'page' : page, 'moviescount' : moviescount,'title':name,'image':image}),            
        listitem=list_item,
        isFolder=folder)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")
    return ok
    
def getJson(url,post=None, params=None, auth=None, data=None):
    acc_token = addon.getSetting('acc_token')
    headers = {
    'User-Agent': 'pl.cda 1.0 (version 1.2.115 build 16083; Android 9; Samsung SM-J330F)',
    'Accept': 'application/vnd.cda.public+json',
    'Host': 'api.cda.pl',}

    if not auth:
        headers.update({'Authorization': 'Basic YzU3YzBlZDUtYTIzOC00MWQwLWI2NjQtNmZmMWMxY2Y2YzVlOklBTm95QlhRRVR6U09MV1hnV3MwMW0xT2VyNWJNZzV4clRNTXhpNGZJUGVGZ0lWUlo5UGVYTDhtUGZaR1U1U3Q'})
    else:
        headers.update({'Authorization': 'Bearer '+acc_token})
    if not post:
        jsdata = sess.get(url, headers=headers, params=params, verify=False).json()
    else:

        jsdata = sess.post(url, headers=headers, params=params, data=data,verify=False).json()
        
    return jsdata

def LogowanieCda():
    username = addon.getSetting('username')
    password = addon.getSetting('password')  
    refr_token = addon.getSetting('refr_token')  
    if username and password:
        
        if not refr_token:
            import hashlib
            import hmac
            import base64
            #if sys.version_info >= (3,0,0):
            passw = password.encode('utf-8') if sys.version_info >= (3,0,0) else password
            md5password=hashlib.md5(passw).hexdigest()    
            secret = "s01m1Oer5IANoyBXQETzSOLWXgWs01m1Oer5bMg5xrTMMxRZ9Pi4fIPeFgIVRZ9PeXL8mPfXQETZGUAN5StRZ9P"
            if sys.version_info >= (3,0,0):
                secret = secret.encode('utf-8')
                md5password = md5password.encode('utf-8')
            hashedpassword = base64.b64encode(hmac.new(secret, md5password, digestmod=hashlib.sha256).digest())
            if sys.version_info >= (3,0,0):
                hashedpassword = hashedpassword.decode('utf-8')
            
            hashedpassword = hashedpassword.replace("/","_").replace("+","-").replace("=","")
            params = (
                    ('grant_type', 'password'),
                    ('login', username),
                    ('password', hashedpassword),
                    )

            response = getJson(url='https://api.cda.pl/oauth/token', post=True, params=params)#.json()
            tok = response.get('access_token',None)

            if tok:
                addon.setSetting('acc_token',tok)
                refr = response.get('refresh_token',None)
                addon.setSetting('refr_token',username+'|'+refr)
                profil = getProfile()
                return True,profil
                
            else:
                return '',''
        else:
            usr, refr_token=refr_token.split('|')

            if username == usr:

                refr_token = refr_token.split('|')[-1]
                params = (
                        ('grant_type', 'refresh_token'),
                        ('refresh_token', refr_token),)
    
                response = getJson(url='https://api.cda.pl/oauth/token', post=True, params=params)#.json()
                tok = response.get('access_token',None)
                if tok:
                    addon.setSetting('acc_token',tok)
                    refr = response.get('refresh_token',None)
                    addon.setSetting('refr_token',username+'|'+refr)
                    profil = getProfile()
                    return True,profil
                else:
                    return '',''
            else:
                addon.setSetting('refr_token','')
                return LogowanieCda()
    else:
        return '',''
def getProfile():
    vv=''
    response = getJson(url='https://api.cda.pl/user/me', auth=True)#.json()
    response2 = getJson(url='https://api.cda.pl/user/me/premium', auth=True)#.json()
    login_name = response.get('login',None)
    login_id = response.get('id',None)
    addon.setSetting('login_id',str(login_id))

    status = response2.get('status',None)
    if status.get('premium',None) == 'tak':
        wygasa = status.get('wygasa',None)
        wygasa = wygasa if wygasa else ''

        dod = ' [COLOR gold](premium)[/COLOR]'
        if wygasa:
            dod = ' [COLOR gold](premium) do '+ str(wygasa)+'[/COLOR]'
        if status.get('tv_access',None) != 'false':
            tvaccbas = status.get("tv_access_expire_at",None).get("basic",None)  
            tvaccbas = status.get("tv_access_expire_at",None).get("full",None)  
        login_name = login_name+dod#'|premium do '+ str(wygasa)
    return login_name
def home():
    log,profil = LogowanieCda()
    if log:
        
        add_item('', 'Zalogowano jako:%s'%(str(profil)), 'DefaultMovies.png', "  ", False)  
        add_item('', 'Ulubione', 'DefaultMovies.png', "ulubione", True) 
        add_item('', 'CDA TV - Telewizja Online', 'DefaultMovies.png', "listtv", True) 

        add_item('f', "Filmy", 'DefaultMovies.png', "menucda", True) 
        add_item('s', "Seriale", 'DefaultMovies.png', "menucda", True) 
        
        
        add_item('d', "Dla dzieci", 'DefaultMovies.png', "menucda", True) 
        add_item('u', "Wideo użytkowników", 'DefaultMovies.png', "listcontent", True) 
    
        add_item('', '[COLOR lightblue]Szukaj[/COLOR]', 'DefaultAddonsSearch.png', "search", True)    
    else:
        add_item('', 'Zaloguj', 'DefaultMovies.png', "logowanie", False)
    xbmcplugin.endOfDirectory(addon_handle)
 
def getPlot(title,html):
    plot=''
    title=title.replace('+','.')
    regex=title+"(.+?)timeline-station"
    try:
        dane=re.findall(regex,html,re.DOTALL)[0]
        plots=re.findall("""class="title.+?>(.+?)<.+?class="time">(.+?)<.+?class="time-stop">(.+?)<""",dane,re.DOTALL)
        plot=''
        if plots:
            for tyt,rozp,zakon in plots:
                zakon=zakon.replace('&nbsp;-',' -')
                plot+='[B][COLOR yellowgreen]'+rozp+zakon+'[/COLOR] '+tyt+'[/B][CR]'
        else:
            plot=''
    except:
        plot=''
        return plot    
    return plot   
    
def getHtml():
    UA='Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
    headers = {
        'User-Agent': UA,
        'X-Requested-With': 'XMLHttpRequest',}
    data = {
    'stations':'1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180'}
    res = requests.post('https://m.teleman.pl/profile', headers=headers, data=data,timeout=30,verify=False)
    headers = {
        'User-Agent': UA,
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',}
    
    html = requests.get('https://m.teleman.pl/timeline', headers=headers,cookies=res.cookies,timeout=30,verify=False).content
    if PY3:     
        html = html.decode(encoding='utf-8', errors='strict')
    html = parseDOM(html, 'div', attrs={'class': "timeline"})[0]
    
    
    #html=html.replace('/stations/13-Ulica"','13 Ulica"') 
    #html=html.replace('/stations/Ale-Kino"','ale kino+"') 
    html=html.replace('/stations/AMC"','amc_hd"') 
    #html=html.replace('/stations/Animal-Planet-HD"','Animal Planet"') 
    #html=html.replace('/stations/AXN"','AXN"') 
    #html=html.replace('/stations/AXN-Black"','AXN Black"') 
    #html=html.replace('/stations/AXN-Spin"','AXN Spin"') 
    html=html.replace('/stations/AXN-White"','AXN White"') 
    html=html.replace('/stations/BBC-Brit"','bbc_brit_hd"') 
    html=html.replace('/stations/BBC-Earth"','bbc_earth_hd"') 
    html=html.replace('/stations/BBC-First"','bbc_first_hd"') 
    html=html.replace('/stations/BBC-Lifestyle"','bbc_lifestyle_hd"') 
    #html=html.replace('/stations/Boomerang"','Boomerang"') 
    #html=html.replace('/stations/CanalPlus-1"','CANAL+ 1"') 
    #html=html.replace('/stations/CanalPlus-4K"','CANAL+ 4K Ultra HD"') 
    #html=html.replace('/stations/CanalPlus-Dokument"','CANAL+ Dokument"') 
    #html=html.replace('/stations/Domo"','CANAL+ Domo"') 
    #html=html.replace('/stations/CanalPlus-Family"','CANAL+ Family"') 
    #html=html.replace('/stations/CanalPlus-Film"','CANAL+ Film"') 
    #html=html.replace('/stations/Kuchnia-TV"','CANAL+ Kuchnia"') 
    #html=html.replace('/stations/CanalPlus"','CANAL+ Premium"') 
    #html=html.replace('/stations/CanalPlus-Seriale"','CANAL+ Seriale"') 
    #html=html.replace('/stations/CanalPlus-Sport"','CANAL+ Sport"') 
    #html=html.replace('/stations/CanalPlus-Sport-2"','CANAL+ Sport 2"') 
    #html=html.replace('/stations/CanalPlus-Sport-3"','CANAL+ Sport 3"') 
    #html=html.replace('/stations/CanalPlus-Sport-4"','CANAL+ Sport 4"') 
    #html=html.replace('/stations/Cartoon-Network"','Cartoon Network"') 
    html=html.replace('/stations/CBS-Europa"','cbs_europa_hd"') 
    html=html.replace('/stations/CBS-Reality"','cbs_reality_hd"') 
    html=html.replace('/stations/Crime-Investigation-Network"','polsat_crime_investigation_hd"') 
    #html=html.replace('/stations/Cinemax"','Cinemax"') 
    #html=html.replace('/stations/Cinemax2"','Cinemax 2"') 
    #html=html.replace('/stations/Comedy-Central"','Comedy Central"') 
    #html=html.replace('/stations/Discovery-Channel"','Discovery Channel"') 
    #html=html.replace('/stations/Discovery-Historia"','Discovery Historia"') 
    #html=html.replace('/stations/Discovery-Life"','Discovery Life"') 
    #html=html.replace('/stations/Discovery-Science"','Discovery Science"') 
    #html=html.replace('/stations/Disney-Channel"','Disney Channel"') 
    #html=html.replace('/stations/Disney-Junior"','Disney Junior"') 
    #html=html.replace('/stations/Disney-XD"','Disney XD"') 
    #html=html.replace('/stations/DTX"','DTX (d. Discovery Turbo Xtra)"') 
    #html=html.replace('/stations/Eleven-Sports-1"','Eleven Sports 1"') 
    #html=html.replace('/stations/Eleven-Sports-2"','Eleven Sports 2"') 
    #html=html.replace('/stations/Eleven-Sports-3"','Eleven Sports 3"') 
    #html=html.replace('/stations/Eleven-4"','Eleven Sports 4"') 
    html=html.replace('/stations/Epic-Drama"','"epic_drama_hd"') 
    #html=html.replace('/stations/Eurosport"','Eurosport 1"') 
    #html=html.replace('/stations/Eurosport-2"','Eurosport 2"') 
    html=html.replace('/stations/Extreme"','extreme_sports_hd"') 
    html=html.replace('/stations/Filmbox-Action"','filmbox_action"') 
    #html=html.replace('/stations/FilmBox-Arthouse"','FilmBox Arthouse"') 
    html=html.replace('/stations/Filmbox-Extra-HD"','filmbox_extra_hd"') 
    html=html.replace('/stations/Filmbox-Family"','filmbox_family"') 
    html=html.replace('/stations/Filmbox-Premium"','filmbox_premium_hd"') 
    #html=html.replace('/stations/Fokus-TV"','Fokus TV"') 
    #html=html.replace('/stations/Food-Network"','Food Network"') 
    #html=html.replace('/stations/FOX"','FOX"') 
    #html=html.replace('/stations/FOX-Comedy"','FOX Comedy"') 
    #html=html.replace('/stations/HBO"','HBO"') 
    #html=html.replace('/stations/HBO2"','HBO 2"') 
    #html=html.replace('/stations/HBO3"','HBO 3"') 
    #html=html.replace('/stations/HGTV"','HGTV"') 
    html=html.replace('/stations/History"','history_hd"') 
    html=html.replace('/stations/H2"','history2_hd"') 
    #html=html.replace('/stations/ID"','ID"') 
    html=html.replace('/stations/Kino-Polska"','kino_polska_hd"') 
    html=html.replace('/stations/Kino TV"','kino_tv_hd"') 
    #html=html.replace('/stations/Lifetime"','Lifetime"') 
    #html=html.replace('/stations/Metro-TV"','Metro TV"') 
    #html=html.replace('/stations/Mezzo"','Mezzo"') 
    #html=html.replace('/stations/MiniMini"','MiniMini+"') 
    #html=html.replace('/stations/MTV-Polska"','MTV Polska"') 
    #html=html.replace('/stations/Nat-Geo-People"','Nat Geo People"') 
    #html=html.replace('/stations/National-Geographic"','National Geographic"') 
    #html=html.replace('/stations/Nat-Geo-Wild"','National Geographic Wild"') 
    #html=html.replace('/stations/Nickelodeon"','Nickelodeon"') 
    #html=html.replace('/stations/Nicktoons"','Nicktoons"') 
    #html=html.replace('/stations/Nowa-TV"','Nowa TV"') 
    #html=html.replace('/stations/nSport"','nSport+"') 
    #html=html.replace('/stations/Paramount-Channel"','Paramount Channel"') 
    #html=html.replace('/stations/Planete"','PLANETE+"') 
    html=html.replace('/stations/Polonia-1"','polonia1_hd"') 
    html=html.replace('/stations/Polsat"','polsat"') 
    #html=html.replace('/stations/Polsat-2"','Polsat 2"') 
    #html=html.replace('/stations/Polsat-Cafe"','Polsat Cafe"') 
    #html=html.replace('/stations/Comedy-Central-Family"','Polsat Comedy Central Extra"') 
    #html=html.replace('/stations/Polsat-Doku"','Polsat Doku"') 
    #html=html.replace('/stations/Polsat-Film"','Polsat Film"') 
    #html=html.replace('/stations/Polsat-Games"','Polsat Games"') 
    #html=html.replace('/stations/Polsat-News"','Polsat News"') 
    #html=html.replace('/stations/Polsat-Play"','Polsat Play"') 
    #html=html.replace('/stations/Polsat-Rodzina"','Polsat Rodzina"') 
    #html=html.replace('/stations/Polsat-Seriale"','Polsat Seriale"') 
    #html=html.replace('/stations/Polsat-Sport"','Polsat Sport"') 
    #html=html.replace('/stations/Polsat-Sport-Extra"','Polsat Sport Extra"') 
    #html=html.replace('/stations/Polsat-Sport-Fight"','Polsat Sport Fight"') 
    #html=html.replace('/stations/Polsat-Sport-News"','Polsat Sport News"') 
    #html=html.replace('/stations/Polsat-Sport-Premium-1"','Polsat Sport Premium 1"') 
    #html=html.replace('/stations/Polsat-Sport-Premium-2"','Polsat Sport Premium 2"') 
    html=html.replace('/stations/Viasat-Explorer"','polsat_viasat_explore_hd""') 
    html=html.replace('/stations/Viasat-History"','polsat_viasat_history_hd"') 
    html=html.replace('/stations/Viasat-Nature"','polsat_viasat_nature_hd"') 
    html=html.replace('/stations/Romance-TV"','romance_tv_hd"') 
    #html=html.replace('/stations/SCI-FI"','SCI FI"') 
    #html=html.replace('/stations/SportKlub"','SportKlub"') 
    html=html.replace('/stations/Stopklatka-TV"','stopklatka_tv_hd"') 
    html=html.replace('/stations/Sundance-Channel-HD"','sundance_hd"') 
    #html=html.replace('/stations/Super-Polsat"','Super Polsat"') 
    #html=html.replace('/stations/Superstacja"','Superstacja"') 
    html=html.replace('/stations/Tele-5"','tele5_hd"') 
    #html=html.replace('/stations/TLC"','TLC"') 
    #html=html.replace('/stations/TNT"','TNT"') 
    #html=html.replace('/stations/Travel-Channel"','Travel"') 
    #html=html.replace('/stations/TTV"','TTV"') 
    html=html.replace('/stations/TV4"','tv4"') 
    #html=html.replace('/stations/TV6"','TV 6"') 
    #html=html.replace('/stations/Puls"','TV Puls"') 
    #html=html.replace('/stations/Puls-2"','TV Puls 2"') 
    html=html.replace('/stations/TV-Republika"','tv_republika_hd"') 
    html=html.replace('/stations/TV-Trwam"','tv_trwam"') 
    #html=html.replace('/stations/TVN"','TVN"') 
    #html=html.replace('/stations/TVN-Siedem"','TVN 7"') 
    #html=html.replace('/stations/TVN-Fabula"','TVN Fabuła"') 
    #html=html.replace('/stations/TVN-Style"','TVN Style"') 
    #html=html.replace('/stations/TVN-Turbo"','TVN Turbo"') 
    #html=html.replace('/stations/TVN24"','TVN24"') 
    #html=html.replace('/stations/TVN-24-Biznes-i-Swiat"','TVN24 Biznes i Świat"') 
    html=html.replace('/stations/TVP-1"','tvp1_hd"') 
    html=html.replace('/stations/TVP-2"','tvp2_hd"') 
    #html=html.replace('/stations/TVP-ABC"','TVP ABC"') 
    #html=html.replace('/stations/tvp-dokument"','TVP Dokument"') 
    #html=html.replace('/stations/TVP-HD"','TVP HD"') 
    #html=html.replace('/stations/TVP-Historia"','TVP Historia"') 
    #html=html.replace('/stations/TVP-Info"','TVP Info"') 
    #html=html.replace('/stations/TVP-Kobieta"','TVP Kobieta"') 
    #html=html.replace('/stations/TVP-Kultura"','TVP Kultura"') 
    #html=html.replace('/stations/tvp-kultura-2"','TVP Kultura 2"') 
    #html=html.replace('/stations/TVP-Polonia"','TVP Polonia"') 
    #html=html.replace('/stations/TVP-Rozrywka"','TVP Rozrywka"') 
    #html=html.replace('/stations/TVP-Seriale"','TVP Seriale"') 
    #html=html.replace('/stations/TVP-Sport"','TVP Sport"') 
    html=html.replace('/stations/TVS"','tvs"') 
    html=html.replace('/stations/WP"','wp_hd"') 
    html=html.replace('/stations/Zoom-TV"','zoom_tv_hd"') 
    return html
 
 
def ListTv():
    content = getHtml()
    url = 'https://api.cda.pl/tv/channels'
    response = getJson(url=url, auth=True)
    channels = response.get("channels",None)
    if channels:
        for chan in channels:
            tytul = chan.get("title",None).encode('utf-8')
            urltyt = chan.get("url",None)
            imag = chan.get("logo_light",None)
            drm_header_value = chan.get("drm_header_value",None)
            manifest_dash = chan.get("manifest_dash",None)
            if not manifest_dash:
                continue
            drm_widevine = chan.get("drm_widevine",None)
            drm_header_name = chan.get("drm_header_name",None)

            urlid = {'dash':manifest_dash, 'widevine':drm_widevine, 'drm_header_value': drm_header_value,'drm_header_name':drm_header_name}
            try:
                ab= json.dumps(urlid)
            except:
                pass

            actprogram = chan.get("program",None).get("actual",None)
            plottit = actprogram.get("title",None)
            plotstart = actprogram.get("start_time",None)
            plotend = actprogram.get("end_time",None)

            plotmain='[B][COLOR yellowgreen]'+plotstart+' - '+plotend+'[/COLOR] '+plottit+'[/B][CR]'

            plot = getPlot(urltyt,content)
            plot = plot if plot else plotmain
            add_item(name=tytul, url=ab, mode='playtv', image=imag, folder=False, infoLabels={'plot':plot,'title':tytul})    
        xbmcplugin.endOfDirectory(addon_handle)
    else:
        xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Brak materiałów do wyświetlenia[CR]lub nie masz dostępu (premium).',xbmcgui.NOTIFICATION_INFO, 8000,False)

    
    
def getFolder(foldid,pg):
    fav = ''
    try:
        autid, vidfold, fav = foldid.split('|')
    except:
        
        autid, vidfold = foldid.split('|')
    
    
    url = 'https://api.cda.pl/user/%s/folders/%s/files?order=created_asc&page=%s&count=20'%(str(autid),str(vidfold),str(pg))
    
    url ='https://api.cda.pl/user/%s/favorites/%s/files?order=created_asc&page=%s&count=20'%(str(autid),str(vidfold),str(pg)) if fav else url
    response = getJson(url=url, auth=True)

    try:
        totpages = response.get('paginator',None).get('total_pages',None)
    except:
        totpages = 0
    datasy = response.get('data',None)


    
    for dt in datasy:
        
        tytul = dt.get('title',None).encode('utf-8')
        imag = dt.get('thumb',None).encode('utf-8')

        vid = dt.get('id',None).encode('utf-8')

        mud = 'playvid' 
        fold = False
        if dt.get('is_series',None):
            mud = 'listserial'
            fold = True
            
    
        add_item(name=tytul, url=vid, mode=mud, image=imag, folder=fold, infoLabels={'plot':tytul,'title':tytul})    

    
    
    if datasy:
        if int(pg)<int(totpages):

            add_item(name='[COLOR blue]>> Nastepna strona [/COLOR]', url=foldid, mode='getfolder', image='', folder=True, page=int(pg)+1)
        xbmcplugin.endOfDirectory(addon_handle)
    else:
        xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Brak materiałów do wyświetlenia[CR]Może zmień ustawienia.',xbmcgui.NOTIFICATION_INFO, 8000,False)
def ListSeriale(id,pg):
    vv=''
    url = 'https://api.cda.pl/video/'+str(id)

    response = getJson(url=url, auth=True)
    videodata = response.get("video",None)
    
    vidfold = videodata.get('folder_id',None) 
    autid = videodata.get('author',None).get('id',None) 
    

    foldid = str(autid)+'|'+str(vidfold)
    getFolder(foldid,pg)


def ListContent(id,pg,srch=''):

    if not srch:
        vv=''

        url = 'https://api.cda.pl/video?type=premium&page='+str(pg)+'&count=20'
        if 'f' in id:
            url +=dataf
        elif 's' in id:
            url +=datas+'&category=43'
        elif 'd' in id:
            url +=datas+'&category=35'
        elif 'u' in id:
            url = 'https://api.cda.pl/video?type=promoted&page='+str(pg)+'&count=20'
    else:
            url = srch+dataszukaj

    response = getJson(url=url, auth=True)#.json()
    cvb=''
    totpages = response.get('paginator',None).get('total_pages',None)
    datasy = response.get('data',None)
    if 'u' in id:
        datasy = response.get('videos',None)

    for dt in datasy:
        
        tytul = dt.get('title',None).encode('utf-8')
        try:
            imag = dt.get('cover',None).encode('utf-8')
        except:
            imag = dt.get('thumb',None).encode('utf-8')
        durat = dt.get('duration',None)
        qual = dt.get('quality',None).encode('utf-8')
        vid = dt.get('id',None).encode('utf-8')
        premium = dt.get('premium',None)#.encode('utf-8')
        premium_free = dt.get('premium_free',None)#.encode('utf-8')#'premium_free'
        mud = 'playvid' 
        fold = False
        if dt.get('is_series',None):
            mud = 'listserial'
            fold = True
        contextmenu = []
        if dt.get('author',None):
            foldid = dt.get('author',None).get('id',None)
            foldname = dt.get('author',None).get('login',None) if sys.version_info >= (3,0,0) else dt.get('author',None).get('login',None).encode('utf-8')
            

            contextmenu.append(('Pokaż foldery[B][COLOR gold] %s[/B][/COLOR]'%str(foldname), 'Container.Update(%s)'% build_url({'mode': 'foldery', 'url' : str(foldid)})),)
            
        elif mud == 'playvid':
            contextmenu.append(('[B][COLOR gold]Dodaj do ulubionych[/B][/COLOR]', 'Container.Update(%s)'% build_url({'mode': 'dodaj', 'url' : str(vid)})),)

        add_item(name=tytul, url=vid, mode=mud, image=imag, folder=fold, infoLabels={'plot':tytul,'title':tytul,'duration':int(durat),'code':qual},contextmenu=contextmenu)    

    
    
    if datasy:
        if int(pg)<int(totpages):

            add_item(name='[COLOR blue]>> Nastepna strona [/COLOR]', url=id, mode='listcontent', image='', folder=True, page=int(pg)+1)
        xbmcplugin.endOfDirectory(addon_handle)
    else:
        xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Brak materiałów do wyświetlenia[CR]Może zmień ustawienia.',xbmcgui.NOTIFICATION_INFO, 8000,False)

def dodaj(id):
    url='https://api.cda.pl/user/%s/favorites'%(login_id)
    data = {'file_id': str(id)}
    vv=''

    response = getJson(url=url, auth=True, post=True, data=data)

    try:
        if response.get('file',None).get('status',None) == 'ok':
            xbmcgui.Dialog().notification('[B]Info[/B]', 'Dodano do ulubionych',xbmcgui.NOTIFICATION_INFO, 8000,False)
        else:
            xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie udało się dodać[CR]do ulubionych.',xbmcgui.NOTIFICATION_INFO, 8000,False)
    except:
            xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie udało się dodać[CR]do ulubionych.',xbmcgui.NOTIFICATION_INFO, 8000,False)
    return
    
 

def ListFolders(foldidm,pg,fav=False):

    id,foldid = foldidm.split('|')
    url ='https://api.cda.pl/user/%s/folders/%s?page=%s&count=25'%(str(id),str(foldid),str(pg))
    url ='https://api.cda.pl/user/%s/favorites/%s?page=%s&count=25'%(str(id),str(foldid),str(pg)) if fav else url
    response1 = getJson(url=url, auth=True)
    
    url = 'https://api.cda.pl/user/%s/folders/%s/files?order=created_asc&page=%s&count=25'%(str(id),str(foldid),str(pg))
    url ='https://api.cda.pl/user/%s/favorites/%s/files?order=created_asc&page=%s&count=25'%(str(id),str(foldid),str(pg)) if fav else url
    response2 = getJson(url=url, auth=True)
    total_pages = response2.get('paginator',None).get('total_pages')

    foldery = response1.get('folder',None).get('folders',None)
    datasy = foldery.get('data',None)
    for dt in datasy:
        try:
            tytul = dt.get('name',None).encode('utf-8')
        except:
            tytul = dt.get('title',None).encode('utf-8')
        foldid = dt.get('id',None)#.encode('utf-8')
        hrefn = str(id)+'|'+str(foldid)
        files_count = dt.get('files_count',None)
        folders_count = dt.get('folders_count',None)

        if PY3:
            ABC = (' [[COLOR gold]%s files[/COLOR]] [[COLOR gold]%s folders[/COLOR]]'%(str(files_count),str(folders_count))).encode(encoding='utf-8', errors='strict')

        else:
            ABC = (' [[COLOR gold]%s files[/COLOR]] [[COLOR gold]%s folders[/COLOR]]'%(str(files_count),str(folders_count)))

        tytul = tytul + ABC
        mud = 'listfoldersfav' if fav else 'listfolders'
        add_item(name=tytul, url=hrefn, mode=mud, image=ikona, folder=True, page=1)
    pliki = response2.get('data',None)
    for plik in pliki:
        try:
            
            tytul = plik.get('title',None).encode('utf-8')
        except:
            tytul = plik.get('name',None).encode('utf-8')
        imag = plik.get('thumb',None).encode('utf-8')
    
        vid = plik.get('id',None).encode('utf-8')
    
        mud = 'playvid' 
        fold = False
        if plik.get('is_series',None):
            mud = 'listserial'
            fold = True
            
    
        add_item(name=tytul, url=vid, mode=mud, image=imag, folder=fold, infoLabels={'plot':tytul,'title':tytul}) 
    
    if datasy or pliki:
        if int(pg)<int(total_pages):
            mud = 'listfoldersfav' if fav else 'listfolders'
            add_item(name='[COLOR blue]>> Nastepna strona [/COLOR]', url=foldidm, mode=mud, image='', folder=True, page=int(pg)+1)
    

        xbmcplugin.endOfDirectory(addon_handle)

def Foldery(id,pg,fav=False):
    url = 'https://api.cda.pl/user/%s/folders'%str(id)
    url = 'https://api.cda.pl/user/%s/favorites'%str(id) if fav else url
    response = getJson(url=url, auth=True)
    alldata = response.get('folder',None)
    folders_count = alldata.get('folders_count',None)
    files_count = alldata.get('files_count',None)
    
    foldid = alldata.get('id',None)
    ntid = str(id)+'|'+str(foldid)
    return ListFolders(ntid,pg,fav)
    
        
def PlayVid(id,tv=False):

    if not tv:

        url = 'https://api.cda.pl/video/'+str(id)
        
        response = getJson(url=url, auth=True)
        if 'access_token_expired' in response:
            log,profil = LogowanieCda()    
            response = getJson(url=url, auth=True)
        videodata = response.get("video",None)

        tytul = videodata.get("title",None).encode('utf-8')
        try:
            descr = videodata.get("description",None).encode('utf-8')
        except:
            descr = tytul
        try:
            img = videodata.get("cover",None).encode('utf-8')
            thumb_premium = videodata.get("thumb_premium",None).encode('utf-8')
        
        except:
            
            
            img = videodata.get("thumb",None).encode('utf-8')
            thumb_premium = img
        durat = int(videodata.get("duration",None))
        genre = videodata.get("categories",None)

        try:
            kateg = ','.join([(x.strip()).encode('utf-8') for x in genre]) if genre else ''
        except:
            kateg = ','.join([(x.strip()) for x in genre]) if genre else ''
        qualities = videodata.get("qualities",None)
        if not wybormax:
            ab=max(qualities,key=lambda items:int(items["name"].replace('p','')))    
            stream_url= ab.get('file',None)
        else:
            pokolei = sorted(qualities, key=lambda items: int(items["name"].replace('p','')),reverse=True)
            out=[]
    
            for k in pokolei:
    
                href = k.get('file',None)
    
                label = k.get('name',None)
                out.append({'label':label,'url':href})
    
            labels = [x.get('label') for x in out]
            sel = xbmcgui.Dialog().select('Wybierz jakość:',labels)    
            if sel>-1:
                stream_url=out[sel].get('url')
    
            else:
                quit()
    
            
    else:
        abn=''
        jsdata=json.loads(id)
        stream_url = jsdata.get('dash',None)
        lic_url = jsdata.get('widevine',None)
        drm_header_value = jsdata.get('drm_header_value',None)
        drm_header_name = jsdata.get('drm_header_name',None)

        nmm=''
    play_item = xbmcgui.ListItem(path=stream_url)
    play_item.setProperty("IsPlayable", "true")    

    if not tv:
        play_item.setArt({'thumb': thumb_premium, 'poster': img, 'banner': img, 'fanart': FANART})
        play_item.setInfo(type="Video", infoLabels={"title": tytul,'plot':descr, 'duration':durat,'genre':kateg})
    else:
        PROTOCOL = 'mpd'
        DRM = 'com.widevine.alpha'

        is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
        if is_helper.check_inputstream():
            play_item.setArt({'thumb': rys, 'poster': rys, 'banner': rys, 'fanart': FANART})
            play_item.setInfo(type="Video", infoLabels={"title": nazwa,'plot':nazwa})
            play_item.setMimeType('application/xml+dash')
            play_item.setContentLookup(False)
            if sys.version_info >= (3,0,0):
                play_item.setProperty('inputstream', is_helper.inputstream_addon)
            else:
                play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)    
            if lic_url:
                play_item.setProperty('inputstream.adaptive.license_type', DRM)

                hea = 'Content-Type=&%s=%s'%(str(drm_header_name),str(drm_header_value))

                play_item.setProperty('inputstream.adaptive.license_key', lic_url+'|' + hea+'|R{SSM}|')

    #xbmc.Player().play(stream_url,play_item)
    
    xbmcplugin.setResolvedUrl(addon_handle, True, play_item)
def MenuCDA(id):

    if 'f' in id:
        tyt = 'filmy'
        katn = fkatn
        sortn = fsortn
        wern = fwern
        typn = ftypn
    elif 's' in id:
        tyt = 'seriale'
        sortn = ssortn
        wern = swern
        typn = stypn
    elif 'd' in id:
        tyt = 'dla dzieci'    

        sortn = dsortn
        wern = dwern
        typn = dtypn

    add_item(id, 'Wyświetl '+tyt, 'DefaultMovies.png', "listcontent", True) 
    add_item('', "-    [COLOR lightblue]typ:[/COLOR] [B]"+typn+'[/B]','DefaultRecentlyAddedMovies.png', 'filtr:%styp'%(str(id)), folder=False,fanart='')
    if 'f' in id:
        add_item('', "-    [COLOR lightblue]kategoria:[/COLOR] [B]"+katn+'[/B]','DefaultRecentlyAddedMovies.png', 'filtr:%skat'%(str(id)), folder=False,fanart='')



    add_item('', "-    [COLOR lightblue]sortowanie:[/COLOR] [B]"+sortn+'[/B]','DefaultRecentlyAddedMovies.png', 'filtr:%ssort'%(str(id)), folder=False,fanart='')
    add_item('', "-    [COLOR lightblue]wersja:[/COLOR] [B]"+wern+'[/B]','DefaultRecentlyAddedMovies.png', 'filtr:%swer'%(str(id)), folder=False,fanart='')


    xbmcplugin.endOfDirectory(addon_handle)


def PLchar(char):
    if type(char) is not str:
        char=char.encode('utf-8')
    char = char.replace('\\u0105','\xc4\x85').replace('\\u0104','\xc4\x84')
    char = char.replace('\\u0107','\xc4\x87').replace('\\u0106','\xc4\x86')
    char = char.replace('\\u0119','\xc4\x99').replace('\\u0118','\xc4\x98')
    char = char.replace('\\u0142','\xc5\x82').replace('\\u0141','\xc5\x81')
    char = char.replace('\\u0144','\xc5\x84').replace('\\u0144','\xc5\x83')
    char = char.replace('\\u00f3','\xc3\xb3').replace('\\u00d3','\xc3\x93')
    char = char.replace('\\u015b','\xc5\x9b').replace('\\u015a','\xc5\x9a')
    char = char.replace('\\u017a','\xc5\xba').replace('\\u0179','\xc5\xb9')
    char = char.replace('\\u017c','\xc5\xbc').replace('\\u017b','\xc5\xbb')
    char = char.replace('&#8217;',"'")
    char = char.replace('&#8211;',"-")    
    char = char.replace('&#8230;',"...")    
    char = char.replace("&gt;",">")    
    char = char.replace("&Iacute;","Í").replace("&iacute;","í")
    char = char.replace("&icirc;","î").replace("&Icirc;","Î")
    char = char.replace('&oacute;','ó').replace('&Oacute;','Ó')
    char = char.replace('&quot;','"').replace('&amp;quot;','"')
    char = char.replace('&bdquo;','"').replace('&rdquo;','"')
    char = char.replace("&Scaron;","Š").replace("&scaron;","š")
    char = char.replace("&ndash;","-").replace("&mdash;","-")
    char = char.replace("&Auml;","Ä").replace("&auml;","ä")

    char = char.replace('&#8217;',"'")
    char = char.replace('&#8211;',"-")    
    char = char.replace('&#8230;',"...")    
    char = char.replace('&#8222;','"').replace('&#8221;','"')    
    char = char.replace('[&hellip;]',"...")
    char = char.replace('&#038;',"&")    
    char = char.replace('&#039;',"'")
    char = char.replace('&quot;','"')
    char = char.replace('&nbsp;',".").replace('&amp;','&')
    
    
    
    char = char.replace('Napisy PL',"[COLOR lightblue](napisy pl)[/COLOR]")
    char = char.replace('Lektor PL',"[COLOR lightblue](lektor pl)[/COLOR]")
    char = char.replace('Dubbing PL',"[COLOR lightblue](dubbing pl)[/COLOR]")    
    return char    

    
def router(paramstring):
    args = dict(parse_qsl(paramstring))
    
    if args:
        mode = args.get('mode', None)

        if 'filtr' in mode:
            ff = mode.split(':')[1]
            if 'wer' in ff:
                dd='quality:'
                
                value=['',"n=1","l=1"]
                label=['wszystkie',"tylko z napisami","tylko z lektorem"]

            elif 'kat' in ff:
                dd='genre:'
                value=["","category=10","category=284","category=1","category=196","category=2","category=9","category=157","category=16","category=18","category=44","category=19","category=17","category=23","category=32","category=69","category=42","category=22","category=51","category=26","category=25","category=39","category=27","category=12","category=66","category=11","category=67","category=21"]
                label=["Wszystkie gatunki" ,"Akcja" ,"Bartosz Walaszek Poleca" ,"Biograficzny" ,"CDA Poleca"  ,"Dokumentalny" ,"Dramat" ,"Europejski" ,"Familijny" ,"Fantasy" ,"Historyczny" ,"Horror" ,"Komedia" ,"Komedia romantyczna" ,"Kryminał" ,"Młodzieżowy" ,"Muzyczny" ,"Obyczajowy" ,"Polskie" ,"Przygodowy" ,"Psychologiczny" ,"Romans" ,"Sci-fi" ,"Sensacyjny"  ,"Sztuki walki" ,"Thriller" ,"Western" ,"Wojenny"]

            elif 'sort' in ff:
                dd='sortowanie:'
                value=["sort=views30" ,"sort=views7" ,"sort=views3" ,"sort=views" ,"sort=new" ,"sort=alpha" ,"sort=best" ,"sort=popular" ,"sort=release"]
                label=["popularne w ciągu ostatnich 30 dni" ,"popularne w ciągu ostatnich 7 dni" ,"popularne w ciągu ostatnich 3 dni" ,"najczęściej oglądane" ,"nowo dodane" ,"alfabetycznie" ,"najlepiej oceniane na IMDb" ,"najcześciej oceniane na IMDb" ,"data premiery kinowej"]

                if 'szuk' in ff:
                    value=["sort=alf" ,"sort=best" ,"sort=date" ,"sort=popular" ,"sort=new" ,"sort=rate" ]
                    label=["alfabetycznie" ,"najtrafniejsze" ,"najnowsze" ,"najpopularniejsze" ,"najlepiej oceniane" ]

                
                
            elif 'typ' in ff:
                dd='typ:'
                value=["", "free=1"]
                label=["premium","darmowe"]
            
            elif 'qual' in ff:
                dd='jakość:'
                value=["" ,"quality=480p" ,"quality=720p" ,"quality=1080p"  ]
                label=["każda jakość" ,"średnia jakość 480p" ,"wysoka jakość 720p" ,"bardzo wysoka jakość 1080p" ]
            
            elif 'durat' in ff:
                dd='długość:'
                value=["" ,"duration=short" ,"duration=medium" ,"duration=long"  ]
                label=["każda długość" ,"krótkie (poniżej 5 minut)" ,"średnie (powyżej 20 minut)" ,"długie (powyżej 60 minut)" ]

            sel = xbmcgui.Dialog().select('Select '+dd,label)

            if sel != -1:

                sel = sel if sel>-1 else quit()
                v = '&'+'%s'%value[sel] if value[sel] else ''
                n = label[sel]
                a = ff+'V'
                b = ff+'N'

                addon.setSetting(ff+'V',v)
                addon.setSetting(ff+'N',n)
                
                fsortv = addon.getSetting('fsortV')
                fkatv = addon.getSetting('fkatV')
                fwerv = addon.getSetting('fwerV')
                ftypv = addon.getSetting('ftypV')
                
                
                
                ssortv = addon.getSetting('ssortV')
                swerv = addon.getSetting('swerV')
                stypv = addon.getSetting('stypV')
                
                dsortv = addon.getSetting('dsortV')
                dwerv = addon.getSetting('dwerV')
                dtypv = addon.getSetting('dtypV')
                
                squalv = addon.getSetting('szukqualV')
                sduratv = addon.getSetting('szukduratV')
                szuksortv = addon.getSetting('szuksortV')

                dataf=fkatv+fwerv+fsortv+ftypv
                datas=swerv+ssortv+stypv
                datad=dwerv+dsortv+dtypv
                dataszukaj = squalv+sduratv+szuksortv
                
                
                
                addon.setSetting('fdata',dataf)
                addon.setSetting('sdata',datas)
                addon.setSetting('ddata',datad)
                xbmc.executebuiltin('Container.Refresh')
            else:
                quit()

        elif mode == 'szukaj':
            query = xbmcgui.Dialog().input(u'Szukaj...', type=xbmcgui.INPUT_ALPHANUM)
            if query:    
                query = query.replace(' ','+')
                url = 'https://api.cda.pl/video/search?query=%s&page=1&limit=20'%(str(query))

                ListContent('1',1,url)

            else:
                quit()
        elif mode=='search':

            add_item('', 'Szukaj', 'DefaultMovies.png', "szukaj", True) 
            add_item('', "-    [COLOR lightblue]jakość:[/COLOR] [B]"+squaln+'[/B]','DefaultRecentlyAddedMovies.png', 'filtr:szukqual', folder=False,fanart='')
            add_item('', "-    [COLOR lightblue]długość:[/COLOR] [B]"+sduratn+'[/B]','DefaultRecentlyAddedMovies.png', 'filtr:szukdurat', folder=False,fanart='')
            add_item('', "-    [COLOR lightblue]sortowanie:[/COLOR] [B]"+szuksortn+'[/B]','DefaultRecentlyAddedMovies.png', 'filtr:szuksort', folder=False,fanart='')
            xbmcplugin.endOfDirectory(addon_handle)

                
        elif mode=='logowanie':    
            addon.openSettings()
            xbmc.executebuiltin('Container.Refresh()')
                
        elif mode=='menucda':    
            MenuCDA(exlink)

        elif mode == 'listcontent':
            ListContent(exlink,page)
        elif mode =='playvid':
            PlayVid(exlink)
            
        elif mode == 'listserial':
            ListSeriale(exlink,page)
        elif mode == 'getfolder':
            getFolder(exlink,page)
        elif mode == 'listtv':
            ListTv()
        elif mode == 'playtv':
            PlayVid(exlink,True)
        
        
        elif mode =='foldery':
            Foldery(exlink,page)
        elif mode =='dodaj':
            dodaj(exlink)
        elif mode =='ulubione':
            Foldery(login_id,page,fav=True)
            
        elif mode == 'listfoldersfav':
            ListFolders(exlink,page,fav=True)
        elif mode == 'listfolders':
            ListFolders(exlink,page)
            
            
            
            
        
    else:
        home()    
if __name__ == '__main__':
    router(sys.argv[2][1:])
