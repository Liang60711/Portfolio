# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 12:28:42 2020

@author: LIANG
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import re
from matplotlib.font_manager import FontProperties
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False

# 使用requests, BeautifulSoup抓取網頁
def getSoup(url):
    resp=requests.get(url)
    resp.encoding='utf-8-sig'
    if resp.status_code==200:
        soup=BeautifulSoup(resp.text,'lxml')
        return soup
    return None

# 抓取中獎清冊list
def getLinkList(url):
    soup=getSoup(url)
    trs=soup.find(id="tablet01").find('tbody').find_all('tr')
    
    link_list=[]
    for tr in trs:
        if '中獎清冊' in tr.find('a').text:
            #print(tr.find('a').text)
            link_list.append('https://www.etax.nat.gov.tw/'+tr.find('a')['href'])
    return link_list

# 抓1000萬元的名冊
def get1000(link_list):
    datas_1000=[]
    data=[]
    count=0
    for link in link_list:
        soup=getSoup(link)
        tds=soup.find(id="fbonly").find_all('td')
        for td in tds:
            if count%5==0:
                pass
            else:
                data.append(td.text)
            if count%5==4:
                datas_1000.append(data)
                data=[]
            count+=1
    return datas_1000

# 抓200萬元的名冊
def get200(link_list):
    datas_200=[]
    data=[]
    count=0
    for link in link_list:
        soup=getSoup(link)
        # td位置和1000不同
        tds=soup.find(id="fbonly_200").find_all('td')
        for td in tds:
            if count%5==0:
                pass
            else:
                data.append(td.text)
            if count%5==4:
                datas_200.append(data)
                data=[]
            count+=1
    return datas_200

# 統計中獎地區
def getCityData(df1000,df200):
    citys_1000=[data[:3] for data in df1000['營業地址']]
    citys_200=[data[:3] for data in df200['營業地址']]

    dict_200={}
    for city in set(citys_200):
        if city!='臺北市' and city!='台北市':
            dict_200[city]=citys_200.count(city)
    dict_200['臺北市']=citys_200.count('臺北市')+citys_200.count('台北市')
    dict_1000={}
    for city in set(citys_1000):
        if city!='臺北市' and city!='台北市':
            dict_1000[city]=citys_1000.count(city)
    dict_1000['臺北市']=citys_1000.count('臺北市')+citys_1000.count('台北市')    

    cityData=pd.DataFrame([dict_1000,dict_200],index=[1000,200]).T.sort_values(by=1000,ascending=False)
    
    return cityData



# 抓取中獎清冊網址
url='https://www.etax.nat.gov.tw/etw-main/web/ETW183W1/'
link_list=getLinkList(url)

# 取得二維資料
datas_1000=get1000(link_list)
datas_200=get200(link_list)
df1000=pd.DataFrame(datas_1000,columns=['發票號碼','開立發票營業人','營業地址','交易項目'])
df200=pd.DataFrame(datas_200,columns=['發票號碼','開立發票營業人','營業地址','交易項目'])
cityData=getCityData(df1000,df200)

conv_store=['統一超商','OK便利','萊爾富','全家便利','來來超商','全聯','加油站','大潤發','家樂福','美聯社','醫院','百貨','停車']
cost=r'(\d*)元'

# 1000萬資料
df1000=pd.DataFrame(datas_1000,columns=['發票號碼','開立發票營業人','營業地址','交易項目'])
for i in range(len(df1000)):
    if '台北市' in df1000.loc[i,'營業地址']:
        df1000.loc[i,'營業地址']=df1000.loc[i,'營業地址'].replace('台北市','臺北市')
    city=df1000.loc[i,'營業地址'][:3]
    area=df1000.loc[i,'營業地址'][:6]
    df1000.loc[i,'縣市']=city
    df1000.loc[i,'區域']=area
    
    try:
        df1000.loc[i,'交易項目']=df1000.loc[i,'交易項目'].replace(',','')
        df1000.loc[i,'交易金額']=int(re.findall(cost,df1000.loc[i,'交易項目'])[0])
    except:
        df1000.loc[i,'交易金額']=None
    
    for c in conv_store:
        if c in df1000.loc[i,'開立發票營業人']:
            df1000.loc[i,'店名']=c
            break
        df1000.loc[i,'店名']='其他'
        
# 200萬資料
df200=pd.DataFrame(datas_200,columns=['發票號碼','開立發票營業人','營業地址','交易項目'])
for i in range(len(df200)):
    if '台北市' in df200.loc[i,'營業地址']:
        df200.loc[i,'營業地址']=df200.loc[i,'營業地址'].replace('台北市','臺北市')
    city=df200.loc[i,'營業地址'][:3]
    area=df200.loc[i,'營業地址'][:6]
    df200.loc[i,'縣市']=city
    df200.loc[i,'區域']=area
    try:
        df200.loc[i,'交易項目']=df200.loc[i,'交易項目'].replace(',','')
        df200.loc[i,'交易金額']=int(re.findall(cost,df200.loc[i,'交易項目'])[0])
    except:
        df200.loc[i,'交易金額']=None
    
    for c in conv_store:
        if c in df200.loc[i,'開立發票營業人']:
            df200.loc[i,'超商種類']=c
            break
        df200.loc[i,'超商種類']='非超商'


# bar figure
plt.figure(figsize=(18,6))
index=range(len(cityData)*4)
plt.bar(index[1::4],cityData[1000],color='orange',edgecolor='r',width=0.8,label=1000)
plt.bar(index[2::4],cityData[200],color='bisque',edgecolor='r',width=0.8,label=200)
plt.title('各縣市中獎分布',fontsize=20)
plt.ylabel('中獎個數',fontsize=16)
plt.xlabel('縣市',fontsize=16)
plt.xticks(index[1::4],cityData.index,fontsize=12)
plt.legend()
plt.show()


# pie figure
explode_1000=[0.2 if i==max(cityData[:5][1000].values) else 0 for i in cityData[:5][1000].values]
explode_200=[0.2 if i==max(cityData[:5][200].values) else 0 for i in cityData[:5][200].values]
other_1000=cityData[1000].sum()-cityData[:5][1000].sum()
other_200=cityData[200].sum()-cityData[:5][200].sum()
df=cityData[:5]
df.loc['其他']=[other_1000,other_200]

plt.figure(figsize=(24,14))
plt.subplot(1,2,1)
explode_1000=[0.2 if i==0 else 0 for i in range(len(df))]
index=df[1000].index
colors,texts,pct=plt.pie(df[1000],labels=index,explode=explode_1000,shadow=True,textprops={'fontsize':14},autopct='%.2f%%')
plt.axis('equal')
plt.title('1000萬中獎縣市Top5',fontsize=20,y=0.92)
plt.subplot(1,2,2)
explode_200=[0.2 if i==0 else 0 for i in range(len(df))]
index=df[200].index
plt.pie(df[200],labels=index,explode=explode_200,shadow=True,textprops={'fontsize':14},autopct='%.2f%%')
plt.axis('equal')
plt.title('200萬中獎縣市Top5',fontsize=20,y=0.92)
plt.legend(loc=1,fontsize=14)
plt.show()

# catplot figure
df1=pd.concat([df1000,df200],ignore_index=True)
df1=df1[df1['交易金額']<=1000]
df1=df1[(df1['店名']!='False')].set_index('發票號碼').reset_index()
ax=sns.catplot(x='店名',y='交易金額',data=df1,height=6,aspect=2)
plt.show()

# relplot
plt.figure(figsize=(10,6))
df_city=df1.groupby('縣市')['發票號碼'].count()
df_cost=df1.groupby('縣市')['交易金額'].sum()
df_conv=df1['超商種類']
df2=pd.DataFrame([df_city,df_cost],index=['總中獎數','總交易金額',]).T.sort_values('總交易金額',ascending=False).reset_index()
sns.regplot(x=df2["總中獎數"], y=df2["總交易金額"], data=df2)
# sns.relplot(x='總中獎數',y='總交易金額',data=df2,height=5,aspect=1.5)
plt.show()


# heatmap
df3=df1.groupby(['縣市','店名']).count()
piv=df3.pivot_table(index='縣市',columns='店名',values='發票號碼')
piv=piv.fillna(value=0).astype(int)
plt.figure(figsize=(12,10))
ax=sns.heatmap(piv, annot=True,fmt='d')
ax.set_title('各縣市商家中獎次數分布',fontsize=20)
plt.show()





















