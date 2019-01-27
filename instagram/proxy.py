import zipfile, uuid, re
from instagram.settings.settings import *
import json


def build_chrome_ext(proxy):
    """
    creates a chrome extension for proxy authentication
    :param proxy: proxies object containing proxy settings:  ip, port, username and password
    :return: chrome extension path
    """
    # get proxy settings
    try:
        ip = proxy.proxies['address']
        port = proxy.proxies['port']
        username = proxy.proxies['username']
        password = proxy.proxies['password']
    except:
        return

    # create filepath to store the extension if not already existing
    path = os.path.join(cwd, 'instagram', 'proxy')
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    # create zip
    chrome_extension = str(uuid.uuid4()) + '.zip'
    zip = zipfile.ZipFile(path + '\\' + chrome_extension, mode='x')

    # add manifest
    manifest = json.dumps({
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version": "22.0.0"
    })
    zip.writestr('manifest.json', manifest)

    background = r'var config={mode:"fixed_servers",rules:{singleProxy:{scheme:"http",host:"%proxy_host",port:parseInt(%proxy_port),},bypassList:["foobar.com"]}};chrome.proxy.settings.set({value:config,scope:"regular"},function(){});function callbackFn(details){return{authCredentials:{username:"%username",password:"%password"}};}chrome.webRequest.onAuthRequired.addListener(callbackFn,{urls:["<all_urls>"]}'+",['blocking']);"

    # update background
    background = re.sub(r'%proxy_host', ip, background)
    background = re.sub(r'%proxy_port', port, background)
    background = re.sub(r'%username', username, background)
    background = re.sub(r'%password', password, background)

    # add background
    zip.writestr('background.js', background)

    return path + '\\' + chrome_extension
