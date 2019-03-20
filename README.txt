爬取微信公众号文章及阅读量、点赞量
	2019-1-30

       首先，我们选择任意一个公众号进行尝试，需用到Fiddler抓包工具（自行配置）。微信进入公众号，点击右上角查看历
史消息，这时，我们会从Fiddler捕捉到请求，url为mp/profile_ext?action=home&__biz=MjM5MTY3OTYyMQ==
&scene=124&uin=NDQ1MDE3MzY0&key=ab4ef62e45f04b50b994d388eb47238deba71d3b8bf0fc53cfc925b07936bbc
b05980a87143be1d2101bb85f64c71f802001bcd14f839af03209704c9f80c201cbf23fea330ca077b0944fe791a752ba
&devicetype=Windows+10&version=6206061c&lang=zh_CN&a8scene=7
&pass_ticket=hXip58hmXp4wAXA41N2Z3qxfhtIRnpUbanYmfHfvl5Aq01TOhxn9FasD6fUCoysI&winzoom=1，
另外，我们发现公众号历史消息是可以往下查看更多的，同样用Fiddler我们可以捕捉到一个json形式的文件,url为
/mp/profile_ext?action=getmsg&__biz=MjM5MTY3OTYyMQ==&f=json&offset=10&count=10&is_ok=1
&scene=124&uin=NDQ1MDE3MzY0&key=da3ec8f0fca1de035b511e0887b98743e9ee8f6
1beae0eaa4010cc7b032fd63e140ff7abd4b57c6f75fd3cea232f633d769557374c486617268c8708597e791510
f7d622f8a626ff73e85f7a5c274d1e
&pass_ticket=hXip58hmXp4wAXA41N2Z3qxfhtIRnpUbanYmfHfvl5Aq01TOhxn9FasD6fUCoysI&wxtoken=
&appmsg_token=993_NOirjZWY5FEBFH%252FebEmoVPNEXjbKjXUHQnX-DQ~~&x5=0&f=json
我们对这两个url进行分析，并且用python进行调试，发现其中重要的几个参数为：action(home/getmsg)  
__biz 类似于公众号的唯一ID（后面的==也是）     f=json json形式      offset：从第几个开始请求(注意这里的offset，
同一天发布的文章的offset是相同的，和后文的idx对应)   count:请求数量(无论写什么微信都默认为10)
 uin(user information)  类似用户的唯一ID       key加密参数且只有十五分钟左右的时效，类似于每个公众号提供接口，
而且不同公众号的key是不能共用的，但是同一个公众号的key好像是能共用的。通过调试我们还发现，把第二个的offset
改为0便能请求到进入公众号时最初的那几篇文章，因此我们选择用python向第二个url发送请求，需要有User-Agent(最
好是移动端)和Cookie(Fiddler里复制),得到json文件。
      分析返回的json文件，发现所有的数据都在general_msg_list里，因此我们选择用re匹配出一个公众号所有文章的
文章名以及链接(注意，这里只爬取有链接的文章，没有链接的文章一概过滤)。另外还有一点很重要的是content_url里的
&amp，/其实是经过转义的，原链接中根本没有，我们用replace函数替换,便可得到文章的路径和文章名。此外，在链接中
我们能得到两个重要的参数sn、mid，下面要用到。
     
      下一步就是爬取每篇文章的阅读量等后台数据了。仍然使用Fiddler，点开任意一篇文章，我们可以捕捉到一个
/mp/getappmsgext?    请求，里面的appmsgstat里就有read_num和like_num，分析该请求。发现url中有两个关键
参数 uin 和 key 。另外，还需传递某些数据才会返回给你like_num和read_num，否则数据会为空，这就是为什么从浏览器
等等都得不到浏览量的原因。经过分析筛选，发现data中必穿的五个数据 __biz     appmsg_type     mid    sn   idx     is_only_read。
appmsg_type和is_only_read具体不知道是什么意思，但是参照几个公众号发现它们都相同，因此，这里直接把它们写死。
sn 和 mid 可以通过之前文章的url能够得到。 idx大概意思是同一天写了的第几篇文章，如果同一天只写了一篇文章则idx始终是1。
需注意，举个例子，一个公众号一天写了五篇文章(idx分别为1-5)，他删除了第二篇文章，但是后续的idx不会随之改变，仍然是345
，因此需要异常处理。另外，如果爬取速度过快，微信会对之进行验证。

      最后我们对程序进行整理，将其封装进一个函数，需要传递的值有__biz(公众号ID) 、offset(想要多少自己套循环，步长为10) 
（注意offset是天数，如果一天写两篇，则输出有二十篇（不考虑有无链接文章的情况），如果一天写十篇，则输出为十篇） 、  
uin(这里我用的是自己微信的uin，将它写死了) 	以及key。

     key为一大难点无法攻破。只有在微信客户端下点击某一个公众号的查看历史消息才能捕捉到key，并且具有时效。
现有一想法就是   在公众号历史消息中点击复制链接地址, 如https://mp.weixin.qq.com/mp/profile_ext?
action=home&__biz=MzUzMDk1MzMxNQ==&scene=124#wechat_redirect， 可以看到 微信内部访问公众号是不需要
key的，但是点击默认浏览器打开则会跳出验证页面，因此模拟微信浏览器登录获取key成了关键。