#!/usr/bin/env python3
import logging
import multiprocessing
import os
import random
import time
from glob import glob

from PIL import Image


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


def list_all_files(file_path):
    """列出文件，不包含文件夹，返回列表

    Arguments:
        file_path {str} -- 需要列出所有文件的路径

    Returns:
        list -- 返回包含所有文件的列表
    """
    return [f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]


def check_dir(input_path):
    """检查输入文件夹列表是否都存在，不存在则创建

    Arguments:
        input_path {list} -- 待检测文件夹列表
    """
    for i in input_path:
        if os.path.exists(i):
            logger.info('{0} folder already exists'.format(i))
        else:
            os.mkdir(i)


def rm_img(input_img):
    """对已有图片进行删除

    Arguments:
        input_img {str} -- 要删除的图片路径
    """
    if os.path.exists(input_img):
        os.remove(input_img)
        logger.info('{0} folder already deleted'.format(input_img))
    else:
        logger.info('no such file: {0}'.format(input_img))


def check_img(input_img):
    """对图片进行检测并根据实际情况进行转换

    Arguments:
        input_img {str} -- 待检测图片路径
    """
    logger.info('checking {0}'.format(input_img))
    image = Image.open(input_img)
    img_mode_len = len(image.split())
    new_img = input_img[:input_img.rindex('.')] + '.jpg'
    if img_mode_len == 1:
        image.convert('RGB').save(new_img)
        rm_img(input_img)
    if img_mode_len == 4:
        image.convert('RGB').save(new_img)
        rm_img(input_img)
        logger.info('{0} has been changed, new img is {1}'.format(
            input_img, new_img))
    logger.info('{0} has been checked'.format(input_img))


def compress_img(input_img, output_img, rate=80):
    """对图片进行压缩

    Arguments:
        input_img {str} -- 输入图片路径
        output_img {str} -- 输出图片路径

    Keyword Arguments:
        rate {int} -- 压缩率 (default: {80})
    """
    check_img(input_img)
    logger.info('compressing {0}'.format(input_img))
    image = Image.open(input_img)
    image.save(output_img, quality=rate)
    logger.info('{0} has been compressed'.format(input_img))


def resize_img(input_img, output_img):
    """更改图片尺寸，进行统一化处理

    Arguments:
        input_img {str} -- 输入图片路径
        output_img {str} -- 输出图片路径
    """
    check_img(input_img)
    logger.info('resizing {0}'.format(input_img))
    image = Image.open(input_img)
    img_size = min(image.size)
    region = image.resize((img_size, img_size), Image.ANTIALIAS)
    region.save(output_img)
    logger.info('{0} has been resized'.format(input_img))


def transpose_img(input_img, output_img, trans_type):
    """对图片进行旋转、镜像等操作

    Arguments:
        input_img {str} -- 输入图片路径
        output_img {str} -- 输出图片路径
        trans_type {int} -- 操作类型
    """
    check_img(input_img)
    logger.info('transposing {0}'.format(input_img))
    image = Image.open(input_img)
    image.transpose(trans_type).save(output_img)
    logger.info('{0} has been transposed'.format(input_img))


def get_test_and_train_list(input_path):
    file_list = list_all_files(input_path)
    random.shuffle(file_list)
    list_len = len(file_list)
    test_list = file_list[:list_len // 7]
    train_list = file_list[list_len // 7:]
    return test_list, train_list


def trans_imgs(img, output_type, input_path, output_path):
    """对图像进行一系列操作，增强数据集

    Arguments:
        input_path {str} -- 待处理的文件夹路径
        output_path {str} -- 处理后的图片保持路径
    """
    input_dir = input_path + img
    if output_type == 'test':
        output_dir = output_path + 'test/'
    elif output_type == 'train':
        output_dir = output_path + 'train/'
    check_dir([output_dir])
    img_size = os.path.getsize(input_dir)
    if img_size > 1024 * 1024 * 2:
        compress_img(input_dir, output_dir + img, rate=60)
    elif 1024 * 1024 < img_size < 1024 * 1024 * 2:
        compress_img(input_dir, output_dir + img, rate=80)
    resize_img(input_dir, output_dir + img)
    transpose_img(
        output_dir + img,
        output_dir + 'flr_' + img,
        trans_type=Image.FLIP_LEFT_RIGHT
    )
    transpose_img(
        output_dir + img,
        output_dir + 'ftb_' + img,
        trans_type=Image.FLIP_TOP_BOTTOM
    )
    transpose_img(
        output_dir + img,
        output_dir + 'r90_' + img,
        trans_type=Image.ROTATE_90
    )
    transpose_img(
        output_dir + img,
        output_dir + 'r180_' + img,
        trans_type=Image.ROTATE_180
    )
    transpose_img(
        output_dir + img,
        output_dir + 'r270_' + img,
        trans_type=Image.ROTATE_270
    )


if __name__ == '__main__':
    start = time.time()
    input_cataract_path = 'input/cataract/'
    output_cataract_path = 'output/cataract/'
    input_normal_path = 'input/normal/'
    output_normal_path = 'output/normal/'
    check_dir([
        output_cataract_path,
        output_normal_path
    ])
    cataract_test_file_list, cataract_train_file_list = get_test_and_train_list(
        input_cataract_path)
    normal_test_file_list, normal_train_file_list = get_test_and_train_list(
        input_normal_path)
    pool = multiprocessing.Pool(processes=3)
    for c_test in cataract_test_file_list:
        pool.apply_async(trans_imgs, args=(
            c_test, 'test', input_cataract_path, output_cataract_path))
    for c_train in cataract_train_file_list:
        pool.apply_async(trans_imgs, args=(c_train, 'train',
                                           input_cataract_path, output_cataract_path))
    for n_test in normal_test_file_list:
        pool.apply_async(trans_imgs, args=(
            n_test, 'test', input_normal_path, output_normal_path))
    for n_train in normal_train_file_list:
        pool.apply_async(trans_imgs, args=(
            n_train, 'train', input_normal_path, output_normal_path))
    pool.close()
    pool.join()
    end = time.time()
    logger.info('程序执行时间: {0}'.format(end - start))
