
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
import requests
from bs4 import BeautifulSoup
import math
import csv
import re
from fake_useragent import UserAgent
import time
import os

baseurl='https://www.duxiu.com/'

result_pattern=re.compile('[\d]+')
resultdir='.//bookdetail'



def saveDat(cur_Dat=None, filename=""):

    fulltargetname = os.path.join(resultdir, filename + ".csv")
    if os.path.isfile(fulltargetname):
        cur_Dat.to_csv(fulltargetname, encoding="utf_8_sig", mode='a', header=False)
    else:
        cur_Dat.to_csv(fulltargetname, encoding="utf_8_sig")

# def getnum(author):
#     ua = UserAgent()
#     headers = {"Connection": "keep-alive","User-Agent": ua.random}
#     url = 'https://book.duxiu.com/search?Field=all&channel=search&sw={}&ecode=utf-8&edtype=&searchtype=&view=0'.format(author)
#     # headers = {'User-Agent': ua.random,"Connection": "false"}
#     r = requests.get(url,headers = headers,timeout=30)
#     soup = BeautifulSoup(r.text, 'lxml')
#     # count = soup.find('span',{'class':'leftF'}).text
#     count1 = soup.find_all(text = re.compile('用时'))
#     # allbooks = str(count1[0]).split("种")[0]
#     allbooks = int(str(count1[0]).split("种")[0])
#     pages = math.ceil(allbooks/10)
#     numlist = []
#     for i in range(pages):
#         url1 = 'https://book.duxiu.com/search?channel=search&gtag=&sw={}&ecode=utf-8&Field=all&Sort=&adminid=&btype=&seb=0&pid=0&year=&sectyear=&showc=0&fenleiID=&searchtype=&authid=0&exp=0&expertsw=&Pages={}'.format(author,i+1)
#         # headers = {'User-Agent': ua.random,"Connection": "false"}
#         r1 = requests.get(url1, headers=headers, timeout=30)
#         soup1 = BeautifulSoup(r1.text, 'lxml')
#         allhtml = soup1.find_all("div", {"class": "books"})
#         eachpagebooks = len(allhtml)
#         for j in range(eachpagebooks):
#             html = allhtml[j]
#             citetext = html.find_all(text=re.compile('总被引'))
#             # citetext = html.find('div',{"class":"cited rightF"}).text
#             try:
#                 num = re.findall(r"\d+\.?\d*", citetext[0])
#             # print(num)
#                 numlist.append(int(num[0]))
#             except:
#                 numlist.append(0)
#             # print(i,j)
#     print(len(numlist))
#     print(sum(numlist))

def get_bookInfo(name='',result_num=-1):
    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get(baseurl)
    try:
        WebDriverWait(browser, 60).until(lambda x: x.find_element_by_id("top_menu"))
        booklabel=browser.find_element_by_id('top_menu').find_elements_by_xpath('ul//li')[3]
        booklabel.find_element_by_xpath('a').click()
        time.sleep(1)

        checkbutton=browser.find_element_by_css_selector("div[class='zsearchb']")
        checkbutton.find_elements_by_xpath('input')[2].click()
        time.sleep(1)

        nameinput = browser.find_element_by_css_selector("input[id='sw']")
        nameinput.send_keys(name)
        nameinput.submit()
        time.sleep(5)
        try:
            WebDriverWait(browser, 60).until(lambda x: x.find_element_by_id("searchinfo"))
            resultinfo=browser.find_element_by_id('searchinfo').find_element_by_xpath('span').text
            print(resultinfo)
            resultNum=int(result_pattern.search(resultinfo).group())
            if resultNum==0:
                browser.quit()
                return 0,[]
            else:
                pageNum=int((resultNum/10)+(1 if resultNum%10 else 0))
                TurnPageTimes=2 if pageNum>3 else pageNum-1

                setOptionButton=browser.find_element_by_css_selector("div[class='mrpx rightF']").\
                    find_element_by_xpath('dl//dt')
                setOptionButton.click()
                time.sleep(1)
                optionlist=browser.find_element_by_css_selector("div[class='mrpx rightF']").\
                    find_elements_by_xpath('dl//dd//ul//li')
                optionlist[6].click()
                time.sleep(2)

                Finalist=[]
                turnpage_index=0

                while True:
                    if turnpage_index==0:

                        booklist=browser.find_elements_by_class_name('books')
                        for book in booklist:
                            tmplist=[]
                            anchorInfo=book.find_element_by_xpath('ul//li//dl')
                            title=anchorInfo.find_element_by_xpath('dt').text
                            tmplist.append(title)
                            otherinfo=anchorInfo.find_elements_by_xpath('dd')

                            tmpstr = ''
                            for bookitem in otherinfo:
                                tmpstr += bookitem.text + "#"
                            tmplist.append(tmpstr[:-1])
                            Finalist.append(tmplist)

                        turnpage_index += 1
                        continue
                    if turnpage_index>TurnPageTimes:
                        break
                    else:
                            anchor=browser.find_element_by_id("pageinfo").find_element_by_xpath('b')
                            pageButtonList=anchor.find_elements_by_xpath('..//a')
                            if turnpage_index==1:
                                pageButtonList[0].click()
                            else:
                                pageButtonList[turnpage_index].click()
                            time.sleep(5)

                            booklist = browser.find_elements_by_class_name('books')
                            for book in booklist:
                                tmplist=[]
                                anchorInfo = book.find_element_by_xpath('ul//li//dl')
                                title = anchorInfo.find_element_by_xpath('dt').text
                                tmplist.append(title)
                                otherinfo = anchorInfo.find_elements_by_xpath('dd')
                                # print(len(otherinfo))
                                tmpstr=''
                                for bookitem in otherinfo:
                                    tmpstr+=bookitem.text+"#"
                                tmplist.append(tmpstr[:-1])
                                Finalist.append(tmplist)

                            turnpage_index+=1
                #
                # print(len(Finalist))
                # print(Finalist)
                browser.quit()
                return resultNum,Finalist




        except Exception as e:
            browser.quit()
            print(e.args)
            return -1,[]

    except Exception as e:
        browser.quit()
        # print(e.message)
        print(e.args)
        return -1,[]


def main_function(authorlist_dir="",level=-1):

    author_dat = pd.read_excel(authorlist_dir, encoding='utf_8'). \
        drop_duplicates().values.tolist()

    search_index = 0
    while True:
        if search_index < level:
            search_index += 1
            continue

        if search_index != 0 and search_index % 50 == 0:
            time.sleep(180)

        if search_index == len(author_dat):
            break
        else:
            print(author_dat[search_index])
            # exit(11)
            nameitem = author_dat[search_index][0]
            insitem = author_dat[search_index][1]
            dis2info = author_dat[search_index][3]

            print('开始搜索' + "No." + str(search_index + 1) + ':' + nameitem + '//' + dis2info)

            bn, bl = get_bookInfo(nameitem)

            # 指令集 -99断网 0不做修改 1修改
            if bn == -1:
                time.sleep(120)
                continue
            elif bn == 0:
                print(nameitem + '未找到相关图书成果')
                search_index += 1
                time.sleep(10)
                continue
            else:
                file_name = nameitem + "_" + dis2info + "_" + insitem
                Finaldat = pd.DataFrame(data=np.array(bl), columns=['title', 'des'])
                saveDat(Finaldat, file_name)
                print('结束搜索' + "No." + str(search_index + 1) + ':' + nameitem + '//' + dis2info)
                search_index += 1
                time.sleep(10)
                continue


if os.path.exists(resultdir):
    pass
else:
    os.mkdir(resultdir)

level=-1
authorlist_dir='.//download//name_list_with_new_ins_newspublish.xlsx'
main_function(authorlist_dir)


