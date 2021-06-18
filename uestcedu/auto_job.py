#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    ：2021/4/18 20:11
@Author  ：维斯
@File    ：auto_job.py
@Version ：1.0
@Function：组件_刷作业
"""

import random
import time

from selenium.webdriver.chrome.webdriver import WebDriver


def job_auto_start(driver_job: WebDriver, course_name):
    result_list = []

    # 判断是否有作业（作业提交1、作业提交2、作业提交3）
    def check_job():
        time.sleep(5)
        return True if '作业提交1' in driver_job.page_source else False

    if check_job():
        jobs = ['作业提交1']  # '作业提交1', '作业提交2', , '作业提交2', '作业提交3'
        print(f'校验成功，此课程含有作业(课程：{course_name})')
        for i in jobs:  # 循环操作3个作业
            driver_job.switch_to.window(driver_job.window_handles[1])  # 切换到第二个标签页
            # 刷新当前页面
            driver_job.refresh()
            driver_job.switch_to.frame('w_main')
            time.sleep(1)
            try:
                driver_job.find_element_by_xpath(f'//*[text()="{i}"]').click()
            except:
                time.sleep(5)
                driver_job.find_element_by_xpath(f'//*[text()="{i}"]').click()
            time.sleep(5)
            driver_job.switch_to.default_content()
            driver_job.switch_to.frame('w_main')
            driver_job.switch_to.frame('cboxIframe')
            driver_job.switch_to.frame('w_lms_content')
            driver_job.switch_to.frame('w_sco')
            # 进入考试
            buttons = driver_job.find_elements_by_tag_name('input')
            try:
                is_name = driver_job.find_element_by_xpath('//*[@id="btnExam"]').get_attribute('value')
            except:
                is_name = ''
            if '开始考试' == is_name or '继续考试' == is_name or '继续提交' == is_name:
                # 是第一次考试（无二次确认弹框）
                print(f'{course_name} -> {i}：是第一次考试')
                driver_job.switch_to.default_content()
                driver_job.switch_to.frame('w_main')
                driver_job.switch_to.frame('cboxIframe')
                driver_job.switch_to.frame(0)
                driver_job.switch_to.frame('w_sco')
                try:
                    driver_job.find_element_by_xpath('//input[contains(@value,"考试")]').click()
                except:
                    try:
                        driver_job.find_element_by_xpath('//input[contains(@value,"继续考试")]').click()
                    except:
                        element = driver_job.find_element_by_xpath('//*[@id="btnExam"]')
                        driver_job.execute_script("arguments[0].click();", element)
                        print('执行到这里了bbbbbbbbbbbbbbbbbbb')
            else:
                # 不是第一次考试（有二次确认弹框）
                print(f'{course_name} -> {i}：不是第一次考试')
                driver_job.find_element_by_xpath('//*[@id="btnExam"]').click()
                time.sleep(1)
                try:
                    driver_job.switch_to.alert.accept()
                except:
                    time.sleep(5)
                    driver_job.switch_to.alert.accept()
            time.sleep(5)
            driver_job.switch_to.frame(1)  # 切入“frame” 参数只能用序号（从上到下
            # 从0开始 是第几个frame 参数就填几）
            job_elements = driver_job.find_elements_by_xpath('//tr[contains(@id,"tr_tblDataList_")]')
            print(f'{course_name} -> {i}：共有{len(job_elements)}道题')
            for job_alone in driver_job.find_elements_by_xpath(
                    '//*[contains(@id,"tblItem_")]'):  # /tbody/tr/td[2]/table/tbody/tr[1]/td
                count = driver_job.find_elements_by_xpath(
                    '//*[contains(@id,"tblItem_")]').index(job_alone) + 1
                i_id = job_alone.get_attribute('id')
            # 查看答案
            title_answer_list = answer_look(driver_job, course_name, i)
            # 填写答案（判断是否是本门课程最后一个作业）
            if jobs.index(i) == len(jobs) - 1:
                result_list.append(answer_write(driver_job, course_name, title_answer_list, i, True, by_index=True,
                                                by_index_tile=True))
            else:
                result_list.append(
                    answer_write(driver_job, course_name, title_answer_list, i, by_index=True, by_index_tile=True))
    else:
        print(f'校验失败，此课程无作业(课程：{course_name})')
        # TODO：校验失败 此课程无作业 则继续输入课程 继续校验
    aa = '====================【考试结果】===================='
    print(f'\n{aa}')
    print(*result_list, sep='\n')
    print('=' * (len(aa) + 4))
    print('\n')
    return result_list


def answer_look(driver_job: WebDriver, course_name, job_name):
    """
    查看答案
    :param driver_job:
    :param course_name:
    :param job_name: 当前作业名称
    :return: [{'title':'','answer':['A','B']},{},...,{}]
    """
    # 点击交卷前 在新标签页中打开当前网址 并进入对应作业考试页面
    current_url = driver_job.current_url
    driver_job.execute_script(f'window.open("{current_url}")')
    # print(f'当前窗口数量：{len(driver_job.window_handles)}')
    new_win = driver_job.window_handles[2]  # 第3个win是新打开的标签页
    driver_job.switch_to.window(new_win)
    driver_job.switch_to.frame('w_main')
    time.sleep(1)
    try:
        driver_job.find_element_by_xpath(f'//span[text()="{job_name}"]').click()
    except:
        time.sleep(5)
        driver_job.find_element_by_xpath(f'//span[text()="{job_name}"]').click()
    time.sleep(5)
    driver_job.switch_to.frame('cboxIframe')
    driver_job.switch_to.frame('w_lms_content')
    driver_job.switch_to.frame('w_sco')
    try:
        driver_job.find_element_by_xpath(f'//input[contains(@value,"考试")]').click()
    except:
        time.sleep(5)
        element = driver_job.find_element_by_xpath('//*[@id="btnExam"]')
        driver_job.execute_script("arguments[0].click();", element)
        print('执行到这里了aaaaaaaaaaa')
    time.sleep(1)
    # step1 切换至第二个标签页 点击交卷
    old_win = driver_job.window_handles[1]  # 第2个win是需要交卷的标签页（用来查看答案）
    driver_job.switch_to.window(old_win)
    sec = random.randint(20, 30)
    print(f'已在考试页面，随机等待20-30秒后再交卷，当前等待时间：{sec}s')
    time.sleep(sec)  # 进入考试页面后 等待N秒再交卷
    driver_job.switch_to.frame('w_main')
    driver_job.switch_to.frame('cboxIframe')
    driver_job.switch_to.frame('w_lms_content')
    driver_job.switch_to.frame('w_sco')
    driver_job.switch_to.frame('w_right')
    driver_job.switch_to.parent_frame()
    driver_job.switch_to.frame('w_left')
    driver_job.find_element_by_xpath('//*[@id="btnSubmit"]').click()  # 交卷按钮
    # step2 2个二次确认
    try:
        driver_job.switch_to.alert.accept()
    except:
        time.sleep(5)
        driver_job.switch_to.alert.accept()
    time.sleep(1)
    try:
        driver_job.switch_to.alert.accept()
    except:
        time.sleep(5)
        driver_job.switch_to.alert.accept()
    time.sleep(5)
    driver_job.switch_to.parent_frame()

    # step3 点击查看考卷
    driver_job.find_element_by_xpath(
        '//*[@id="_block_content_exam_info"]/table[3]/tbody/tr[8]/td/input[2]').click()  # 查看考卷按钮
    time.sleep(3)
    # step4 题目与答案做保存
    title_answer_list = []
    job_answers = driver_job.find_elements_by_xpath('//*[contains(@id,"trScore_")]')
    for i in job_answers:
        title = str(i.find_element_by_xpath('.//td[2]/table[1]/tbody/tr[1]/td').text) \
            .replace('\u3000', ' ').replace('\ue004', '')
        true_answer = str(i.find_element_by_xpath('.//div[contains(text(),"[参考答案：")]').text) \
            .replace('\u3000', ' ').replace('\ue004', '')
        # 正确答案清洗（原：[参考答案：A]  分值：5 清洗后：A）
        true_answer_ = true_answer.split(']')[0]
        true_answer = list(true_answer_.split('：')[1])

        # 根：/td[2]/table[1]/tbody/tr[2]/td
        optional_answer_list = []
        # 单选题：/div[1]/table/tbody/tr[{j_index}]/td[3]/label
        # 多选题：/span/div/span/div/div/div/span/div/div[1]/table/tbody/tr[{j_index}]/td[3]/label
        # 判断下级元素（div单选、span多选）
        try:
            # if title.startswith('“谋事在人，成事在天"是反映'):
            #     print('来咯来咯')
            #     print('aaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            # 单选 //*[@id="trScore_448458111"]/td[2]/table[1]/tbody/tr[2]/td/div[1]/table/tbody/tr[4]/td[3]/label
            dan_answers = i.find_elements_by_xpath('.//td[2]/table[1]/tbody/tr[2]/td/div[1]/table/tbody/tr')
            if len(dan_answers) <= 1:
                # 特例 标题是：“谋事在人，成事在天"是反映（　　　）的历史观 xpath不一样
                dan_answers = i.find_elements_by_xpath(
                    './/td[2]/table[1]/tbody/tr[2]/td/span/div/div[1]/table/tbody/tr')
                if len(dan_answers) <= 1:
                    # 针对答案在一行的科目（如英语） # //td[2]/table[1]/tbody/tr[2]/td/div[1]/table/tbody/tr/td[3]/label 最后一个是3 表示第一个答案的文本
                    xpath_alone = './/td[2]/table[1]/tbody/tr[2]/td/div[1]/table/tbody/tr/td'
                    dan_answers = i.find_elements_by_xpath(xpath_alone)
                    if len(dan_answers) <= 1:
                        raise Exception
            # 单选题-答案不在一行
            if len(dan_answers) <= 4:
                for i_dan in dan_answers:  # 查找当前单选题目的所有答案列表
                    answer_j_text = str(i_dan.find_element_by_xpath(f'.//td[3]/label').text) \
                        .replace('\u3000', ' ').replace('\ue004', '')
                    optional_answer_list.append(answer_j_text)
            # 单选题-答案在一行
            else:
                for alone_an in range(int(len(dan_answers) / 3)):
                    answer_j_text = str(i.find_element_by_xpath(f'{xpath_alone}[{(alone_an + 1) * 3}]/label').text) \
                        .replace('\u3000', ' ').replace('\ue004', '')
                    optional_answer_list.append(answer_j_text)
        except:
            # TODO:多选--答案不在一行（代码还未编写）
            # 多选--答案在一行（多选题的答案 xpath路径有差异 目前就下面2个差异）
            # len(i.find_elements_by_xpath('.//td[2]/table[1]/tbody/tr[2]/td/span  /div/span/div/div/div/span/div /div[1]/table/tbody/tr'))
            # len(i.find_elements_by_xpath('.//td[2]/table[1]/tbody/tr[2]/td/span  /div/div/div                   /div[1]/table/tbody/tr'))
            chayi = [
                '/div/span/div/div/div/span/div',
                '/div/div/div'
            ]
            duo_answers = i.find_elements_by_xpath(
                f'.//td[2]/table[1]/tbody/tr[2]/td/span{chayi[0]}/div[1]/table/tbody/tr')
            if len(duo_answers) == 0:
                duo_answers = i.find_elements_by_xpath(
                    f'.//td[2]/table[1]/tbody/tr[2]/td/span{chayi[1]}/div[1]/table/tbody/tr')
            for i_duo in duo_answers:  # 查找当前多选题目的所有答案列表
                answer_j_text = str(i_duo.find_element_by_xpath(f'.//td[3]/label').text) \
                    .replace('\u3000', ' ').replace('\ue004', '')
                optional_answer_list.append(answer_j_text)
        if title == '':
            print('MYERROR:', f'{course_name} -> {job_name} -> 第{job_answers.index(i) + 1}题：未获取到题目')
        if true_answer == '':
            print('MYERROR:', f'{course_name} -> {job_name} -> 第{job_answers.index(i) + 1}题：未获取到正确答案')
        if len(optional_answer_list) == 0:
            print('MYERROR:', f'{course_name} -> {job_name} -> 第{job_answers.index(i) + 1}题：未获取到答案列表')
        title_answer_list.append(
            {
                'title': title,
                'true_answer': true_answer,
                'answer_list': optional_answer_list
            }
        )

    print(f'\n{"=" * 15}【题目数据】{course_name}->{job_name} {"=" * 15}')
    print(*title_answer_list, sep='\n')
    # TODO:还没有做保存
    # step5 返回题目与正确答案
    return title_answer_list


def answer_write(driver_job: WebDriver, course_name, title_answer_list, job_name, is_finish_close=False,
                 by_index=False, by_index_tile=False):
    """
    填写答案
    :param driver_job:
    :param course_name:
    :param title_answer_list:
    :param job_name: 作业名称（作业提交1、作业提交2、作业提交3）
    :param is_finish_close: 单门课程作业是否已昨晚
    :param by_index: 是否通过答案序号来选择答案
    :param by_index_tile：是否通过序号来查找题目
    :return: 返回考试分数
    """

    def answer_write_by_index():
        if by_index_tile:
            j_now = j
        else:
            if j['title'] == i_title_text:
                j_now = j
            else:
                operation_jobs.append(
                    f'{course_name} -> {job_name} -> 第{jobs.index(i) + 1}题：{j["title"]}')
        # 取出正确答案的序号
        true_an_list = j_now['true_answer']
        for true_an_list_i in true_an_list:
            true_element = driver_job.find_element_by_xpath(f'//*[@id="tr_tblDataList_{jobs.index(i)}"]')
            # 点击当前正确答案序号前面的单选or多选框
            el_tr = true_element.find_elements_by_xpath(
                f'.//input[@value="{true_an_list_i}" and (@type="radio" or @type="checkbox")]')
            if len(el_tr) == 1:
                try:
                    el_tr[0].click()
                    print(f'{course_name} -> {job_name} -> 第{jobs.index(i) + 1}题：已填写')
                except:
                    driver_job.execute_script("arguments[0].click();", el_tr[0])
                    print(f'{course_name} -> {job_name} -> 第{jobs.index(i) + 1}题：已填写')
                time.sleep(1)
            else:
                print(f'MYERROR：有多个元素，{el_tr}')

    # driver切换到第三个标签页（即新打开的标签页）
    time.sleep(5)
    # print(f'\n当前标签页数量：{len(driver_job.window_handles)}')
    new_win = driver_job.window_handles[2]
    driver_job.switch_to.window(new_win)
    time.sleep(1)
    driver_job.switch_to.frame('w_main')
    driver_job.switch_to.frame('cboxIframe')
    driver_job.switch_to.frame('w_lms_content')
    driver_job.switch_to.frame('w_sco')
    driver_job.switch_to.frame('w_right')
    # 进入当前iframe
    # 查看题目列表 //*[@id="tblItem_19385"]/tbody/tr/td[2]/table/tbody/tr[1]/td
    jobs = driver_job.find_elements_by_xpath('//*[contains(@id,"tr_tblDataList_")]')
    operation_jobs = []
    print('Look up by serial number') if by_index else print('Search through the answer text')

    input('>>>:')
    time.sleep(6)

    for i in jobs:  # 依次循环做每道题
        i_title_text = str(i.find_element_by_xpath('.//tbody/tr/td[2]/table/tbody/tr[1]/td').text) \
            .replace('\u3000', ' ').replace('\ue004', '')
        for j in title_answer_list:  # 遍历参考答案中的题目
            if by_index:
                j = title_answer_list[jobs.index(i)]
                answer_write_by_index()
                break
            else:
                if j['title'] == i_title_text:
                    # 未获取到答案 或者答案中有重复元素 则需手工填写
                    if len(j['answer_list']) == 0 or len(j['answer_list']) != len(set(j['answer_list'])):
                        operation_jobs.append(
                            f'{course_name} -> {job_name} -> 第{jobs.index(i) + 1}题：{j["true_answer"]}')
                        break
                    # 取出正确答案的文本
                    i_true_answer_text = []
                    an_an = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
                    for an in j['true_answer']:
                        if an in an_an:
                            i_true_answer_text.append(j['answer_list'][an_an.index(an)])
                    for i_a in i_true_answer_text:
                        # 找到正确答案的文本所在xpath（若精确查找不到 就模糊查找 若模糊也查不到 就从左往右一个字符一个字符的比较 直到最终找到一个为止）
                        try:
                            alone_answer = i.find_element_by_xpath(f'.//label[text()="{i_a}"]')  # 精确查找
                        except:
                            try:
                                alone_answer = i.find_elements_by_xpath(f'.//label[contains(text(),"{i_a}")]')[
                                    0]  # 模糊查找
                            except:
                                compare = ''
                                is_true = False
                                # [超级匹配1]就从左往右一个字符一个字符的比较 直到最终找到一个为止
                                for char_com in i_a:
                                    compare += char_com
                                    alone_answer_l = i.find_elements_by_xpath(
                                        f'.//label[contains(text(),\'{compare}\')]')
                                    if len(alone_answer_l) == 1:
                                        alone_answer = alone_answer_l[0]
                                        print(f'超级匹配1成功：\n数据库值：{i_a}\n目标值：{alone_answer.text}\n最小模糊值：{compare}')
                                        is_true = True
                                        break
                                # [超级匹配2]从中间切开然后依次往后匹配
                                if not is_true:
                                    i_b = i_a[int(len(i_a) / 2):]
                                    for char_com in i_b:
                                        compare += char_com
                                        alone_answer_l = i.find_elements_by_xpath(
                                            f'.//label[contains(text(),\'{compare}\')]')
                                        if len(alone_answer_l) == 1:
                                            alone_answer = alone_answer_l[0]
                                            print(f'超级匹配2成功：\n数据库值：{i_a}\n目标值：{alone_answer.text}\n最小模糊值：{compare}')
                                            is_true = True
                                            break
                                # [超级匹配3] 分3份 近匹配中间那一截 从左到右依次匹配
                                if not is_true:
                                    if len(i_a) > 3:
                                        c_index = int(len(i_a) / 3)
                                        i_c = i_a[c_index:-c_index]
                                        for char_com in i_c:
                                            compare += char_com
                                            alone_answer_l = i.find_elements_by_xpath(
                                                f'.//label[contains(text(),\'{compare}\')]')
                                            if len(alone_answer_l) == 1:
                                                alone_answer = alone_answer_l[0]
                                                print(f'超级匹配3成功：\n数据库值：{i_a}\n目标值：{alone_answer.text}\n最小模糊值：{compare}')
                                                is_true = True
                                                break
                                            if i_c.index(char_com) == len(i_c) - 1:
                                                print('超级匹配3失败')
                                    else:
                                        print('超级匹配3失败')
                        # 点击当前正确答案文本前面的单选or多选框
                        if len(alone_answer.find_elements_by_xpath('./../../td')) <= 4:
                            # 答案不在一行
                            alone_answer.find_element_by_xpath('./../../td[1]/input').click()  # 点击选择答案
                        else:
                            # 答案在一行
                            for_id = alone_answer.get_attribute('for')
                            alone_answer.find_element_by_xpath(f'./../../*/input[@id="{for_id}"]').click()  # 点击选择答案
                        time.sleep(0.5)
                    break
                else:
                    if j['title'][:-8] == i_title_text[:-8]:
                        print(f'\nMYERROR：{course_name} -> {job_name} -> 第{jobs.index(i)}题题目无法完全匹配')
                        print(f'当前试卷题目：{i_title_text}')
                        print(f'题库中的题目：{j["title"]}\n')
    if len(operation_jobs) != 0:
        print('\n\n' + '=' * 50)
        print('|' * 50)
        print('V' * 50)
        print('以下题目需手工填写 填写完成后输入 “已完成” 即继续执行自动化')
        print(*operation_jobs, sep='\n')
        while True:
            if input('若已手工填写，请输入“已完成” >>>：') == '已完成':
                break
        print('=' * 50 + '\n\n')
    # 点击交卷
    sec = random.randint(5, 10)
    print(f'答案填写完成，随机等待5-10秒后再交卷，当前等待时间：{sec}s')
    time.sleep(sec)
    driver_job.switch_to.parent_frame()
    driver_job.switch_to.frame('w_left')
    driver_job.find_element_by_xpath('//*[@id="btnSubmit"]').click()
    time.sleep(1)
    try:
        driver_job.switch_to.alert.accept()
    except:
        time.sleep(5)
        driver_job.switch_to.alert.accept()
    time.sleep(1)
    try:
        driver_job.switch_to.alert.accept()
    except:
        time.sleep(5)
        driver_job.switch_to.alert.accept()
    time.sleep(5)
    # 查看考试得分
    driver_job.switch_to.parent_frame()
    try:
        is_finish = str(driver_job.find_element_by_xpath(
            '//*[@id="_block_content_exam_info"]/table[3]/tbody/tr[7]/td[2]/font').text).split('(')[0]
        is_finish = f'考试分数[{course_name} -> {job_name}]：{is_finish}分'
    except:
        is_finish = f'考试分数[{course_name} -> {job_name}]：未获取到考试分数'
    driver_job.switch_to.default_content()
    driver_job.switch_to.frame('w_main')
    driver_job.find_element_by_xpath('//*[@id="cboxClose"]').click()
    print(is_finish)
    time.sleep(1)
    driver_job.close()
    if is_finish_close:
        # 关闭最后一个标签页
        new_win = driver_job.window_handles[1]
        driver_job.switch_to.window(new_win)
        driver_job.switch_to.default_content()
        driver_job.switch_to.frame('w_main')
        driver_job.find_element_by_xpath('//*[@id="cboxClose"]').click()
        time.sleep(1)
        driver_job.close()
        # 切换到第一个标签
        driver_job.switch_to.window(driver_job.window_handles[0])
    return is_finish
