# xmw-searchbot
小码王社区查询QQ机器人

## 安装
本项目需要[Mirai](mamoe/mirai)以及[mirai-http-api](project-mirai/mirai-api-http)提供支持，请自行阅读[文档](https://github.com/mamoe/mirai/blob/dev/docs/ConsoleTerminal.md)进行配置。

本项目推荐使用Python3.6或Python3.7环境进行运行。

### 依赖

使用pip安装：

```shell
pip3 install yiri-mirai
pip3 install requests
pip3 install Beautifulsoup4
pip3 install urllib3
```
同时安装ASGI服务，只需要安装以下依赖中任意一个：
```shell
pip3 install uvicorn
# 或
pip3 install hypercorn
```

### 配置

进入`main.py`文件，修改第6~12行：
```python
#=====================
# 配置机器人账号信息
ACCOUNT = 123456789 #QQ号
VERIFY_KEY = '114514' #mirai-http-api密钥
HOST = 'localhost' #Mirai地址（一般情况下不需要修改）
PORT = 8080 #mirai-http-api端口
#=====================
```
如果你不熟悉mirai-http-api，请阅读[mirai-http-api文档](https://github.com/project-mirai/mirai-api-http/blob/master/README.md)

### 运行

```shell
python3 main.py
```

*请注意：结束程序QQ机器人将不会工作*
