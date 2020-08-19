import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains

import selenium
import time
import re
import os
import uuid

baseurl='http://ipub.exuezhe.com/search.html?adv=1'
# basedir='.\dat\\result\\finalResult_1'
resultDir='.\\part2rd'

pattern = re.compile('[\u4E00-\u9FA5]+、*[\u4E00-\u9FA5]+')
split_pattern = re.compile('#')

title=['scholarName','institutionInfo','dis2','selectedPaperNum']

def getSelectPapers(scholarName='王宁',institutionName='清华大学',browser=None,option1=False,option2=True,cur_dis_index=[]):

    browser.refresh()
    #
    # browser = webdriver.Chrome()
    # browser.maximize_window()
    # browser.get(baseurl)
    time.sleep(10)

    WebDriverWait(browser,60).until(lambda x: x.find_element_by_class_name("classify_tit"))
    classifier=browser.find_element_by_class_name("classify_tit").find_elements_by_xpath('span//img')[1]
    classifier.click()
    time.sleep(2)

    nameAnchor=browser.find_element_by_id('li1').find_elements_by_xpath('label')
    nameseter=nameAnchor[0]
    Select(nameseter.find_element_by_xpath('select')).select_by_index(2)
    nameinput=nameAnchor[1]
    nameinput.find_element_by_xpath('input').send_keys(scholarName)
    nameoption=nameAnchor[2]
    Select(nameoption.find_element_by_xpath('select')).select_by_index(1)
    time.sleep(1)

    if len(scholarName)>2:
        option1=False

    if option1:
        institutionAnchor=browser.find_element_by_id('li2').find_elements_by_xpath('label')
        institutionseter=institutionAnchor[1]
        Select(institutionseter.find_element_by_id('sltSch2')).select_by_index(19)
        institutionoption=institutionAnchor[3]
        Select(institutionoption.find_element_by_xpath('select')).select_by_index(0)
        institutioninput = institutionAnchor[2]
        institutioninput.find_element_by_xpath('input').send_keys(institutionName)

    if option2:
        for dis_index in np.arange(1,10):
            if dis_index in cur_dis_index:
                id_info="treeDemo"+"_"+str(dis_index)+"_check"
                checkbox=browser.find_element_by_id(id_info)
                checkbox.click()

    # print('hahahahaha')
    # browser.find_element_by_class_name('main_right') .find_element_by_xpath('div//span//input').click()
    submiter=browser.find_element_by_css_selector("[src='images/search1_07.png']")
    ActionChains(browser).move_to_element(submiter).perform()
    browser.find_element_by_css_selector("[src='images/search1_07.png']").click()
    time.sleep(5)
    # js='document.getElementById("btn-search").firstElementChild.click();'
    # browser.execute_script(js)
    WebDriverWait(browser, 60).until(lambda x: x.find_element_by_id("page_list"))

    pagebutton_list=browser.find_element_by_id('page_list').find_elements_by_xpath("a")
    if len(pagebutton_list)>0:
        pagenum=int(pagebutton_list[-3].text)
        pagebutton_list[-3].click()
        time.sleep(10)
        content_list = browser.find_element_by_class_name('con_list').find_elements_by_xpath("ul//li")
        total=(pagenum-1)*20+len(content_list)
        return total
    else:

        content_list=browser.find_element_by_class_name('con_list').find_elements_by_xpath("ul//li")
        if len(content_list)==0:
            return 0
        else:
            return len(content_list)

def workerForRenDaFuYin(dis_index=[]):
    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get(baseurl)
    Finallist=[]
    for index in range(len(author_dat)):
        Finallist.clear()
        flag=int(author_dat[index][5])
        print(flag)
        if flag==-3:
            continue
        dis2_info = author_dat[index][2]
        dis2=split_pattern.split(dis2_info)[0]
        name = author_dat[index][1]
        ins=author_dat[index][3]

        print(name+"in"+ins+":开始检索")
        # exit(11)
        # continue
    #     continue
    #
    # fileList = os.listdir(basedir)
    # disciplineDat=[]
    # total=0
    #
    # for fileItem in fileList:
    #
    #     if pattern.search(fileItem)==None:
    #         continue
    #
    #
    #     disciplineDat.clear()
    #
    #     total=total+1
    #     disciplineName = pattern.search(fileItem).group()
    #     print(str(total)+'  '+disciplineName+'  '+' 开始' )
    #     # print(disciplineName)
    #     fullFileDir = basedir + '\\' + fileItem
    #     currentAuthorList = pd.read_csv(fullFileDir, encoding='utf-8', engine='python',header=None,names=['id','discipline','scholar','institutionSet','institutionNum','politicalLabel'])
    #     # print(fileItem)
    #     # print(currentAuthorList)
    #     searchInfo=currentAuthorList.loc[:,['scholar','institutionSet','institutionNum']].values.tolist()
    #     # print(searchInfo)
    #
    #     for scholarItem in searchInfo:
    #         time.sleep(5)
    #         if scholarItem[2]==1:
    #     scholarName=scholarItem[0]
    #     institutionName=scholarItem[1]
    #     selectedNum = 0
        if len(name)==2:
            option1=True
        else:
            option1=False
        option2=True
        selectedNum=getSelectPapers(name,ins,browser,option1,option2,dis_index)
        # print("结果："+result_info)
        if selectedNum==0:
            print("无引用")
            continue
        else:
            print("引用:"+str(selectedNum))
            # continue
            # # selectedNum=int(result_info)
            tmpSearchResult=[]
            # tmpSearchResult.append(uuid.uuid4())
            tmpSearchResult.append(name)
            tmpSearchResult.append(ins)
            tmpSearchResult.append(dis2)
            tmpSearchResult.append(selectedNum)
            Finallist.append(tmpSearchResult)
            finalDat=pd.DataFrame(data=np.array(Finallist),columns=title)
            # print(finalDat)
            fullpath=os.path.join(resultDir,name+'_RenDaFuYin_statics.xlsx')
            finalDat.to_excel(fullpath,encoding="utf_8_sig")
        time.sleep(10)

    browser.quit()


def RenDaFuYinTask(dis_index=[]):
    if os.path.exists(resultDir) == False:
        os.mkdir(resultDir)
    workerForRenDaFuYin(dis_index)




authorlist_dir='.//download//name_list_with_new_ins_newspublish.csv'
author_dat=pd.read_csv(authorlist_dir,encoding='utf_8').drop_duplicates().values.tolist()
dis_index=[8]
RenDaFuYinTask(dis_index)