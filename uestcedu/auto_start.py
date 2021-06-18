#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    ：2021/4/18 23:11
@Author  ：维斯
@File    ：auto_start.py
@Version ：1.0
@Function：启动前置
    1、登录学生管理平台
    2、进入指定课程学习页面（含作业与视频的列表页面）
"""

import time

from selenium import webdriver

from uestcedu.auto_job import job_auto_start
from uestcedu.auto_video import video_auto_start

chrome_path = "E:\Code\VerificationCode\chromedriver.exe"
driver = webdriver.Chrome(chrome_path)


def close_driver():
    driver.close()


def login():
    """
    登录电子科技大学学生管理平台
    """
    url = "https://student.uestcedu.com/console/"
    driver.get(url)
    driver.find_element_by_xpath('/html/body/div/div/div/div/div/ul/li[2]').click()
    input("请扫描登录后按任意键进行下一步...")
    # 判断是否登录成功
    try:
        driver.find_element_by_xpath('//*[@id="left_menu_ul"]/li[1]/a').text
        print('登录成功')
        return driver
    except Exception as e:
        print('登录失败', e)
        return False
    return driver


def in_course(course_name, operation=0):
    """
    进入指定课程
    :param course_name: 课程名称
    :param operation: 0刷作业，1刷课
    :return:
    """
    # step1 进入”在线学习“页面
    driver.find_element_by_xpath('//*[@id="left_menu_ul"]/li[3]/a').click()  # ”在线学习“按钮

    def check_alert():
        try:
            driver.switch_to.alert.accept()
        except:
            print('未发现弹框（继续循环检测）！！！！！！！！！！！')
            time.sleep(1)
            return check_alert()

    check_alert()
    time.sleep(10)
    # step2 进入指定学科
    # 判断课程是否存在
    driver.switch_to.frame('f_M00370003')
    element_list = driver.find_elements_by_xpath('//tr[starts-with(@id,"tr_tblDataList_")]')
    print('课程数量：', len(element_list))

    if element_list is not None:
        def check_course_name(cm):
            course_name_xpath = '//*[@id="tr_tblDataList_{}"]/td[2]'  # 课程名称
            start_learn = '//*[@id="tr_tblDataList_{}"]/td[8]/a[1]'  # 开始学习：//tr[2]/td[8]/a[1]
            is_have = False
            for i in element_list:
                try:
                    now_course_name = i.find_element_by_xpath(course_name_xpath.format(element_list.index(i))).text
                    try:
                        now_start_learn = i.find_element_by_xpath(start_learn.format(element_list.index(i))).text
                    except:
                        pass
                except Exception as e:
                    print(f'报错了（{element_list.index(i)}）：', e)
                if cm == now_course_name and now_start_learn == '开始学习':
                    print(f'课程查找成功，且可学习（课程：{cm}）')
                    driver.switch_to.parent_frame()
                    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="f_M00370003"]'))
                    i.find_element_by_xpath(start_learn.format(element_list.index(i))).click()  # 点击开始学习
                    time.sleep(5)
                    # TODO：网站不安全的警示
                    handles = driver.window_handles
                    driver.switch_to.window(handles[1])
                    driver.find_element_by_xpath('//*[@id="proceed-button"]').click()  # 点击“表单不安全”标签页中的“仍然发送”按钮
                    count = 0
                    while True:
                        if count > 60: break
                        try:
                            driver.switch_to.frame(
                                driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/iframe'))
                            break
                        except:
                            time.sleep(5)
                            count += 1
                            continue
                    # 调用其他组件（作业、刷课）
                    if operation == 0:
                        return job_auto_start(driver, cm)  # 刷作业
                    elif operation == 1:
                        return video_auto_start(driver, cm)  # 刷课
                else:
                    driver.switch_to.parent_frame()
                    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="f_M00370003"]'))
            if not is_have:
                print(f'输入的课程名称不存在，或者当前课程不可学习（{cm}）')
                return check_course_name(input('请重新输入课程名称 >>>：'))

        return check_course_name(course_name)


def start_job():
    """
    作业
    """
    login()
    print('单门课程预计耗时 6min 左右')
    re_l = []
    old_time = time.time()
    tep = ''
    while True:
        if tep != 'error':
            input_text = input('请输入课程名称（多个课程用“,”隔开） >>>：')
            input_text_list = str(input_text).split(',')
            for i in input_text_list:
                result_text = in_course(i)
                if type(result_text).__name__ == 'list':
                    re_l += result_text
        in_text = input('是否继续其他课程的考试（Y/N）>>>：')
        if in_text == 'N':
            break
        elif in_text == 'Y':
            tep = ''
            continue
        else:
            tep = 'error'
    time_tup = divmod(int(time.time() - old_time), 60)

    aa = '====================【所有课程考试结果】===================='
    print(f'\n{aa}')
    print(*re_l, sep='\n')
    print('=' * (len(aa) + 6))
    print('\n')

    print(f'实际耗时：{time_tup[0]}min {time_tup[1]}s')
    input('点击任意键 关闭driver >>>：')
    close_driver()


def start_course():
    """
    视频课件
    """
    login()
    # print('单门课程预计耗时 6min 左右')
    re_l = []
    old_time = time.time()
    tep = ''
    while True:
        if tep != 'error':
            input_text = input('请输入课程名称（多个课程用“,”隔开） >>>：')
            input_text_list = str(input_text).split(',')
            for i in input_text_list:
                result_text = in_course(i, 1)
                if type(result_text).__name__ == 'list':
                    re_l += result_text
        in_text = input('是否继续刷其他课程的视频课件（Y/N）>>>：')
        if in_text == 'N':
            break
        elif in_text == 'Y':
            tep = ''
            continue
        else:
            tep = 'error'
    time_tup = divmod(int(time.time() - old_time), 60)

    print(f'实际耗时：{time_tup[0]}min {time_tup[1]}s')
    input('点击任意键 关闭driver >>>：')
    close_driver()


class Params:
    P_JOB = 'JOB'
    P_COURSE = 'COURSE'


def start(type):
    if type == Params.P_JOB:
        start_job()
    elif type == Params.P_COURSE:
        start_course()
    else:
        print(f'类型值错误（预期：{Params.P_JOB}or{Params.P_COURSE}，实际：{type}）')
