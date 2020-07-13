'''
五个一政策下的回国航班查询器
Flights to Mainland China Checker during COVID-19 situation
Version:0.3
Author: Vincent Cui
'''

import requests
import streamlit as st
import bs4
from lxml import html
from bs4 import BeautifulSoup
from distutils.filelist import findall
import re
import pandas as pd
import functools
from urllib.request import urlopen
from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
import time
import datetime
import random
import os




def make_clickable(url, text):
    return f'<a target="_blank" href="{url}">{text}</a>'
def cache_on_button_press(label, **cache_kwargs):
    """Function decorator to memoize function executions.
    Parameters
    ----------
    label : str
        The label for the button to display prior to running the cached funnction.
    cache_kwargs : Dict[Any, Any]
        Additional parameters (such as show_spinner) to pass into the underlying @st.cache decorator.
    Example
    -------
    This show how you could write a username/password tester:
    >>> @cache_on_button_press('Authenticate')
    ... def authenticate(username, password):
    ...     return username == "buddha" and password == "s4msara"
    ...
    ... username = st.text_input('username')
    ... password = st.text_input('password')
    ...
    ... if authenticate(username, password):
    ...     st.success('Logged in.')
    ... else:
    ...     st.error('Incorrect username or password')
    """
    internal_cache_kwargs = dict(cache_kwargs)
    internal_cache_kwargs['allow_output_mutation'] = True
    internal_cache_kwargs['show_spinner'] = False
    
    def function_decorator(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            @st.cache(**internal_cache_kwargs)
            def get_cache_entry(func, args, kwargs):
                class ButtonCacheEntry:
                    def __init__(self):
                        self.evaluated = False
                        self.return_value = None
                    def evaluate(self):
                        self.evaluated = True
                        self.return_value = func(*args, **kwargs)
                return ButtonCacheEntry()
            cache_entry = get_cache_entry(func, args, kwargs)
            if not cache_entry.evaluated:
                if st.button(label):
                    cache_entry.evaluate()
                else:
                    raise st.ScriptRunner.StopException
            return cache_entry.return_value
        return wrapped_func
    return function_decorator
#Searching function

def Search(dept,arrv,date,cur,ali):
    url = 'https://www.google.com/flights?hl=zh-CN#'
    df_record = pd.DataFrame(columns=['日期','始发机场','到达机场','航空公司' ,'航班号','票价','官网购票链接'])  
#     dept='LAX'
#     arrv='SFO'
#     date='2020-11-21'
#     cur='USD'
#     ali='UA'
    if date.month <10:
        mo='0'+str(date.month)
    else:
        mo=str(date.month)
    if date.day <10:
        da='0'+str(date.day)
    else:
        da=str(date.day)
    date1=str(date)
    date2=str(date.year)[:2]+str(mo)+str(da)
    date3=str(date.year)+str(mo)+str(da)
    
    #this part is use to optimize the server, if you run on your local computer, or if you got any problem from these part you can just delete some of them
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
    #chrome_options.binary_location = "/usr/bin/chromium-browser"  #if you are using google chrome, not chromium, you dont need this row

    
    driver = webdriver.Chrome(chrome_options=chrome_options)
    url1=url+'flt='+dept+'.'+arrv+'.'+date1+';c:'+cur+';e:1'+';s:0;a:'+ali+';sd:1;t:f;tt:o'
    driver.get(url1)
    #wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".gws-flights__flex-filler")))
    time.sleep(1)
    #results = driver.find_elements_by_class_name('LJTSM3-v-d')
    #search=driver.find_elements_by_xpath("//div[@class='gws-flights-results__carriers']")
    #print(driver.find_element_by_css_selector('.gws-flights-results__itinerary-price').text)
    elem = driver.find_element_by_xpath("//*")
    source_code = elem.get_attribute("outerHTML")
    driver.quit()
    bs = BeautifulSoup(source_code, 'html.parser')
    a = bs.find_all('div', class_='gws-flights-results__itinerary-card-summary')
    if a==[]:
        pass
    else:
        for tag in a: 
            fls = tag.findAll('div', class_='gws-flights-results__carriers')
            a1=str(a)
            #for i in range(1,12):
                #if i <= a1.count('gws-flights-results__carriers'):
            fl=fls[0].get_text()
            num = str(tag.find('div',class_="gws-flights-results__select-header gws-flights__flex-filler"))
            num1 = num[num.find(arrv):num.find('class')][4:9]
            price=tag.find('div', class_='gws-flights-results__itinerary-price').text
            global link
            if ali=='UA':
                link='https://www.united.com/ual/en/US/flight-search/book-a-flight/results/rev?f='+dept+'&t='+arrv+'&d='+date1+'&tt=1&sc=7&px=1&taxng=1&newHP=True&idx=1'
            elif ali=='MU':
                link='http://www.ceair.com/booking/'+dept+'-'+arrv+'-'+date2+'_CNY.html'
            elif ali=='CZ':
                link='https://oversea.csair.com/new/us/zh/flights?m=0&p=100&flex=1&t='+dept+'-'+arrv+'-'+date3
            elif ali=='MF':
                link='https://www.xiamenair.com/zh-cn/nticket.html?tripType=OW&orgCodeArr%5B0%5D='+dept+'&dstCodeArr%5B0%5D='+arrv+'&orgDateArr%5B0%5D='+date1+'&dstDate=&isInter=true&adtNum=1&chdNum=0&JFCabinFirst=false&acntCd=&mode=Money&partner=false&jcgm=false' 
            elif ali=='HU':
                link='https://new.hnair.com/hainanair/ibe/deeplink/ancillary.do?DD1='+date1+'&DD2=&TA=1&TC=0&TI=0&TM=&TP=&ORI='+dept+'&DES='+arrv+'&SC=A&ICS=F&PT=F&FLC=1&CKT=&DF=&NOR=&PACK=T&HC1=&HC2=&NA1=&NA2=&NA3=&NA4=&NA5=&NC1=&NC2=&NC3=&NC4='
            elif ali=='3U':
                link='http://www.sichuanair.com/'
            elif ali=='JD':
                link='https://new.jdair.net/jdair/?tripType=OW&originCode='+dept+'&destCode='+arrv+'&departureDate='+date1+'&returnDate=&cabinType=ECONOMY&adtNum=1&chdNum=0&const_id=5f0a8017p2ZZg9hvG7URRHemkpAMhpvwRfIFTPm1&token=#/ticket/tripList'
            elif ali=='LH':
                link='https://www.lufthansa.com/cn/zh/homepage'
            elif ali=='TK':
                link='https://www.turkishairlines.com/zh-cn/index.html'
            elif ali=='CA':
                link='http://et.airchina.com.cn/InternetBooking/AirLowFareSearchExternal.do?&tripType=OW&searchType=FARE&flexibleSearch=false&directFlightsOnly=false&fareOptions=1.FAR.X&outboundOption.originLocationCode='+dept+'&outboundOption.destinationLocationCode='+arrv+'&outboundOption.departureDay='+str(da)+'&outboundOption.departureMonth='+str(mo)+'&outboundOption.departureYear='+str(date.year)+'&outboundOption.departureTime=NA&guestTypes%5B0%5D.type=ADT&guestTypes%5B0%5D.amount=1&guestTypes%5B1%5D.type=CNN&guestTypes%5B1%5D.amount=0&guestTypes%5B3%5D.type=MWD&guestTypes%5B3%5D.amount=0&guestTypes%5B4%5D.type=PWD&guestTypes%5B4%5D.amount=0&pos=AIRCHINA_CN&lang=zh_CN&guestTypes%5B2%5D.type=INF&guestTypes%5B2%5D.amount=0'
            else:
                link=url1
            df_record = df_record.append({'日期':date1, '始发机场':dept,'到达机场':arrv,'航空公司':fl, '航班号':num1, '票价':price, '官网购票链接':link}, ignore_index=True)
    df_record['官网购票链接'] = df_record['官网购票链接'].apply(make_clickable, args = ('点击前往',))
    return df_record

   
#North America
@cache_on_button_press('Search') 
def NA(start,end,cur):
    date=start
    df1 = pd.DataFrame(columns=['日期','始发机场','到达机场','航空公司' ,'航班号','票价','官网购票链接']) 
    while date <= end:
        if date.weekday()==0:
            df1=df1.append(Search('LAX','XMN',date,cur,'MF'))
            date=date+datetime.timedelta(days=1)
            time.sleep(random.randint(0,10)/10)
        elif date.weekday()==1:
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==2:
            df1=df1.append(Search('JFK','PVG',date,cur,'MU'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('SFO','PVG',date,cur,'UA'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('YYZ','PEK',date,cur,'HU'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('YVR','CAN',date,cur,'CZ'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('YVR','CTU',date,cur,'3U'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==3:
            df1=df1.append(Search('SEA','PVG',date,cur,'DL'))
            date=date+datetime.timedelta(days=1)
            time.sleep(random.randint(0,10)/10)
        elif date.weekday()==4:
            df1=df1.append(Search('DTW','PVG',date,cur,'DL'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('YVR','XMN',date,cur,'MF'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==5:
            df1=df1.append(Search('YYZ','PVG',date,cur,'MU'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('SFO','PVG',date,cur,'UA'))
            date=date+datetime.timedelta(days=1)
            time.sleep(random.randint(0,10)/10)
        else:
            df1=df1.append(Search('YVR','PEK',date,cur,'CA'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('LAX','PEK',date,cur,'CA'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('LAX','CAN',date,cur,'CZ'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
    return df1

#Europe
@cache_on_button_press('Search') 
def EU(start,end,cur):
    date=start
    df1 = pd.DataFrame(columns=['日期','始发机场','到达机场','航空公司' ,'航班号','票价','官网购票链接']) 
    while date <= end:
        if date.weekday()==0:
            df1=df1.append(Search('AMS','PVG',date,cur,'MU'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('CPH','PEK',date,cur,'CA'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('FRA','NKG',date,cur,'LH'))
            date=date+datetime.timedelta(days=1)
            time.sleep(random.randint(0,10)/10)
        elif date.weekday()==1:
            df1=df1.append(Search('FRA','PVG',date,cur,'MU'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('BRU','PEK',date,cur,'HU'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('CDG','CAN',date,cur,'CZ'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('LHR','PVG',date,cur,'VS'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==2:
            df1=df1.append(Search('CDG','PEK',date,cur,'CA'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('FRA','PVG',date,cur,'LH'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('AMS','XMN',date,cur,'MF'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('IST','CAN',date,cur,'TK'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==3:
            df1=df1.append(Search('LHR','CAN',date,cur,'CZ'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('CDG','PVG',date,cur,'AF'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('SVO','PVG',date,cur,'turkSU'))
            date=date+datetime.timedelta(days=1)
            time.sleep(random.randint(0,10)/10)
        elif date.weekday()==4:
            df1=df1.append(Search('LHR','PVG',date,cur,'MU;CA'))
            time.sleep(1)
            df1=df1.append(Search('WAW','PEK',date,cur,'CA'))
            time.sleep(1)
            df1=df1.append(Search('MSQ','PEK',date,cur,'CA'))
            time.sleep(1)
            df1=df1.append(Search('ARN','PEK',date,cur,'CA'))
            time.sleep(1)
            df1=df1.append(Search('SVO','PEK',date,cur,'CA'))
            time.sleep(1)
            df1=df1.append(Search('AMS','CAN',date,cur,'CZ'))
            time.sleep(1)
            df1=df1.append(Search('LHR','TAO',date,cur,'JD'))
            time.sleep(1)
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==5:
            df1=df1.append(Search('FRA','PVG',date,cur,'CA'))
            time.sleep(1)
            df1=df1.append(Search('MAD','PEK',date,cur,'CA'))
            time.sleep(1)
            df1=df1.append(Search('VIE','PEK',date,cur,'CA'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('ATH','PEK',date,cur,'CA'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('LIS','XIY',date,cur,'JD'))
            date=date+datetime.timedelta(days=1)
            time.sleep(1)
        else:
            df1=df1.append(Search('CDG','PVG',date,cur,'MU'))
            time.sleep(1)
            df1=df1.append(Search('HEL','PVG',date,cur,'HO'))
            time.sleep(1)
            date=date+datetime.timedelta(days=1)
    return df1

#Japan-Korea
def JK(start,end,cur):
    date=start
    df1 = pd.DataFrame(columns=['日期','始发机场','到达机场','航空公司' ,'航班号','票价','官网购票链接']) 
    while date <= end:
        if date.weekday()==0:
            df1=df1.append(Search('CJU','PVG',date,cur,'9C'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('ICN','XMN',date,cur,'MF'))
            date=date+datetime.timedelta(days=1)
            time.sleep(random.randint(0,10)/10)
        elif date.weekday()==1:
            df1=df1.append(Search('KIX','PVG',date,cur,'HO'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('ICN','CGQ',date,cur,'OZ'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==2:
            df1=df1.append(Search('ICN','WEH',date,cur,'7C'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==3:
            df1=df1.append(Search('NRT','PVG',date,cur,'CA'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('NRT','SHE',date,cur,'CZ'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('NRT','DLC',date,cur,'JL'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==4:
            df1=df1.append(Search('ICN','PVG',date,cur,'MU'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('NRT','PVG',date,cur,'MU'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('ICN','PEK',date,cur,'CA'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('ICN','TAO',date,cur,'SC'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('NRT','FOC',date,cur,'MF'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('ICN','SZX',date,cur,'BX'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
        elif date.weekday()==5:
            df1=df1.append(Search('YYZ','PVG',date,cur,'MU'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('ICN','TAO',date,cur,'QW'))
            date=date+datetime.timedelta(days=1)
            time.sleep(random.randint(0,10)/10)
        else:
            df1=df1.append(Search('NRT','PVG',date,cur,'9C'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('NRT','PVG',date,cur,'NH'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('ICN','SHE',date,cur,'CZ'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('NRT','HRB',date,cur,'9C'))
            time.sleep(random.randint(0,10)/10)
            df1=df1.append(Search('ICN','NKG',date,cur,'OZ'))
            time.sleep(random.randint(0,10)/10)
            date=date+datetime.timedelta(days=1)
    return df1

st.title("五个一回国航班查询APP")
st.write('''请先在左侧选择出发区域，之后设置查询日期区间和票价货币选择，最大
    查询范围为一周，查询间隔为1秒，北美出发一周的航班大概查询时间为2分钟，
    请耐心等待。查询完毕后将会有列表显示有票结果以及官方购票链接''')
event_list=['请选择区域','北美','欧洲','日韩','更多区域正在开发中']
# event_list=['北美','欧洲','澳洲','非洲','日韩','东南亚','中东及非洲','南亚']
event_type = st.sidebar.selectbox(
'选择出发区域',
event_list
)

#set app width
st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 1280px;
        padding-top: 3rem;
        padding-right: 3rem;
        padding-left: 3rem;
        padding-bottom: 3rem;
    }}

</style>
""",
        unsafe_allow_html=True,
    )

start=st.date_input('起始日期', datetime.date.today())
end=st.date_input('结束日期', start)
cur_list=['人民币','美元','欧元','日元','韩元']
cur1= st.selectbox(
'选择货币',
cur_list
)
intv=end-start

if cur1=='人民币':
    cur='CNY'
elif cur1=='美元':
    cur='USD'
elif cur1=='日元':
    cur='JPY'
elif cur1=='韩元':
    cur='KRW'
else:
    cur='EUR'
if intv.days>6:
    st.write('为了优化性能，间隔请勿超过一周')
elif event_type =='北美':
    df_record=NA(start,end,cur)
    if len(df_record) == 0:
        st.write("查询日期范围内该地区的机票可能已售罄，建议更改日期范围或前往航空公司官网申请候补")
    else:
        df = df_record.to_html(escape=False)
        st.write(df, unsafe_allow_html=True)
elif event_type =='欧洲':
    df_record=EU(start,end,cur)
    if len(df_record) == 0:
        st.write("查询日期范围内该地区的机票可能已售罄，建议更改日期范围或前往航空公司官网申请候补")
    else:
        df = df_record.to_html(escape=False)
        st.write(df, unsafe_allow_html=True)
elif event_type =='日韩':
    df_record=JK(start,end,cur)
    df_record.to_csv('E://flight//flight_search_jk.csv',encoding="utf-8")
    df_record.reset_index(drop=True, inplace=True)
    if len(df_record) == 0:
        st.write("查询日期范围内该地区的机票可能已售罄，建议更改日期范围或前往航空公司官网申请候补")
    else:
        df = df_record.to_html(escape=False)
        st.write(df, unsafe_allow_html=True)
else:
    pass
st.write("""
谢谢使用五个一航班查询app，请刷新网页（或按F5）开始新的查询。
部分高需求航班可能会被航空公司锁仓所以不会显示在这里，部分国内航司需要上官网预约登记购票。
疫情之下并不是所有机场都允许转机，有些国家可能需要核酸证明等文件，具体注意事项可以参照<a href="https://www.uscreditcardguide.com/xinguanyiqingzhixiaruhehuiguo/">这篇文章</a>。
10月24日是航空公司的换季日，之后的航班信息可能会有变动\n
很高兴能帮到您抢到机票，如果这个app让您感到舒适，可以考虑点击下方donate按钮奖励我一杯奶茶钱：）
如果有任何改进建议也可以在我的<a href="https://vincentc.us/">博客页面</a>留言，谢谢！\n
祝愿大家都能顺利回国，一路平安，笔芯！❤ \n
Refresh page (or press F5) to start a new search
Some high-demand tickets may locked up by airlines
Thank you for using Flight Checker Version: 0.3\n
Released on: 11/07/2020
Source code is available at: https://github.com/Vincent-Cui/flights_checker
Developer: Vincent Cui
if you think it is helpful, you can click the button below to donate me some milk tea money:)
""",unsafe_allow_html=True)

