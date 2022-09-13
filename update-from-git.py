#!/usr/bin/env python3
import urllib.request
import urllib.error
import os
import platform
import io
import json
import pandas as pd
# import subprocess
import pysimpleconfig as pyconf

_pre = 'https://api.github.com/repos/'
_suf = '/releases/latest'

pkgdatafile = 'pkg.csv'
# packagedata = pd.read_csv(pkgdatafile)

config = pyconf.SimpleJsonSingleConfig('pyGitZipInstaller', 'config.json')
try:
    pkg_list = config['pkgs',]
except KeyError:
    config['pkgs',] = {}
    pkg_list = config['pkgs',]
assert type(pkg_list) is dict

for key in pkg_list:
    _project = config['pkgs', key, 'repo']
    _dl_regex = config['pkgs', key, 'dl_regex']
    _prev_url = config['pkgs', key, 'prev_url']
    assert type(_project) is str
    fname = _project.replace('/','_')

    try:
        with urllib.request.urlopen(_pre+_project+_suf) as response:
            body = json.loads(response.read())
            # headers = response.getheaders()
            # status = response.getcode()

            # print(headers)
            # print(body)
            # print(status)

    except urllib.error.URLError as e:
        body = None
        print('-'*8+'error'+'-'*8)
        print(e.reason)

    assert body is not None
    assets = pd.DataFrame(body['assets'])
    # print(assets.name)

    _download_index = assets.name.str.match(_dl_regex)

    if len(assets[_download_index].browser_download_url) != 1:
        print(f'## WARNING ##')
        print(f'You have to reconsider the regex for specifying')
        print(f'the asset file you would like to install for')
        print(f'package: {_project}')
        print(f'##')
        continue

    _url = ''
    for _url in assets[_download_index].browser_download_url:
        print(f'Checking update for {_project}...')
        _url=_url

    if _url == _prev_url:
        print(f'{_project} is up to date')
        continue
    else:
        tempdf = pd.DataFrame(
            {"project": [_project],
             "dl_regex": [_dl_regex],
             'prev_url': _url})

        # begin downoad and installations
        print(f'updating {_project}')

        _PLATFORM = platform.system()
        if (_PLATFORM == 'Windows'):
            print('Windows')

        elif (_PLATFORM == 'Linux'):
            print('Linux')

        print(f'downloading from {_url}')

        # if the url ended with deb
        _data = urllib.request.urlopen(_url)
        with io.open(
                os.path.join(config.config_dir, f'{key}.zip'),
                "wb") as file:
            file.write(_data.read())
        # TODO: install zipfiles
        # subprocess.check_call(['sudo', 'apt', 'install', '/tmp/temp.deb'])
        # if the url ended with tar.gz

        # do below on success
        config['pkgs', key, 'prev_url'] = _url

