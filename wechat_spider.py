import re
import requests
import time


def wechat_spider(__biz, offset, key):
    # action __biz f=json offset count uin key 为关键参数
    # __biz为公众号ID,offset为从第几天开始(注意是天数，一天写多篇文章仍然是1),
    # count为请求数量(还是天数),uin为user information,key为加密参数且有时效,不同文章对应的是不同的key

    uin = "NDQ1MDE3MzY0"
    url = "http://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=%s&f=json&offset=%s&count=10" \
          "&uin=%s&key=%s"\
          % (__biz, offset, uin, key)
    # 设置headers
    headers = {
        'Cookie': 'rewardsn=; wxtokenkey=777; wxuin=445017364; devicetype=Windows10; version=6206061c; '
                  'lang=zh_CN; pass_ticket=OnyWHUm0qJgYUSwH24Y4h1NB+zsED7h9jx8DO6wucgnKGt5PK3px2JkPxIaqt3PH;'
                  ' wap_sid2=CJTamdQBElw4NXl5NEFTUGE3YVdVQ1BnSlBhaU5YR0NUWHF'
                  'telQ0SHF4SXdNU2szZ2tLSS1rSnRZanRhWDlTc2ZrSjZSST'
                  'JBZ1NlWFJPZW1YcDROTXIxT1BwdThyZUVEQUFBfjDxubriBTgNQJVO',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat'
                      ' QBCore/3.43.901.400 QQBrowser/9.0.2524.400',
        'Connection': 'keep-alive'
    }

    # 正则爬取返回的json文件的文章名和链接
    # 这里只爬取有链接的文章，无链接的文章一概过滤
    content = requests.post(url, headers=headers).json()
    # print(content['general_msg_list'])
    # print(content)
    name_list = re.findall(r'"title":"(.*?)"', content['general_msg_list'])
    hrefs_list = re.findall(r'"content_url":"(.*?)"', content['general_msg_list'])
    # 爬取链接中的mid、sn
    for i in range(0, len(hrefs_list)):
        hrefs_list[i] = hrefs_list[i].replace("amp;", "")
    # print(hrefs_list)
    mid_list = []
    sn_list = []
    for i in range(len(hrefs_list)):
        # print(hrefs_list[i].split("&"))
        try:
            mid = hrefs_list[i].split("&")[1]
            mid_list.append(mid[4::])
            sn = hrefs_list[i].split("&")[3]
            sn_list.append(sn[3::])
        # 这里如果公众号删除某篇文章，所有数据会变为" ",因此需做异常处理
        except IndexError:
            del name_list[i]

    # print(mid_list)
    # print(sn_list)

    # 重要的六个参数uin key __biz mid sn id
    # 设置url和data数据,爬出一篇公众号的所有文章的阅读量和点赞量
    url_article = "http://mp.weixin.qq.com/mp/getappmsgext?&uin=%s&key=%s" % (uin, key)
    read = ""
    like = ""
    final_data = {}
    idx = 1
    for i in range(len(mid_list)):
        # idx为同一天发布的第几篇文章，如果同一天发布多篇文章，则idx会随之增加
        try:
            if i == 0:
                idx = 1
            elif mid_list[i] == mid_list[i-1]:
                idx += 1
            else:
                idx = 1
            # print(idx)
            data = {
                "__biz": __biz,
                "appmsg_type": "9",
                "mid": mid_list[i],
                "sn": sn_list[i],
                "idx": idx,
                "is_only_read": "1",

            }
            content = requests.post(url_article, headers=headers, data=data).json()
            print(content)
            print(content["appmsgstat"]["read_num"], content["appmsgstat"]["like_num"])
            read = content["appmsgstat"]["read_num"]
            like = content["appmsgstat"]["like_num"]
        # 如果同一天删除一篇文章,其他文章的idx不会改变,因此需做异常处理,后续文章的idx加一，被删除文章报错
        except KeyError:
            print("KeyError")
            read = "Error"
            like = "Error"
            idx += 1
            time.sleep(3)
        finally:
            final_data[name_list[i]] = str("阅读量为: " + str(read) + " , " + "点赞量为: " + str(like))
            time.sleep(2)

    return final_data


if __name__ == '__main__':
    __biz = "MzI3NjAxMTUzOA=="
    key = "39cbc9cfec0936c207ee477d196da25a41930ac6f3e52cf75970a1a65e1adb3266291b50df9816e56a8eb24b5d8cba42f6b4456ee8b5dcc92624e274bbe104dd2072d723a3cadc0f731c48a413cce16f"

    dict1 = wechat_spider(__biz, 0, key)
    all_dict = dict1
    print(all_dict)
    """
    # 爬取公众号最新写文章的30天的所有文章
    for offset in range(11, 31, 10):
        print(offset)
        dict2 = wechat_spider(__biz, offset, key)
        all_dict = dict(all_dict, **dict2)
        if dict2 == {}:
            break
    print(all_dict)
    """
    """
    # 爬取全部文章
    offset = 11
    while True:
        dict2 = wechat_spider(__biz, offset, key)
        # print(dict2)
        
        if not dict2 == {}:
            offset += 10
            all_dict = dict(all_dict, **dict2)
        else:
            break
    print(all_dict)
    """
"""
MzUzMDk1MzMxNQ==
MzI3NjAxMTUzOA==
MzI3Nzc5OTYyMQ==
MzA5ODcwODkzNg==
"""