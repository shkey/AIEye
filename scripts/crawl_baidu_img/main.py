#!/usr/bin/env python3
import json
import logging
import multiprocessing
import os

import requests

BAIDU_IMG_URL = 'https://image.baidu.com/'
PARAMS = 'search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&cl=2&lm=-1&ie=utf-8&oe=utf-8&word={0}&st=-1&face=0&istype=2&nc=1&pn={1}&rn=30'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
}


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('output.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


def save_img(url, file_name, path):
    if os.path.exists(path):
        logger.info('folder already exists')
    else:
        os.mkdir(path)
    req = requests.get(url, headers=HEADERS)
    with open('/'.join([path, file_name]), 'wb+') as f:
        f.write(req.content)


def crawl_imgs(word, pn, path):
    request_url = BAIDU_IMG_URL + PARAMS
    r = requests.get(request_url.format(word, pn), headers=HEADERS)
    logger.info('now is saving pn={0}'.format(pn))
    img_json = json.loads(r.text.replace("\\'s", '_s'))
    for i in range(len(img_json['data']) - 1):
        url = img_json['data'][i]['middleURL']
        file_name = str(pn) + str(i) + '.jpg'
        logger.info('now is saving file={0}'.format(file_name))
        save_img(url, file_name, path)


if __name__ == '__main__':
    cataract_pn = 1000
    cataract_word = '白内障眼睛'
    cataract_path = 'cataract'
    for i in range(0, cataract_pn, 30):
        p = multiprocessing.Process(
            target=crawl_imgs, args=(cataract_word, i, cataract_path))
        p.start()
    normal_pn = 1000
    normal_word = '人眼睛'
    normal_path = 'normal'
    for i in range(0, normal_pn, 30):
        p = multiprocessing.Process(
            target=crawl_imgs, args=(normal_word, i, normal_path))
        p.start()
    slitlamp_pn = 1000
    slitlamp_word = '裂隙灯 眼睛'
    slitlamp_path = 'slitlamp'
    for i in range(0, slitlamp_pn, 30):
        p = multiprocessing.Process(
            target=crawl_imgs, args=(slitlamp_word, i, slitlamp_path))
        p.start()
    eye_pn = 1000
    eye_word = '眼睛特写'
    eye_path = 'eye'
    for i in range(0, eye_pn, 30):
        p = multiprocessing.Process(
            target=crawl_imgs, args=(eye_word, i, eye_path))
        p.start()
