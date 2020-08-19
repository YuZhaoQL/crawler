import os
import numpy as np
import pandas as pd
import re
import time
import math

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains

from operator import itemgetter

import selenium
import traceback

matchpattern = re.compile('[\u4E00-\u9FA5]+[、]*[\u4E00-\u9FA5]*')
splitpattern = re.compile('#')
splitpattern_field = re.compile(';')
getnum_pattern = re.compile('[\d]*[,]*[\d]+')
date_from_to_type1 = ['2014', '2019']
date_from_to_type2 = ['2019', '2019']

# title=['name','ins_old','ins','dis2_used','dis2_list']

resultdir = './/part2'
baseurl = 'http://kns.cnki.net/kns/brief/result.aspx?dbprefix=CJFQ'
mapdir = './/base//map.csv'
relation_dir='.//base//dis_relation.xlsx'
# authorlist_dir = './/download//经济学_download_part1.xlsx'


# 存放用户信息

def saveDat(cur_Dat=None, filename=""):
    fulltargetname = os.path.join(resultdir, filename + ".xlsx")
    # print(fulltargetname)
    if os.path.isfile(fulltargetname):
        fulltargetname = os.path.join(resultdir, filename + ".csv")
        cur_Dat.to_csv(fulltargetname, encoding="utf_8_sig", mode='a', header=False)
    else:
        cur_Dat.to_excel(fulltargetname, encoding="utf_8_sig")


def find_info(name='',ins='', positionlist=[],datetype=-1,scope=-1, option=False):
    # 设置初始值
    # edited=False
    Au_info = []
    if datetype == 1:
        cur_date_from_to_type = date_from_to_type1
    elif datetype == 2:
        cur_date_from_to_type = date_from_to_type2
    else:
        return -100, []

    browser = webdriver.Chrome()
    browser.maximize_window()
    try:
        browser.get(baseurl)
        # print(position1)
        # 登入网页结束

        WebDriverWait(browser, 120).until(lambda x: x.find_element_by_id("XuekeNavi_Div"))

        # for index in np.arange(5,10):
        level1checked_list=[]

        btnList = browser.find_element_by_id('XuekeNavi_Div').find_elements_by_xpath(
                "div[@class='opt']//input[@class='btn']")
        btnList[0].click()

        checkList = browser.find_elements_by_class_name("navi_firstfloor")
        print(positionlist)
        # exit(11)
        for item in positionlist:
            indexLevel1=int(splitpattern.split(item)[0])
            indexLevel2=int(splitpattern.split(item)[1])

            if indexLevel1 not in level1checked_list:
                position1=indexLevel1
                position2=indexLevel2
                level1checked_list.append(indexLevel1)

                if position1 >= 2:
                    key = checkList[position1 - 2].get_attribute('value')
                    parent_key = key + 'first'
                    parent_button = browser.find_element_by_id(parent_key)
                    parent_button.click()
                    time.sleep(3)
                    child_key = key + 'child'
                    WebDriverWait(browser, 60).until(lambda x: x.find_element_by_id(child_key))

                    childlist = browser.find_element_by_id(child_key).find_elements_by_xpath('dd')
                    child_button = childlist[position2 - 1].find_element_by_xpath("span//input[@id='selectbox']")
                    child_button.click()
            else:
                position1 = indexLevel1
                position2 = indexLevel2
                if position1 >= 2:
                    key = checkList[position1 - 2].get_attribute('value')
                    # parent_key = key + 'first'
                    # parent_button = browser.find_element_by_id(parent_key)
                    # parent_button.click()
                    # time.sleep(3)
                    child_key = key + 'child'
                    childlist = browser.find_element_by_id(child_key).find_elements_by_xpath('dd')
                    child_button = childlist[position2 - 1].find_element_by_xpath("span//input[@id='selectbox']")
                    child_button.click()
        if scope==1:
                LevelRadio = browser.find_element_by_id('mediaBox3')
                LevelRadio.click()
        elif scope==2:
               LevelRadio = browser.find_element_by_id('mediaBox4')
               LevelRadio.click()


        au_input = browser.find_element_by_id("au_1_value1")
        au_input.send_keys(name)


        if option or  len(name)==2:
            au_input1 = browser.find_element_by_id("au_1_value2")
            au_input1.send_keys(ins)
            au_select = browser.find_element_by_id('au_1_special2')
            Select(au_select).select_by_index(0)


        time.sleep(1)
        date_from_input = browser.find_element_by_id("year_from")
        Select(date_from_input).select_by_value(cur_date_from_to_type[0])
        time.sleep(2)
        date_from_input = browser.find_element_by_id("year_to")
        Select(date_from_input).select_by_value(cur_date_from_to_type[1])

        searchbutton = browser.find_element_by_class_name('btnPlace2').find_element_by_xpath('input')
        searchbutton.click()
        try:
            WebDriverWait(browser, 60).until(lambda x: x.find_element_by_id("iframeResult"))
            iframe = browser.find_element_by_id('iframeResult')
            browser.switch_to.frame(iframe)

            # 切换到所搜结果部分结束

            WebDriverWait(browser, 60).until(lambda x: x.find_element_by_class_name("pageBar_min"))
            ResultBar = browser.find_element_by_class_name('pageBar_min').find_element_by_xpath(
                "div[@class='pagerTitleCell']")
            resultInfo = ResultBar.text
            num_str=getnum_pattern.search(resultInfo).group()
            if ','in num_str:
                browser.quit()
                return 100, []
            else:
                current_total = int(num_str)
                if current_total == 0:
                    browser.quit()
                    return 0, []
                elif current_total > 100:
                    browser.quit()
                    return 50, []
                else:
                    # print(resultInfo)
                    turn_page = browser.find_element_by_class_name("TitleLeftCell")
                    pagebutton = turn_page.find_elements_by_xpath("a")

                    content_positon = browser.find_element_by_class_name("GridTableContent")
                    content_list = content_positon.find_elements_by_xpath("tbody//tr")
                    # print(len(content_list))
                    first_time_flag = True
                    for content in content_list:
                        if first_time_flag:
                            first_time_flag = False
                            continue
                        info_list = content.find_elements_by_xpath("td")
                        tmplist = []
                        for info_index in np.arange(1, 5):
                            tmplist.append(info_list[info_index].text)
                        Au_info.append(tmplist)

                    click_num = math.floor(current_total / 20)
                    if not (current_total % 20):
                        click_num -= 1
                    # print(click_num)
                    # # print(current_total%20)
                    # # exit(11)
                    if click_num:
                        for page_index in np.arange(0, click_num):
                            turn_page = browser.find_element_by_class_name("TitleLeftCell")
                            pagebutton = turn_page.find_elements_by_xpath("a")
                            if page_index>0:
                                pagebutton[page_index+2].click()
                            else:
                                pagebutton[page_index].click()
                            time.sleep(5)
                            content_positon = browser.find_element_by_class_name("GridTableContent")
                            content_list = content_positon.find_elements_by_xpath("tbody//tr")

                            first_time_flag = True
                            for content in content_list:
                                if first_time_flag:
                                    first_time_flag = False
                                    continue
                                info_list = content.find_elements_by_xpath("td")
                                tmplist = []
                                for info_index in np.arange(1, 5):
                                    tmplist.append(info_list[info_index].text)
                                Au_info.append(tmplist)
                            time.sleep(2)
                    print(len(Au_info))
                    if len(Au_info) != current_total:
                        browser.quit()
                        return -1, Au_info
                    else:
                        browser.quit()
                        return 1, Au_info

        except Exception as e:
            print(traceback.format_exc())
            print('抓取失败')
            browser.quit()
            return -99, []
    except Exception as e:
        print(traceback.format_exc())
        print('联网失败')
        browser.quit()
        return -99, []


def main_function(authorlist_dir="", map_dat=None,
                  other_dis2_list=[],datetype=-1,scope=-1,opt=False):
    is_shuangzi = False

    map_dat = map_dat
    author_dat = pd.read_csv(authorlist_dir, encoding='utf_8').\
        drop_duplicates().values.tolist()
    # print(len(author_dat))
    relation_data = pd.read_excel(relation_dir)
    # print(relation_data.columns)
    # exit(11)



    search_index = 0
    while True:
        if search_index <76:
            # print(search_index)
            search_index += 1
            continue

        if search_index != 0 and search_index % 250 == 0:
            time.sleep(600)

        if search_index == len(author_dat):
            break
        else:
            targetlist=[]
            # print(author_dat[search_index])
            # exit(11)
            nameitem = author_dat[search_index][1]
            insitem = author_dat[search_index][4]
            dis2info = author_dat[search_index][2]
            dis2list = splitpattern.split(dis2info)
            targetlist=dis2list+other_dis2_list
            # print(targetlist)
            for item in dis2list:
                dis1name=relation_data[relation_data['discipline2']==item].drop_duplicates().iloc[:,2].values.tolist()[0]
                childdis2=relation_data[relation_data['discipline1']==dis1name].drop_duplicates().iloc[:,0].values.tolist()
                for index in np.arange(0,len(childdis2)):
                    if childdis2[index] in targetlist:
                        continue
                    else:
                        targetlist.append(childdis2[index])

            print(targetlist)
  
            positionList=[]
            for dis2Iitem in targetlist:
                filterdat = map_dat[map_dat['dis2'] == dis2Iitem].iloc[0, [3, 4]].values.tolist()
                positionitem1 = filterdat[0]
                positionitem2 = filterdat[1]
                positionList.append(str(positionitem1)+"#"+str(positionitem2))


            if is_shuangzi:
                opt= True

            print('开始搜索' + "No." + str(search_index + 1) + ':' + nameitem + '//' + dis2list[0])
            # print(nameitem)
            # print(dis2item)
            # print(insitem)
            check_flag, Cur_list = find_info(nameitem, insitem, positionList,datetype=datetype, scope=scope,option=opt)

            # 指令集 -99断网 0不做修改 1修改
            if check_flag == -99:
                time.sleep(100)
                is_shuangzi = False
                continue
            elif check_flag == 0:
                print(nameitem + '未找到相关成果')
                search_index += 1
                time.sleep(10)
                is_shuangzi = False
                continue
            elif check_flag == -1:
                print(nameitem + "爬取出错")
                Cur_DatFrame = pd.DataFrame(data=np.array(Cur_list), columns=["title", "namelist", "journal", "date"])

                file_name = nameitem + "_" + dis2list[0] + "_" + insitem + "err"
                saveDat(Cur_DatFrame, file_name)
                search_index += 1
                time.sleep(10)
                is_shuangzi = False
                continue
            elif check_flag == 50:
                print("双字名问题出现")
                time.sleep(10)
                is_shuangzi = True
                continue
            elif check_flag == 1:
                # print(Cur_list)
                Cur_DatFrame = pd.DataFrame(data=np.array(Cur_list), columns=["title", "namelist", "journal", "date"])

                file_name = nameitem + "_" + dis2list[0] + "_" + insitem
                saveDat(Cur_DatFrame, file_name)
                search_index += 1
                is_shuangzi = False
                time.sleep(20)
                continue


if os.path.exists(resultdir) == False:
        os.mkdir(resultdir)

def start(authorlist_dir='',other_dis2_list=[]):
    map_dat = pd.read_csv(mapdir, encoding='utf_8')
    # print(map_dat)
    opt= False
    datetype=1
    scope=2
    main_function(authorlist_dir, map_dat, other_dis2_list,datetype,scope,opt)

authorlist_dir = './/download//name_list_with_new_ins_newspublish.csv'
other_dis2_list=[]
start(authorlist_dir,other_dis2_list)
