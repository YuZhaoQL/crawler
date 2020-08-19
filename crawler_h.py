from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import os
import xlwt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time
import re
import math
import random

import traceback

match_pattern=re.compile('[\d]+')
split_pattern=re.compile('#')
title=['title','citenum']

mapdir = './/base//map.csv'
relation_dir='.//base//dis_relation.xlsx'
IdList=['A','B','C','D','E','F','G','H','I','J']


def download(name="", ins="",positionList=[],browser=None):

    auInfolist=[]
    browser.refresh()
    time.sleep(5)
    browser.find_element_by_id("indiceH").click()
    time.sleep(2)
    browser.find_element_by_id("nameTxt").send_keys(name)
    browser.find_element_by_xpath('//*[@id="searchAuthorExact"]/option[2]').click()
    time.sleep(2)

    browser.find_element_by_id('selectAll').click()
    time.sleep(5)
    checkbuttonlist=browser.find_elements_by_xpath('//*[@id="zcDls"]/div/dl/dd/ul/li')
    print(positionList)

    curpos1=-100
    for checkitem in positionList:
        print(checkitem)
        level1Chechindex=int(split_pattern.split(checkitem)[0])
        level2Chechindex = int(split_pattern.split(checkitem)[1])
        pos1=level1Chechindex-2
        pos2=level2Chechindex-1
        if pos1!=curpos1:
            curpos1=pos1
            checkbuttonlist[curpos1].find_element_by_xpath('a').click()
            time.sleep(1)
            idname="subDomainBox_"+IdList[curpos1]
            print(idname)
            level2buttonlist=browser.find_element_by_id(idname).find_elements_by_xpath('li')
            level2button=level2buttonlist[pos2]
            level2button.find_element_by_xpath('input').click()
        else:
            idname = "subDomainBox_" + IdList[curpos1]
            print(idname)
            level2buttonlist = browser.find_element_by_id(idname).find_elements_by_xpath('li')
            level2button = level2buttonlist[pos2]
            level2button.find_element_by_xpath('input').click()
        time.sleep(1)
    # time.sleep(100)
    # exit(11)
    browser.find_element_by_xpath('//*[@id="JCore"]').click()
    browser.find_element_by_id('analySubmitBtn').click()
    try:
        WebDriverWait(browser, 10).until(lambda x: x.find_element_by_class_name("noDataP"))
        noinfoPosition=browser.find_element_by_class_name('noDataP')
        print('无引用信息')
        return 0,[]
    except Exception as e:
        try:
            # print(traceback.format_exc())

            datapositionL=browser.find_element_by_class_name("datamod").find_elements_by_xpath('a')
            datapositionL[1].click()
            time.sleep(3)

            pagecheckStart=browser.find_element_by_class_name('pagebt')
            pagechecklist=pagecheckStart.find_elements_by_xpath('a')
            if len(pagechecklist)!=0:
                # 多页
                citepage_num=pagecheckStart.find_elements_by_xpath('span')[0].text
                total=int(match_pattern.search(citepage_num).group())
                pagenum=int(math.floor(total/20))+(1 if(total%20)>0 else 0)
                total=0
                for pageIndex in np.arange(0,pagenum):
                    if pageIndex==0:
                        tablepositon = browser.find_element_by_css_selector("div[class='toplistcont bdn']")
                        infolist = tablepositon.find_elements_by_xpath('table//tbody//tr')
                        for infoitem in infolist:
                            info=infoitem.find_elements_by_xpath('td')
                            tmplist=[]
                            title=info[1].text
                            cite_num=info[2].find_element_by_xpath('a').text
                            tmplist.append(title)
                            tmplist.append(cite_num)
                            auInfolist.append(tmplist)

                    else:
                        pagecheckStart = browser.find_element_by_class_name('pagebt')
                        pagechecklist = pagecheckStart.find_elements_by_xpath('a')
                        pagechecklist[-1].click()
                        time.sleep(3)
                        tablepositon = browser.find_element_by_css_selector("div[class='toplistcont bdn']")
                        infolist = tablepositon.find_elements_by_xpath('table//tbody//tr')
                        for infoitem in infolist:
                            info = infoitem.find_elements_by_xpath('td')
                            tmplist = []
                            title = info[1].text
                            cite_num = info[2].find_element_by_xpath('a').text
                            tmplist.append(title)
                            tmplist.append(cite_num)
                            auInfolist.append(tmplist)
                return len(auInfolist),auInfolist
            else:
                tablepositon=browser.find_element_by_css_selector("div[class='toplistcont bdn']")
                infolist=tablepositon.find_elements_by_xpath('table//tbody//tr')
                for infoitem in infolist:
                    info = infoitem.find_elements_by_xpath('td')
                    tmplist = []
                    title = info[1].text
                    cite_num = info[2].find_element_by_xpath('a').text
                    tmplist.append(title)
                    tmplist.append(cite_num)
                    auInfolist.append(tmplist)
                return len(auInfolist),auInfolist
        except:
            print('未取到相关元素')
            return -1,[]


def task(otherdis2List=[],resultDir='',authorlist_dir=''):
    map_dat = pd.read_csv(mapdir, encoding='utf_8')
    relation_data = pd.read_excel(relation_dir)
    print(relation_data.columns.values)


    author_dat=pd.read_csv(authorlist_dir,encoding='utf_8').drop_duplicates()
    # print(author_dat)
    # exit(11)

    namelist=author_dat.iloc[:,1:3].drop_duplicates().values.tolist()


    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get("http://ref.cnki.net/REF/AuthorAnalyzer/AuthorAnalysis")
    time.sleep(5)

    index_name=0
    while True:
        if index_name<0:
            index_name+=1
            continue


        if index_name==len(namelist):
            browser.quit()
            break


        if index_name %10 == 0 and index_name != 0:
            print('超时重新联网')
            browser.quit()
            time.sleep(60)
            browser = webdriver.Chrome()
            browser.maximize_window()
            browser.get("http://ref.cnki.net/REF/AuthorAnalyzer/AuthorAnalysis")
            time.sleep(5)

        authorname = namelist[index_name][0]
        dis2info= namelist[index_name][1]
        tmplist=re.split('#',dis2info)
        curdis2List=[]
        for item in tmplist:
            curdis2List.append(item)
        # print(curdis2List)
        # print(namelist[index_name])
        # exit(11)


        targetlist=[]
        for item in curdis2List:
            dis1name = relation_data[relation_data['discipline2'] == item].drop_duplicates().iloc[:, 2].values.tolist()[
                0]
            childdis2 = relation_data[relation_data['discipline1'] == dis1name].drop_duplicates().iloc[:,
                        0].values.tolist()
            for index in np.arange(0, len(childdis2)):
                if childdis2[index] in targetlist:
                    continue
                else:
                    targetlist.append(childdis2[index])

        for item in otherdis2list:
            targetlist.append(item)
        print(targetlist)

        positionList = []
        for dis2Iitem in targetlist:
            filterdat = map_dat[map_dat['dis2'] == dis2Iitem].iloc[0, [3, 4]].values.tolist()
            positionitem1 = filterdat[0]
            positionitem2 = filterdat[1]
            positionList.append(str(positionitem1) + "#" + str(positionitem2))

        print(positionList)
        # exit(11)

        print(str(index_name + 1) + ":" + authorname + " 开始")

        flag,infolist=download(authorname, ins="清华大学",positionList=positionList,browser=browser)
        print(flag)

        if flag==-1:
            print('断网重新联网')
            browser.quit()
            time.sleep(300)
            browser = webdriver.Chrome()
            browser.maximize_window()
            browser.get("http://ref.cnki.net/REF/AuthorAnalyzer/AuthorAnalysis")
            time.sleep(10)
            continue
        else:
            # print(flag)
            # print(infolist)
            if len(infolist)!=0:
                dat=pd.DataFrame(data=np.array(infolist),columns=title)
                filename=authorname+"_cited.xlsx"
                fullpath=os.path.join(resultDir,filename)
                dat.to_excel(fullpath)

            print(str(index_name + 1) + ":" + authorname + " 结束")
            index_name += 1
            sleeptime=random.randint(5,20)
            time.sleep(sleeptime)


resultDir='.\\part2HCdetail'
authorlist_dir='.//download//name_list_with_new_ins_newspublish.csv'
otherdis2list=[]




if os.path.exists(resultDir):
    pass
else:
    os.mkdir(resultDir)


task(otherdis2list,resultDir,authorlist_dir)

