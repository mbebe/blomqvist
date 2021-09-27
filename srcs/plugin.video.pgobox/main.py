# -*- coding: UTF-8 -*-
from __future__ import absolute_import
import sys, re, os

try:
    import http.cookiejar
    import urllib.request, urllib.parse, urllib.error
    from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
except ImportError:
    import cookielib
    import urllib
    import urlparse
    from urllib import urlencode, quote_plus, quote, unquote
    from urlparse import parse_qsl

import requests
import urllib3

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs

import json

import inputstreamhelper

import datetime

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.pgobox')

PATH            = addon.getAddonInfo('path')
if sys.version_info[0] > 2:
    DATAPATH        = xbmcvfs.translatePath(addon.getAddonInfo('profile'))#.decode('utf-8')
else:
    DATAPATH        = xbmc.translatePath(addon.getAddonInfo('profile'))
RESOURCES       = PATH+'/resources/'
COOKIEFILE = os.path.join(DATAPATH,'ipla.cookie')

ikona = RESOURCES+'../icon.png'
FANART=RESOURCES+'../fanart.jpg'
sys.path.append( os.path.join( RESOURCES, "lib" ) )

exlink = params.get('url', None)
name= params.get('name', None)
page = params.get('page','')

rys= params.get('image', None)

kukz=''

TIMEOUT=15
UAIPLA = "pg_pc_windows_firefox_html/1 (Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0)"#"www_iplatv/12345 (Mozilla/5.0 Windows NT 6.1; Win64; x64; rv:84.0 Gecko/20100101 Firefox/84.0)"
OSINFO = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"#"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
sess = requests.Session()
if sys.version_info[0] > 2:
    sess.cookies = http.cookiejar.LWPCookieJar(COOKIEFILE)
else:
    sess.cookies = cookielib.LWPCookieJar(COOKIEFILE)

serialkatv = addon.getSetting('serialkatV')
if not serialkatv:
    addon.setSetting('serialkatV','')
serialkatn = addon.getSetting('serialkatN') if serialkatv else 'wszystkie'
sortowaniev = addon.getSetting('sortowanieV')
if not sortowaniev:
    addon.setSetting('sortowanieV','"12"')
sortowanien = addon.getSetting('sortowanieN') if '12' not in sortowaniev else 'Ostatnio dodane'
sortowanien = 'ostatnio dodane' if '12' in sortowaniev else 'alfabetycznie'
filmkatv = addon.getSetting('filmkatV')
if not filmkatv:
    addon.setSetting('filmkatV','')
filmkatn = addon.getSetting('filmkatN') if filmkatv else 'wszystkie'

programykatv = addon.getSetting('programykatV')
if not programykatv:
    addon.setSetting('programykatV','')
programykatn = addon.getSetting('programykatN') if programykatv else 'wszystkie'

sportkatv = addon.getSetting('sportkatV')
if not sportkatv:
    addon.setSetting('sportkatV','')
sportkatn = addon.getSetting('sportkatN') if sportkatv else 'wszystkie'

newskatv = addon.getSetting('newskatV')
if not newskatv:
    addon.setSetting('newskatV','')
newskatn = addon.getSetting('newskatN') if newskatv else 'wszystkie'

wiedzakatv = addon.getSetting('wiedzakatV')
if not wiedzakatv:
    addon.setSetting('wiedzakatV','')
wiedzakatn = addon.getSetting('wiedzakatN') if wiedzakatv else 'wszystkie'

dziecikatv = addon.getSetting('dziecikatV')
if not dziecikatv:
    addon.setSetting('dziecikatV','')
dziecikatn = addon.getSetting('dziecikatN') if dziecikatv else 'wszystkie'

def build_url(query):
    try:
        urlencode = urllib.urlencode(query)
    except:
        urlencode = urllib.parse.urlencode(query)

    return base_url + '?' + urlencode

def add_item(url, name, image, mode, folder=False, IsPlayable=False, infoLabels=False, movie=True,itemcount=1, page=0,fanart=FANART,moviescount=0):
    list_item = xbmcgui.ListItem(label=name)

    if IsPlayable:
        list_item.setProperty("IsPlayable", 'True')
        isp = []
        isp.append(('Informacja', 'XBMC.Action(Info)'))
        list_item.addContextMenuItems(isp, replaceItems=False)
        
    if infoLabels:
        list_item.setInfo(type="video", infoLabels=infoLabels)
    else:

        infoLabels={'title': name,'plot':name}

    art_keys = ['thumb', 'poster', 'banner', 'fanart', 'clearart', 'clearlogo', 'landscape', 'icon']
    art = dict(zip(art_keys, [image for x in art_keys]))
    art['landscape'] = FANART
    art['fanart'] = FANART
    list_item.setArt(art)

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
    
def home():
    IPLA().logowanie()

    add_item('', 'LIVE', ikona, "listLIVES", folder=True,fanart=FANART)
    add_item('', 'Kanały TV', ikona, "listTVS", folder=True,fanart=FANART)
    add_item('', 'VOD', ikona, "listVODcateg", folder=True,fanart=FANART)
    add_item('', 'HBO', ikona, "HBO", folder=True,fanart=FANART)

    add_item('', '[B][COLOR khaki]Szukaj[/COLOR][/B]', ikona, "szukaj", folder=True,fanart=FANART)
    add_item('', 'Opcje', ikona, "opcje", folder=False,fanart=FANART)
    if IPLA().LOGGED == 'true':
        add_item('', '[B][COLOR blue]Wyloguj[/COLOR][/B]', ikona, "logout", folder=False,fanart=FANART)
        
def HBOsubmenu():
    add_item('reco_list|25|Polecane', 'Polecane', ikona, "packcontent", folder=True,fanart=FANART)
    add_item('media_type|movie|Filmy', 'Filmy', ikona, "packcontent", folder=True,fanart=FANART)
    add_item('key_categories|1754|Seriale', 'Seriale', ikona, "packcontent", folder=True,fanart=FANART)
    add_item('genres|Dla Dzieci|Kids filmy', 'KIDS filmy', ikona, "packcontent", folder=True,fanart=FANART)
    add_item('key_categories|5001096|Kids seriale', 'KIDS seriale', ikona, "packcontent", folder=True,fanart=FANART)
    add_item('media_type|tv|Kanały TV', 'Kanały TV', ikona, "packcontent", folder=True,fanart=FANART)
    xbmcplugin.endOfDirectory(addon_handle) 
    
def HBOmenu():
    if IPLA().LOGGED == 'true':
        acc=IPLA().checkAccess('HBOacc')
        if acc:
            HBOsubmenu()
        else:
            xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie masz dostępu do tego pakietu.',xbmcgui.NOTIFICATION_INFO, 6000,False)
    else:
        xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie jesteś zalogowany.',xbmcgui.NOTIFICATION_INFO, 6000,False)
        
def ListPacketContent(datas,page):
    items,itemss,npage = IPLA().getPacketContent(datas,page)
    if items:
        fold=False
        mud='playtvs'
        ispla=True
        for item in items:
            add_item(item['url'], item['title'], item['image'], mud, folder=fold, IsPlayable=ispla, infoLabels={'title':item['title'], 'image': item['image'], 'plot':item['plot'],'OriginalTitle':item['originaltitle'],'year':item['year'],'duration': item['duration'],'genre': item['genre'],'country':item['country'] },fanart=FANART)
    if itemss:
        fold=True
        mud='listContent'
        ispla=False
        for item in itemss:
            add_item(item['url'], item['title'], item['image'], mud, folder=fold, IsPlayable=ispla, infoLabels={'plot':item['plot']},fanart=FANART)
    if npage:
        f=npage[0]
        add_item(name=f.get('title'), url=f.get('url'), mode="packcontent", image=f.get('image'), folder=True,page=f.get('page'))
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%Y")

    setView('tvshows')
    #sxbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle) 
        
def ListVODcateg():
    if IPLA().LOGGED == 'true':

    #    items=[{'url': 5024044, 'plot': 'To miejsce dla miłośników wszystkich seriali Telewizji Polsat i nie tylko. Tu znajdziecie swoje ulubione seriale komediowe, obyczajowe i kryminalne.', 'img': 'https://r.dcs.redcdn.pl/http/o2/redefine/redb/64/6443791fd5030a9be3114f72ab366ff5.jpg', 'title': 'SERIAL'}, {'url': 5024059, 'plot': 'Największe internetowe kino w Polsce. Każdy miłośnik X Muzy znajdzie tu coś dla siebie. ', 'img': 'https://r.dcs.redcdn.pl/http/o2/redefine/redb/a5/a548757da60de0894d63a6f91becd5a3.jpg', 'title': 'FILM'}, {'url': 5024077, 'plot': 'Każdy kibic znajdzie tu coś dla siebie. Relacje z Ligi Mistrzów w piłce nożnej i piłce ręcznej, Ligi Europejskiej, siatkarska Plusliga i Plusliga Kobiet, sporty walki, sporty samochodowe i wiele innych wydarzeń sportowych.', 'img': 'https://r.dcs.redcdn.pl/http/o2/redefine/redb/d4/d4ce016f9f8c11eb1f6c14da33ceb965.jpg', 'title': 'SPORT'}, {'url': 5002787, 'plot': 'Przyjemność poprzez relaks! Kabarety, Muzyka, Talk shows - tutaj każdy znajdzie coć dla siebie.', 'img': 'https://r.dcs.redcdn.pl/http/o2/redefine/redb/3b/3bae15a5a5009189bdd40e54ad99f1e8.jpg', 'title': 'ROZRYWKA'}, {'url': 5002788, 'plot': 'Zbiór informacji o otaczającej nas rzeczywistości!', 'img': 'https://r.dcs.redcdn.pl/http/o2/redefine/redb/61/61e3597b651a7b223fe2c52a753d33eb.jpg', 'title': 'NEWS'}, {'url': 5002789, 'plot': 'Zestaw przydatnych informacji o życiu i świecie wraz z przykładami ich wykorzystywania.', 'img': 'https://r.dcs.redcdn.pl/http/o2/redefine/redb/16/161e7fa69332ebfd9d06688cfc415a70.jpg', 'title': 'WIEDZA'}, {'url': 5001096, 'plot': 'DLA DZIECI - zbiór bajek i kreskówek. Znajdziecie tu takie tytuły jak: Atomówki, Laboratorium Dextera, Bugs Bunny, Bob Budowniczy czy Strażak Sam. Dodatkowo w ofercie znalazły się również rozrywkowo-edukacyjne programy dla najmłodszych, np. przygotowane przez TVP: Jedynkowe przedszkole, Budzik czy Domisie. ', 'img': 'https://r.dcs.redcdn.pl/http/o2/redefine/redb/8d/8d10fc3ff57b5019a8b546836dfbbd8f.jpg', 'title': 'DZIECI'}]
        items = [{'url': 5024044,'plot': 'To miejsce dla miłośników wszystkich seriali Telewizji Polsat i nie tylko. Tu znajdziecie swoje ulubione seriale komediowe, obyczajowe i kryminalne.','img': ikona,'title': 'SERIAL' }, {'url': 5024059,'plot': 'Największe internetowe kino w Polsce. Każdy miłośnik X Muzy znajdzie tu coś dla siebie. ','img': ikona,'title': 'FILM' }, {'url': 5024077,'plot': 'Każdy kibic znajdzie tu coś dla siebie. Relacje z Ligi Mistrzów w piłce nożnej i piłce ręcznej, Ligi Europejskiej, siatkarska Plusliga i Plusliga Kobiet, sporty walki, sporty samochodowe i wiele innych wydarzeń sportowych.','img': ikona,'title': 'SPORT' }, {'url': 5024076,'plot': 'Każdy kibic znajdzie tu coś dla siebie. Relacje z Ligi Mistrzów w piłce nożnej i piłce ręcznej, Ligi Europejskiej, siatkarska Plusliga i Plusliga Kobiet, sporty walki, sporty samochodowe i wiele innych wydarzeń sportowych.','img': ikona,'title': 'PROGRAMY' }, {'url': 5024078,'plot': 'DLA DZIECI - zbiór bajek i kreskówek. Znajdziecie tu takie tytuły jak: Atomówki, Laboratorium Dextera, Bugs Bunny, Bob Budowniczy czy Strażak Sam. Dodatkowo w ofercie znalazły się również rozrywkowo-edukacyjne programy dla najmłodszych, np. przygotowane przez TVP: Jedynkowe przedszkole, Budzik czy Domisie. ','img': ikona,'title': 'DZIECI' }]        
        for item in items:
            urlk=str(item['url'])+'|'+item['title'].lower()
            add_item(urlk, item['title'], item['img'], 'ListVODsubcateg', folder=True, IsPlayable=False, infoLabels={'plot':item['plot']},fanart=FANART)
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle) 
    else:
        xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie jesteś zalogowany.',xbmcgui.NOTIFICATION_INFO, 6000,False)
def getNew(categid):

    id,nazwa=categid.split('|')

    kat=''
    typ=''
    dysc=''

    kat = nazwa+'katn'

    typ = nazwa
    return kat,dysc, typ
def ListVODsubCateg(categid):

    kat,dysc, typ = getNew(categid)
    add_item('', "-    [COLOR lime]Sortowanie:[/COLOR] [B]"+sortowanien+"[/B]",'DefaultRecentlyAddedMovies.png', 'sortowanie', folder=False)
    if kat:
        kateg = "Dyscypliny:" if 'sport' in kat else 'Kategorie:'
        add_item('', "-        [COLOR lime]"+kateg+"[/COLOR] [B]"+eval(kat)+"[/B]",'DefaultRecentlyAddedMovies.png', '%s:kateg'%typ, folder=False)
    add_item(categid, 'Wyświetl materiały', rys, 'listContent', folder=True, IsPlayable=False,fanart=FANART)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
    xbmcplugin.endOfDirectory(addon_handle)

    
def Szukaj(query):
    items,itemss = IPLA().getSzukaj(query)
    if itemss:
        fold=True
        mud='listContent'
        ispla=False
        for item in itemss:
            add_item(item['url'], item['title'], item['image'], mud, folder=fold, IsPlayable=ispla, infoLabels={'plot':item['plot']},fanart=FANART)
    if items:
        fold=False
        mud='playtvs'
        ispla=True
        for item in items:
            add_item(item['url'], item['title'], item['image'], mud, folder=fold, IsPlayable=ispla, infoLabels={'title':item['title'], 'image': item['image'], 'plot':item['plot'],'OriginalTitle':item['originaltitle'],'year':item['year'],'duration': item['duration'],'genre': item['genre'],'country':item['country'] },fanart=FANART)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%Y")
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)
    
    
def ListContent(categid,page):

    items,itemss,npage = IPLA().getContent(categid,page)
    if items:
        fold=False
        mud='playtvs'
        ispla=True
        for item in items:
            add_item(item['url'], item['title'], item['image'], mud, folder=fold, IsPlayable=ispla, infoLabels={'title':item['title'], 'image': item['image'], 'plot':item['plot'],'OriginalTitle':item['originaltitle'],'year':item['year'],'duration': item['duration'],'genre': item['genre'],'country':item['country'] },fanart=FANART)
        setView('movies')

        #   xbmcplugin.setContent(addon_handle, 'videos')   
    if itemss:
        fold=True
        mud='listContent'
        ispla=False
        for item in itemss:
            add_item(item['url'], item['title'], item['image'], mud, folder=fold, IsPlayable=ispla, infoLabels={'plot':item['plot']},fanart=FANART)
        setView('tvshows')
        #xbmcplugin.setContent(addon_handle, 'videos')  
    if npage:
        f=npage[0]
        add_item(name=f.get('title'), url=f.get('url'), mode='listContent', image=f.get('image'), folder=True,page=f.get('page'))
        
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%Y")

    xbmcplugin.endOfDirectory(addon_handle) 
def ListTVS():
    if IPLA().LOGGED == 'true':
        
        items = IPLA().getChannels()
        dups=IPLA().getEpgs()
        
        opis=''
        for item in items:
    
            try:
                opis=dups[0][item.get('id')]
            except:
                try:
                    opis=dups[0][item.get('url')]
                except:
                    opis=''
        
       # for item in items:
            add_item(item['url'], item['title'], item['img'], 'playtvs', folder=False, IsPlayable=True, infoLabels={'plot':opis},fanart=FANART)
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        setView('tvshows')
    #   xbmcplugin.setContent(addon_handle, 'videos')   
        xbmcplugin.endOfDirectory(addon_handle) 
    else:
        xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie jesteś zalogowany.',xbmcgui.NOTIFICATION_INFO, 6000,False)
def ListLives():
    if IPLA().LOGGED == 'true':
        items = IPLA().getLives()
        for item in items:
            add_item(item['url'], item['title'], item['img'], 'playtvs', folder=False, IsPlayable=True, infoLabels={'plot':item['plot']},fanart=FANART)
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask = "%R, %Y, %P")
        setView('tvshows')
        #xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle) 
    else:
        xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie jesteś zalogowany.',xbmcgui.NOTIFICATION_INFO, 6000,False)

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
        content=sess.post(url,headers=headers,json=data, params=params, verify=False).json()
    else:
        content=sess.get(url,headers=headers, params=params, verify=False).json()
    return content

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

class IPLA(object):

    def __init__(self):
    
        self.api_base   = 'https://b2c-www.redefine.pl/rpc/'#'https://b2c-mobile.redefine.pl/rpc/'

        self.NAVIGATE   = self.api_base+'navigation/'   
        
        self.AUTH       = self.api_base+'auth/'
        self.HEADERSx = {'Accept-Charset': 'UTF-8',
                        'Content-Type': 'application/json',
                        'User-Agent': 'mipla_a/136 (Linux; U; Android 9.0; SAMSUNG; widevine=TRUE)',
                        'Host': 'b2c-www.redefine.pl',}
            

        self.HEADERS = {
            'Host': 'b2c-www.redefine.pl',
            'User-Agent': OSINFO,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': 'https://polsatboxgo.pl/',
            'DNT': '1',
            'Referer': 'https://polsatboxgo.pl/'}

        self.DEVICE_ID = addon.getSetting('device_id')
        self.CLIENT_ID = addon.getSetting('client_id')
        self.ID_ = addon.getSetting('id_')
        
        self.LOGIN = addon.getSetting('username')
        self.PASSWORD = addon.getSetting('password')
        self.LOGUJ = addon.getSetting('logowanie')

        self.SESSTOKEN = addon.getSetting('sesstoken')
        self.SESSEXPIR = addon.getSetting('sessexpir')
        self.SESSKEY= addon.getSetting('sesskey')
        
        self.LOGGED = addon.getSetting('logged')
        
        self.MYPERMS = addon.getSetting('myperm')
        self.ILOSC = int(addon.getSetting('ilosc'))
        self.KLIENT = addon.getSetting('klient')

        self.DANE = self.SESSTOKEN+'|'+self.SESSEXPIR+'|{0}|{1}'

        self.settingsFix()

    def settingsFix(self):
        from os import sep as osSeparator
        
        try:
            if sys.version_info[0] < 3:
                copy = xbmcaddon.Addon().getAddonInfo('path') + osSeparator + 'resources' + osSeparator + 'format' + osSeparator + 'settings_py2.xml'
                dest = xbmcaddon.Addon().getAddonInfo('path') + osSeparator + 'resources' + osSeparator + 'settings.xml'

                copyStat = os.stat(copy)
                copySize = copyStat.st_size

                stat = os.stat(dest)
                size = stat.st_size
                
                if size > (copySize + 100):
                    success = xbmcvfs.copy(copy, dest)

            else:
                copy = xbmcaddon.Addon().getAddonInfo('path') + osSeparator + 'resources' + osSeparator + 'format' + osSeparator + 'settings_py3.xml'
                dest = xbmcaddon.Addon().getAddonInfo('path') + osSeparator + 'resources' + osSeparator + 'settings.xml'

                copyStat = os.stat(copy)
                copySize = copyStat.st_size

                stat = os.stat(dest)
                size = stat.st_size

                if size < copySize:
                    success = xbmcvfs.copy(copy, dest)
        except Exception as ex:
            xbmc.log('No need to change settings.xml')

    def logowanie(self):
        if self.DEVICE_ID == '' or self.CLIENT_ID == '' or self.ID_ == '':
            self.createDatas()

        if self.LOGGED == 'true':
            
            if self.LOGIN and self.PASSWORD:
                self.DEVICE_ID = addon.getSetting('device_id')
                self.CLIENT_ID = addon.getSetting('client_id')
                self.KLIENT = addon.getSetting('klient')
                abc=self.KLIENT
                
                if self.KLIENT != 'polsatbox':
                
                     POST_DATA={"id":1,"jsonrpc":"2.0","method":"login","params":{"ua":"pbg_mobile_android_chrome_html/1 (Mozilla/5.0 (Linux; Android 10; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36)","deviceId":{"type":"other","value":self.DEVICE_ID},"userAgentData":{"portal":"pbg","deviceType":"mobile","application":"chrome","player":"html","build":1,"os":"android","osInfo":"Mozilla/5.0 (Linux; Android 10; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36"},"clientId":self.CLIENT_ID,"authData":{"authProvider":"icok","login":self.LOGIN,"password":self.PASSWORD,"deviceId":{"type":"other","value":self.DEVICE_ID}}}}
                    
                else:
                    
                    POST_DATA={"id":1,"jsonrpc":"2.0","method":"login","params":{"ua":UAIPLA,"deviceId":{"type":"other","value":self.DEVICE_ID},"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":OSINFO},"clientId":self.CLIENT_ID,"authData":{"login":self.LOGIN,"password":self.PASSWORD,"deviceId":{"type":"other","value":self.DEVICE_ID}}}}


                data = getRequests(self.AUTH, data = POST_DATA, headers=self.HEADERS)

                try:
                    if data['error']['data']["type"] == "RulesException":
                        POST_DATA={"id":1,"jsonrpc":"2.0","method":"acceptRules","params":{"ua":"pbg_mobile_android_chrome_html/1 (Mozilla/5.0 (Linux; Android 10; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36)","deviceId":{"type":"other","value":self.DEVICE_ID},"userAgentData":{"portal":"pbg","deviceType":"mobile","application":"chrome","player":"html","build":1,"os":"android","osInfo":"Mozilla/5.0 (Linux; Android 10; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36"},"clientId":self.CLIENT_ID,"rulesIds":[105],"authData":{"authProvider":"icok","login":self.LOGIN,"password":self.PASSWORD,"deviceId":{"type":"other","value":self.DEVICE_ID}}}}
                        data = getRequests(self.AUTH, data = POST_DATA, headers=self.HEADERS)
                except:
                    pass
                if data.get('error', None):


                    msg = data['error']['data']['userMessage']
                    addon.setSetting('sesstoken', '')
                    addon.setSetting('sessexpir', '')
                    addon.setSetting('sesskey', '')
                    addon.setSetting('myperm', '')
                    addon.setSetting('device_id', '')
                    addon.setSetting('client_id', '')
                    
                    xbmcgui.Dialog().notification('[B]Błąd[/B]', PLchar(msg),xbmcgui.NOTIFICATION_INFO, 6000,False)
                    
                    add_item('', '[B][COLOR blue]Zaloguj[/COLOR][/B]', ikona, "login", folder=False,fanart=FANART)
                    return False

                else:
                    myper=[]
                    for i in data["result"]["accessGroups"]:
                        if 'sc:' in i:
                            myper.append(str(i))
                        if 'oth:' in i:
                            myper.append(str(i))
                        if 'loc:' in i:
                            myper.append(str(i))
                        if 'cp_sub_ext:' in i:
                            myper.append(str(i.replace('cp_sub_ext','sc')))
                        if 'cp_sub_base:' in i:
                            myper.append(str(i.replace('cp_sub_base','sc')))
                            
                            

                    addon.setSetting('myperm', str(myper))

                    sesja=data['result']['session']
            
                    self.SESSTOKEN=sesja['id']
                    self.SESSEXPIR=str(sesja['keyExpirationTime'])
                    self.SESSKEY=sesja['key']
                    
                    addon.setSetting('sesstoken', self.SESSTOKEN)
                    addon.setSetting('sessexpir', str(self.SESSEXPIR))
                    addon.setSetting('sesskey', self.SESSKEY)
                    
                    set_setting('logged', self.LOGGED)
                    
                    return True

        if self.LOGGED != 'true':
            add_item('', '[B][COLOR blue]Zaloguj[/COLOR][/B]', ikona, "login", folder=False,fanart=FANART)
        return True
        
    def createDatas(self):
        import random
        def getSystemId(il):
            def gen_hex_code(myrange=6):
                return ''.join([random.choice('0123456789ABCDEF') for x in range(myrange)])
        
            systemid = gen_hex_code(il) + '-' + gen_hex_code(4) + '-' + gen_hex_code(4) + '-' + gen_hex_code(4) + '-' + gen_hex_code(12)
            systemid = systemid.strip()

            return systemid

        def uniq_id():
            device_id = ''
        
            if addon.getSetting('device_id'):
                device_id = addon.getSetting('device_id')
            else:
                device_id = getSystemId(10)
            set_setting('device_id', device_id)
            return device_id
            
        def client_id():
            client_id = ''
        
            if addon.getSetting('client_id'):
                client_id = addon.getSetting('client_id')
            else:
                client_id = getSystemId(10)
            set_setting('client_id', client_id)
            return client_id
            
        def id_():
            id_ = ''
        
            if addon.getSetting('id_'):
                id_ = addon.getSetting('id_')
            else:
                id_ = str(int(''.join([str(random.randint(0,9)) for _ in range(4)])))
            set_setting('id_', id_)
            return id_
        self.DEVICE_ID =uniq_id()
        self.CLIENT_ID =client_id()
        self.ID_ = id_()
        
    def getHmac(self,dane):

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
        secretAccessKey = base64_decode(self.SESSKEY.replace('-','+').replace('_','/'))
        
        auth = hmac.new(secretAccessKey, ssdalej.encode("ascii"), sha256)
        vv= base64.b64encode(bytes(auth.digest())).decode("ascii")

        aa=vv
        bb=ssdalej+'|'+aa.replace('+','-').replace('/','_')

        return bb

        
    def sesja(self,data):
        sesja=data['result']['session']
        self.SESSTOKEN=sesja['id']
        self.SESSEXPIR=str(sesja['keyExpirationTime'])
        self.SESSKEY=sesja['key']
        
        addon.setSetting('sesstoken', self.SESSTOKEN)
        addon.setSetting('sessexpir', str(self.SESSEXPIR))
        addon.setSetting('sesskey', self.SESSKEY)
        return self.SESSTOKEN+'|'+self.SESSEXPIR+'|{0}|{1}'
        
        
    def newtime(self,ff):
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
    
    def getSzukaj(self,query):
        self.getSesja()
        itemsf=[]
        itemss=[]
        dane = (self.DANE).format('navigation','searchContentWithTreeNavigation')
        authdata=self.getHmac(dane)
        POST_DATA = {"id":1,"jsonrpc":"2.0","method":"searchContentWithTreeNavigation","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"query":query,"offset":0,"limit":self.ILOSC,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        data = getRequests(self.NAVIGATE, data = POST_DATA, headers=self.HEADERS)
        dane = data['result']['results']
        for f in dane:
            imag = f.get('posters','')#
            imag = imag [-1]['src'].encode('utf-8') if imag else f['thumbnails'][-1]['src'].encode('utf-8')
            mid = f['id']
            if f.get('title',None):
                tytul = f['title'].encode('utf-8')
            else:
                tytul = f['name'].encode('utf-8')

            plotx = f['description'].encode('utf-8')
            plotx = plotx if plotx  else tytul
            urlid='%s|%s'%(mid,'kk')

            orgtit = f.get("originalTitle",'')
            orgtit = orgtit.encode('utf-8') if orgtit else ''
            year = f.get("releaseYear",'')
            year = year if year else ''
            durat = f.get("duration",'')
            durat = int(durat) if durat else ''
            genre = f.get("genres",[])
            genre = ','.join([x.strip() for x in genre]) if genre else ''
            countries = f.get("countries",'')
            countries = ','.join([x.strip() for x in countries]) if countries else ''

            if f.get("keyCategoryId",None):#.get("planet",None):
                reporting ='SERIAL'
                urlid='%s|%s'%(mid,'null')
                itemss.append({'title':tytul,'url':urlid,'image':imag,'plot':plotx})    

            else:
                itemsf.append({'title':tytul,'url':urlid,'image':imag,'plot':plotx,'year':year,'originaltitle': orgtit,'duration':durat,'genre': genre,'country':countries})    

        
        return itemsf,itemss

    def checkAccessList(self,idsy_):
    
        dane = self.DANE.format('drm','checkProductsAccess')
        authdata=self.getHmac(dane)

        POST_DATA = {"id":1,"jsonrpc":"2.0","method":"checkProductsAccess","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"products":idsy_,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        data = getRequests('https://b2c-www.redefine.pl/rpc/drm/', data = POST_DATA, headers=self.HEADERS)
        return data

        
    def getLives(self):
        self.getSesja()
        items = []
        dane = (self.DANE).format('navigation','getLiveChannels')
        authdata=self.getHmac(dane)
        POST_DATA = {"id":1,"jsonrpc":"2.0","method":"getLiveChannels","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        data = getRequests(self.NAVIGATE, data = POST_DATA, headers=self.HEADERS)
        item={}
        item1={}
        items=[]
        items1=[]
        zz=data['result']['results']
        for i in zz:
            z,data = self.newtime(i["publicationDate"]) 

            item['img'] = i['thumbnails'][-1]['src'].encode('utf-8')
            item['id'] = i["product"]['id']
            if sys.version_info[0] > 2:
                item['title'] = '%s - %s'%(data,i['title'].upper())
            else:
                item['title'] = '%s - %s'%(data,i['title'].upper().encode('utf-8')) 
            item['plot'] = i['description'].encode('utf-8')
            item['plot'] = item['plot'] if item['plot']  else item['title']

            item = {'url':i['id'],'img':item['img'],'plot':item['plot']}
            item1 = {'id': i['product']['id'],"type":i['product']['type'],"subType":i['product']['subType']}
            items.append(item)
            items1.append(item1)
        data = self.checkAccessList(items1)
        items3=[]
        for d in data['result']:
                for i in items:

                    try:
                        if d["product"]["id"]==i['id']:
                            if d['access']["statusDescription"]!='has access':
                                i['title']+=' [COLOR red](brak w twoim pakiecie)[/COLOR]'
                             #   i['title']=i['title'].encode('ascii', 'ignore')

                            items3.append(i)   
                    except:
                        pass

        return items3

    def getPacketContent(self,datas,page):
        tp,vl,nm = datas.split('|')
        page=int(page)
        self.getSesja()
        itemsf=[]
        itemss=[]
        npout=[]
        
        dane = (self.DANE).format('navigation','getPacketContent')

        authdata=self.getHmac(dane)

        POST_DATA = {"id":1,"jsonrpc":"2.0","method":"getPacketContent","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"packetCode":"hbo","limit":self.ILOSC,"offset":page,"filters":[{"name":nm,"type":tp,"value":vl}],"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}

        data = getRequests(self.NAVIGATE, data = POST_DATA, headers=self.HEADERS)
        dane = data['result']['results']
        npage = data['result']["total"]
        if page+self.ILOSC<npage:
            npout.append({'title':'[B][COLOR green] >>> Następna strona >>> [/B][/COLOR]','url':datas,'image':RESOURCES+'nextpage.png','plot':'','page':page+self.ILOSC})
        
        for f in dane:
            imag = f.get('posters','')
            imag = imag [-1]['src'].encode('utf-8') if imag else f['thumbnails'][-1]['src'].encode('utf-8')
            mid = f['id']
            if f.get('title',None):
                tytul = f['title'].encode('utf-8')
            else:
                tytul = f['name'].encode('utf-8')

            plotx = f['description'].encode('utf-8')
            plotx = plotx if plotx  else tytul
            urlid='%s|%s'%(mid,'kk')
            if vl =='tv':
                urlid='%s|%s'%(mid,'HBOtv')
            orgtit = f.get("originalTitle",'')
            orgtit = orgtit.encode('utf-8') if orgtit else ''
            year = f.get("releaseYear",'')
            year = year if year else ''
            durat = f.get("duration",'')
            durat = int(durat) if durat else ''
            genre = f.get("genres",[])
            genre = ','.join([x.strip() for x in genre]) if genre else ''
            countries = f.get("countries",'')
            countries = ','.join([x.strip() for x in countries]) if countries else ''

            if 'key_categories' in datas:#f.get("reporting",'').get("planet",None):
                reporting ='SERIAL'
                urlid='%s|%s'%(mid,'null')
                itemss.append({'title':tytul,'url':urlid,'image':imag,'plot':plotx})    


            else:
                itemsf.append({'title':tytul,'url':urlid,'image':imag,'plot':plotx,'year':year,'originaltitle': orgtit,'duration':durat,'genre': genre,'country':countries})    

        return itemsf,itemss,npout

    def getContent(self,categid,page):
        page=int(page)
        catid,rodzaj = categid.split('|')
        self.getSesja()
        itemsf=[]
        itemss=[]
        npout=[]
        
        dane = (self.DANE).format('navigation','getCategoryContentWithFlatNavigation')

        authdata=self.getHmac(dane)

        POST_DATA={"id":1,"jsonrpc":"2.0","method":"getCategoryContentWithFlatNavigation","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"catid":int(catid),"offset":page,"filters":[],"collection":{"type":"sortedby","name":eval(sortowaniev),"default":True,"value":eval(sortowaniev)},"limit":self.ILOSC,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}

        if rodzaj == 'film':
            if filmkatv:

                kateg = eval(json.dumps(eval(filmkatv[:-1])))
                
                POST_DATA={"id":1,"jsonrpc":"2.0","method":"getCategoryContentWithFlatNavigation","params":{"catid":int(catid),"offset":page,"limit":40,"filters":[{"type":"genres","value":kateg}],"collection":{"type":"sortedby","name":eval(sortowaniev),"default":True,"value":eval(sortowaniev)},"ua":"pbg_pc_windows_firefox_html/1 (Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0)","deviceId":{"type":"other","value":self.DEVICE_ID},"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":OSINFO},"clientId":self.CLIENT_ID}}

        elif rodzaj == 'serial':
            if serialkatv:

                kateg = eval(json.dumps(eval(serialkatv[:-1])))
                POST_DATA={"id":1,"jsonrpc":"2.0","method":"getCategoryContentWithFlatNavigation","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"catid":int(catid),"offset":page,"filters":[{"type":"genres","value":kateg}],"collection":{"type":"sortedby","name":eval(sortowaniev),"default":True,"value":eval(sortowaniev)},"limit":self.ILOSC,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        elif rodzaj == 'programy':
            if programykatv:

                kateg = eval(json.dumps(eval(programykatv[:-1])))
                

                POST_DATA={"id":1,"jsonrpc":"2.0","method":"getCategoryContentWithFlatNavigation","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"catid":int(catid),"offset":page,"filters":[{"type":"genres","value":kateg}],"collection":{"type":"sortedby","name":eval(sortowaniev),"default":True,"value":eval(sortowaniev)},"limit":self.ILOSC,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        elif rodzaj == 'sport':
            if sportkatv:

                kateg = eval(PLchar((json.dumps(eval(sportkatv[:-1])))))
                if sys.version_info[0] > 2:
                    kateg = eval((json.dumps(eval(sportkatv[:-1]))))
                POST_DATA={"id":1,"jsonrpc":"2.0","method":"getCategoryContentWithFlatNavigation","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"catid":int(catid),"offset":page,"filters":[{"type":"genres","value":kateg}],"collection":{"type":"sortedby","name":eval(sortowaniev),"default":True,"value":eval(sortowaniev)},"limit":self.ILOSC,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        elif rodzaj == 'news':
            if newskatv:
                kateg = eval(json.dumps(eval(newskatv[:-1])))
                POST_DATA={"id":1,"jsonrpc":"2.0","method":"getCategoryContentWithFlatNavigation","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"catid":int(catid),"offset":page,"filters":[{"type":"genres","value":kateg}],"collection":{"type":"sortedby","name":eval(sortowaniev),"default":True,"value":eval(sortowaniev)},"limit":self.ILOSC,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        elif rodzaj == 'wiedza':
            if wiedzakatv:
                kateg = eval(PLchar((json.dumps(eval(wiedzakatv[:-1])))))
                if sys.version_info[0] > 2:
                    kateg = eval((json.dumps(eval(wiedzakatv[:-1]))))
                POST_DATA={"id":1,"jsonrpc":"2.0","method":"getCategoryContentWithFlatNavigation","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"catid":int(catid),"offset":page,"filters":[{"type":"genres","value":kateg}],"collection":{"type":"sortedby","name":eval(sortowaniev),"default":True,"value":eval(sortowaniev)},"limit":self.ILOSC,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        
        elif rodzaj == 'dzieci':
            if dziecikatv:
                kateg = eval(PLchar((json.dumps(eval(dziecikatv[:-1])))))
                if sys.version_info[0] > 2:
                    kateg = eval((json.dumps(eval(dziecikatv[:-1]))))
                POST_DATA={"id":1,"jsonrpc":"2.0","method":"getCategoryContentWithFlatNavigation","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"catid":int(catid),"offset":page,"filters":[{"type":"genres","value":kateg}],"collection":{"type":"sortedby","name":eval(sortowaniev),"default":True,"value":eval(sortowaniev)},"limit":self.ILOSC,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}

        data = getRequests(self.NAVIGATE, data = POST_DATA, headers=self.HEADERS)

        dane = data['result']['results']
        npage = data['result']["total"]
        if page+self.ILOSC<npage:
            npout.append({'title':'[B][COLOR green] >>> Następna strona >>> [/B][/COLOR]','url':categid,'image':RESOURCES+'nextpage.png','plot':'','page':page+self.ILOSC})

        for f in dane:

            imag = f.get('posters','')#
            imag = imag [-1]['src'].encode('utf-8') if imag else f['thumbnails'][-1]['src'].encode('utf-8')
            mid = f['id']
            if f.get('title',None):
                tytul = f['title'].encode('utf-8')
            else:
                tytul = f['name'].encode('utf-8')

            plotx = f['description'].encode('utf-8')
            plotx = plotx if plotx  else tytul
            urlid='%s|%s'%(mid,rodzaj)

            orgtit = f.get("originalTitle",'')
            orgtit = orgtit.encode('utf-8') if orgtit else ''
            year = f.get("releaseYear",'')
            year = year if year else ''
            durat = f.get("duration",'')
            durat = int(durat) if durat else ''
            genre = f.get("genres",[])
            genre = ','.join([x.strip() for x in genre]) if genre else ''
            countries = f.get("countries",'')
            countries = ','.join([x.strip() for x in countries]) if countries else ''

            if f.get("reporting",'').get("planet",None):
                reporting ='SERIAL'
                urlid='%s|%s'%(mid,'null')
                itemss.append({'title':tytul,'url':urlid,'image':imag,'plot':plotx})    


            else:
                itemsf.append({'title':tytul,'url':urlid,'image':imag,'plot':plotx,'year':year,'originaltitle': orgtit,'duration':durat,'genre': genre,'country':countries})    

        return itemsf,itemss,npout

    def getChannels(self):
        self.getSesja()
        items = []

        dane = (self.DANE).format('navigation','getTvChannels')
        
        authdata=self.getHmac(dane)

      #  POST_DATA = {"id":1,"jsonrpc":"2.0","method":"getTvChannels","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
#
     #   POST_DATA = {"id":1,"jsonrpc":"2.0","method":"getTvChannels","params":{"filters":[],"ua":UAIPLA,"deviceId":{"type":"other","value":self.DEVICE_ID},"userAgentData":{"portal":"pg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":OSINFO},"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
    
        
        
        
       # POST_DATA = {"id":1,"jsonrpc":"2.0","method":"getTvChannels","params":{"offset":0,"limit":40,"filters":[],"ua":UAIPLA,"deviceId":{"type":"other","value":self.DEVICE_ID},"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":OSINFO},"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        POST_DATA = {"id":1,"jsonrpc":"2.0","method":"getTvChannels","params":{"filters":[],"ua":UAIPLA,"deviceId":{"type":"other","value":self.DEVICE_ID},"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","player":"html","build":1,"os":"windows","osInfo":OSINFO},"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
        
        
        data = getRequests(self.NAVIGATE, data = POST_DATA, headers=self.HEADERS)

        myper=[]
        for i in eval(self.MYPERMS):
            if 'sc:' in i:

                myper.append(str(i))
            if 'oth:' in i:
                myper.append(str(i))
            if 'loc:' in i:
                myper.append(str(i))
            if 'cp_:' in i:
                myper.append(str(i))
            
                
        
        for i in data['result']['results']:
            item = {}
            channelperms = i['grantExpression'].split('*')
            channelperms = [w.replace('+plat:all', '') for w in channelperms]
            for j in myper:
                if j in channelperms or i['title']=='Polsat' or i['title']=='TV4':
                    item['img'] = i['thumbnails'][-1]['src'].encode('utf-8')
                    item['id'] = i['id']
                    item['title'] = i['title'].upper().encode('utf-8')
                    item['plot'] = i['description'].encode('utf-8')
                    item['plot'] = item['plot'] if item['plot']  else item['title']
                    item = {'title':item['title'],'url':item['id'],'img':item['img'],'plot':item['plot']}
                    items.append(item)
        
        dupes = []
        filter = []
        for entry in items:
            if not entry['url'] in dupes:
                filter.append(entry)
                dupes.append(entry['url'])
        addon.setSetting('kanaly', str(dupes))
        
        items = filter
        return items
    def getSesja(self):
        dane = (self.DANE).format('auth','getSession') #'|auth|getSession'
        authdata=self.getHmac(dane)

        POST_DATA ={"id":1,"jsonrpc":"2.0","method":"getSession","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}

        data = getRequests(self.AUTH, data = POST_DATA, headers=self.HEADERS)

        self.DANE=self.sesja(data)
        return
    def checkAccess(self,id_):
        acc=False
        dane = self.DANE.format('drm','checkProductAccess')
        authdata=self.getHmac(dane)
        POST_DATA = {"id":1,"jsonrpc":"2.0","method":"checkProductAccess","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"product":{"id":id_,"type":"media","subType":"movie"},"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}

        if 'HBOacc' in id_:

            POST_DATA = {"id":1,"jsonrpc":"2.0","method":"checkProductAccess","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"product":{"id":"hbo","type":"multiple","subType":"packet"},"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}   
        elif 'HBOtv' in id_:
                id_=id_.split('|')[0]
                POST_DATA = {"id":1,"jsonrpc":"2.0","method":"checkProductAccess","params":{"userAgentData":{"portal":"pbg","deviceType":"pc","application":"firefox","os":"windows","build":1,"osInfo":OSINFO},"ua":UAIPLA,"product":{"id":id_,"type":"media","subType":"tv"},"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}    

        data = getRequests('https://b2c-www.redefine.pl/rpc/drm/', data = POST_DATA, headers=self.HEADERS)
        
        acc = True if data['result']["statusDescription"] =="has access" else False

        return acc
        
    def getEpgs(self):
        kanaly = addon.getSetting('kanaly')
        kanaly=eval(kanaly)
        
        import datetime 
        now = datetime.datetime.now()
        now2 = datetime.datetime.now()+ datetime.timedelta(days=1)
        aa1=now.strftime('%Y-%m-%dT%H:%M:%S') + ('.%03dZ' % (now.microsecond / 10000))
        aa=now2.strftime('%Y-%m-%dT%H:%M:%S') + ('.%03dZ' % (now.microsecond / 10000))

        dane =self.SESSTOKEN+'|'+self.SESSEXPIR+'|navigation|getChannelsProgram'
        authdata=self.getHmac(dane)

        POST_DATA={"jsonrpc":"2.0","method":"getChannelsProgram","id":1,"params":{"channelIds":kanaly,"fromDate":aa1,"toDate":aa,"ua":UAIPLA,"authData":{"sessionToken":authdata}}}
        response = getRequests(self.NAVIGATE, data = POST_DATA, headers=self.HEADERS)

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

                        nowy,format_date=self.newtime(dane[i]["startTime"])
                        nowy2,format_date2=self.newtime(dane[i+1]["startTime"])
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
                        
                    except Exception as e:

                        pass

                    
            else:
                continue
            items[kanal]=el1
        dupek.append(items)
        
        return dupek
        
        
    def PlayIpla(self,id_,cpid=0):

        self.getSesja()
        acc=True
        if '|' in id_ :
            cpid= 1
            if not 'HBOtv' in id_:
                id_ = id_.split('|')[0]
                #cpid= 0
            else:   
                id_ = id_#.split('|')[0]
            acc=self.checkAccess(id_)
        if acc:
            if 'HBOtv' in id_:
                id_ = id_.split('|')[0]
                cpid= 0
            dane = self.DANE.format('navigation','prePlayData')
            
            authdata=self.getHmac(dane)

            POST_DATA = {"jsonrpc":"2.0","id":1,"method":"prePlayData","params":{"ua":"pbg_pc_windows_firefox_html/1 (Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0) (Windows 7; widevine=True)","userAgentData":{"deviceType":"pc","application":"firefox","os":"windows","build":2160500,"portal":"pbg","player":"html","widevine":True},"cpid":cpid,"mediaId":id_,"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}
            
            
            
            data = getRequests(self.NAVIGATE, data = POST_DATA, headers=self.HEADERS)

            playback = data ['result']['mediaItem']['playback']
            mediaid = playback['mediaId']['id']
            mediaSources = playback['mediaSources'][0]
            keyid = mediaSources['keyId']
            sourceid = mediaSources['id']
            cc= mediaSources.get('authorizationServices',None).get('pseudo',None)
            if not cc:

                UAcp=  'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
                stream_url = mediaSources['url']

                hd = {'Accept-Charset': 'UTF-8','User-Agent': UAcp,}

                LICENSE_URL = mediaSources['authorizationServices']['widevine']['getWidevineLicenseUrl']

                dane = self.DANE.format('drm','getWidevineLicense')
                authdata=self.getHmac(dane)
                devcid=(self.DEVICE_ID).replace('-','')

                data=quote('{"jsonrpc":"2.0","id":1,"method":"getWidevineLicense","params":{"userAgentData":{"deviceType":"pc","application":"firefox","os":"windows","build":2160500,"portal":"pbg","player":"html","widevine":true},"cpid":%s'%cpid+',"mediaId":"'+mediaid+'","sourceId":"'+sourceid+'","keyId":"'+keyid+'","object":"b{SSM}","deviceId":{"type":"other","value":"'+devcid+'"},"ua":"pbg_pc_windows_firefox_html/2160500","authData":{"sessionToken":"'+authdata+'"},"clientId":"'+self.CLIENT_ID+'"}}')
                
                import inputstreamhelper
                import ssl
                try:
                    _create_unverified_https_context = ssl._create_unverified_context
                except AttributeError:
                    pass
                else:
                    ssl._create_default_https_context = _create_unverified_https_context
                certificate_data="MIIF6TCCBNGgAwIBAgIQCYbp7RbdfLjlakzltFsbRTANBgkqhkiG9w0BAQsFADBcMQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3d3cuZGlnaWNlcnQuY29tMRswGQYDVQQDExJUaGF3dGUgUlNBIENBIDIwMTgwHhcNMjAxMTAzMDAwMDAwWhcNMjExMjA0MjM1OTU5WjBWMQswCQYDVQQGEwJQTDERMA8GA1UEBxMIV2Fyc3phd2ExHDAaBgNVBAoTE0N5ZnJvd3kgUG9sc2F0IFMuQS4xFjAUBgNVBAMMDSoucmVkZWZpbmUucGwwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC5dmzwoPSg3vOOSuRUHGVAKTvXQZEMwGCEhL6uojxn5BEKDTs00zdoOEkPdD8WFFEvYEKwZ/071XYPGuEMaiFs5zV0DYp7MsAi/nKZy0vTDn8FwdK2bPay2HwfjOAXhf+qjtJfWUI2o43kMLHa/TB9Nb61MSGbGGR1t3UxvJbLkJNdIFLdbU+oKof68PB7EZ9QDTCqklWhXokfxXbEmFGEicL1V8dQVmq2VzX/s7ICAg3WnFJ5Y/iJJV5em0JYNCRYYdf/Vohvp8C1yY0TP6XsfjgZZysdioFlHrDE5ilDIEu54jiCOCIAvnpTAR7wol66ok8pldoJiXkLn8OSFyPlAgMBAAGjggKrMIICpzAfBgNVHSMEGDAWgBSjyF5lVOUweMEF6gcKalnMuf7eWjAdBgNVHQ4EFgQUYG0/Qi/unb45V9e9z81Nn/opejcwJQYDVR0RBB4wHIINKi5yZWRlZmluZS5wbIILcmVkZWZpbmUucGwwDgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjA6BgNVHR8EMzAxMC+gLaArhilodHRwOi8vY2RwLnRoYXd0ZS5jb20vVGhhd3RlUlNBQ0EyMDE4LmNybDBMBgNVHSAERTBDMDcGCWCGSAGG/WwBATAqMCgGCCsGAQUFBwIBFhxodHRwczovL3d3dy5kaWdpY2VydC5jb20vQ1BTMAgGBmeBDAECAjBvBggrBgEFBQcBAQRjMGEwJAYIKwYBBQUHMAGGGGh0dHA6Ly9zdGF0dXMudGhhd3RlLmNvbTA5BggrBgEFBQcwAoYtaHR0cDovL2NhY2VydHMudGhhd3RlLmNvbS9UaGF3dGVSU0FDQTIwMTguY3J0MAwGA1UdEwEB/wQCMAAwggEEBgorBgEEAdZ5AgQCBIH1BIHyAPAAdgD2XJQv0XcwIhRUGAgwlFaO400TGTO/3wwvIAvMTvFk4wAAAXWO0xv2AAAEAwBHMEUCIQDN5p0QqITEtjMexdGmGjHR/8PxCN4OFiJDMFy7j74MgwIgXtmZfGnxI/GUKwwd50IVHuS6hmnua+fsLIpeOghE9XoAdgBc3EOS/uarRUSxXprUVuYQN/vV+kfcoXOUsl7m9scOygAAAXWO0xw9AAAEAwBHMEUCIQDNcrHQBd/WbQ3/sUvd0D37D5oZDIRf/mx3V5rAm6PvzwIgRJx+5MiIu/Qa4NN9vk51oBL171+iFRTyglwYR/NT5oQwDQYJKoZIhvcNAQELBQADggEBAHEgY9ToJCJkHtbRghYW7r3wvER8uGKQa/on8flTaIT53yUqCTGZ1VrjbpseHYqgpCwGigqe/aHBqwdJfjtXnEpFa5x1XnK2WgwK3ea7yltQxta3O3v8CJ7mU/jrWrDMYJuv+3Vz79kwOVmQN0kvlK56SnNR5PrHjO0URInGKbQenB2V0I5t/IjLsLCfKKao+VXoWCCzTY+GagcqNAt9DIiG//yXKs00vnj8I2DP74J9Up6eBdPgS7Naqi8uetaoharma9/59a/tb5PugixAmDGUzUf55NPl9otRsvVuCyT3yaCNtI2M09l6Wfdwryga1Pko+KT3UlDPmbrFUtwlPAU="                
                PROTOCOL = 'mpd'
                DRM = 'com.widevine.alpha'
                is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
                if is_helper.check_inputstream():
                    play_item = xbmcgui.ListItem(path=stream_url)#
                    play_item.setMimeType('application/xml+dash')
                    play_item.setContentLookup(False)
                    if sys.version_info[0] > 2:
                        play_item.setProperty('inputstream', is_helper.inputstream_addon)
                    else:
                        play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
                    play_item.setProperty("IsPlayable", "true")
                    
                    play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                    play_item.setProperty('inputstream.adaptive.license_type', DRM)

                    if addon.getSetting('drmcert') == 'true':
                        play_item.setProperty('inputstream.adaptive.server_certificate',certificate_data)

                    play_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')

                    play_item.setProperty('inputstream.adaptive.stream_headers', 'Referer: https://polsatboxgo.pl&User-Agent=' + quote(UAcp))
                    
                    play_item.setProperty('inputstream.adaptive.license_key',
                                        LICENSE_URL + '|Content-Type=application%2Fjson&Referer=https://polsatboxgo.pl/&User-Agent=' + quote(UAcp) +
                                        '|'+data+'|JBlicense')   
                     
                    play_item.setProperty('inputstream.adaptive.license_flags', "persistent_storage")
            else:
                dane = self.DANE.format('drm','getPseudoLicense')
                authdata=self.getHmac(dane)
                devcid=(self.DEVICE_ID).replace('-','')

                POST_DATA = {"jsonrpc":"2.0","id":1,"method":"getPseudoLicense","params":{"ua":UAIPLA,"userAgentData":{"deviceType":"pc","application":"firefox","os":"windows","build":1,"portal":"pbg","osInfo":OSINFO,"player":"html","widevine":True},"cpid":cpid,"mediaId":mediaid,"sourceId":sourceid,"deviceId":{"type":"other","value":devcid},"authData":{"sessionToken":authdata},"clientId":self.CLIENT_ID}}

                data = getRequests('https://b2c-www.redefine.pl/rpc/drm/', data = POST_DATA, headers=self.HEADERS)

                str_url=data['result']['url']
                play_item = xbmcgui.ListItem(path=str_url)#

            xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

        else:
            xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie masz dostępu do tego materiału.',xbmcgui.NOTIFICATION_INFO, 6000)
            sys.exit(0)
    
if __name__ == '__main__':

    mode = params.get('mode', None)
    
    if not mode:
        
        home()
        #xbmcplugin.setContent(addon_handle, 'videos')  
        xbmcplugin.endOfDirectory(addon_handle)     

    elif mode=='search':
        if IPLA().LOGGED == 'true':
            query = xbmcgui.Dialog().input(u'Szukaj..., Podaj tytuł filmu', type=xbmcgui.INPUT_ALPHANUM)
            if query:   
                PLAYERPL().ListSearch(query.replace(' ','+'))
            else:
                pass
        else:
            xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie jesteś zalogowany.',xbmcgui.NOTIFICATION_INFO, 6000,False)

    elif mode=='login':
        set_setting('logged', 'true')
        addon.openSettings()
        xbmc.executebuiltin('Container.Refresh') 

        
    elif mode=='logout':

        yes = xbmcgui.Dialog().yesno("[COLOR orange]Uwaga[/COLOR]", 'Czy na pewno chcesz się wylogować?',yeslabel='TAK', nolabel='NIE')
        if yes:
            set_setting('sesstoken', '')
            set_setting('sessexpir', '')
            set_setting('sessexpir', '')
            set_setting('logged', 'false')
            IPLA().LOGGED = addon.getSetting('logged')
            
            IPLA().SESSTOKEN = addon.getSetting('sesstoken')
            IPLA().SESSEXPIR = addon.getSetting('sessexpir')
            IPLA().SESSKEY= addon.getSetting('sesskey')
            
            set_setting('device_id', '')
            set_setting('client_id', '')
            set_setting('id_', '')      
            xbmc.executebuiltin('Container.Refresh') 
    elif mode == 'listTVS':
        ListTVS()
    elif mode == "listLIVES":
        ListLives() 
    elif mode == "listVODcateg":
        ListVODcateg()  
    elif mode == "ListVODsubcateg":
        ListVODsubCateg (exlink)    
    elif mode == 'playtvs':
        IPLA().PlayIpla(exlink)
    elif mode == 'listContent':
        ListContent(exlink,page)

        
    elif 'kateg' in mode:
        msg = 'kategorie'
        if 'film' in mode:
            myMode = 'filmkat'
            
            
            label =["wszystkie","akcja","animowany","biograficzny","dla dzieci","dokument","dramat","familijny","fantastyka","horror","komedia","kryminalny","muzyczny","obyczajowy","przygodowy","przyrodniczy","romans","thriller","wojenny"]
            value =["","Akcja","Animowany","Biograficzny","Dla Dzieci","Dokument","Dramat","Familijny","Fantastyka","Horror","Komedia","Kryminalny","Muzyczny","Obyczajowy","Przygodowy","Przyrodniczy","Romans","Thriller","Wojenny"]

            
            
            #label =["wszystkie","akcja","animowany","biograficzny","dla dzieci","dokument","dramat","familijny","fantastyka","horror","komedia","muzyczny","obyczajowy","przygodowy","przyrodniczy","romans","studio filmowe kadr","thriller","wojenny","zrekonstruowana klasyka"]
            #value =["","Akcja","Animowany","Biograficzny","Dla Dzieci","Dokument","Dramat","Familijny","Fantastyka","Horror","Komedia","Muzyczny","Obyczajowy","Przygodowy","Przyrodniczy","Romans","Studio Filmowe KADR","Thriller","Wojenny","Zrekonstruowana klasyka"]

        elif 'serial' in mode:
            myMode = 'serialkat'
            
            label =["wszystkie","animowany","dokumentalny","dramatyczny","familijny","historyczny","komediowy","kryminalny","obyczajowy","paradokumentalny","sensacyjny"]
            value =["","Animowany","Dokumentalny","Dramatyczny","Familijny","Historyczny","Komediowy","Kryminalny","Obyczajowy","Paradokumentalny","Sensacyjny"]

            
            
            #label =["wszystkie","animowany","dokumentalny","dramatyczny","dzieci","familijny","historyczny","komediowy","kryminalny","obyczajowy","paradokumentalny","sensacyjny","starszaki"]
            #value =["","Animowany","Dokumentalny","Dramatyczny","DZIECI","Familijny","Historyczny","Komediowy","Kryminalny","Obyczajowy","Paradokumentalny","Sensacyjny","Starszaki"]
        elif 'programy' in mode:
            myMode = 'programykat'
            
            
            label =["wszystkie","biznes","gry","historia","kabarety","kuchnia","kultura","magazyny reporterskie","moda i uroda","muzyka","nauka","paradokumentalny","podr\u00f3\u017ce","poradniki i hobby","programy dokumentalne","programy rozrywkowe","publicystyka","talk shows","zdrowie"]
            value =["","Biznes","Gry","Historia","Kabarety","Kuchnia","Kultura","Magazyny reporterskie","Moda i uroda","Muzyka","Nauka","Paradokumentalny","Podr\u00f3\u017ce","Poradniki i hobby","Programy dokumentalne","Programy rozrywkowe","Publicystyka","Talk shows","Zdrowie"]

            
            
            
        #    label =["wszystkie","gry","kabarety","kultura","moda i uroda","muzyka","programy rozrywkowe","talk shows"]
        #    value =["","Gry","Kabarety","Kultura","Moda i uroda","Muzyka","Programy rozrywkowe","Talk shows"]
        elif 'sport' in mode:
            myMode = 'sportkat'
            
            label =["wszystkie","inne","koszykówka","magazyny sportowe","motoryzacja","piłka nożna","piłka ręczna","siatkówka","sporty walki","tenis"]
            value =["", "Inne","Koszykówka","Magazyny sportowe","Motoryzacja","Piłka nożna","Piłka ręczna","Siatkówka","Sporty walki","Tenis"]
            msg = 'dyscyplinę'

        elif 'dzieci in mode':
            myMode = 'dziecikat'
            label =["wszystkie","najmłodsi","nastolatki","starszaki"]       
            value =["","Najmłodsi","Nastolatki","Starszaki"]    
            
        try:
            sel = xbmcgui.Dialog().multiselect('Wybierz '+msg,label)
        except:
            sel = xbmcgui.Dialog().select('Wybierz '+msg,label)
        if not sel: sel=quit()
        if isinstance(sel,list):
    
            n = '%s'%','.join( [ label[i] for i in sel]) if sel[0]>-1 else ''           
            v= ''.join('"{0}",'.format(value[i]) for i in sel) if sel[0]>-1 else ''
            if 'wszystkie' in n:    
                n='wszystkie'
                v=''
    
        else:
            sel = sel if sel>-1 else quit()
            
            v = '"%s"'%(value[sel])
            n = '%s'%(label[sel])
            if 'wszystkie' in n:
                v=''
        addon.setSetting(myMode+'V',v)
        addon.setSetting(myMode+'N',n)
        xbmc.executebuiltin("Container.Refresh")    
        
    elif 'sortowanie' in mode:
        myMode = 'sortowanie'
        label =["ostatnio dodane","alfabetycznie"]
        value =["12","13"]

        msg = 'sposob sortowania'

        sel = xbmcgui.Dialog().select('Wybierz '+msg,label)

        sel = sel if sel>-1 else quit()
        
        v = '"%s"'%(value[sel])
        n = '%s'%(label[sel])
    
        addon.setSetting(myMode+'V',v)
        addon.setSetting(myMode+'N',n)      
        xbmc.executebuiltin("Container.Refresh") 
        
    elif mode == 'szukaj':
        if IPLA().LOGGED == 'true':
            query = xbmcgui.Dialog().input(u'Szukaj, Podaj tytuł...', type=xbmcgui.INPUT_ALPHANUM)
            if query:       
                Szukaj(query)
        else:
            xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie jesteś zalogowany.',xbmcgui.NOTIFICATION_INFO, 6000,False)
    elif mode == 'HBO':
        HBOmenu()
    elif mode == 'packcontent':
        ListPacketContent(exlink,page)
    elif mode == 'opcje':
        addon.openSettings()   