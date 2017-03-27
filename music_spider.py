# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import requests
from bs4 import BeautifulSoup
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
import json
import os
import base64
from Crypto.Cipher import AES
from pprint import pprint


HOST = "http://music.163.com"
PAGE_FMT = urljoin(HOST, '{href}')
COMMENT_FMT = urljoin(HOST,'weapi/v1/resource/comments/R_SO_4_{song_id}/?csrf_token=')
LYRIC_FMT = urljoin(HOST,'api/song/lyric?os=pc&id={song_id}&lv=-1&kv=-1&tv=-1')

def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(text.encode('hex'), 16)**int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

headers = {
    'Referer': 'http://music.163.com/',
    'Host': 'music.163.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.3.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Cookie': 'appver=1.5.0.75771;',
}

text = {
    'username': '邮箱',
    'password': '密码',
    'rememberLogin': 'true'
}
modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'
text = json.dumps(text)
secKey = createSecretKey(16)
encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
encSecKey = rsaEncrypt(secKey, pubKey, modulus)
data = {
    'params': encText,
    'encSecKey': encSecKey
}

play_url = 'http://music.163.com/playlist?id=628879062'

s = requests.session()
s = BeautifulSoup(s.get(play_url, headers=headers).content,"lxml")
main = s.find('ul', {'class': 'f-hide'})

song_names = set()
page_links = set()

for music in main.find_all('a'):
    song_name = music.text
    href = music['href']
    song_id = str(href).split("id=")[1]
    page_link = PAGE_FMT.format(href = href)
    song_names.add(song_name)
    page_links.add(page_link)
    s = requests.session()
    s = BeautifulSoup(s.get(page_link, headers=headers).content, "lxml")
    title = s.find('title').text
    song = str(title).split("-")[0]
    singer = str(title).split("-")[1]
    comment_url = COMMENT_FMT.format(song_id=song_id)
    lyric_url = LYRIC_FMT.format(song_id=song_id)
    req = requests.post(comment_url, headers=headers, data=data)

    req_lyric = requests.post(lyric_url, headers=headers, data=data)

    print ('{} - {} - {} - {}'.format(song_id,song, singer ,page_link))
    print req_lyric.json()['lrc']['lyric'].encode('utf-8')
    for content in req.json()['hotComments']:
        print content['user']['nickname'].encode('utf-8') +":  " + content['content'].encode('utf-8')
    print "********************************************************************************"


# print song_names
# print page_links

# for page_link in page_links:
#     s = requests.session()
#     s = BeautifulSoup(s.get(page_link, headers=headers).content, "lxml")
#     title = s.find('title').text
#     song = str(title).split("-")[0]
#     singer = str(title).split("-")[1]
#     print ('{} : {}'.format(song, singer))
