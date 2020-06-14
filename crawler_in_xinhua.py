# -*- coding: utf-8 -*-
"""
aim: 获取新华文摘

@author: zy
"""
import requests
from bs4 import BeautifulSoup
import math
import csv
import re
import time
import numpy as np
import pandas as pd
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import os
import traceback


title=  ['学者', '书名', '作者', '所属期刊', '栏目', '原发期刊']
split_pattern=re.compile('#')
basedir=".//part2xh"

def saveDat(cur_Dat=None,filename=""):
    fulltargetname = os.path.join(basedir, filename+".xlsx")
    # print(fulltargetname)
    if os.path.isfile(fulltargetname):
        fulltargetname = os.path.join(basedir, filename+".csv")
        cur_Dat.to_csv(fulltargetname, encoding="utf_8_sig", mode='a', header=False)
    else:
        cur_Dat.to_excel(fulltargetname, encoding="utf_8_sig")


def task():
    for index in range(len(author_dat)):
        Finallist=[]
        subject_info = author_dat[index][2]
        subject=split_pattern.split(subject_info)[0]
        author_name = author_dat[index][0]
        ins_info=author_dat[index][1]
        print(author_name+":开始检索")

        driver = webdriver.Chrome()
        driver.maximize_window()
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get('http://www.xinhuawz.com/page/BuySearchContent.aspx?type=1&cata=&txt=&adsql=%20\
        (%20(author%20%3D%27%3F{}%27))'.format(author_name))
        time.sleep(10)
        try:
            t = driver.find_element_by_xpath("//ul[@style='overflow: hidden;color:#999;']").text
                # print(t,type(t))
            total_count = int(t[8:-1])
            count_per_page = 6
            page_count = math.ceil(total_count / count_per_page)
            # print(total_count,page_count)
            now_num = driver.find_elements_by_tag_name('li')
                # print(now_num)
                # print(int(len(now_num)))
            # book_name_list = []
            for j in range(1, int(len(now_num)) + 1):
                driver.find_elements_by_css_selector('.info_list > li:nth-child({})'.format(j))
                paper_title = driver.find_element_by_css_selector('.info_list > li:nth-child({}) > div:nth-child(1) > a:nth-child(1)'.format(j)).text
                # book_name_list.append(book_name)
                # print(book_name)
                # exit(11)
                author = driver.find_element_by_tag_name('font').text
                strr = driver.find_element_by_css_selector('.info_list > li:nth-child({}) > div:nth-child(2) > div:nth-child(1)'.format(j)).text
                # print(author)
                # print(strr)
                # exit(11)
                a = strr.index('作者')
                b = strr.index('所属')
                c = strr.index('栏目')
                d = strr.index('原发')
                author = strr[a + 3:b]
                joural = strr[b + 5:c]
                lanmu = strr[c + 3:d]
                yuan_joural = strr[d + 5:]
                    # print(author[:int(len(author_name))])
                # if author[:int(len(author_name))] in author_name:
                tmplist=[]
                tmplist.append(author_name)
                tmplist.append(paper_title)
                tmplist.append(author)
                tmplist.append(joural)
                tmplist.append(lanmu)
                tmplist.append(yuan_joural)
                Finallist.append(tmplist)
            try:
                nowpage = 2
                while nowpage <= page_count:
                    driver.find_element_by_link_text("后一页").click()
                    time.sleep(5)
                    now_num = driver.find_elements_by_tag_name('li')
                        # print(now_num)
                        # print(int(len(now_num)))
                    for k in range(1, int(len(now_num)) + 1):
                        driver.find_elements_by_css_selector('.info_list > li:nth-child({})'.format(k))
                        paper_title = driver.find_element_by_css_selector('.info_list > li:nth-child({}) > div:nth-child(1) > a:nth-child(1)'.format(k)).text
                        # book_name_list.append(book_name)
                        strr = driver.find_element_by_css_selector('.info_list > li:nth-child({}) > div:nth-child(2) > div:nth-child(1)'.format(k)).text
                        a = strr.index('作者')
                        b = strr.index('所属')
                        c = strr.index('栏目')
                        d = strr.index('原发')
                        author = strr[a + 3:b]
                        joural = strr[b + 5:c]
                        lanmu = strr[c + 3:d]
                        yuan_joural = strr[d + 5:]
                            # print(author[:int(len(author_name))])
                        # if author[:int(len(author_name))] in author_name:
                        tmplist = []
                        tmplist.append(author_name)
                        tmplist.append(paper_title)
                        tmplist.append(author)
                        tmplist.append(joural)
                        tmplist.append(lanmu)
                        tmplist.append(yuan_joural)
                        Finallist.append(tmplist)
                    nowpage = nowpage + 1
            except:
                pass
            driver.quit()
            print(Finallist)
            Cur_DatFrame = pd.DataFrame(data=np.array(Finallist), columns=title)

            file_name = subject + "_" + author_name + "_" + ins_info
            saveDat(Cur_DatFrame, file_name)
        except Exception as e:
            print(traceback.format_exc())
            print('{}学者没有内容'.format(author_name))
            driver.quit()
        print('第{}个人{}完成'.format(index, author_name))
        time.sleep(3)

authorlist_dir='.//download//管理学_download_part2.xlsx'
author_dat=pd.read_excel(authorlist_dir,encoding='utf_8').drop_duplicates().values.tolist()
task()





