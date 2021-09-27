# -*- coding: UTF-8 -*-

import sys,re,os

if sys.version_info >= (3,0,0):
# for Python 3

    from urllib.parse import parse_qs, parse_qsl, urlencode, quote_plus
    import http.cookiejar as cookielib

else:
    # for Python 2

    from urllib import urlencode, quote_plus

    import cookielib
    from urlparse import parse_qsl, parse_qs


import requests
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc, xbmcvfs

import json

import inputstreamhelper

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.playermb')

PATH            = addon.getAddonInfo('path')
try:
    DATAPATH        = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
except:
    DATAPATH    = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')



RESOURCES       = PATH+'/resources/'
COOKIEFILE = os.path.join(DATAPATH,'player.cookie')
SUBTITLEFILE = os.path.join(DATAPATH,'temp.sub')


ikona =RESOURCES+'../icon.png'
FANART=RESOURCES+'../fanart.jpg'
sys.path.append( os.path.join( RESOURCES, "lib" ) )

exlink = params.get('url', None)
name= params.get('name', None)
page = params.get('page','')

rys= params.get('image', None)

kukz=''


kanalydata=[{"id":97,"name":"dla dzieci"},{"id":142,"name":"sport"},{"id":143,"name":"programy"},{"id":144,"name":"filmy"},{"id":145,"name":"seriale"},{"id":146,"name":"informacje"}]
menudata=[{'url': 1, 'slug': 'seriale-online', 'title': 'Seriale'}, {'url': 2, 'slug': 'programy-online', 'title': 'Programy'}, {'url': 3, 'slug': 'filmy-online', 'title': 'Filmy'}, {'url': 4, 'slug': 'bajki-dla-dzieci', 'title': 'Dla dzieci'}, {'url': 5, 'slug': 'strefa-sport', 'title': 'Sport'}, {'url': 7, 'slug': 'canal-plus', 'title': 'CANAL+'}, {'url': 8, 'slug': 'hbo', 'title': 'HBO'},  {'url': 17, 'slug': 'live', 'title': 'Kanały TV'}, {'url': 21, 'slug': 'motortrend', 'title': 'MotorTrend'}, {'url': 22, 'slug': 'hotel-paradise', 'title': 'Hotel Paradise'},{'url':23, 'slug': 'discovery-plus', 'title': 'Discovery+'}]

serialemenu = {"1":[{"id":7,"name":"Bajki","externalId":11},{"id":8,"name":"Obyczajowy","externalId":12},{"id":9,"name":"Komedia","externalId":13},{"id":10,"name":"Sensacyjny","externalId":14},{"id":11,"name":"Dokumentalny","externalId":16},{"id":17,"name":"Thriller","externalId":31},{"id":18,"name":"Horror","externalId":32},{"id":19,"name":"Dramat","externalId":33},{"id":20,"name":"Science Fiction","externalId":34},{"id":22,"name":"Familijny","externalId":36},{"id":26,"name":"Inne","externalId":41},{"id":30,"name":"Akcja","externalId":50},{"id":31,"name":"Animowany","externalId":51},{"id":32,"name":"Biograficzny","externalId":52},{"id":34,"name":"Fantasy","externalId":54},{"id":35,"name":"Historyczny","externalId":55},{"id":36,"name":"Kostiumowy","externalId":56},{"id":37,"name":"Kryminalny","externalId":57},{"id":38,"name":"Melodramat","externalId":58},{"id":39,"name":"Musical","externalId":59},{"id":40,"name":"Przygodowy","externalId":60},{"id":41,"name":"Psychologiczny","externalId":61},{"id":42,"name":"Western","externalId":62},{"id":43,"name":"Wojenny","externalId":63},{"id":46,"name":"Komediodramat","externalId":66},{"id":47,"name":"Telenowela","externalId":67},{"id":52,"name":"Programy edukacyjne","externalId":72},{"id":53,"name":"Filmy animowane","externalId":73}],
            "2":[{"id":1,"name":"Rozrywka","externalId":5},{"id":2,"name":"Poradniki","externalId":6},{"id":3,"name":"Kuchnia","externalId":7},{"id":4,"name":"Zdrowie i Uroda","externalId":8},{"id":5,"name":"Talk-show","externalId":9},{"id":6,"name":"Motoryzacja","externalId":10},{"id":7,"name":"Bajki","externalId":11},{"id":8,"name":"Obyczajowy","externalId":12},{"id":11,"name":"Dokumentalny","externalId":16},{"id":12,"name":"Informacje","externalId":18},{"id":13,"name":"Podróże i Przyroda","externalId":19},{"id":14,"name":"Dokument i Reportaż","externalId":20},{"id":23,"name":"Motorsport","externalId":38},{"id":26,"name":"Inne","externalId":41},{"id":27,"name":"Muzyka","externalId":42},{"id":29,"name":"Dom i Ogród","externalId":48},{"id":31,"name":"Animowany","externalId":51},{"id":32,"name":"Biograficzny","externalId":52},{"id":48,"name":"Hobby","externalId":68},{"id":49,"name":"Kultura","externalId":69},{"id":50,"name":"Moda","externalId":70},{"id":51,"name":"Popularno-naukowe","externalId":71},{"id":52,"name":"Programy edukacyjne","externalId":72},{"id":53,"name":"Filmy animowane","externalId":73}],
            "5":[{"id":6,"name":"Motoryzacja","externalId":10},{"id":12,"name":"Informacje","externalId":18},{"id":23,"name":"Motorsport","externalId":38},{"id":24,"name":"Piłka nożna","externalId":39},{"id":25,"name":"Sporty ekstremalne","externalId":40},{"id":26,"name":"Inne","externalId":41},{"id":59,"name":"Sporty zimowe","externalId":79}],
            "22":[{"id":1,"name":"Rozrywka","externalId":5}],
            "21":[{"id":1,"name":"Rozrywka","externalId":5},{"id":2,"name":"Poradniki","externalId":6},{"id":6,"name":"Motoryzacja","externalId":10},{"id":13,"name":"Podróże i Przyroda","externalId":19},{"id":14,"name":"Dokument i Reportaż","externalId":20},{"id":23,"name":"Motorsport","externalId":38},{"id":48,"name":"Hobby","externalId":68},{"id":49,"name":"Kultura","externalId":69}],
            "7":[{"id":45,"name":"Dokument","externalId":65},{"id":60,"name":"Film","externalId":80},{"id":61,"name":"Serial","externalId":81},{"id":62,"name":"Sport","externalId":82},{"id":63,"name":"Dla dzieci","externalId":83}],
            "8":[{"id":45,"name":"Dokument","externalId":65},{"id":60,"name":"Film","externalId":80},{"id":61,"name":"Serial","externalId":81},{"id":63,"name":"Dla dzieci","externalId":83},{"id":64,"name":"Disney","externalId":84},{"id":65,"name":"Styl życia","externalId":85}],
            "17":[{"id":97,"name":"dla dzieci"},{"id":142,"name":"sport"},{"id":143,"name":"programy"},{"id":144,"name":"filmy"},{"id":145,"name":"seriale"},{"id":146,"name":"informacje"}],
            "3":[{"id":1,"name":"Rozrywka","externalId":5},{"id":3,"name":"Kuchnia","externalId":7},{"id":7,"name":"Bajki","externalId":11},{"id":8,"name":"Obyczajowy","externalId":12},{"id":9,"name":"Komedia","externalId":13},{"id":10,"name":"Sensacyjny","externalId":14},{"id":11,"name":"Dokumentalny","externalId":16},{"id":14,"name":"Dokument i Reportaż","externalId":20},{"id":16,"name":"Piosenki","externalId":30},{"id":17,"name":"Thriller","externalId":31},{"id":18,"name":"Horror","externalId":32},{"id":19,"name":"Dramat","externalId":33},{"id":20,"name":"Science Fiction","externalId":34},{"id":22,"name":"Familijny","externalId":36},{"id":26,"name":"Inne","externalId":41},{"id":30,"name":"Akcja","externalId":50},{"id":31,"name":"Animowany","externalId":51},{"id":32,"name":"Biograficzny","externalId":52},{"id":33,"name":"Erotyczny","externalId":53},{"id":34,"name":"Fantasy","externalId":54},{"id":35,"name":"Historyczny","externalId":55},{"id":36,"name":"Kostiumowy","externalId":56},{"id":37,"name":"Kryminalny","externalId":57},{"id":38,"name":"Melodramat","externalId":58},{"id":39,"name":"Musical","externalId":59},{"id":40,"name":"Przygodowy","externalId":60},{"id":41,"name":"Psychologiczny","externalId":61},{"id":42,"name":"Western","externalId":62},{"id":43,"name":"Wojenny","externalId":63},{"id":44,"name":"Filmy na życzenie","externalId":64},{"id":53,"name":"Filmy animowane","externalId":73}],
            "4":[{"id":7,"name":"Bajki","externalId":11},{"id":9,"name":"Komedia","externalId":13},{"id":10,"name":"Sensacyjny","externalId":14},{"id":16,"name":"Piosenki","externalId":30},{"id":22,"name":"Familijny","externalId":36},{"id":26,"name":"Inne","externalId":41},{"id":30,"name":"Akcja","externalId":50},{"id":31,"name":"Animowany","externalId":51},{"id":34,"name":"Fantasy","externalId":54},{"id":39,"name":"Musical","externalId":59},{"id":40,"name":"Przygodowy","externalId":60},{"id":44,"name":"Filmy na życzenie","externalId":64},{"id":52,"name":"Programy edukacyjne","externalId":72},{"id":53,"name":"Filmy animowane","externalId":73}],
            "23":[{"id":1,"name":"Rozrywka","externalId":5},{"id":2,"name":"Poradniki","externalId":6},{"id":3,"name":"Kuchnia","externalId":7},{"id":4,"name":"Zdrowie i Uroda","externalId":8},{"id":6,"name":"Motoryzacja","externalId":10},{"id":11,"name":"Dokumentalny","externalId":16},{"id":13,"name":"Podróże i Przyroda","externalId":19},{"id":14,"name":"Dokument i Reportaże","externalId":20},{"id":26,"name":"Inne","externalId":41},{"id":29,"name":"Dom i Ogród","externalId":48},{"id":48,"name":"Hobby","externalId":68},{"id":49,"name":"Kultura","externalId":69},{"id":50,"name":"Moda","externalId":70},{"id":51,"name":"Popularno-naukowe","externalId":71}]}


TIMEOUT=15

sess = requests.Session()
sess.cookies = cookielib.LWPCookieJar(COOKIEFILE)
def build_url(query):
    return base_url + '?' + urlencode(query)

def add_item(url, name, image, mode, folder=False, IsPlayable=False, infoLabels=False, movie=True,itemcount=1, page=1,fanart=FANART,moviescount=0):
    list_item = xbmcgui.ListItem(label=name)

    if IsPlayable:
        list_item.setProperty("IsPlayable", 'True')
    if not infoLabels:
        infoLabels={'title': name,'plot':name}
    list_item.setInfo(type="video", infoLabels=infoLabels)    
    list_item.setArt({'thumb': image, 'poster': image, 'banner': image, 'fanart': FANART})
    ok=xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url = build_url({'mode': mode, 'url' : url, 'page' : page, 'moviescount' : moviescount,'movie':movie,'name':name,'image':image}),            
        listitem=list_item,
        isFolder=folder)

    return ok
def setView(typ):
    if addon.getSetting('auto-view') == 'false':
        xbmcplugin.setContent(addon_handle, 'videos')
    else:
        xbmcplugin.setContent(addon_handle, typ)
    
def getmenu():

    for menu in menudata:
        mud="listcateg"
        if menu['slug']=='live':
            mud='listcateg'
        add_item(str(menu['url'])+':'+menu['slug'], menu['title'], ikona, mud, folder=True,fanart=FANART)


def getMetaDane(data):
    tytul =''
    opis = ''
    foto = ''
    

    if data.get("active",None):
        tytul = data['title']
        opis = data.get("description",None)
        opis = remove_html_tags(opis)
        foto = data['images']['pc'][0]['mainUrl']
        foto = 'https:' + foto if foto.startswith('//') else foto
        sezony = data.get("showSeasonNumber",None)
        if data.get("type")=='SERIAL':
            sezon=True
        else:
            sezon = True if sezony else False
        epizody = data.get("showEpisodeNumber",None)
        epizod  = True if epizody else False
        
    return tytul, opis, foto, sezon, epizod
    
def getMetaDane2(data):
    tytul =''
    opis = ''
    foto = ''
    sezon=False
    epizod=False

    #if data.get("active",None):
    tytul = data['title']
    opis = data.get("description",None)
    #opis = remove_html_tags(opis)
    foto = data['images']['pc'][0]['mainUrl']
    foto = 'https:' + foto if foto.startswith('//') else foto
    sezony = data.get("showSeasonNumber",None)
    sezon = True if sezony else False
    epizody = data.get("showEpisodeNumber",None)
    epizod  = True if epizody else False
    return tytul, opis, foto, sezon, epizod
def remove_html_tags(text):
    """Remove html tags from a string"""

    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)
def home():
    PLAYERPL().sprawdzenie1()

    PLAYERPL().sprawdzenie2()
    add_item('', '[B][COLOR khaki]Ulubione[/COLOR][/B]', ikona, "favors", folder=True,fanart=FANART)
    getmenu()
    add_item('', 'Kolekcje', ikona, "collect", folder=True,fanart=FANART)
    add_item('', '[B][COLOR khaki]Szukaj[/COLOR][/B]', ikona, "search", folder=True,fanart=FANART)
    add_item('', '[B][COLOR blue]Opcje[/COLOR][/B]', ikona, "opcje", folder=False,fanart=FANART)
    if PLAYERPL().LOGGED == 'true':
        add_item('', '[B][COLOR blue]Wyloguj[/COLOR][/B]', ikona, "logout", folder=False,fanart=FANART)
    
def get_addon():
    return addon

def set_setting(key, value):
    return get_addon().setSetting(key, value)

def dialog_progress():
    return xbmcgui.DialogProgress()
    
def xbmc_sleep(time):
    return xbmc.sleep(time)

    

    
    
    

def getRequests(url, data={}, headers={}, params ={}):
    if data:
        if headers.get('Content-Type', '').startswith('application/json'):

            content=sess.post(url,headers=headers,json=data, params=params, verify=False).json()
        else:

            content=sess.post(url,headers=headers,data=data, params=params, verify=False).json()
    else:
        content=sess.get(url,headers=headers, params=params, verify=False).json()
    return content
    
def idle():

    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    else:
        xbmc.executebuiltin('Dialog.Close(busydialog)')


def busy():

    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    else:
        xbmc.executebuiltin('ActivateWindow(busydialog)')

 
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
    char = char.replace('&#8222;','"').replace('&#8221;','"')    
    char = char.replace('[&hellip;]',"...")
    char = char.replace('&#038;',"&")    
    char = char.replace('&#039;',"'")
    char = char.replace('&quot;','"')
    char = char.replace('&nbsp;',".").replace('&amp;','&')
    return char    
    
class PLAYERPL():
    def __init__(self):
    
        self.api_base = 'https://player.pl/playerapi/'
        self.login_api = 'https://konto.tvn.pl/oauth/' 
        
        self.GETTOKEN = self.login_api + 'tvn-reverse-onetime-code/create'
        self.POSTTOKEN = self.login_api + 'token'
        self.SUBSCRIBER = self.api_base + 'subscriber/login/token'
        self.SUBSCRIBERDETAIL = self.api_base + 'subscriber/detail' 
        self.JINFO = self.api_base + 'info'
        self.TRANSLATE = self.api_base + 'item/translate'
        self.KATEGORIE = self.api_base + 'item/category/list'
        
        self.PRODUCTVODLIST = self.api_base + 'product/vod/list'
        self.PRODUCTLIVELIST= self.api_base + 'product/list/list'
        
        self.PARAMS = {'4K': 'true','platform': 'ANDROID_TV'}
        
        self.HEADERS3 = { 'Host': 'konto.tvn.pl','user-agent': 'okhttp/3.3.1 Android','content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        

        
        
        
        self.ACCESS_TOKEN = addon.getSetting('access_token')
        self.USER_PUB = addon.getSetting('user_pub')
        self.USER_HASH = addon.getSetting('user_hash')
        self.REFRESH_TOKEN = addon.getSetting('refresh_token')
        self.DEVICE_ID = addon.getSetting('device_id')
        self.TOKEN = addon.getSetting('token')
        self.MAKER = addon.getSetting('maker_id')
        self.USAGENT = addon.getSetting('usagent_id')
        self.USAGENTVER = addon.getSetting('usagentver_id')
        self.SELECTED_PROFILE = addon.getSetting('selected_profile')
        self.SELECTED_PROFILE_ID = addon.getSetting('selected_profile_id')
        self.ENABLE_SUBS = addon.getSetting('subtitles')
        self.SUBS_DEFAULT = addon.getSetting('subtitles_lang_default')
        self.LOGGED = addon.getSetting('logged')

        self.HEADERS2 = {
            'Authorization': 'Basic',
            'API-DeviceInfo': '%s;%s;Android;9;%s;1.0.38(62);'%(self.USAGENT, self.USAGENTVER, self.MAKER ),
            'API-DeviceUid': self.DEVICE_ID,
            'User-Agent': 'okhttp/3.3.1 Android',
            'Host': 'player.pl',
            'X-NewRelic-ID': 'VQEOV1JbABABV1ZaBgMDUFU='
        }
        self.HEADERS2['API-Authentication'] =  self.ACCESS_TOKEN
        self.HEADERS2['API-SubscriberHash'] =  self.USER_HASH
        self.HEADERS2['API-SubscriberPub'] =  self.USER_PUB
        self.HEADERS2['API-ProfileUid'] =  self.SELECTED_PROFILE_ID    
        
        
    def createDatas(self):

        def gen_hex_code(myrange=6):
            import random
            return ''.join([random.choice('0123456789abcdef') for x in range(myrange)])
            
            
        def uniq_usagent():
            usagent_id = ''
        
            if addon.getSetting('usagent_id'):
                usagent_id = addon.getSetting('usagent_id')
            else:
                usagent_id = '2e520525f3'+ gen_hex_code(6)
            set_setting('usagent_id', usagent_id)
            return usagent_id
        
            
        def uniq_usagentver():
            usagentver_id = ''
        
            if addon.getSetting('usagentver_id'):
                usagentver_id = addon.getSetting('usagentver_id')
            else:
                usagentver_id = '2e520525f2'+ gen_hex_code(6)
            set_setting('usagentver_id', usagentver_id)
            return usagentver_id
            
        def uniq_maker():
            maker_id = ''
        
            if addon.getSetting('maker_id'):
                maker_id = addon.getSetting('maker_id')
            else:
                maker_id = gen_hex_code(16)
            set_setting('maker_id', maker_id)
            return maker_id
            
        def uniq_id():
            device_id = ''
        
            if addon.getSetting('device_id'):
                device_id = addon.getSetting('device_id')
            else:
                device_id = gen_hex_code(16)
            set_setting('device_id', device_id)
            return device_id
        self.DEVICE_ID =uniq_id()
        self.MAKER = uniq_maker()
        self.USAGENT = uniq_usagent()
        self.USAGENTVER = uniq_usagentver()
        return
        
    def sprawdzenie1(self):

        if not self.DEVICE_ID or not self.MAKER or not self.USAGENT or not self.USAGENTVER:
            self.createDatas()
        if not self.REFRESH_TOKEN and self.LOGGED == 'true':
            POST_DATA = 'scope=/pub-api/user/me&client_id=Player_TV_Android_28d3dcc063672068'
            data = getRequests(self.GETTOKEN, data = POST_DATA, headers=self.HEADERS3)
            kod = data.get('code')
            dg = dialog_progress()
            dg.create('Uwaga','Przepisz kod: [COLOR gold][B]%s[/COLOR][/B]\n Na stronie https://player.pl/zaloguj-tv'%kod)
            
            time_to_wait=340
            secs = 0
            increment = 100 // time_to_wait
            cancelled = False
            b= 'acces_denied'
            while secs <= time_to_wait:
                if (dg.iscanceled()): cancelled = True; break
                if secs != 0: xbmc_sleep(3000)
                secs_left = time_to_wait - secs
                if secs_left == 0: percent = 100
                else: percent = increment * secs
                POST_DATA = 'grant_type=tvn_reverse_onetime_code&code=%s&client_id=Player_TV_Android_28d3dcc063672068'%kod
                data = getRequests(self.POSTTOKEN, data=POST_DATA, headers=self.HEADERS3)
                token_type = data.get("token_type",None)
                errory = data.get('error',None)
                if token_type == 'bearer': break
                secs += 1
            
            
                dg.update(percent)
                secs += 1
            dg.close()
            
            if not cancelled:
                self.ACCESS_TOKEN = data.get('access_token',None)
                self.USER_PUB = data.get('user_pub',None)
                self.USER_HASH = data.get('user_hash',None)
                self.REFRESH_TOKEN = data.get('refresh_token',None)
            
                set_setting('access_token', self.ACCESS_TOKEN)
                set_setting('user_pub', self.USER_PUB)
                set_setting('user_hash', self.USER_HASH)
                set_setting('refresh_token', self.REFRESH_TOKEN)
                
    def sprawdzenie2(self):

        if self.REFRESH_TOKEN:
        
            PARAMS = {'4K': 'true','platform': 'ANDROID_TV'}
            self.HEADERS2['Content-Type'] =  'application/json; charset=UTF-8'

            POST_DATA = {"agent":self.USAGENT,"agentVersion":self.USAGENTVER,"appVersion":"1.0.38(62)","maker":self.MAKER,"os":"Android","osVersion":"9","token":self.ACCESS_TOKEN,"uid":self.DEVICE_ID}
            data = getRequests(self.SUBSCRIBER, data = POST_DATA, headers=self.HEADERS2,params=PARAMS)
        
        
            self.SELECTED_PROFILE = data.get('profile',{}).get('name',None)
            self.SELECTED_PROFILE_ID = data.get('profile',{}).get('externalUid',None)
        
            self.HEADERS2['API-ProfileUid'] =  self.SELECTED_PROFILE_ID
        
            
            set_setting('selected_profile_id', self.SELECTED_PROFILE_ID)
            set_setting('selected_profile', self.SELECTED_PROFILE)
        if self.LOGGED != 'true':
            add_item('', '[B][COLOR blue]Zaloguj[/COLOR][/B]', ikona, "login", folder=False,fanart=FANART)
    
    def getTranslate(self,id_):

        PARAMS = {'4K': 'true','platform': 'ANDROID_TV', 'id': id_}
        data = getRequests(self.TRANSLATE,headers = self.HEADERS2, params = PARAMS)
        return data
    
    def getPlaylist(self,id_):
        self.refreshTokenTVN()

        HEADERSz = {
            'Authorization': 'Basic',
            'API-DeviceInfo': '%s;%s;Android;9;%s;1.0.38(62);'%(self.USAGENT, self.USAGENTVER, self.MAKER ),
            'API-Authentication': self.ACCESS_TOKEN,
            'API-DeviceUid': self.DEVICE_ID,
            'API-SubscriberHash': self.USER_HASH,
            'API-SubscriberPub': self.USER_PUB,
            'API-ProfileUid': self.SELECTED_PROFILE_ID,
            'User-Agent': 'okhttp/3.3.1 Android',
            'Host': 'player.pl',
            'X-NewRelic-ID': 'VQEOV1JbABABV1ZaBgMDUFU=',
        }
    
    
        rodzaj ='MOVIE'
        if 'kanal' in id_:
            id_=id_.split(':')[0]
            rodzaj = 'LIVE'
        urlk='https://player.pl/playerapi/product/%s/player/configuration?type=%s&4K=true&platform=ANDROID_TV'%(str(id_),rodzaj)
    
        data = getRequests(urlk,headers = HEADERSz)
    
        try:
            vidsesid = data["videoSession"]["videoSessionId"]
            prolongvidses = data["prolongVideoSessionUrl"]
        except:
            vidsesid=False
            pass
        PARAMS = {'type': rodzaj,'platform': 'ANDROID_TV'}
    
        data = getRequests(self.api_base+'item/%s/playlist'%(str(id_)),headers = HEADERSz, params = PARAMS)
    
        if not data:
    
            urlk='https://player.pl/playerapi/item/%s/playlist?type=%s&platform=ANDROID_TV&videoSessionId=%s'%(str(id_),rodzaj,str(vidsesid))
            
            
            
            data = getRequests(urlk,headers = HEADERSz, params = {})
    
        vid=data['movie']
        outsub=[]
        try:
            subs = vid['video']['subtitles']
            for lan, sub in subs.items():
                lang = sub['label']
                
                srcsub = sub['src']
                outsub.append({'lang':lang, 'url':srcsub}) 
        except:
            pass

   
        src=vid['video']['sources']['dash']['url']
        widev=vid['video']['protections']['widevine']['src']
        if vidsesid:
            widev+='&videoSessionId=%s'%vidsesid
    
        src=requests.get(src,allow_redirects=False,verify=False)
        src=src.headers['Location']
        return src,widev,outsub
    
    def refreshTokenTVN(self):

        POST_DATA = 'grant_type=refresh_token&refresh_token=%s&client_id=Player_TV_Android_28d3dcc063672068'%self.REFRESH_TOKEN
        data = getRequests(self.POSTTOKEN,data = POST_DATA, headers=self.HEADERS3)
        if data.get('error_description',None) == 'Token is still valid.':
            return
        else:
    
            self.ACCESS_TOKEN = data.get('access_token',None)
            self.USER_PUB = data.get('user_pub',None)
            self.USER_HASH = data.get('user_hash',None)
            self.REFRESH_TOKEN = data.get('refresh_token',None)
            set_setting('access_token', self.ACCESS_TOKEN)
            set_setting('user_pub', self.USER_PUB )
            set_setting('user_hash', self.USER_HASH)
            set_setting('refresh_token', self.REFRESH_TOKEN)
            return data
    
    def playvid(self,id):

        data = self.getTranslate(str(id))
    
        stream_url, license_url, subtitles = self.getPlaylist(str(id))
        subt = ''
        if subtitles and self.ENABLE_SUBS =='true':
            t = [ x.get('lang') for x in subtitles]
            u = [ x.get('url') for x in subtitles]
            al = "subtitles"    
        
            if len(subtitles)>1:  

                if self.SUBS_DEFAULT != '' and self.SUBS_DEFAULT in t:
                    subt = next((x for x in subtitles if x.get('lang') == self.SUBS_DEFAULT), None).get('url')
                else:
                    select = xbmcgui.Dialog().select(al, t)
                    if select > -1:
                       subt = u[select];
                       addon.setSetting(id='subtitles_lang_default', value=str(t[select]))
  
                    else:
                       subt =''
            else:
                subt = u[0];
    
    
    
        import inputstreamhelper
    
        PROTOCOL = 'mpd'
        DRM = 'com.widevine.alpha'
    
        str_url=stream_url
        
        HEADERSz = {
            'Authorization': 'Basic',
            'API-DeviceInfo': '%s;%s;Android;9;%s;1.0.38(62);'%(self.USAGENT, self.USAGENTVER, self.MAKER ),
            'API-Authentication': self.ACCESS_TOKEN,
            'API-DeviceUid': self.DEVICE_ID,
            'API-SubscriberHash': self.USER_HASH,
            'API-SubscriberPub': self.USER_PUB,
            'API-ProfileUid': self.SELECTED_PROFILE_ID,
            'User-Agent': 'okhttp/3.3.1 Android',
            'Host': 'player.pl',
            'X-NewRelic-ID': 'VQEOV1JbABABV1ZaBgMDUFU=',
        }

        is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
        if is_helper.check_inputstream():
        
            play_item = xbmcgui.ListItem(path=str_url)
            play_item.setContentLookup(False)
            if subt:
                r = requests.get(subt)
                with open(SUBTITLEFILE, 'wb') as f:
                   f.write(r.content)
                play_item.setSubtitles([SUBTITLEFILE])
                
                
            if sys.version_info >= (3,0,0):
                play_item.setProperty('inputstream', is_helper.inputstream_addon)
            else:
                play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)

            play_item.setMimeType('application/xml+dash')
            play_item.setContentLookup(False)
            play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
            play_item.setProperty('inputstream.adaptive.license_type', DRM)
            play_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            play_item.setProperty('inputstream.adaptive.license_key', license_url+'|Content-Type=|R{SSM}|')
            play_item.setProperty('inputstream.adaptive.license_flags', "persistent_storage")
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    
    def ListCollection(self):
        self.refreshTokenTVN()

        data = getRequests('https://player.pl/playerapi/product/section/list?order=asc&maxResults=0&firstResult=0&4K=true&platform=ANDROID_TV',headers = self.HEADERS2, params = {})
        mud="listcollectContent"
        for vod in data:
            id_=vod['id']
            slug = vod['slug']
            typ = vod['type']
            foto = vod['images']['pc'][0]['mainUrl']
            foto = 'https:' + foto if foto.startswith('//') else foto
            tytul = PLchar(vod["title"])

            add_item(str(id_)+':'+str(slug), tytul, foto, mud, folder=True,fanart=FANART)
        setView('movies')
        #xbmcplugin.setContent(addon_handle, 'movies')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)    

    def ListFavorites(self):
        self.refreshTokenTVN()

        data = getRequests('https://player.pl/playerapi/subscriber/bookmark?type=FAVOURITE&4K=true&platform=ANDROID_TV',headers = self.HEADERS2, params = {})
        try:
            vods = data['items']
            if len(vods)>0:
                for vod in vods:
                    vod=vod['item']
                    id_=vod['id']
                    
                    typ = vod['type']
                    foto = vod['images']['pc'][0]['mainUrl']
                    foto = 'https:' + foto if foto.startswith('//') else foto
                    tytul = vod["title"]
                    opis = remove_html_tags(vod["lead"])
                    dod=''
                    mud = 'listcategSerial'
                    fold = True
                    playk =False
                    if typ != 'SERIAL':
                        mud = 'playvid'
                        fold = False
                        playk =True
                    add_item(id_, PLchar(tytul)+dod, foto, mud, folder=fold, IsPlayable=playk, fanart=FANART)
            setView('tvshows')    
            #xbmcplugin.setContent(addon_handle, 'tvshows')
            xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
            xbmcplugin.endOfDirectory(addon_handle)    
        except:
            xbmc.executebuiltin("ActivateWindow(10134)")
    def ListSearch(self,query):
        self.refreshTokenTVN()

        mylist = getRequests('https://player.pl/playerapi/subscriber/product/available/list?4K=true&platform=ANDROID_TV',headers = self.HEADERS2, params = {})
        
        PARAMS = {}
        urlk='https://player.pl/playerapi/product/live/search?keyword=%s&4K=true&platform=ANDROID_TV'%(query)
    
        lives = getRequests(urlk,headers = self.HEADERS2, params = PARAMS)
        lives = lives['items']
        if len(lives)>0:
            for live in lives:
                ac=''
        urlk='https://player.pl/playerapi/product/vod/search?keyword=%s&4K=true&platform=ANDROID_TV'%(query)
    
        vods = getRequests(urlk,headers = self.HEADERS2, params = PARAMS)
        vods = vods['items']
        if len(vods)>0:
            for vod in vods:
                id_=vod['id']
                
                typ = vod['type']
                foto = vod['images']['pc'][0]['mainUrl']
                foto = 'https:' + foto if foto.startswith('//') else foto
                tytul = vod["title"]
                opis = remove_html_tags(vod["lead"])
                dod=''
                mud = 'listcategSerial'
                fold = True
                playk =False
                
                if vod.get("payable",None) or vod.get("ncPlus",None):
    
                    if vod['id'] not in mylist:
                        dod=' - [I][COLOR khaki](brak w pakiecie)[/COLOR][/I]'
                        fold = True
                        playk =False
                        mud = ' ' 
                if typ != 'SERIAL':
                    mud = 'playvid'
                    fold = False
                    playk =True
                    if vod.get("payable",None) or vod.get("ncPlus",None):
                        if vod['id'] not in mylist:
                            dod=' - [I][COLOR khaki](brak w pakiecie)[/COLOR][/I]'
                            fold =False
                            playk =False
                            mud = ' ' 
                add_item(id_, PLchar(tytul)+dod, foto, mud, folder=fold, IsPlayable=playk, fanart=FANART)
        #setView('tvshows')    
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)        
        
    def ListEpizody(self,tytsezid):
        idmain,idsezon = tytsezid.split(':')
        self.refreshTokenTVN()

        PARAMS = {}
        urlk='https://player.pl/playerapi/product/vod/serial/%s/season/%s/episode/list?4K=true&platform=ANDROID_TV'%(str(idmain), str(idsezon))
    
        epizody = getRequests(urlk,headers = self.HEADERS2, params = PARAMS)
        mylist = getRequests('https://player.pl/playerapi/subscriber/product/available/list?4K=true&platform=ANDROID_TV',headers = self.HEADERS2, params = {})
        mud ='playvid'
        fold =False
        for f in epizody:
    
            urlid = str(f["id"])
            epiz = f["episode"]
            opis = remove_html_tags(f["lead"])
            foto = f['images']['pc'][0]['mainUrl']
            foto = 'https:' + foto if foto.startswith('//') else foto
            sez = (f["season"]["number"])
            tyt = PLchar((f["season"]["serial"]["title"]))
            if 'fakty-' in f.get('shareUrl',None):
                tytul = '%s - %s'%(tyt,PLchar(f['title']))
            else:
                tytul = '%s - S%02dE%02d'%(tyt,sez,epiz)
            dod=''
            mud ='playvid'
            fold =False
            playk =True
            if f.get("payable",None) or f.get("ncPlus",None):
                if f['id'] not in mylist:
                    dod=' - [I][COLOR khaki](brak w pakiecie)[/COLOR][/I]'
                    playk =False
                    fold = False
                    mud = '   '
                
                
            add_item(urlid, PLchar(tytul)+dod, foto, mud, folder=fold, IsPlayable=playk, infoLabels={'plot':opis}, fanart=FANART)
        setView('episodes')
        #xbmcplugin.setContent(addon_handle, 'episodes')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)    
    def getSezony(self,id,tytul, opis, foto,typ):
        self.refreshTokenTVN()

        PARAMS = {}
        urlk='https://player.pl/playerapi/product/vod/serial/%s/season/list?4K=true&platform=ANDROID_TV'%(str(id))
        out=[]
        sezony = getRequests(urlk,headers = self.HEADERS2, params = PARAMS)
        for sezon in sezony:
            seas=str(sezon['number'])
            urlid = '%s:%s'%(str(id),str(sezon['id']))
            title = '%s - Sezon %s'%(tytul,seas)
            if not typ:
                seas=str(sezon["display"])
                title = '%s / %s'%(tytul,seas)
            out.append({'title':PLchar(title),'url':urlid,'img':foto,'plot':PLchar(opis)})    
        return out
        
    def ListCategSerial    (self,id):    
        self.refreshTokenTVN()

        PARAMS = {}
    
        urlk = 'https://player.pl/playerapi/product/vod/serial/%s?4K=true&platform=ANDROID_TV'%str(id)
    
        data = getRequests(urlk,headers = self.HEADERS2, params = PARAMS)
        tytul, opis, foto, sezon, epizod = getMetaDane(data)
    
        typ=True
        if sezon or epizod:
            if not sezon:
                typ=False
            items=self.getSezony(id,tytul, opis, foto,typ)
            for f in items:
                add_item(name=f.get('title'), url=f.get('url'), mode='listEpizody', image=f.get('img'), folder=True, infoLabels=f)
        setView('episodes')    
        #xbmcplugin.setContent(addon_handle, 'episodes')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)    
        
    def ListCollectContent(self,idslug):
        self.refreshTokenTVN()
        id,slug = idslug.split(':')
        PARAMS ={}
        urlk = 'https://player.pl/playerapi/product/section/%s?4K=true&platform=ANDROID_TV&firstResult=0&maxResults=250'%(id)
        data = getRequests(urlk,headers = self.HEADERS2, params = PARAMS)
    
    
        mylist = getRequests('https://player.pl/playerapi/subscriber/product/available/list?4K=true&platform=ANDROID_TV',headers = self.HEADERS2, params = {})
        
        items = data['items']
        for item in items:
            tytul, opis, foto, sezon, epizod=getMetaDane2(item)
            dod=''
    
            fold = False
            playk =True
            mud = 'playvid'
            
            if item["type"] == 'SERIAL':
                fold = True
                mud = 'listcategSerial'
                playk =False
            if item.get("payable",None) or item.get("ncPlus",None):
                if item['id'] not in mylist:
                    dod=' - [I][COLOR khaki](brak w pakiecie)[/COLOR][/I]'
                    playk =False
                    mud = '   '

            add_item(str(item['id']), PLchar(item['title'])+dod, foto, mud, folder=fold,IsPlayable=playk,fanart=FANART)
        setView('movies')    
        #xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)
    
    
    def ListCategContent(self,idslug):
        self.refreshTokenTVN()
        id,slug = idslug.split(':')

    
        PARAMS = {'firstResult':'0','maxResults':'250','category[]':slug,'sort':'createdAt','order':'desc','genreId[]':id,'4K':'true','platform':'ANDROID_TV'}
    
        urlk=self.PRODUCTVODLIST
    
        data = getRequests(urlk,headers = self.HEADERS2, params = PARAMS)
    
    
        mylist = getRequests('https://player.pl/playerapi/subscriber/product/available/list?4K=true&platform=ANDROID_TV',headers = self.HEADERS2, params = {})
        
        items = data['items']
        for item in items:
    
            dod=''
    
            fold = False
            playk =True
            mud = 'playvid'
            if item["type"] == 'SERIAL':
                fold = True
                mud = 'listcategSerial'
                playk =False
            if item["payable"]:
                if item['id'] not in mylist:
                    dod=' - [I][COLOR khaki](brak w pakiecie)[/COLOR][/I]'
                    playk =False
                    mud = '   '
            add_item(str(item['id']), PLchar(item['title'])+dod, ikona, mud, folder=fold,IsPlayable=playk,fanart=FANART)
        setView('tvshows')    
        #xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)
    
    def getTvs(self):
        self.refreshTokenTVN()

        urlk='https://player.pl/playerapi/product/live/list?4K=true&platform=ANDROID_TV'
    
        out=[]
        
        data = getRequests(urlk,headers = self.HEADERS2, params = {})
        
        mylist = getRequests('https://player.pl/playerapi/subscriber/product/available/list?4K=true&platform=ANDROID_TV',headers = self.HEADERS2, params = {})
        

        for dd in data:
            id_=dd['id']
            tyt=dd['title']
            foto = dd['images']['pc'][0]['mainUrl']
            foto = 'https:' + foto if foto.startswith('//') else foto
            urlid = '%s:%s'%(id_,'kanal')
            try:
                opis = dd['lead']
            except:
                opis=''
            dod=''
            if dd["payable"]:
                if dd['id'] not in mylist:
                    dod=' - [I][COLOR khaki](brak w pakiecie)[/COLOR][/I]'
                    playk =False
                    mud = '   '
            out.append({'title':PLchar(tyt)+dod,'url':urlid,'img':foto,'plot':PLchar(opis)})    
        return out
    def ListCateg(self,idslug):
        id,slug = idslug.split(':')
        mud = "listcategContent"
        fold = True
        playk=False
    
        if slug=='live':
            mud ='playvid'
            fold=False
            playk=True
            dane = self.getTvs()
            for f in dane:
    
                add_item(name=f.get('title'), url=f.get('url'), mode='playvid', image=f.get('img'), folder=False,  IsPlayable=True,infoLabels=f)
    
        else:
            
            dane=serialemenu[id]
            for f in dane:
                urlk = str(f['id'])+':'+slug
                add_item(urlk, f['name'], ikona, mud, folder=fold, IsPlayable=playk,fanart=FANART)
        setView('tvshows')        
    #    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')        
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)        
    
    
if __name__ == '__main__':

    mode = params.get('mode', None)
    
    if not mode:
        
        home()
        setView('tvshows')    
        #xbmcplugin.setContent(addon_handle, 'tvshows')    
        xbmcplugin.endOfDirectory(addon_handle)        

        
    elif mode == "listcateg":
        PLAYERPL().ListCateg(exlink)
        
        
    elif mode == "listcategContent"    :
        PLAYERPL().ListCategContent(exlink)    
        
    elif mode == "listcategSerial"    :
        PLAYERPL().ListCategSerial    (exlink)
    elif mode == "listEpizody"    :
        PLAYERPL().ListEpizody    (exlink)

    elif mode=='search':
        query = xbmcgui.Dialog().input(u'Szukaj..., Podaj tytuł filmu', type=xbmcgui.INPUT_ALPHANUM)
        if query:      
            PLAYERPL().ListSearch(query.replace(' ','+'))
        else:
            pass
    elif mode == 'favors':
        PLAYERPL().ListFavorites()
    elif mode == "collect":
        PLAYERPL().ListCollection()
        
    elif mode == "listcollectContent":
        PLAYERPL().ListCollectContent(exlink)
        
    elif mode=='playvid':    
        PLAYERPL().playvid(exlink)
    
    elif mode=='login':

        set_setting('logged', 'true')
        PLAYERPL().LOGGED = addon.getSetting('logged')
        xbmc.executebuiltin('Container.Refresh()')
        
    elif mode=='opcje':
        addon.openSettings()
        
        
    elif mode=='logout':

        yes = xbmcgui.Dialog().yesno("[COLOR orange]Uwaga[/COLOR]", 'Wylogowanie spowoduje konieczność ponownego wpisania kodu na stronie.[CR]Jesteś pewien?',yeslabel='TAK', nolabel='NIE')
        if yes:
            set_setting('refresh_token', '')
            set_setting('logged', 'false')
            PLAYERPL().REFRESH_TOKEN = addon.getSetting('refresh_token')
            PLAYERPL().LOGGED = addon.getSetting('logged')
            xbmc.executebuiltin('Container.Refresh()')