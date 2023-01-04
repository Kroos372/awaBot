import json, time
import numpy as np

# 莫名其妙的编码问题，很让我头疼啊~
def dec(cont: str) -> str:
    if cont.startswith(u"\ufeff"):
        return cont.encode("utf8")[3:].decode("utf8")
    else:
        return cont
# 返回日期
def nowDay() -> str:
    now = time.localtime()
    return f"{now.tm_year}{now.tm_mon:0>2}{now.tm_mday:0>2}"

# 读取文件们
FILENAME = "hash.json"
with open("info.json", encoding="utf8") as f:
    info = json.loads(dec(f.read()))
with open("design.json", encoding="utf8") as f:
    designs = json.loads(dec(f.read()))
with open(FILENAME, encoding="utf8") as f:
    data = json.loads(dec(f.read()))
with open("userData.json", encoding="utf8") as f:
    userData = json.loads(dec(f.read()))
with open("reply.json", encoding="utf8") as f:
    replys = json.loads(dec(f.read()))
with open("answer.json", encoding="utf8") as f:
    answer = json.loads(dec(f.read()))

#命令前缀
PREFIX = ";"

# [0涩图开关, 1报时开关, 2休眠开关, 3当前日期]
sysList = [False, True, False, nowDay()]
# [0象棋开关, 1轮到谁, 2结束游戏的人, 3[红方, 黑方], 4当前棋盘]
CCList = [False, None, None, [None, None], []]
# [0真心话开关, 1{昵称：摇出的数字}, 2[玩游戏中的hash]]
truthList = [False, {}, []]
# [0炸弹数字, 1[在玩的人], 2轮到序号, 3初始最小值, 4初始最大值, 5是否在玩, 6本轮最小值, 7本轮最大值]
bombs = [0, [], 0, 1, 1000, False, 1, 1000]
# [0扑克开关, 1{在玩的人:[拥有的牌]}, 2轮到序号, 3当前牌堆, 4底牌, 5地主, 6是否在叫牌阶段, 7[玩家名称], 8谁拿地主牌, 9{叫牌人:叫几分}, 10本轮第一出牌的序号, 11上家的牌]
pokers = [False, {}, 0, [], [], None, False, [], None, {}, None, None]
# [0五子棋开关, 1轮到序号, 2[黑方, 白方], 3]
# gobang = [False, 0, []]
# 在这的变量和在sysList里的区别是，在这里的变量都不需要直接改变，只在原来基础上增删；
# 在sysList中的则需要，例如游戏中的hash和摇出的数字都会在结算中清空，储存在一个列表中就避免了各种莫名其妙的作用域问题
allMsg, afk, leftMsg, ignored, banned = [], {}, {}, userData["ignored"], userData["banned"]
userHash, userTrip, userColor, engUsers = {}, {}, {}, userData["engUsers"]
blackList, blackName, whiteList = userData["blackList"], userData["blackName"], userData["whiteList"]
meaningful = []
#常量
channel, nick, passwd, color = info["channel"], info["nick"], info["passwd"], info["color"],
owner, called = info["owner"], info["called"]
# 主人：我无所不能的卡密哒！
OWNER = info["ownerTrip"]

CLOLUMN, LETTERS = ["| \\ |1|2|3|4|5|6|7|8|9|", "|-|-|-|-|-|-|-|-|-|-|"], list("ABCDEFGHIJ")
RED, BLACK = ["==车==", "==马==", "==相==", "==士==", "==帥==", "==兵==", "==炮=="], ["車", "馬", "象", "仕", "將", "卒", "砲"]
# WHITE, GRAY = "O", "X"
CARDS = ['3', '4', '5', '6', '7', '8', '9', 'H', 'J', 'Q', 'K', 'A', '2']
JOKERS = ["小", "大"]
SORT = dict(zip(CARDS+JOKERS, range(15)))
PINIT = CARDS*4 + JOKERS
# 自定义回复，包含了主人对我的满满心意，诶嘿嘿~
RANDLIS = [
    [f"找{owner}去吧。", "早上好！", "干什么?", "想下象棋吗？发送菜单看看？", "好好好~", "有什么吩咐~", "sender寂寞了吧", "发送菜单了解我的功能~", "怎么了？",
    "![](https://i.gyazo.com/eab45f465ed035c58c8595159eb9f6e2.gif)", "在这在这~", "@sender", "Hello", "Yes?"], #0
    replys[0], #1
    ["sender最可爱了", "sender棒棒", "sender是小天使", "/shrug", "是这样的", "你说得对", "违法内容，请终止当前话题。", "？"], #2
    ["hi, joiner", "hello, joiner", "joiner!", "Sup", "joiner! Hows ur day?", "出现了，joiner!", "这不是joiner吗~", "你好诶，joiner，新的一天也要加油哦！",
     "Welcome, joiner!", "好久不见啊，joiner~", "早上好，joiner!"], #3
    ["没活了可以咬打火机。", "理论上说，所谓的无聊都只是懒而已。", "学习，做一些自己感兴趣的事情？", "错误的", "给大家整个活：", "发电发电！", "紫砂吧。", "好好好", "陪我玩。", "真的假的"], #4
    replys[1], #5
    ["也没有那么傻", "知道了知道了", "没想到sender意外地有自知之明呢", "啊对对对", "智将（确信）", "没活整可以咬打火机。", "正确的", "我就知道" ], #6
    ["有",  "嗯（冷漠）", "没", "sender不会是寂寞了吧", "人……人……有吧？", "你叫一声？" ], #7
    ["拜", "bye~", "下次再来啊~", "等着你哦", "别忘了这里哦~", "see u" ], #8
    ["hello~", "hi", "欢迎", "今天过得怎么样", "还好吗", "你好", "whats up", "Good morning", "早上好！", "sender啊，好好", "sender~"], #9
]
del replys
RULE = "\n".join([
    "好、的，听清楚规则了哦~",
    "如你所见，棋盘一共有10行，从上到下依次为ABCDEFGHIJ；又有9列，从左到右依次为123456789。",
    "用这个方法可以表示出棋盘上的任何位置，例如左上角的马，其坐标应为A2。",
    "发送`@bot名 旧位置 新位置`移动棋子，例如`@awaBot C2 C3`可以将左上角的炮向右挪动一格。",
    "明白了吗？开始吧~",
    "温馨提示：使用暗色主题棋盘显示效果更佳~"
])
CCMENU = "\n".join([
    f"/w sender 使·用·说·明\\~\n哟，这不是sender吗，我是来自阿瓦国的狂热象棋Bot{called}哦，很高兴认识你\\~",
    "以下是我能做的事情，如果能帮上你的忙的话我会很高兴的！~~请随意使用我吧~~",
    "`@Bot名 加入游戏`：加入游戏或者创建一个游戏\\~",
    "`@Bot名 结束游戏`：结束游戏，如果你执意要这么做的话……",
    "`@Bot名 帮助`：显示这一段话~~，也就是套娃啦！~~",
    "芜湖，就这么多了，虽然我也知道我很棒不过毕竟人的能力是有限的嘛~但放心，我每天都在努力学习，也许明天，下个小时或者下一分钟，\
    在你不注意的时候，我就有新功能啦，ᕕ( ᐛ )ᕗ\\~"
])
BOMBMENU = "\n".join([
    "/w sender 数字炸弹——",
    "规则很简单，在一个给定的范围中设某个数字为「炸弹」，玩家轮流猜数缩小范围，直到某人猜到炸弹。以下是关于数字炸弹的命令：",
    "`bomber` : 加入数字炸弹游戏！",
    "`*bom` : 让机器人加入！",
    "`开始b` : 开始数字炸弹，至少需要两个人。",
    "`结束b` : 结束数字炸弹……",
    "`b 数字` : 猜数。",
    "就是这么多了，祝你好运，ᕕ( ᐛ )ᕗ\\~"
])
POKERMENU = "\n".join([
    "/w sender 斗地主...",
    "poker: 开始或加入一场斗地主，满三人后自动开始。",
    "poker t: 在开始之前退出对局。",
    "p 牌: 出牌，具体规则请查看出牌规则。",
    f"@{nick} 结束p: 在对局中结束游戏。",
    f"@{nick} 扑克规则: 获取扑克的出牌规则。",
])
POKERRULE = "\n".join([
    "/w sender 游戏规则请自行参考[此处](https://baike.baidu.com/item/%E4%B8%89%E4%BA%BA%E6%96%97%E5%9C%B0%E4%B8%BB/9429860)，要注意的是这里用==H==代表==10==，==小==代表小王，==大==代表大王。以下是出牌规则：",
    "使用==p 牌==出牌，例如==p 1==, ==p J==，大小写均可；",
    "使用==p .==跳过回合、==p check==查看自己目前的牌；",
    "多张相同面值的牌间使用==牌*张数==，例如==p 3*2==，==p 4*3==；",
    "顺子使用==最小牌-最大牌==，例如==p 4-8==，==p 6-A==；",
    "双顺或三顺使用==最小-最大*张数==，例如==p 3-5*2==，==p 4-5*3==；",
    "三带二、飞机等带的对子中不使用==*==，例如==p K*3 77==，==p 8-9*3 33 44==",
    "王炸直接发送==p 王炸==即可；",
    "剩余的就将这两种组合，不同组别用空格隔开即可，例如==p 4-5*3 7 9== ==p 7*4 99 HH==……",
    "玩得开心~"
])
CINIT=np.array([
    [RED[0], RED[1], RED[2], RED[3], RED[4], RED[3],RED[2], RED[1], RED[0]],
    ["&ensp;"]*9,
    ["&ensp;", RED[6], "&ensp;", "&ensp;", "&ensp;", "&ensp;", "&ensp;", RED[6], "&ensp;"],
    [RED[5], "&ensp;", RED[5], "&ensp;", RED[5], "&ensp;", RED[5], "&ensp;", RED[5]],
    ["&ensp;"]*9,

    ["&ensp;"]*9,
    [BLACK[5], "&ensp;", BLACK[5], "&ensp;", BLACK[5], "&ensp;", BLACK[5], "&ensp;", BLACK[5]],
    ["&ensp;", BLACK[6], "&ensp;", "&ensp;", "&ensp;", "&ensp;", "&ensp;", BLACK[6], "&ensp;"],
    ["&ensp;"]*9,
    [BLACK[0], BLACK[1], BLACK[2], BLACK[3], BLACK[4], BLACK[3], BLACK[2], BLACK[1], BLACK[0]],
])
# GINIT = np.array([["&ensp;"]*15]*15)

MENUMIN = "\n".join([
    "菜单：",
    "普通用户：",
    f">{PREFIX}hasn, {PREFIX}hash, {PREFIX}code, {PREFIX}colo, {PREFIX}left, {PREFIX}peep, {PREFIX}welc, {PREFIX}last, " +
    f"{PREFIX}lost, {PREFIX}unlo, {PREFIX}prim, {PREFIX}rand, {PREFIX}repl, r, rprime, letter, 真心话, 涩图, @{nick} 象棋, " + 
    f"@{nick} 数字炸弹, @{nick} 斗地主",
    ">",
    "白名单用户：",
    ">0setu, 0time, 0addb, 0delb, 0kill, 0bans, 0uban, 0addn, 0deln, 0bcol, 0setb",
    ">",
    "发送==菜单.max==可以获得详细菜单（消息较长）。"
])
MENU = [
    "功能菜单\\~",
    "|命令|介绍|例|备注|",
    "|:-:|:-:|:-:|:-:|",
    f"|{PREFIX}peep 整数|浏览历史的X条消息|{PREFIX}peep 10|目前最多存377条~~，因为不想存太多而且存太多大概也发不出去吧~~|",
    f"|{PREFIX}colo 昵称|查看某人的颜色值 | {PREFIX}colo @{nick}| `@`可省略~~用colo而非color只是为了让所有命令字数一致~~|",
    f"|{PREFIX}hash 昵称|查看某人的历史昵称 | {PREFIX}hash @{nick}| `@`可省略|",
    f"|{PREFIX}code hash码| 查看某hash的历史昵称| {PREFIX}code abcdefg | 可使用`/myhash`查看自己的hash码|",
    f"|{PREFIX}left 昵称 文本|留言，在昵称上线时将您的话传达给ta|{PREFIX}left @{nick} hello world|借鉴自[3xi573n7ivli5783vR](?math)，`@`可省略~~如果在你要留言的人上线之前bot下线了的话肯定就没办法……~~|",
    f"|{PREFIX}welc 文本| 为当前识别码设置/清除欢迎语 | {PREFIX}welc ᕕ( ᐛ )ᕗ | 自eebot。按照识别码储存!要清除的话单独发送{PREFIX}welc |",
    f"|{PREFIX}last 文本| 留下一句话 | {PREFIX}last v我50 | 作用类似于留言，最好在自己要走或afk的时候用。需要识别码。 |",
    f"|{PREFIX}lost 昵称| 查看某人留下的话 | {PREFIX}lost @{owner} | `@`可……你知道我要说什么 |",
    f"|{PREFIX}unlo 昵称| 清除留下的话 | {PREFIX}unlt @{owner} | 请求清除者的识别码须和留言者一样。用完就扔是个好习惯哦~ |",
    f"|{PREFIX}prim 正整数 | 分解质因数 | {PREFIX}prim 1234567890123 | 最多十三位数，超过会被自动截断 |",
    f"|{PREFIX}rand 正整数|获取X个极为抽象的随机设计|{PREFIX}rand 1|来自[这里](https://protobot.org/#zh)，一次最多十件。 |",
    f"|{PREFIX}repl 提问 回答|自定义阿瓦娅回答|{PREFIX}repl 1+1 2|支持正则表达式，提问中请使用`~`代表空格，`\\~`代表\\~。|",
    # "|insane| 发电实录 |insane| \\ |",

    "|afk|标记自己为挂机状态，标记后发言时自动解除|afk 吃饭|借鉴自bo_od|",
    "|r|获取随机数|r 100|r后面若加空格与整数则代表取 1\\~该数字(含)或该数字（含）\\~1间的随机数，否则取1\\~1000间。|",
    "|rollen|反复r，将r到的数作为最大值继续r，直到1|rto1 9999|后面加参数表示初始最大值，如果不设则为1000|",
    f"|rprime|获取随机数并分解质因数|rprim 999|规则与{PREFIX}prim, r相同~~质因数分解玩魔怔了~~|",
    "|letter|获取一封信|letter|来自[这里](https://www.thiswebsitewillselfdestruct.com/)，很适合无聊的时候看，只不过大多是英语|",
    "|listwh/bn/bl/ig|列出白名单/黑名单/忽略名单etc.|listbn| \\ |",
    f"|@bot名 文本|聊天|@{nick} help| API来自[青云客](https://api.qingyunke.com/)~~也有一部分是我主人亲笔写的~~|",
    f"|@bot名 象棋|象棋bot的帮助|@{nick} 帮助|象棋！|",
    f"|@bot名 数字炸弹| 数字炸弹bot的帮助|@{nick} 数字炸弹|好玩|",
    "|menu|Return English version of this menu. |menu|\\|",
]
MENUFT = [
    "其他命令：涩图、真心话，功能和名字一样所以就没单独列出来（）",
    "Bot源码请查看[这里](https://github.com/Kroos372/awaBot/)。",
    "注： 我可能会因为某些~~疯狂的人为~~原因卡出一些不可逆的bug，届时只能重启，所以请酌情使用呢，感谢您的配合\\~"
]
MENUSP = [
    "|菜单w|白名单用户的特殊菜单|菜单w| \\ |",
] + MENUFT
MENUSSP = [
    "|菜单\\~|主人的特殊菜单\\~|菜单\\~| 最后的波浪线也是命令的一部分哦 |",
] + MENUSP
ADMMENU = [
    "白名单用户的特殊服务~",
    "|命令|介绍|例|备注|",
    "|:-:|:-:|:-:|:-:|",
    "|0setu 0或1|涩图开关，0关1开|0setu 1| 实际上是int后面的语句 |",
    "|0time 0或1|报时开关，同上|0time 0|同上|",
    "|0kill 昵称| 使用LaTeX对某人进行刷屏并使用ModBot的kick |0kill qaq|需要注意的是这只有在对方开启LaTeX的情况下才有用、|",
    "|0bans 昵称| 封禁某人，和kill一样，但会持续 | 0bans abcd | \\ |",
    "|0uban 序号| 取消封禁某人 | 0uban abcd | \\ |",
    f"|0addb 昵称|添加黑名单用户（输入的是昵称，添加的是hash）|0addb {owner}| ==addb==lacklist user|",
    f"|0delb 昵称|删除黑名单用户|0delb {owner}| \\ |",
    f"|0addn 昵称|添加黑名单昵称|0addn {owner}| 同上 |",
    f"|0deln 昵称|删除黑名单昵称|0deln {owner}| 同上 |",
    "|0bcol 颜色值|修改bot颜色值|0bcol aaaaaa| \\ |",
    "|0setb 最小值 最大值|设置数字炸弹的最小值与最大值|0setb 1 100| \\ |",
]
OWNMENU = "\n".join(["只为主人提供的秘密服务❤~"] + ADMMENU[1:] + [
    f"|0addw 识别码|添加白名单用户（识别码）|0addw {OWNER}| ==addw==hitelist user|",
    f"|0delw 识别码|删除白名单用户|0delw {OWNER}| \\ |",
    f"|0igno 昵称|不记录某人消息|0igno @{owner}| `@`，省略，懂？最好在真心话的时候用。 |",
    f"|0unig 昵称|记录某人信息|0unig @{owner}| 同上 |",
    "|0stfu 0或1| 1为休眠，使bot只回复白名单用户，0为取消休眠 | 0stfu | 刷屏什么的去死好了。 |",
    "|0remake| 重启 |0remake|restart太长了|",
    "|0chkr 问题 序号|查看某个问题的回答或第序号个回答，序号可选。|0chkr 什么鬼| ==ch==ec==k== ==r==eply |",
    "|0delr 问题 序号|删除某个问题的回答或第序号个回答，序号可选。|0delr 什么鬼| \\ |",
    "其他：自己去他妈看源码去！"
])
ENGMENU = [
    "Here are all functions menu:",
    "|Command|Description|e.g.|Note|",
    "|:-:|:-:|:-:|:-:|",
    f"|{PREFIX}peep <integers>|View last <integers> history messages| {PREFIX}peep 10| <integers> up to 377.|",
    f"|{PREFIX}colo <nickname>| Return <nickname>'s hex color value. | {PREFIX}colo @{nick}| `@` can be omitted.|",
    f"|{PREFIX}hash <nickname>| Return history nicknames of <nickname>. | {PREFIX}hash @{nick}| `@` can be omitted. |",
    f"|{PREFIX}code <hashcode>| Return history nicknames of <hashcode>. | {PREFIX}code abcdefg | Use `/myhash` to check your hashcode.|",
    f"|{PREFIX}left <nickname> <message> | Leave a message for <nickname>, <message> will be whispered to him/her when he/she join" +
    f"the channel|{PREFIX}left @{nick} hello world| `@` can be omitted. |",
    f"|{PREFIX}welc <message> | Set welcome text for current trip. | {PREFIX}welc ᕕ( ᐛ )ᕗ | Trip is a must, send `{PREFIX}welc` to cancel. |",
    f"|{PREFIX}last <message> | Leave a message that everyone can check. | {PREFIX}last I'll be back tomorrow. | Trip is a must. |",
    f"|{PREFIX}lost <nickname> | Check the message that <nickname> left. | {PREFIX}lost @{owner} | `@` can be... u know what im going to say :D |",
    f"|{PREFIX}unlo <nickname> | Clear the message that u left by `{PREFIX}last` | {PREFIX}unlt @{owner} | <nickname>'s trip must be as same as yours. |",
    f"|{PREFIX}prim <digit> | Decomposing prime factors for <digit>. | {PREFIX}prim 1234567890123 | Up to 13 digits, more than that will be automatically cut off. |",
    f"|{PREFIX}rand <digit>|Get <digit> kinda random designs|{PREFIX}rand 1|API from [HERE](https://protobot.org/#zh), <digit> up to 10|",

    "|afk| Mark yourself as afk, automatically unmark the next time you say sth. |afk sleeping| AFK(Away From Keyboard) |",
    "|r| Get a random number. |r 100| if r followed by a space and an integer, return a random number between 1 to that integer" +
    "(include) or that integer(include) to 1, else return random number between 1 to 1000. |",
    f"|rprime| Decomposing prime factors for a random number. |rprim 9999| Rules are as same as `r` + `{PREFIX}prim` |",
    "|rollen| Repeatedly generate random numbers until 1. | rollen 9999 | Rules same. |",
    "|listwh| List whitelist trips. | listwh |==list wh==itelist users|",
    "|listbl| List blacklist trips. | listbl | \\ |",
    f"|@<botname> <message> | Chat in Chinese with bot. | @{nick} help | API from [HERE](https://api.qingyunke.com/). |",
    f"|@<botname> 象棋| Help message of Chinese Chess Bot. | @{nick} 帮助| \\ |",
    f"|@<botname> 数字炸弹| Help message of Number Bomb Bot. (A kinda game) | @{nick} 数字炸弹| \\ |",
    "|真心话| Start a Truth ~~or Dare~~ game. | 真心话 | \\ |",
    "|菜单| Return Chinese version of this menu. | 菜单 | \\ |",
    "|涩图| Beatiful pictures XD | 涩图 | API from [Lolicon](https://api.lolicon.app/). |",
    "| engvers | Use english version for current trip (All reply *for you* will be in English)| engvers | Not supported now, to be continue...| ",
]
ENGMENUFT = [
    "This bot is open-sourced, you can view all source code [HERE](https://github.com/Kroos372/awaBot/).",
]
ENGMENUSP = [
    "|menuw| special menu for whitelist users | menuw | \\ |",
] + MENUFT
ENGMENUSSP = [
    "|menu~| special menu for owner\\~| menu\\~| `~` is also a part of command. |",
] + MENUSP
ENGADMMENU = [
    "Special whitelist user~",
    "|Command|Description|e.g.|Note|",
    "|:-:|:-:|:-:|:-:|",
    "| 0setu 0 or 1 | Picture switch | 0setu 1 | `int()` is what program actually done |",
    "| 0time 0或1 | Chime switch | 0time 0 | Ibid |",
    f"| 0addb <nick> | Add blacklist user.(hash) |0addb {owner}| \\ |",
    f"| 0delb <nick> | Delete blacklist user. |0delb {owner}| \\ |",
    f"|0addn <nick> | Add blacklist name.|0addn {owner}| \\ |",
    f"|0deln <nick> |Delete blacklist name.|deln {owner}| \\ |",
    f"| 0bcol <hex color value> | Change bot's color |0bcol aaaaaa| \\ |",
]
ENGOWNMENU = "\n".join(["Only for master❤~"] + ENGADMMENU[1:] + [
    f"|0addw <trip>|Add whitelist user|0addw {OWNER}| \\ |",
    f"|0delw <trip>|Delete whitelist user|0delw {OWNER}| \\ |",
    f"|0igno <nickname> | Stop recording sb.'s message. |0igno @{owner}| `@` can be... |",
    f"|0unig <nickname>| Start to record sb.'s message. |0unig @{owner}| Ibid |",
    "|0stfu 0 or 1 | 1 means sleep, let bot not reply any messages, 0 cancel it. | 0stfu | \\ |",
    "|0bans <nick>| Ban someone by LaTeX. | 0bans abcd | \\ |",
    "|0uban <nick> | Unban someone. | 0uban abcd | \\ |",
    "|0remake| Restart. |0remake| \\ |",
])
GAMEMENU = "\n".join([
    "真心话现在开始啦，发送*r*来获取随机数，*结算*来结算，*结束游戏*来结束游戏~",
    "以下是注意事项：",
    "1\\.愿赌服输，所谓的**真心话**的意思是什么，参与了就不能后悔了，",
    "2\\.不要把游戏当成拷问，提的问题请在能够接受的范围内，",
    "3\\.尺度请自行把握，不用过于勉强自己也不要勉强他人，感到不适可以要求对方更换问题，",
    "4\\.玩得愉快。",
    f"PS: ***实在***没活整了可以发送==@{nick} 提问==获取些离谱小问题，当然你要是把这当成功能的一部分的话我就\\*优美的中国话\\*",
    f"PSS: 获取随机数只能用*r*，而不是*r 数字*，后者在真心话中会被忽略。"
])

def bom()->str:
    if not bombs[5]:
        if not nick in bombs[1]:
            bombs[1].append(nick)
            return "已成功添加机器人进入游戏！"
        else: return "机器人已经加入过了！"
    else: return "这局已经开始了，等下局吧~"
def truth()->str:
    if not truthList[0]:
        truthList[0] = True
        return GAMEMENU
    else: return "已经在玩了哦╮(╯_╰)╭"
def atLast()->str:
    if truthList[0]:
        if len(truthList[2]) < 2: return "有句话叫什么，一个巴掌拍不响(°o°；)"
        else:
            sort = sorted(truthList[1].items(), key=lambda x: x[1])
            loser, winner = sort[0], sort[-1]
            fin = "\n".join([f"本轮参与人数：{len(truthList[1])}。",f"最大：{winner[1]}（{winner[0]}），",
                f"最小：{loser[1]}（{loser[0]}）。", f"@{winner[0]} 向@{loser[0]} 提问，@{loser[0]} 回答。"])
            truthList[1] = {}
            truthList[2] = []
            return fin
    else: return "真心话还没开始你在结算什么啊(▼皿▼#)"
def endTruth()->str:
    if truthList[0]:
        truthList[0] = False
        return "好吧好吧，结束咯(一。一;;）"
    return "真心话还没开始你在结束什么啊(▼皿▼#)"

LINE = {
    # 纪念零姬……
    "0.0": ["0.0.0"],
    "贴贴": ["贴贴sender~"],
    "#精神状态": ["ᕕ( ᐛ )ᕗ", "良好，谢谢", "🤔", "哇啊啊啊！"],
    "engvers": ["To be continue..."],
    "6": ["6", "9", "36", "还得是你", "陆"],
    "？": ["？", "不对劲", "你在疑惑什么", "¿", "..."],
    "我是傻逼": RANDLIS[6],
    "hi": RANDLIS[9],

    "涩图": lambda: colorPic() if sysList[0] else "害，别惦记你那涩涩了。",
    "listwh": lambda: f"当前白名单识别码：{'，'.join(whiteList)}",
    "listbn": lambda: f"当前黑名单昵称：{'，'.join(blackName)}",
    "listbl": lambda: f"当前黑名单hash：{'，'.join(blackList)}",
    "listig": lambda: f"当前被忽略的用户：{'，'.join(ignored)}",
    "listba": lambda: f"当前被封禁的hash：{'，'.join(banned)}",
    "真心话": truth,
    "结算": atLast,
    "结束游戏": endTruth,
    "*bom": bom,
}
INLINE = {
    "有人吗": RANDLIS[7],
    "拜拜|bye": RANDLIS[8],
    "无聊": RANDLIS[4],
    "awa": ["qaq", "qwq", "qwp", "ovo", ";a;", "TAT", "QAQ", "\\>_<", "@w@", "uwu"],
}

# 仿rate-limiter
records, halflife, threshold = {}, 25, 12

def now()->int:
    return int(time.time())
# 获取信息
def search(name: str)->dict:
    record = records.get(name)
    if not record:
        record = records[name] = {"time": now(), "score": 0, "warned": False}
    return record
# 监测与增加刷屏分（？）
def frisk(name: str, delta: float):
    record = search(name)
    score = record["score"]
    # 使分数随时间衰减，半衰期(与上次发言相差halflife秒时)为0.5
    record["score"] *= 2**(-(now()-record["time"])/halflife)
    # 低于阈值一半时取消警告
    if record["warned"] and score < (threshold/2):
        record["warned"] = False
    # 加分（？）
    record["score"] += delta
    record["time"] = now()
    # 分数达到阈值(threshold)时被rl
    if score >= threshold:
        return "limit"
    # 超过阈值三分之二时警告
    elif score >= (threshold/3*2) and not record["warned"]:
        record["warned"] = True
        return "warn"
    return None