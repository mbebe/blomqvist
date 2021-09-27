# -*- coding: utf-8 -*-


class Playlist:
    EXTM3U = "#EXTM3U\n";
    service = None

    def __init__(self, service):
        self.service = service

    def addM3UChannel(self, count, name, thumb, group, id, source):
        nameStr = unicode(name)
        genreStr = unicode(group)
        self.EXTM3U += '#EXTINF:0, tvg-id="' + nameStr
        self.EXTM3U += '" tvg-name="' + nameStr
        self.EXTM3U += '" tvg-logo="' + str(thumb)
        self.EXTM3U += '" group-title="' + genreStr
        self.EXTM3U += '", ' + nameStr + '\n'
        self.EXTM3U += str(source) + '\n\n'

    def getM3UList(self):
        return self.EXTM3U

