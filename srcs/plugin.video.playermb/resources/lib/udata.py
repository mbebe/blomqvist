# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

# Author: rysson
# License: MIT

import sys
import json
try:
    import xbmcaddon
except ImportError:
    xbmcaddon = None


PY3 = sys.version_info >= (3, )

if PY3:
    basestring = str


class NoDefault:
    pass


class AddonUserData(object):
    """Simple userdata JSON file."""

    def __init__(self, path=None, default=None):
        if not path and xbmcaddon:
            path = xbmcaddon.Addon().getAddonInfo('path')
        self.path = path
        self.default = default
        self.dirty = False
        self._data = None

    @property
    def data(self):
        """Lazy load and get data."""
        if self._data is None:
            try:
                with open(self.path, 'r') as f:
                    self._data = json.load(f)
            except IOError as exc:
                print('UserData(%s): load failed: %r' % (self.path, exc))
        return self._data

    def do_save(self, indent=None):
        """Save data."""
        if self._data is None:
            return
        try:
            with open(self.path, 'w') as f:
                self._data = json.dump(self._data, f, indent=indent)
        except IOError as exc:
            print('UserData(%s): save failed: %r' % (self.path, exc))

    def save(self, indent=None):
        """Save file if data changed."""
        if self.dirty:
            self.do_save(indent=indent)

    def get(self, key, default=NoDefault):
        """Get dot-separated key value."""
        if self.data is None:
            return default
        if default is NoDefault:
            default = self.default
        if isinstance(key, basestring):
            key = key.split('.')
        data = self.data
        for item in key:
            try:
                data = data[item]
            except Exception:
                return default
        return data

    def set(self, key, value):
        """Set dot-separated key value. Force dicts in path."""
        if not key:
            return
        self.dirty = True
        if isinstance(key, basestring):
            key = key.split('.')
        if not isinstance(self.data, dict):
            self._data = {}
        data = self.data
        for item in key[:-1]:
            sub = data.setdefault(item, {})
            if not isinstance(sub, dict):
                data[item] = {}
            data = sub
        data[key[-1]] = value

    def remove(self, key):
        """Remove dot-separated key value."""
        if not key or self.data is None:
            return
        if isinstance(key, basestring):
            key = key.split('.')
        if not isinstance(self.data, dict):
            self._data = {}
        data = self.data
        for item in key[:-1]:
            sub = data.get(item)
            if not isinstance(sub, dict):
                return
            data = sub
        if key[-1] in data:
            self.dirty = True
            del data[key[-1]]

    delete = remove


if __name__ == '__main__':
    with open('/tmp/a.json', 'w') as f:
        f.write('{"a": 42, "b": [11, 22], "c": "nothing", "z": {"a": 22} }')

    d = UserData('/tmp/a.json')
    print(d.data)
    print(d.get('a'))
    print(d.get('b'))
    print(d.get('x'))
    print(d.get('z'))
    print(d.get('z.a'))
    print('---')
    print(d.set('z.b', 111), d.data)
    print(d.set('z.c', 'zażółć'), d.data)
    print(d.remove('z.b'), d.data)
    print(d.remove('z'), d.data)
    print(d.set('y.y', {'y': 'yyy'}), d.data)
    d.save(indent=2)
