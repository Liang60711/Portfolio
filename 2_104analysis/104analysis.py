import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import datetime
import re
import jieba
from selenium import webdriver
from selenium.webdriver.support.ui import Select

# definition
def getSoup(url):
    resp=requests.get(url)
    resp.encoding='utf-8'
    if resp.status_code==200:
        soup=BeautifulSoup(resp.text,'lxml')
        return soup
    return None
	
def getWebdriver(url,bgmode=False,wait=10):
    if bgmode==True:
        options=webdriver.ChromeOptions()
        options.add_argument('--headless')
    try:
        driver=webdriver.Chrome(r'C:\Users\LIANG\Desktop\profilio_sourcecode\2_104analysis\chromedriver')
        driver.implicitly_wait(wait)
        driver.get(url)
    except:
        print('not found')
    return driver



final_data=[]

# 抓取最大頁數
starttime=time.time()
url='https://www.104.com.tw/jobs/main/'
driver=getWebdriver(url,bgmode=False)
driver.find_element_by_xpath('/html/body/article[1]/div/div/div[4]/div/input').send_keys('scala\n')
time.sleep(2)  # 不能省略

soup=BeautifulSoup(driver.page_source,'lxml')
max_page=int(re.findall('\s(\d)+\s\W',soup.find('select',class_="page-select js-paging-select gtm-paging-top").find_all('option')[-1].text)[0])



# 抓取每頁資料
select_bar=Select(driver.find_element_by_xpath('//*[@id="js-job-header"]/div[1]/label[1]/select'))
for page in range(1,max_page+1):
    select_bar.select_by_visible_text(f"第 {page} / {max_page} 頁")
    time.sleep(3)

    soup=BeautifulSoup(driver.page_source,'lxml')
    datas=soup.find(id="js-job-content").select('article')
    
    
    # 抓取每頁職缺資料
    temp=[]
    for data in datas:
        title=data.find('h2').find('a').text.strip()
        link='https:'+data.find('h2').find('a')['href']
        company=data.find('ul',class_="b-list-inline b-clearfix").find_all('li')[1].text.strip()
        industrial=data.find('ul',class_="b-list-inline b-clearfix").find_all('li')[2].text.strip()
        area=data.find('ul',class_="b-list-inline b-clearfix job-list-intro b-content").find_all('li')[0].text.strip()
        experience=data.find('ul',class_="b-list-inline b-clearfix job-list-intro b-content").find_all('li')[1].text.strip()
        education=data.find('ul',class_="b-list-inline b-clearfix job-list-intro b-content").find_all('li')[2].text.strip()
        pay=data.find('div',class_="job-list-tag b-content").find_all('span')[0].text.strip()

        # 尋找該職位Keyword
        driver2=getWebdriver(link)
        time.sleep(1)
        soup=BeautifulSoup(driver2.page_source,'lxml')
        content=driver2.find_element_by_xpath('//*[@id="app"]/div[2]/div/div[1]/div[1]/div[2]/div[1]/p').text.strip()
        condition=driver2.find_element_by_xpath('//*[@id="app"]/div[2]/div/div[1]/div[2]/div[3]/div/div[2]/p').text.strip()
        driver2.quit()
        
        keyword_list=[]
        if content+condition !=[]:
            keyword=re.sub(r'[0-9.,\r\n\t+]','',content+condition)
            keyword = jieba.cut(keyword, cut_all=True)
            for k in keyword:
                if k!=' 'and k!='':
                    keyword_list.append(k)


        temp.extend([title,link,company,industrial,area,experience,education,pay])
        temp.append(keyword_list)
        final_data.append(temp)

    endtime=time.time()
    print('第{}頁抓取完成 花費:{:.2f}秒'.format(page,endtime-starttime))
driver.quit()

# 存csv
df=pd.DataFrame(page_data,columns=['Title','Link','company','Industrial','Area','Experience','Education','Pay','Keyword'])
df.to_csv('scala.csv',encoding='utf-8-sig')
