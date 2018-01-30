import re
import requests
import csv
import random
import time

''''抓取内容 所有电影的名字，主角，类型，评分，国家，电影的迅雷地址'''


# 日韩  http://www.ygdy8.net/html/gndy/rihan/index.html
# 国内  http://www.ygdy8.net/html/gndy/china/index.html
# 欧美  http://www.ygdy8.net/html/gndy/oumei/index.html
#通过上面三个url进行url的构造抓取所有的电影详情页的url，将其步入一个列表中，通过url进行进一步的抓取，提高抓取的效率
#主页url构造  欧美 http://www.ygdy8.net/html/gndy/oumei/list_7_1.html
#日韩 http://www.ygdy8.net/html/gndy/rihan/list_6_2.html
#国内 http://www.ygdy8.net/html/gndy/china/list_4_2.html
#xpath路径  //b/a/@href
#国内2f
#欧美3
#日韩5
agent =[
    'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0',
    'User-Agent:Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
    'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)'
        ]
headers={'User_Agent':random.choice(agent)}

films=[]



def detailed_url():
    #start=time.time()
    #电影天堂的三个类型的电影
    link_key = ['china','oumei','rihan']
    for key in link_key:
        try:
            main_url = 'http://www.ygdy8.net/html/gndy/'+key+'/index.html'
            main_req = requests.get(main_url,headers=headers,timeout = 10)
            main_req.encoding='gbk'
            main_pat = "<a href='list_([0-9])*?_([0-9]*?).html'>末页</a>"
            totall_pages = re.compile(main_pat).findall(main_req.text)[0][1]
            #print(totall_pages)
            tag = re.compile(main_pat).findall(main_req.text)[0][0]
            #print(totall_pages)
            #print(tag)
            for page in range(1, int(totall_pages)):
                url = 'http://www.ygdy8.net/html/gndy/'+ key + '/list_'+str(tag)+'_' + str(page) + '.html'
                print('>>>当前是' + key + '电影的第' + str(page) + '个页面')
                ind = requests.get(url, headers=headers,timeout = 10)
                ind_html = ind.text
                ind_pat = '<a href="(.*?)" class="ulink">'
                ind_href = re.compile(ind_pat).findall(ind_html)
                for ind in ind_href:
                    det_url = 'http://www.ygdy8.net' + ind
                    yield det_url
                    #print(detailed_url)
        except Exception as e:
            with open('error_ind_urls.txt','a')as f:
                f.write(str(e)+'\n')
                f.close()
   # print('>>>详情页面的数量共有：%s'%len(set(detailed_url)))

# 由于没有写入数据库，csv文件中没有默认值，为了提高数据的质量，用此函数，将部分抓取失败的内容有空格写入
def integration(list):
    if len(list) >=1:
        return list[0]
    else:
        return ' '

def draw_key(key_url):
    try:
        output_data =[]
        film = requests.get(key_url, headers=headers,timeout = 10)
        film.encoding = 'gbk'
        name_pat = '<title>.*?《(.*?)》.*?</title>'
        ftp_pat = '<td style.*?<a href="(.*?)">ftp'
        type_pat = '◎类　　别　(.*?)<br />'
        douban_pat = '<br />◎豆瓣评分.*?　(.*?)<br />'
        director_pat = '<br />◎导　　演　(.*?)<br />'
        author_pat = ' <br />◎主　　演　(.*?) <br />'
        film_ftp = re.compile(ftp_pat, re.S).findall(film.text)
        type = re.compile(type_pat,re.S).findall(film.text)
        douban = re.compile(douban_pat,re.S).findall(film.text)
        director = re.compile(director_pat,re.S).findall(film.text)
        author = re.compile(author_pat,re.S).findall(film.text)
        film_name = re.compile(name_pat).findall(film.text)
        #dytt_date.append(film_date)
        dytt_data = [film_name,type,director,author,douban,film_ftp]
        for i in dytt_data:
            this_data = integration(i)
            #部分数据抓取出错，判断数据的长度，来提高数据的正确性，牺牲了性能
            if len(this_data)>150:
                with open('error_re.txt','a')as f:
                    f.write('%s\n'%(film_name[0]))
                    f.close()
                this_data = ' '
            output_data.append(this_data)
        print('>>>%s数据抓取成功'%film_name[0])
        try:
            with open('电影天堂数据.csv','a')as f:
                f_csv = csv.writer(f)
                f_csv.writerow(output_data)
                f.close()
                print('csv数据写入成功')
                print('='*30)
        except Exception as e:
            print(str(e))
            print('='*30)
            with open('error_csv.txt','a')as f:
                f.write(str(e)+'\n')
                f.close()
    except Exception as e:
        print(str(e))
        with open('url_error.txt','a')as f:
            f.write(str(e)+'\n')
            f.close()






start = time.time()
x =0
for i in detailed_url():
    key_url = i
    x+=1
    draw_key(key_url)
end = time.time()
print('共采集到%s条电影天堂数据'%x)
print('该程序共用时%.2f分钟'%((end-start)/60))