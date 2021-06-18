#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    ：2021/4/18 23:58
@Author  ：维斯
@File    ：auto_video.py
@Version ：1.0
@Function：组件-刷视频
"""

import time

from selenium.webdriver.chrome.webdriver import WebDriver


def video_auto_start(driver_job: WebDriver, course_name):
    time.sleep(10)
    o_time = time.time()
    # step1 进入视频课件播放页面
    # 课程xpath：//*[@id="tblDataList"] （若有3个，则第三个为视频课件；若有2个，则第二个为视频课程）
    ele_list = driver_job.find_elements_by_xpath('//*[@id="tblDataList"]')
    if len(ele_list) == 3:
        video_ele = ele_list[2]
    elif len(ele_list) == 2:
        video_ele = ele_list[1]
    else:
        print(f'MYERROR：{course_name} 视频课件xpath获取错误，课程xpath：//*[@id="tblDataList"]，实际获取{len(ele_list)}数')
    # 获取视频课件数量
    video_list = video_ele.find_elements_by_tag_name('a')
    print(f'【{course_name}】课程共有{len(video_list)}个视频课件')
    video_text_list = []
    for i in video_list:
        # print(i.find_element_by_xpath('.//span').text)
        video_text_list.append(i.find_element_by_xpath('.//span').text)
    video_list[0].click()  # 点击第一个视频课件
    time.sleep(5)

    # step2 遍历所有课件 //*[@id="btnNext"]
    must_time = ''
    for i_video in range(len(video_list)):
        # step3 获取单个视频课件数据
        driver_job.switch_to.frame(1)  # 切换到页面右边的部分
        count = 0
        while True:
            if count > 61: break
            try:
                str_text = driver_job.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr') \
                    .find_element_by_xpath('.//td').text
                break
            except:
                print(f'{video_text_list[i_video]}->视频页面尚未加载完成，等待5秒...')
                time.sleep(5)
                count += 1
        while True:
            str_text = driver_job.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr') \
                .find_element_by_xpath('.//td').text
            # 删除字符串前面的空格
            while True:
                if str_text.startswith(' '):
                    str_text = str_text[1:]
                else:
                    break
            # print(str_text)
            if str_text.startswith('您正在'):
                # 2.1 最少学习时间 xpath：/html/body/table/tbody/tr[2]/td/table/tbody/tr 下面的td的文本
                try:
                    must_time = str_text.split('最少要求学习')[1].split('秒')[0]
                except:
                    pass
                # 2.2 已学习时间 00:20:26
                old_time = str_text.split('学习了')[1][:8]
                # print(old_time)
                old_time = old_time.split(':')
                old_time = str(int(old_time[0]) * 3600 + int(old_time[1]) * 60 + int(old_time[2]))
                need_time = int(old_time) - int(must_time)
                if need_time >= 0:
                    need_time = 0
                else:
                    need_time = -need_time
                if need_time == 0:  # 学习时长已完成 需切换PPT /html/body/div/header/div[2] 下的span
                    driver_job.switch_to.frame('w_sco')
                    driver_job.switch_to.frame(0)  # 1
                    driver_job.switch_to.frame(0)  # 2
                    try:
                        s = driver_job.find_element_by_xpath('/html/body/div/header/div[2]').find_elements_by_tag_name(
                            'span')
                    except:
                        time.sleep(10)
                        driver_job.switch_to.parent_frame()
                        driver_job.switch_to.parent_frame()
                        driver_job.switch_to.parent_frame()
                        continue
                    if len(s) > 1:
                        print(f'【{course_name} -> {video_text_list[i_video]}】当前视频课件，学习时长已完成，正在点击切换课件PPT...')
                        for i_s in s:
                            i_s.click()
                            # print(f'{i_s.find_element_by_xpath(".//..//..//h1").text}->{i_s.get_attribute("hd")} PPT已点击')
                            time.sleep(2)
                    driver_job.switch_to.parent_frame()
                    driver_job.switch_to.parent_frame()
                    driver_job.switch_to.parent_frame()
                    continue
                else:
                    wait_time = (int(need_time / 20) + 1) * 20  # 等待时间为20的倍数（因为网站是大约20秒更新一次）
                    print(
                        f'【{course_name} -> {video_text_list[i_video]}】当前视频课件，至少学习{must_time}秒，已经学习{old_time}秒，还需学习{str(need_time)}秒，等待{str(wait_time)}秒')
                    time.sleep(wait_time)
                    continue
            elif str_text.startswith('已经学习完毕'):
                # 进度
                all_count = len(video_list)
                now_count = i_video + 1
                jd = str(int((now_count / all_count) * 100)) + '%'
                # 耗时
                now_time = int(int(time.time()) - int(o_time))
                time_h = divmod(now_time, 3600)  # 时：time_h[0]
                time_m = divmod(time_h[1], 60)  # 分：time_m[0]
                time_s = time_m[1]  # 秒
                tep_times = int((now_time / now_count) * (all_count - now_count))
                tep_times_h = divmod(tep_times, 3600)
                tep_times_m = divmod(tep_times_h[1], 60)
                tep_times_s = tep_times_m[1]
                # 2.3 是否学习完成 “已经学习完毕！获取了10分/总分10分。总计学习时间为：00:07:56。”
                print(
                    f'{course_name} 总进度：{jd}({now_count}/{all_count} 已耗时{str(time_h[0]).zfill(2)}:{str(time_m[0]).zfill(2)}:{str(time_s).zfill(2)} 预计剩余{str(tep_times_h[0]).zfill(2)}:{str(tep_times_m[0]).zfill(2)}:{str(tep_times_s).zfill(2)})  当前视频课件已学习完成【{video_text_list[i_video]}】')
                break
        driver_job.switch_to.parent_frame()
        # 点击下一个视频课件
        driver_job.switch_to.frame(0)
        driver_job.find_element_by_xpath('//*[@id="btnNext"]').click()
        driver_job.switch_to.parent_frame()


"""
增加 已耗时、预计剩余时间    单门课程进度：41%(94/228) 当前视频课件已学习完成【数据库程序设计基础 -> 变量】

"""
