from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage,Image,At
from mirai.models import Forward,ForwardMessageNode
import requests,re,os,json,time,base64,threading,urllib.parse
from bs4 import BeautifulSoup

#=====================
# 配置机器人账号信息
ACCOUNT = 123456789 #QQ号
VERIFY_KEY = '114514' #密钥
HOST = 'localhost' #Mirai地址（一般情况下不需要修改）
PORT = 8080 #mirai-http-api端口
#=====================

def get_json_info(page_html):
    soup=BeautifulSoup(page_html,'html.parser')
    original_json=soup.find_all(id='__NEXT_DATA__')
    #print(original_json[0])
    pattern = re.compile(r'<[^>]+>',re.S)
    result = pattern.sub('', str(original_json[0]))
    return result
    

def matche(url,headers={},resType="text"):
    x = requests.get(url,headers=headers)
    if resType=="text":
        return x.text
    elif resType=="img":
        return x.content
        

    
if __name__ == '__main__':
    
    bot = Mirai(
        qq=ACCOUNT,adapter=WebSocketAdapter(
            verify_key=VERIFY_KEY, HOST, port=PORT
        )
    )
    
    @bot.on(FriendMessage)
    async def stop(event:FriendMessage):
        if str(event.message_chain)=='木屋查停止':
            await bot.send(event, '正在停止')
            exit()
        
    @bot.on(GroupMessage)
    async def getAnalysis(event:GroupMessage):
        if '魔力测评 ' in str(event.message_chain):
            url=str(event.message_chain).split(" ")[1]
            if ('/community/main/compose' in url)==True:
                url=url.split('/')[len(url.split('/'))-1]
            comId=url
            url='https://community-api.xiaomawang.com/api/v1/composition/get-evaluation-info?compositionId='+url
            try:
                jsons=json.loads(matche(url))
                if jsons['message']!='成功':
                    return bot.send(event,'查询失败！')
                scores=jsons['data']['scores']
                await bot.send(event,[
                    "作品"+comId+"的测评结果（数据来自XMW）：",
                    "\n",
                    '学科基础: '+str(scores['subjectBasic']['score'])+' （'+str(scores['subjectBasic']['grade'])+'）',
                    "\n",
                    'Scratch基础: '+str(scores['scratchBasic']['score'])+' （'+str(scores['scratchBasic']['grade'])+'）',
                    "\n",
                    '数据应用: '+str(scores['dataApplication']['score'])+' （'+str(scores['dataApplication']['grade'])+'）',
                    "\n",
                    '用户交互: '+str(scores['userInteractive']['score'])+' （'+str(scores['userInteractive']['grade'])+'）',
                    "\n",
                    '程序结构: '+str(scores['programStructure']['score'])+' （'+str(scores['programStructure']['grade'])+'）',
                    "\n",
                    '程序抽象: '+str(scores['programAbstract']['score'])+' （'+str(scores['programAbstract']['grade'])+'）',
                    "\n",
                    '程序逻辑: '+str(scores['programLogic']['score'])+' （'+str(scores['programLogic']['grade'])+'）',
                    "\n",
                    '总评得分: '+str(scores['total']['score'])+' （'+str(scores['total']['grade'])+'）',
                    '超过'+str(jsons['data']['surpassRate'])+'%的用户！',
                    '\n输入"木屋查功能列表"查看更多！'
                ])
            except Exception as e:
                return bot.send(event,str(e))
                
                
    # 搜索用户作品工作室
    @bot.on(GroupMessage)
    async def search(event:GroupMessage):
        # 指令格式: '搜索[类型:用户/作品/工作室] <内容>'
        if ('搜索' in str(event.message_chain)) and (' ' in str(event.message_chain)):
            searchType=str(event.message_chain).split(' ')[0]
            args=str(event.message_chain).split(' ')
            args.remove(searchType)
            name=' '.join(args)
            await bot.send(event,[At(event.sender.id)," 正在搜索..."])
            if searchType=='搜索作品':
                url='http://world.xiaomawang.com/w/search?name='+urllib.parse.quote(name)
                try:
                    jsons=json.loads(get_json_info(matche(url)))
                    searchList=jsons['props']['initialState']['search']['searchResults'][0]['list']
                except Exception as e:
                    return bot.send(event,str(e))
                headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.105 Safari/537.36','Referer': url}
                returnMsg=[]
                for item in searchList:
                    returnMsg.append(ForwardMessageNode(
                        message_chain=[
                        Image(base64=base64.b64encode(matche(item['coverKey'],headers,'img')).decode()),
                        "[#"+str(searchList.index(item)+1)+"] "+str(item['title'])+'\n编号: '+str(item['compositionId'])+'\n作者: '+str(item['userObject']['nickname'])+' (ID:'+str(item['userObject']['userId'])+')'],
                        sender_id=1328387967,
                        sender_name='搜索界面'
                    ))
                await bot.send(event,["胡梨找到结果啦！最多显示20条"])
                try:
                    await bot.send(event,Forward(node_list=returnMsg))
                except Exception as e:
                    return bot.send(event,str(e))
                
            elif searchType=='搜索用户':
                url='http://world.xiaomawang.com/w/search?type=2&name='+urllib.parse.quote(name)
                try:
                    jsons=json.loads(get_json_info(matche(url)))
                    searchList=jsons['props']['initialState']['search']['searchResults'][1]['list']
                except Exception as e:
                    return bot.send(event,str(e))
                headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.105 Safari/537.36','Referer': url}
                returnMsg=[]
                for item in searchList:
                    returnMsg.append(ForwardMessageNode(
                        message_chain=[
                        Image(base64=base64.b64encode(matche(item['avatarImg'],headers,'img')).decode()),
                        "[#"+str(searchList.index(item)+1)+"] "+str(item['nickname'])+'\nID: '+str(item['userId'])+'\n粉丝数: '+str(item['statObject']['fansCount'])+'\n关注数: '+str(item['statObject']['followCount'])],
                        sender_id=1328387967,
                        sender_name='搜索界面'
                    ))
                await bot.send(event,["胡梨找到结果啦！最多显示20条"])
                try:
                    await bot.send(event,Forward(node_list=returnMsg))
                except Exception as e:
                    return bot.send(event,str(e))
                    
            elif searchType=='搜索工作室':
                url='http://world.xiaomawang.com/w/search?type=3&name='+urllib.parse.quote(name)
                try:
                    jsons=json.loads(get_json_info(matche(url)))
                    searchList=jsons['props']['initialState']['search']['searchResults'][2]['list']
                except Exception as e:
                    return bot.send(event,str(e))
                headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.105 Safari/537.36','Referer': url}
                returnMsg=[]
                for item in searchList:
                    returnMsg.append(ForwardMessageNode(
                        message_chain=[
                            Image(base64=base64.b64encode(matche(item['studioLogo'],headers,'img')).decode()),
                            "[#"+str(searchList.index(item)+1)+"] "+str(item['studioName'])+'\nID: '+str(item['studioId'])+'\n室长: '+str(item['starMemberList'][0]['nickname'])+'\n成员数: '+str(item['userCount'])],
                            sender_id=1328387967,
                            sender_name='搜索界面'
                        
                    ))
                await bot.send(event,["胡梨找到结果啦！最多显示20条"])
                try:
                    await bot.send(event,Forward(node_list=returnMsg))
                except Exception as e:
                    return bot.send(event,str(e))
            else:
                await bot.send(event,["没有找到你想要的类型哦！输入“木屋查功能列表”了解用法！"])
    
    # 最新作品:
    @bot.on(GroupMessage)
    async def dailyRecommend(event: GroupMessage):
        if str(event.message_chain)=='最新作品':
            url='http://world.xiaomawang.com/w/explore?type=2&tagId=-1&page=1&pageSize=20'
            try:
                jsons=json.loads(get_json_info(matche(url)))
                findList=jsons['props']['initialState']['find']['findAllLists']['list']
            except Exception as e:
                    return bot.send(event,str(e))
            await bot.send(event,[
                "胡梨为您找到了最新发布的4个作品！",
                "\n[#1] "+str(findList[0]['title'])+'\n编号: '+str(findList[0]['compositionId']),
                "\n作者: "+str(findList[0]['userObject']['nickname'])+' (ID:'+str(findList[0]['userObject']['userId'])+')',
                "\n-----------------------",
                "\n[#2] "+str(findList[1]['title'])+'\n编号: '+str(findList[1]['compositionId']),
                "\n作者: "+str(findList[1]['userObject']['nickname'])+' (ID:'+str(findList[1]['userObject']['userId'])+')',
                "\n-----------------------",
                "\n[#3] "+str(findList[2]['title'])+'\n编号: '+str(findList[2]['compositionId']),
                "\n作者: "+str(findList[2]['userObject']['nickname'])+' (ID:'+str(findList[2]['userObject']['userId'])+')',
                "\n-----------------------",
                "\n[#4] "+str(findList[3]['title'])+'\n编号: '+str(findList[3]['compositionId']),
                "\n作者: "+str(findList[3]['userObject']['nickname'])+' (ID:'+str(findList[3]['userObject']['userId'])+')',
                "\n输入“木屋查功能列表”查看更多！"
            ])
            
            

    # 基本查询:
    
    @bot.on(GroupMessage)
    async def projectSearch(event: GroupMessage):
        if '查作品 ' in str(event.message_chain):
            urlType=""
            url=str(event.message_chain).split(" ")[1]
            if '/community/main/compose' in url:
                urlType='project'
            elif '/w/person/project/all/' in url:
                urlType='person'
    
            elif '666J' in str(url):
                url='https://world.xiaomawang.com/community/main/compose/'+str(url)
                urlType='project'
            else:
                url='http://world.xiaomawang.com/w/person/project/all/'+str(url)
                urlType="person"
            
            #initial
            headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.105 Safari/537.36','Referer': url}
            try:
                jsons=json.loads(get_json_info(matche(url)))
            except Exception as e:
                    return bot.send(event,str(e))
            if urlType=='project':
                try:
                    project=jsons['props']['initialState']['detail']['composeInfo']
                except Exception as e:
                    return bot.send(event,str(e))
                await bot.send(event,[
                    Image(base64=base64.b64encode(matche(project['coverKey'],headers,'img')).decode()),
                    "\n作品ID: "+str(project['id']),
                    "\n作品标题: "+str(project['title']),
                    "\n作者: "+str(project['userObject']['nickname'])+' (ID:'+str(project['userObject']['userId'])+')',
                    "\n创建日期: "+str(project['createTimeFormat']),
                    "\n发布日期: "+str(project['publishTimeFormat']),
                    "\n保存日期: "+str(project['saveTimeFormat']),
                    "\n观看数: "+str (project['statObject']['viewCount']),
                    "\n点赞数: "+str(project['statObject']['likeCount']),
                    "\n收藏数: "+str(project['statObject']['collectCount']),
                    "\n评论数: "+str(project['statObject']['commentCount']),
                    "\nMD5: "+str(os.path.basename(project['fileKey'])),
                    "\nURL: "+str(url),
                    "\n输入“木屋查功能列表”查看更多！"
                ])
            else:
                await bot.send(event,[At(event.sender.id)," 查询中....."])
                try:
                    projectList=jsons['props']['initialState']['person']['workList']['list']
                except Exception as e:
                    return bot.send(event,str(e))
                returnMsg=[]
                for item in projectList:
                    returnMsg.append(ForwardMessageNode(
                        message_chain=[
                            Image(base64=base64.b64encode(matche(item['coverKey'],headers,'img')).decode()),
                            "[#"+str(projectList.index(item)+1)+"] "+str(item['title'])+'\n编号: '+str(item['compositionId'])+'\n作者: '+str(item['userObject']['nickname'])+' (ID:'+str(item['userObject']['userId'])+')',
                            "\n观看数: "+str (item['statObject']['viewCount']),
                            "\n点赞数: "+str(item['statObject']['likeCount']),
                            "\n收藏数: "+str(item['statObject']['collectCount']),
                            "\n评论数: "+str(item['statObject']['commentCount'])
                        ],
                        sender_id=1328387967,
                        sender_name='搜索界面'
                    ))
                await bot.send(event,["胡梨找到结果啦！最多显示20条"])
                try:
                    await bot.send(event,Forward(node_list=returnMsg))
                except Exception as e:
                    return bot.send(event,str(e))

    @bot.on(GroupMessage)
    async def personSearch(event: GroupMessage):
        if '查用户 ' in str(event.message_chain):
            url=str(event.message_chain).split(" ")[1]
            if ('/w/person/project/all/' in url)==False:
                url='https://world.xiaomawang.com/w/person/project/all/'+str(url)
            headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.105 Safari/537.36','Referer': url}
            try:
                jsons=json.loads(get_json_info(matche(url)))
                person=jsons['props']['initialState']['person']['userData']
            except Exception as e:
                    return bot.send(event,str(e))
            if "studioName" in person['studioObject']:
                studioName=person['studioObject']['studioName']
                studioId=person['studioObject']['studioId']
            else:
                studioName='还没有加入工作室！'
                studioId=-1
            await bot.send(event,[
                Image(base64=base64.b64encode(matche(person['avatarImg'],headers,'img')).decode()),
                "\n用户名: "+str(person['nickname']),
                "\n个性签名: "+str(person['autograph']),
                "\n注册日期: "+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(person['createTime']))),
                "\n最后上线日期: "+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(person['updateTime']))),
                "\n粉丝数: "+str(person['statObject']['fansCount']),
                "\n被赞数: "+str(person['statObject']['likeCount']),
                "\n关注数: "+str(person['statObject']['followCount']),
                "\n作品数: "+str(person['statObject']['compositionCount']),
                "\n工作室: "+str(studioName)+' (ID:'+str(studioId)+')',
                "\nURL: "+str(url),
                "\n输入“木屋查功能列表”查看更多！"
            ])
    
    @bot.on(GroupMessage)
    async def studioSearch(event: GroupMessage):
        if '查工作室' in str(event.message_chain):
            url=str(event.message_chain).split(" ")[1]
            if ('/w/studio-home/' in url)==False:
                url='https://world.xiaomawang.com/w/studio-home/'+str(url)
            headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.105 Safari/537.36','Referer': url}
            try:
                jsons=json.loads(get_json_info(matche(url)))
                studio=jsons['props']['initialProps']['pageProps']['studioDetail']
            except Exception as e:
                    return bot.send(event,str(e))
            await bot.send(event,[
                Image(base64=base64.b64encode(matche(studio['studioLogo'],headers,"img")).decode()),
                "工作室名: "+str(studio['studioName']),
                "\n室长: "+str(studio['starMemberList'][0]['nickname'])+' (ID:'+str(studio['chiefId'])+')',
                "\n工作室标语: "+str(studio['studioSlogan']),
                "\n工作室公告: "+str(studio['studioNotice']),
                "\n工作室简介: "+str(studio['introduce']),
                "\n创建时间: "+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(studio['createTime']))),
                "\n最后更新时间: "+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(studio['updateTime']))),
                "\n作品数: "+str(studio['compositionCount']),
                "\n成员数: "+str(studio['userCount']),
                "\n收藏数: "+str(studio['collectCount']),
                "\nURL: "+str(url),
                "\n输入“木屋查功能列表”查看更多！"
            ])
        
    @bot.on(GroupMessage)
    async def help(event: GroupMessage):
        if str(event.message_chain)=="木屋查功能列表":
            await bot.send(event,[
                "小木屋信息查询 - V1.0.0",
                "\n-----------------------",
                "\n作者: @MarkChai",
                "\n帮助: ",
                "\n查作品 <作品URL or 作品编号>",
                "\n- 1.查询一个作品的信息。",
                "\n查作品 <个人主页URL or 个人主页ID>",
                "\n- 2.查询一个用户的前二十个作品。",
                "\n查用户 <个人主页URL or 个人主页ID>",
                "\n- 查询一个用户的信息",
                "\n查工作室 <工作室URL or 工作室ID>",
                "\n- 查询一个工作室的信息",
                "\n最新作品",
                "\n- 查询社区最新作品",
                "\n搜索用户 <用户名>",
                "\n- 搜索用户，显示前二十条结果",
                "\n搜索作品 <作品名>",
                "\n- 搜索作品，显示前二十条结果。",
                "\n搜索工作室 <工作室名>",
                "\n- 搜索工作室，显示前二十条结果。",
                "\n魔力测评 <作品URL or 作品编号>",
                "\n- 使用小木屋的魔力测评对作品进行测评。"
        ])
    bot.run()
