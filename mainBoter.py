#coding=utf-8
from const import *
import websocket, ssl, requests, re, threading, traceback, sys, os, random

# 存入记忆中！
def writeJson(filename, datas):
    with open(filename, "w", encoding="utf8") as f:
        json.dump(datas, fp=f, ensure_ascii=False, indent=2)
# 名字提纯
def namePure(name: str) -> str: return name.replace("@", "").replace(" ", "")
# 内容转换
def textPure(text: str) -> str: return text.replace("\\~", "~").replace("~", " ")
# 获取沙雕小设计
def randomDesign(num: int=1) -> str:
    full = []
    if num > 10:
        return "最多一次性获取10个(〃｀ 3′〃)"
    elif num < 1:
        return "最少获取一个(〃｀ 3′〃)"
    for i in range(num):
        item = random.choice(designs["items"])
        const = random.choice(designs["constraints"])
        prepend = random.choice(designs["prepend"])
        if const[-1] == "的":
            full.append(f"{prepend}{const}{item}")
            continue
        full.append( f"{const}{prepend}{item}")
    return "，\n".join(full)
# 分解质因数！这是我的数学极限了，呜呜……
def getPrime(i, factors) -> list:
    if i == 1: return ["没法分解啊啊啊啊(+﹏+)"]
    for x in range(2, int(i**0.5 + 1)):
        if i % x == 0:
            factors.append(str(x))
            getPrime(int(i / x), factors)
            return factors
    factors.append(str(i))
    return factors
# r来r去
def rollTo1(maxNum: int=1000) -> str:
    road =  []
    while True:
        ran=random.randint(1, maxNum)
        road.append(str(ran))
        if ran != 1: maxNum = ran
        else: break
    return f"{'，'.join(road)}：{len(road)}"
def hashByCode(code: str) -> str:
    try: return "，".join(data[code])
    except: return "不存在这个hash码(◐_◑)"
def hashByName(name: str, now: bool=False) -> str:
    if now:
        try: return hashByCode(userHash[name])
        except: return "此人当前不在线( ⊙ o ⊙ )"
    else:
        l = []
        for i in data.values():
            if name in i:
                text = "，".join(i)
                l.append(text.replace("_", "\\_"))
        l = list(set(l))
        for i, v in enumerate(l):
            l[i] = f"{i+1}\\. "+l[i]
        return "\n".join(l) or "没有这个名字！"
# 一天不涩涩，癫痫发作作
def colorPic() -> str:
    setu = requests.get("https://api.lolicon.app/setu/v2").json()["data"][0]
    # 过滤离谱关键词
    tags = [i for i in setu["tags"] if not "乳" in i and not "魅" in i and\
    not "内" in i and not "尻" in i and not "屁" in i and not "胸" in i]
    url = setu["urls"]["original"]
    title = setu["title"]
    author = setu["author"]
    return f"{url}\n标题：{title}\n标签：{','.join(tags)}\n作者：{author}"
# 随便搞搞
def getLetter() -> str:
    response = requests.get("https://www.thiswebsitewillselfdestruct.com/api/get_letter").json()
    if response["code"] == "200": return response["body"]
    else: return "出错啦，请稍后再试(◐_◑)"
# 结束
def endBomb():
    bombs[5], bombs[2], bombs[1] = False, 0, []
    bombs[6], bombs[7] = bombs[3], bombs[4]
# 判断数字与更新
def bombRule(chat, num=None):
    old = bombs[1][bombs[2]]
    if old == nick:
        num = random.randint(bombs[6], bombs[7])
    if bombs[6] > num or bombs[7] < num:
        return chat.sendMsg(f"不符合规则，数字必须在{bombs[6]}到{bombs[7]}之间！（含两边）")
    elif bombs[0] > num:
        bombs[6] = num + 1
    elif bombs[0] < num:
        bombs[7] = num - 1
    else:
        endBomb()
        return chat.sendMsg(f"炸弹炸到{old}了！")
    bombs[2] = (bombs[2] + 1) % len(bombs[1])
    player = bombs[1][bombs[2]]
    chat.sendMsg(f"{old}没有踩中！\n现在炸弹范围为{bombs[6]}到{bombs[7]}，轮到@{player} 了！")
    if player == nick:
        bombRule(chat)
# 我该如何回复大家呢？
def reply(sender: str, msg: str) -> str:
    rans = random.randint(1, 10)
    if rans > 4:
        for k, v in answer.items():
            if re.search(k, msg):
                if v: return "&#8205;" + random.choice(v).replace("sender", sender).replace("called", called)
                else: break
    cont = requests.get(f"https://api.qingyunke.com/api.php?key=free&msg={msg}")
    return cont.json()["content"].replace("菲菲", called).replace("{br}", "\n")\
    .replace("help", "==@bot名 help==，==菜单==或==@bot名 帮助==")
# 扑克有关
def landonwer(chat, sender: str): 
    pokers[5] = sender
    pokers[6] = False
    pokers[10] = pokers[2]
    pokers[2] = pokers[7].index(pokers[5])
    pokers[1][sender] += pokers[4]
    pokers[1][sender].sort(key=lambda x: SORT[x])
    cards = " ".join(pokers[1][sender])
    chat.sendMsg(f"{' '.join(pokers[4])}是底牌，{sender}是地主。\n游戏开始，地主@{sender} 先出，发送==@{nick} 扑克规则==可以查看出牌规则哦；")
    chat.sendMsg(f"/w {sender} 以下是您的牌：{cards}")
def passLand(chat, sender: str):
    pokers[2] = (pokers[2]+1)%3
    if pokers[2] == pokers[10]:
        landonwer(chat, pokers[7][pokers[2]])
def sameLen(seq) -> bool:
    try:
        length = len(seq[0])
        for i in seq[1:]:
            if len(i) != length or len(set(i))!=1 or not seq[0] in SORT : return False
        return True
    except: return False
def endPoker():
    pokers[0], pokers[1], pokers[2] = False, {}, 0
    pokers[4], pokers[9], pokers[11] = [], {}, None
def pkReply(chat, msg: str, sender: str):
    msg = msg.upper()
    # 叫牌阶段
    if pokers[6]:
        if msg[:2] == "1 ":
            try:
                point = int(msg[2])
                if not point in [1, 2, 3]: raise Exception
                elif point == 3:
                    landonwer(chat, sender)
                else:
                    for i in pokers[9].values():
                        if i >= point:
                            return chat.sendMsg("叫的数字必须比前面的大！")
                    pokers[9][sender] = point
                    pokers[10] = pokers[2]
                    passLand(chat, sender)
                    chat.sendMsg(f"{sender}叫出了{point}点，轮到@{pokers[7][pokers[2]]} ")
            except: chat.sendMsg("命令错误，请重新确认后再试;")
        elif msg[:1] == "0":
            passLand(chat, sender)
            chat.sendMsg(f"{sender}不叫，轮到@{pokers[7][pokers[2]]} ")
        else: chat.sendMsg("命令错误，啊啊啊")
    # 出牌阶段
    else:
        # 跳过
        if msg == ".":
            pokers[2] = (pokers[2]+1)%3
            if pokers[2] == pokers[10]:
                pokers[11] = None
                chat.sendMsg(f"所有玩家都要不起，@{pokers[7][pokers[2]]} 继续出牌。")
            else:
                chat.sendMsg(f"{sender}跳过，轮到@{pokers[7][pokers[2]]} 。")
        elif msg == "CHECK":
            chat.sendMsg(f"/w {sender} 以下是您的牌：{' '.join(pokers[1][sender])}")
        else:
            senderCards = pokers[1][sender]
            # 本轮第一发
            if pokers[11] is None:
                # 单张
                if msg in SORT and msg in senderCards:
                    senderCards.remove(msg)
                # 对子或三张或四张
                elif re.match(r"^[2-9AHJQK]\*[234]$", msg):
                    if senderCards.count(msg[0])>=int(msg[-1]):
                        for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                    else: return chat.sendMsg("牌数不足！")
                # 顺子
                elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]$", msg):
                    start, end = CARDS.index(msg[0]), CARDS.index(msg[-1])
                    if (end-start) >= 4:
                        for i in CARDS[start:end+1]:
                            if not i in senderCards:
                                return chat.sendMsg("拥有的牌不够！")
                        for i in CARDS[start:end+1]:
                            senderCards.remove(i)
                    else: return chat.sendMsg("顺子最少五个！")
                # 三带一、三带二
                elif re.match(r"^[2-9AHJQK]\*3 [2-9AHJQK]{1,2}$", msg):
                    mult = len(msg.split()[1])
                    if msg[-1] != msg[0]:
                        condition = senderCards.count(msg[0])>=int(msg[2]) and senderCards.count(msg[-1])>=mult
                    # 不会真有人出6*3 6这种的吧
                    else:
                        condition = senderCards.count(msg[0])>=(int(msg[2])+mult)
                    if condition:
                        for i in range(int(msg[2])): senderCards.remove(msg[0])
                        for i in range(mult): senderCards.remove(msg[-1])
                    else: return chat.sendMsg("牌数不足！")
                # 双顺、三顺
                elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*[23]$", msg):
                    start, end, mult = CARDS.index(msg[0]), CARDS.index(msg[2]), int(msg[-1])
                    if (end-start) >= (4-mult):
                        for i in CARDS[start:end+1]:
                            if senderCards.count(i) < mult:
                                return chat.sendMsg("拥有的牌不够！")
                        for i in CARDS[start:end+1]:
                            for _ in range(mult): senderCards.remove(i)
                    else: return chat.sendMsg("牌数不够，三顺最少两个，双顺最少三个;")
                # 四带二
                elif re.match(r"([2-9AHJQK])\*4 (?!.*?\1)(?:([2-9AHJQK])\2 ([2-9AHJQK])\3|[2-9AHJQK] [2-9AHJQK])$", msg):
                    array = msg.split()[1:]
                    if senderCards.count(msg[0])==4 and senderCards.count(array[0])>=len(array[0]) and senderCards.count(array[1])>=len(array[1]):
                        for _ in range(4): senderCards.remove(msg[0])
                        for i in "".join(array): senderCards.remove(i)
                    else: return chat.sendMsg("牌不够，;;;")
                # 飞机
                elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*3 $", msg[:6]):
                    start, end = CARDS.index(msg[0]), CARDS.index(msg[2])
                    if (end-start) < 1: return chat.sendMsg("牌数不够;")
                    else:
                        array = msg[6:].split(" ")
                        if sameLen(array) and len(array) == (end-start+1):
                            for i in CARDS[start:end+1]:
                                if senderCards.count(i) < 3: return chat.sendMsg("牌数不足;;;;")
                                if i in array or i+i in array: return chat.sendMsg("别搞")
                            for i in array:
                                if senderCards.count(i) < len(i): return chat.sendMsg("牌数不足;;;;")
                            for i in CARDS[start:end+1]:
                                for _ in range(3): senderCards.remove(i)
                            for i in array: senderCards.remove(i)
                        else: return chat.sendMsg("不符合规则！")
                # 6
                elif msg == "王炸":
                    if not ("大" in senderCards and "小" in senderCards): return chat.sendMsg("牌数不足！")
                    else:
                        senderCards.remove("大")
                        senderCards.remove("小")
                else: return chat.sendMsg("命令不正确或牌数不足，请查看规则后重试;")
            else:
                last = pokers[11]
                # 单张
                if last in SORT and msg in SORT and msg in senderCards:
                    if SORT[msg] <= SORT[last]: return chat.sendMsg(f"你的牌没有{last}大！")
                    senderCards.remove(msg)
                # 对子或三张或四张
                elif re.match(r"^.\*.$", last) and re.match(rf"^[2-9AHJQK]\*{last[-1]}$", msg):
                    if senderCards.count(msg[0])>=int(msg[-1]):
                        if SORT[msg[0]] <= SORT[last[0]]: return chat.sendMsg(f"你的牌没有{last}大！")
                        for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                    else: return chat.sendMsg("牌数不足！")
                # 顺子
                elif re.match(r"^.-.$", last) and re.match(r"^[3-9AHJQK]-[3-9AHJQK]$", msg):
                    start, end = CARDS.index(msg[0]), CARDS.index(msg[-1])
                    lstart, lend = CARDS.index(last[0]), CARDS.index(last[-1])
                    if (end-start) != (lend-lstart): return chat.sendMsg("牌数不符！")
                    elif lstart >= start: return chat.sendMsg(f"你的牌没有{last}大！")
                    for i in CARDS[start:end+1]:
                        if not i in senderCards:
                            return chat.sendMsg("拥有的牌不够！")
                    for i in CARDS[start:end+1]:
                        senderCards.remove(i)
                # 三带一、三带二
                elif re.match(r"^.\*3 .{1,2}$", last) and re.match(r"^[2-9AHJQK]\*3 [2-9AHJQK大小]{1,2}$", msg):
                    mult = len(msg.split()[1])
                    if msg[-1] != msg[0]:
                        condition = senderCards.count(msg[0])>=int(msg[2]) and senderCards.count(msg[-1])>=mult
                    # 不会真有人出6*3 6这种的吧
                    else:
                        condition = senderCards.count(msg[0])>=(int(msg[2])+mult)
                    if not condition: return chat.sendMsg("牌数不足！")
                    elif SORT[last[0]] >= SORT[msg[0]]: return chat.sendMsg(f"你的牌没有{last}大！")
                    elif len(msg.split()[1]) != len(last.split()[1]) or SORT[msg[0]] <= SORT[last[0]]: return chat.sendMsg("牌型不符合！")
                    for i in range(int(msg[2])): senderCards.remove(msg[0])
                    for i in range(mult): senderCards.remove(msg[-1])
                # 双顺、三顺
                elif re.match(r".-.\*.$", last) and re.match(rf"^[3-9AHJQK]-[3-9AHJQK]\*{last[-1]}$", msg):
                    start, end, mult = CARDS.index(msg[0]), CARDS.index(msg[2]), int(msg[-1])
                    lstart, lend = CARDS.index(last[0]), CARDS.index(last[2])
                    if (end-start) != (lend-lstart): return chat.sendMsg("牌数不符！")
                    elif lstart >= start: return chat.sendMsg(f"你的牌没有{last}大！")
                    for i in CARDS[start:end+1]:
                        if senderCards.count(i) < mult:
                            return chat.sendMsg("拥有的牌不够！")
                    for i in CARDS[start:end+1]:
                        for _ in range(mult): senderCards.remove(i)
                # 四带二
                elif re.match(r".\*4 .*", last) and re.match(r"([2-9AHJQK])\*4 (?!.*?\1)(?:([2-9AHJQK])\2 ([2-9AHJQK])\3|[2-9AHJQK大小] [2-9AHJQK大小])$", msg):
                    array = msg.split()[1:]
                    larray = last.split()[1:]
                    if senderCards.count(msg[0])==4 and senderCards.count(array[0])>=len(array[0]) and senderCards.count(array[1])>=len(array[1]):
                        if len(larray[-1]) != len(array[-1]): return chat.sendMsg("牌型不符！")
                        elif SORT[last[0]] >= SORT[msg[0]]: return chat.sendMsg(f"你的牌没有{last}大！")
                        for _ in range(4): senderCards.remove(msg[0])
                        for i in "".join(array): senderCards.remove(i)
                    else: return chat.sendMsg("牌不够，;;;")
                # 飞机
                elif re.match(r"^.-.\*3 $", last[:6]) and re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*3 $", msg[:6]):
                    start, end = CARDS.index(msg[0]), CARDS.index(msg[2])
                    lstart, lend = CARDS.index(last[0]), CARDS.index(last[2])
                    if (end-start) != (lend-lstart): return chat.sendMsg("牌数不符！")
                    elif SORT[last[0]] >= SORT[msg[0]]: return chat.sendMsg(f"你的牌没有{last}大！")
                    else:
                        array = msg[6:].split(" ")
                        if sameLen(array) and len(array) == (end-start+1):
                            for i in CARDS[start:end+1]:
                                if senderCards.count(i) < 3: return chat.sendMsg("牌数不足;;;;")
                                if i in array or i+i in array: return chat.sendMsg("别搞")
                            for i in array:
                                if senderCards.count(i) < len(i): return chat.sendMsg("牌数不足;;;;")
                            for i in CARDS[start:end+1]:
                                for _ in range(3): senderCards.remove(i)
                            for i in "".join(array): senderCards.remove(i)
                        else: return chat.sendMsg("不符合规则！")
                # 炸弹
                elif re.match(r"^[2-9AHJQK]\*4$", msg) and last != "王炸":
                    if senderCards.count(msg[0])<int(msg[-1]): return chat.sendMsg("牌数不足！")
                    for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                # 6
                elif msg == "王炸":
                    if not ("大" in senderCards and "小" in senderCards): return chat.sendMsg("牌数不足！")
                    else:
                        senderCards.remove("大")
                        senderCards.remove("小")
                else: return chat.sendMsg("牌型不符或牌数不足，请查看规则后重试;")

            pokers[11] = msg
            pokers[10] = pokers[2]
            pokers[2] = (pokers[2]+1)%3
            chat.sendMsg(f"{sender}出了{msg}，轮到@{pokers[7][pokers[2]]} 。")
            if not senderCards:
                if sender == pokers[5]: chat.sendMsg("地主获胜！")
                else: chat.sendMsg("农民获胜！")
                return endPoker()
            elif len(senderCards) < 4: chat.sendMsg(f"{sender}只剩{len(senderCards)}张牌了！")
# 日志日志
def logs(text: str):
    with open(f"log/{sysList[3]}.txt", "a+", encoding="utf8") as f:
        f.write(text+"\n")
def msgGot(chat, msg: str, sender: str, senderTrip: str):
    rans = random.randint(1, 134)
    this_turn = f"{sender}：{msg[:1024]}"
    command = msg[:6]
    logs(this_turn)
    # print(this_turn)

    if sender == nick: return

    if not senderTrip in whiteList:
        hash_ = userHash[sender]
        frisked = frisk(hash_, 0.9+len(msg)/256)
        if frisked == "warn":
            chat.sendMsg(f"@{sender} Warning!!!")
        elif frisked == "limit":
            chat.sendMsg(f"~kick {sender}")
            records[hash_]["score"] = threshold/2
            records[hash_]["warned"] = False
    if not sender in ignored:
        allMsg.append(this_turn)
        if len(allMsg) > 377: del allMsg[0]

    if userHash[sender] in blackList or sender in blackName: return

    mes = afk.get(sender)
    if mes is not None:
        del afk[sender]
        chat.sendMsg(f"@{sender} 不再{mes}了，欢迎回来~~摸鱼~~(\\*￣ω￣)")
    elif msg.lower() == "afk":
        mes = "AFK"
        afk[sender] = mes
        return chat.sendMsg(f"@{sender} {mes}了")
    elif msg[:4].lower() == "afk ":
        mes = msg[4:]
        afk[sender] = mes
        return chat.sendMsg(f"@{sender} 正在{mes}~~，加油~~ヾ(◍°∇°◍)ﾉﾞ")
    else:
        for user in afk:
            if f"@{user.lower()}" in msg.lower():
                chat.sendMsg(f"{user} 正在{afk[user]}，请不要打扰ta……(\\* \"･∀･)ﾉ――◎")
    if msg[0] == PREFIX:
        command = msg[1:6]
        if command == "hash ": chat.sendMsg(hashByName(namePure(msg[6:])))
        elif command == "hasn ": chat.sendMsg(hashByName(namePure(msg[6:]), True))
        elif command == "code ": chat.sendMsg(hashByCode(msg[6:]))
        elif command == "colo ":
            color = userColor.get(namePure(msg[6:]))
            if color is not None:
                if color: chat.sendMsg(color)
                else: chat.sendMsg("该用户还没有设置颜色(￢_￢)")
            else: chat.sendMsg("没有这个用户(╰_╯)#")
        elif command == "left ":
            lis = msg.split()
            if len(lis) < 3:
                chat.sendMsg("命令不正确！")
            elif lis[1] in chat.onlineUsers:
                chat.sendMsg(f"{lis[1]}在线着呢，为什么还要留言啊喂~")
            elif not re.search(r"^@{0,1}[a-zA-Z0-9_]{1,24}$", lis[1]):
                chat.sendMsg("昵称不合法！")
            else:
                leftMsg[time.time()] = [sender, namePure(lis[1]), "".join(lis[2:])]
                chat.sendMsg(f"@{sender}, {lis[1]}将会在加入时收到你的留言！~~如果那时我还在的话~~")
        elif command == "peep ":
            try:
                if msg[6:] == "0": raise ValueError
                array = msg.split(" ")
                if len(array)==2: 
                    want_peep = int(array[1])
                    if want_peep < 0: res = "\n".join(allMsg[:-want_peep])
                    else: res = "\n".join(allMsg[-want_peep:])
                    if len(res) >= 2048: chat.sendMsg(f"/w {sender} 一次查看的消息太多了，请把数字改小一点再试！")
                    else: chat.sendMsg(f"/w {sender} 懒得写提示语了：\n"+ res)
                elif len(array)>2: chat.sendMsg(f"/w {sender} 懒得写提示语了：\n"+ "\n".join(allMsg[int(array[1]):int(array[2])]))
                else: raise ValueError
            except ValueError: chat.sendMsg(f"/w {sender} 然而peep后面需要一个非零整数")
        elif command == "welc ":
            if senderTrip:
                userData["welText"][senderTrip] = msg[6:]
                writeJson("userData.json", userData)
                chat.sendMsg(f"为识别码{senderTrip}设置欢迎语成功了！")
            else: chat.sendMsg("您当前还没有识别码，请重进并在昵称输入界面使用==昵称#密码==设置一个！")
        elif command == "welc":
            if senderTrip in userData["welText"]:
                del userData["welText"][senderTrip]
                writeJson("userData.json", userData)
                chat.sendMsg(f"为识别码{senderTrip}清除欢迎语成功了！")
            else: chat.sendMsg("你还没有设置欢迎语！")
        elif command == "last ":
            if sender in userData["lastText"] and userData["lastText"][sender][0] != senderTrip:
                chat.sendMsg(f"已经有人为{sender}设置过留言了，请换一个名字！")
            elif senderTrip:
                userData["lastText"][sender] = [senderTrip, msg[6:]]
                writeJson("userData.json", userData)
                chat.sendMsg(f"为{sender}({senderTrip})设置留言成功了！记得及时清除哦！")
            else: chat.sendMsg("您当前还没有识别码，请重启并在昵称输入界面使用==昵称#密码==设置一个！")
        elif command == "lost ":
            name, dic = namePure(msg[6:]), userData["lastText"]
            if name in dic:
                chat.sendMsg(f"以下是{name}({dic[name][0]})的留言：\n{dic[name][1]}")
            else: chat.sendMsg("该用户还没有设置留言~")
        elif command == "unlo ":
            name, dic = namePure(msg[6:]), userData["lastText"]
            if name in dic:
                if senderTrip == dic[name][0] or senderTrip in whiteList:
                    del dic[name]
                    writeJson("userData.json", userData)
                    chat.sendMsg("留言已删除，感谢您的使用！")
                else: chat.sendMsg(f"您的识别码与被清除者不同！正确识别码应为{dic[name][0]}！")
            else: chat.sendMsg("此用户还没有设置留言~")
        elif command == "prim ":
            try:
                digit = msg[6:19]
                eq = "\\*".join(getPrime(int(digit), []))
                chat.sendMsg(f"{digit}={eq}")
            except ValueError: chat.sendMsg("请输入一个***正整数***啊啊啊啊(￢_￢)")
        elif command == "rand ":
            try:
                digit = int(msg[6:])
                chat.sendMsg(randomDesign(digit))
            except ValueError: chat.sendMsg("参数必须是1到10之间的正整数(￣_,￣ )")
        elif command == "repl ":
            array = msg.split(" ")
            if len(array) < 3: chat.sendMsg(f"命令错误，请使用`{PREFIX}repl 提问 回答`的格式(‾◡◝)")
            else:
                ans = " ".join(array[2:])
                quest = textPure(array[1])
                if not quest in answer: answer[quest] = [ans]
                else: answer[quest].append(ans)
                chat.sendMsg(f"添加成功(☆▽☆)")
                writeJson("answer.json", answer)
        elif msg[1:5] == "help": chat.sendMsg("发送==菜单==谢谢喵")

    elif msg.strip() == f"@{nick}":
        if rans > 129: chat.sendMsg(random.choice(RANDLIS[1]).replace("sender", sender))
        else: chat.sendMsg(random.choice(RANDLIS[0]).replace("sender", sender))
    elif msg.startswith(f"@{nick} "):
        chat.CCreply(sender, msg[len(nick)+2:])
    elif msg[0] == "r":
        if msg == "r":
            ranNum = random.randint(1, 1000)
            if truthList[0]:
                hashCode = userHash[sender]
                if sender in truthList[1]:
                    chat.sendMsg(f"{sender}已经摇出{truthList[1][sender]}了(ﾉ\"◑ڡ◑)ﾉ")
                elif hashCode in truthList[2]:
                    chat.sendMsg(f"{sender}，不要想开小号哦(￢з￢)σ ")
                else:
                    truthList[1][sender] = ranNum
                    chat.sendMsg(str(ranNum))
                    truthList[2].append(hashCode)
            else: chat.sendMsg(str(ranNum))
        elif msg[:2] == "r ":
            array = msg.split()[1:]
            try: beR = int(array[0])
            except: return chat.sendMsg(str(random.randint(1, 1000)))
            try: r2 = int(array[1])
            except: r2 = 1
            if beR > r2: chat.sendMsg(str(random.randint(r2, beR)))
            else: chat.sendMsg(str(random.randint(beR, r2)))
        elif command == "rollen":
            digit = msg[7:25]
            try: chat.sendMsg(rollTo1(int(digit)))
            except ValueError as e: chat.sendMsg(rollTo1(1000))
        elif command == "rprime":
            digit = msg[7:20]
            try:
                dig=random.randint(1, int(digit))
                if dig > 0:
                    eq = "\\*".join(getPrime(dig, []))
                    chat.sendMsg(f"{dig}={eq}")
                else: raise ValueError
            except ValueError as e:
                digit = str(random.randint(1, 1000))
                eq = "\\*".join(getPrime(int(digit), []))
                chat.sendMsg(f"{digit}={eq}")
        elif msg == "rcolor" and senderTrip in whiteList:
            chat.sendMsg(f"/color {hex(random.randint(0, 0xffffff))[2:]:0>6}")
            chat.sendMsg("自动变色ヽ(*。>Д<)o゜")
    elif msg[:2] == "b " and bombs[5] and sender == bombs[1][bombs[2]]:
        try: num = int(msg[2:])
        except: chat.sendMsg("请输入一个整数ヾ|≧_≦|〃")
        else: bombRule(chat, num)
    elif msg[:2] == "p " and pokers[0] and sender == pokers[7][pokers[2]]:
        pkReply(chat, msg[2:], sender)
    elif msg == "bomber":
        if not bombs[5]:
            if not sender in bombs[1]:
                bombs[1].append(sender)
                chat.sendMsg("您已成功加入游戏・▽・)ノ ")
            else: chat.sendMsg("您已经加入过了(￣▽￣)")
        else: chat.sendMsg("这局已经开始了，等下局吧(￣▽￣)")
    elif msg[:5] == "poker":
        if pokers[0]: chat.sendMsg("这局已经开始了，等下局吧(￣▽￣)")
        elif sender in pokers[1]:
            if msg[-1] == "t":
                del pokers[1][sender]
                chat.sendMsg("已成功退出(‾◡◝)")
            else: chat.sendMsg("你已经加入过了(‾◡◝)")
        else:
            pokers[1][sender] = []
            if len(pokers[1]) == 3:
                # 开始
                pokers[0] = True
                pokers[7] = list(pokers[1].keys())
                pokers[3] = PINIT[:]
                # 选底牌
                for i in range(3):
                    index = random.randrange(0, len(pokers[3]))
                    pokers[4].append(pokers[3].pop(index))
                # 洗牌
                random.shuffle(pokers[3])
                # 发牌
                for i, v in enumerate(pokers[3]):
                    pokers[1][pokers[7][i%3]].append(v)
                # 整理牌、告诉牌
                for k, v in pokers[1].items():
                    v.sort(key=lambda x: SORT[x])
                    cards = " ".join(v)
                    chat.sendMsg(f"/w {k} 以下是您的牌：{cards}")
                pokers[8] = random.choice(pokers[7])
                pokers[2] = pokers[7].index(pokers[8])
                pokers[10] = pokers[2]
                chat.sendMsg(f"好的，发牌完成，随机到@{pokers[8]} 拥有地主牌{random.choice(pokers[1][pokers[8]])}，请发送`p 1 叫分`叫地主或`p 0`选择不叫。")
                pokers[6] = True
            else: chat.sendMsg("加入成功，快再找些人吧(☆▽☆)")
    elif msg == "letter":
        chat.sendMsg(f"/w {sender} 一封信\n{getLetter()}")
    elif msg == "开始b" and not bombs[5]:
        if len(bombs[1]) > 1:
            bombs[5], bombs[6], bombs[7] = True, bombs[3], bombs[4]
            bombs[0] = random.randint(bombs[3], bombs[4])
            chat.sendMsg(f"炸弹已经设置好了，范围在{bombs[3]}到{bombs[4]}（包含两数）之间！\n由@{bombs[1][0]} 开始，发送==b 数字==游玩！")
            if bombs[1][0] == nick: bombRule(chat)
        else: chat.sendMsg("至少需要两个人才能开始(⊙﹏⊙)")
    elif msg == "结束b" and bombs[5]:
        endBomb()
        chat.sendMsg("好吧好吧，结束咯_(:зゝ∠)\\_")
    elif msg[:2] == "菜单" or msg[:4] == "menu":
        if msg == "菜单":
            chat.sendMsg(f"/w {sender} {MENUMIN}")
        elif msg == "菜单.max":
            if senderTrip == OWNER: men = "\n".join(MENU+MENUSSP)
            elif senderTrip in whiteList: men = "\n".join(MENU+MENUSP)
            else: men = "\n".join(MENU+MENUFT)
            chat.sendMsg(f"/w {sender} {men}")
        elif msg == "菜单w" and senderTrip in whiteList:
            men = "\n".join(ADMMENU)
            chat.sendMsg(f"/w {sender} {men}")
        elif msg == "菜单~" and senderTrip == OWNER:
            chat.sendMsg(f"/w {sender} {OWNMENU}")
        elif msg == "menu":
            if senderTrip == OWNER: men = "\n".join(ENGMENU+ENGMENUSSP)
            elif senderTrip in whiteList: men = "\n".join(ENGMENU+ENGMENUSP)
            else: men = "\n".join(ENGMENU+ENGMENUFT)
        elif msg == "menuw" and senderTrip in whiteList:
            men = "\n".join(ENGADMMENU)
            chat.sendMsg(f"/w {sender} {men}")
        elif msg == "menu~" and senderTrip == OWNER:
            chat.sendMsg(f"/w {sender} {ENGOWNMENU}")
    # 古老的梗
    elif namePure(msg) == sender:
        chat.sendMsg("why did you call yourself")
    elif msg.lower() in LINE:
        call = LINE[msg.lower()]
        if hasattr(call, "__call__"): chat.sendMsg(call())
        else: chat.sendMsg(random.choice(call).replace("sender", sender))
    # 白名单功能，阿瓦娅的VIP用户捏~
    elif msg[0] == "0" and senderTrip in whiteList:
        # 涩涩，没有涩涩我要死了！！！
        if command == "0setu ":
            try:
                sysList[0] = int(msg[6:])
                chat.sendMsg("涩涩涩涩涩——")
            except ValueError: chat.sendMsg("你是1还是0？")
        # 小黑屋是不值得学习的！
        elif command == "0addb ":
            name = namePure(msg[6:])
            try: hash_ = userHash[name]
            except: return chat.sendMsg("此人当前不在线(+﹏+)")
            if hash_ in blackList: return chat.sendMsg("可惜他/她已经在咯~")
            else:
                blackList.append(hash_)
                writeJson("userData.json", userData)
                chat.sendMsg("好好好，又进去了一个。")
        elif command == "0delb ":
            try: blackList.pop(int(msg[6:]))
            except: return chat.sendMsg("命令错误或此人不在小黑屋~")
            writeJson("userData.json", userData)
            chat.sendMsg("删除成功！")
        elif command == "0addn ":
            try:
                name=namePure(msg[6:])
                if not name in blackName:
                    blackName.append(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg("好好好，又进去了一个。")
                else: chat.sendMsg("可惜他/她已经在咯~")
            except KeyError: chat.sendMsg("可惜这人现在不在呢…(⊙＿⊙；)…")
        elif command == "0deln ":
            try:
                name=namePure(msg[6:])
                if name in blackName:
                    blackName.remove(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg("删除黑名单用户成功！")
                else: chat.sendMsg("这人不在小黑屋里哦？")
            except KeyError: chat.sendMsg("可惜这人现在不在呢…(⊙＿⊙；)…")
        elif command == "0time ":
            try:
                sysList[1] = int(msg[6:])
                chat.sendMsg("好好好，如你所愿~")
            except ValueError:
                chat.sendMsg("1或者0，明白了吗~")
        elif command == "0bcol ":
            chat.sendMsg(f"/color {msg[6:]}")
            chat.sendMsg("自动变色ヽ(*。>Д<)o゜")
        elif command == "0kill ":
            name = namePure(msg[6:])
            if not name in chat.onlineUsers: chat.sendMsg("此人当前不在线！")
            elif name == chat.nick or userTrip[name] == OWNER: chat.sendMsg("6")
            else:
                chat.sendMsg(f"/w {name} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
                chat.sendMsg(f"~kick {name}")
        elif command == "0bans ":
            name = namePure(msg[6:])
            try: hash_ = userHash[name]
            except: return chat.sendMsg("此人当前不在线(+﹏+)")
            if not hash_ in banned:
                if name == chat.nick or userTrip[name] == OWNER: chat.sendMsg("6")
                else:
                    banned.append(hash_)
                    writeJson("userData.json", userData)
                    chat.sendMsg(f"/w {name} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
                    chat.sendMsg(f"~kick {name}")
            else:
                chat.sendMsg("他/她已经被封了！")
        elif command == "0uban ":
            try: banned.pop(int(msg[6:]))
            except: return chat.sendMsg("命令错误或此人不在小黑屋~")
            writeJson("userData.json", userData)
            chat.sendMsg("删除成功！")
        elif command == "0setb ":
            sp = msg.split()
            try: mini, maxi = int(sp[1]), int(sp[2])
            except: return chat.sendMsg("输入格式有误，请在0setb 后面用空格隔开，输入最小值和最大值两个整数！")
            if (maxi-mini)<1: chat.sendMsg("两数的差别过小，请重新设置！")
            else:
                bombs[3], bombs[4] = mini, maxi
                chat.sendMsg("设置成功！")
        elif senderTrip == OWNER:
            if command == "0addw ":
                name = msg[6:12]
                if not name in whiteList:
                    whiteList.append(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg("添加特殊服务的家伙咯╰(￣▽￣)╮")
                else: chat.sendMsg("你要找的人并不在这里面(๑°ㅁ°๑)‼")
            elif command == "0delw ":
                name = msg[6:12]
                if name in whiteList:
                    whiteList.remove(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg("删除白名单用户成功๑乛◡乛๑")
                else: chat.sendMsg("你要找的人并不在这里面( ˃᷄˶˶̫˶˂᷅ )")
            elif command == "0igno ":
                name = namePure(msg[6:])
                if not name in ignored:
                    ignored.append(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg(f"忽略{name}的消息咯~")
                else: chat.sendMsg("已经在了~")
            elif command == "0unig ":
                name = namePure(msg[6:])
                if name in ignored:
                    ignored.remove(name)
                    writeJson("userData.json", userData)
                    chat.sendMsg(f"恢复记录{name}的消息成功了~")
                else: chat.sendMsg("好消息是他/她的信息本来就被记录着~")
            elif command == "0chkr ":
                array = msg.split()
                if len(array) >= 2:
                    ans = answer.get(textPure(array[1]))
                    if ans:
                        if len(array) == 2:
                            arr = []
                            for i, v in enumerate(ans): arr.append(f"{i}：{v}")
                            col = "\n".join(arr)
                            chat.sendMsg(f"/w {sender} 此问题的回答有：\n{col}")
                        else:
                            try: chat.sendMsg(f"/w {sender} {ans[int(array[2])]}")
                            except: chat.sendMsg(f"/w {sender} 当前问题还没有此序号，请重新确认后查询！")
                    else: chat.sendMsg(f"/w {sender} 当前问题还没有设置回答，请重新确认后查询（用`~`代表空格，`\\~`代表\\~）！")
                else: chat.sendMsg(f"/w {sender} 命令错误，请使用`chkr 问题 序号`的格式（序号可选，用`~`代表空格，`\\~`代表\\~）！")
            elif command == "0delr ":
                array = msg.split()
                if len(array) > 3: return chat.sendMsg(f"/w {sender} 命令错误，请使用`0delr 问题 序号`的格式（序号可选，用`~`代表空格，`\\~`代表\\~）！")
                else: 
                    array[1] = textPure(array[1])
                    if len(array) == 2:
                        try: del answer[array[1]]
                        except: return chat.sendMsg(f"/w {sender} 此问题还未设置答案，请重新确认后再次再试！")
                        else: chat.sendMsg(f"/w {sender} 已成功删除“{array[1]}”的所有回答！")
                    else:
                        try: ans = answer[array[1]].pop(int(array[2]))
                        except: return chat.sendMsg(f"/w {sender} 此问题还未设置答案或序号错误，请重新确认后再次再试！")
                        else: chat.sendMsg(f"/w {sender} 已成功删除回答：“{ans}”！")
                    writeJson("answer.json", answer)
            elif command == "0relo ":
                ind = msg[6:]
                if ind == "0":
                    with open(FILENAME, encoding="utf8") as f:
                        global data
                        data = json.load(f)
                        chat.sendMsg("开盒数据重读成功咯~")
                elif ind == "1":
                    with open("design.json", encoding="utf8") as f:
                        global designs
                        designs = json.load(f)
                        chat.sendMsg("脑瘫设计数据重读成功咯~")
                else:
                    with open("reply.json", encoding="utf8") as f:
                        rpy = json.load(f)
                        RANDLIS[6] = rpy[0]
                        RANDLIS[19] = rpy[1]
                        chat.sendMsg(f"{called}回复信息重读成功咯~")
            elif command == "0stfu ":
                try: sysList[2] = int(msg[6:])
                except: pass
            elif msg == "0remake":
                p = sys.executable
                chat.ws.close()
                os.execl(p, p, *sys.argv)
    # 防踢
    elif command == "~kick " and namePure(msg[6:]).startswith(nick):
        chat.sendMsg(f"/w {nick} aaaa")
    elif rans > 130 and allMsg:
        if rans == 133:
            chat.sendMsg("&#8205;"+random.choice(allMsg).split("：")[1])
        else:
            chat.sendMsg(random.choice(RANDLIS[2]).replace("sender", sender))
    else:
        for k, v in INLINE.items(): 
            if re.search(k, msg):
                chat.sendMsg(random.choice(v).replace("sender", sender))

def join(chat, joiner: str, color: str, result: dict):
    '''{'cmd': 'onlineAdd', 'nick': str, 'trip': str, 
        'uType': 'user', 'hash': str, 'level': 100, 
        'userid': iny, 'isBot': False, 'color': False or str, 
        'channel': str, 'time': int}'''
    chat.onlineUsers.append(joiner)
    trip, hash_ = result.get("trip"), result["hash"]
    dic = userData["welText"]
    msg = "&#8205;"+dic[trip] if trip in dic else random.choice(RANDLIS[3]).replace("joiner", joiner)
    userColor[joiner], userHash[joiner], userTrip[joiner] = color, hash_, trip
    logs(f"{joiner}加入")
    names = data.get(hash_)
    if names:
        if not joiner in names:
            print(f"此hash曾用名：{'，'.join(names)}")
            data[hash_].append(joiner)
            writeJson(FILENAME, data)
    else:
        data[hash_] = [joiner]
        writeJson(FILENAME, data)
    for k, v in leftMsg.copy().items():
        if joiner == v[1]:
            del leftMsg[k]
            chat.sendMsg(f"/w {joiner} {v[0]}曾在（{time.ctime(k)}）给您留言：{v[2]}")
    if hash_ in banned:
        chat.sendMsg(f"/w {joiner} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
        chat.sendMsg(f"~kick {joiner}")
    else: chat.sendMsg(msg)
def onSet(chat, result: dict):
    '''{'cmd': 'onlineSet', 'nicks': list, 'users': 
        [{'channel': str, 'isme': bool,  'nick': str,  'trip': str, 
            'uType': 'user', 'hash': str,  'level': 100, 'userid': int, 
            'isBot': False, 'color': str or False}*x],
        'channel': str, 'time': int}'''
    chat.onlineUsers = result["nicks"]
    for i in result["users"]:
        nick_ = i["nick"]
        userHash[nick_] = i["hash"]
        userColor[nick_] = i["color"]
        userTrip[nick_] = i["trip"]
        names = data.get(i["hash"])
        if names:
            if not nick_ in names:
                data[i["hash"]].append(nick_)
        else:
            data[i["hash"]] = [nick_]
    writeJson(FILENAME, data)
    for i in info["prologue"]: chat.sendMsg(i)
def changeColor(chat, result:dict):
    '''{'nick': str, 'trip': str, 'uType': 'user', 
        'hash': str, 'level': 100, 'userid': int, 
        'isBot': False, 'color': str, 'cmd': 'updateUser', 
        'channel': str, 'time': int}'''
    userColor[result["nick"]] = result["color"]
def leave(chat, leaver: str):
    chat.onlineUsers.remove(leaver)
    logs(f"{leaver}离开")
    del userColor[leaver]
    del userHash[leaver]
    del userTrip[leaver]
def whispered(chat, from_: str, msg: str, result: dict):
    msg = msg[1:]
    command = msg[1:6]
    pre = f"/w {from_} "
    print(f"{from_}对你悄悄说：{msg}")
    if result["channel"] != channel:
        p = sys.executable
        chat.ws.close()
        os.execl(p, p, *sys.argv)
    elif msg[0] == PREFIX:
        if command == "left ":
            lis = msg.split()
            if len(lis) < 3:
                chat.sendMsg(pre + "命令不正确！")
            elif namePure(lis[1]) in chat.onlineUsers:
                chat.sendMsg(pre + f"{lis[1]}在线着呢，为什么还要留言啊喂~")
            elif not re.search(r"^@{0,1}[a-zA-Z0-9_]{1,24}$", lis[1]):
                chat.sendMsg(pre + "昵称不合法！")
            else:
                leftMsg[time.time()] = [from_, namePure(lis[1]), "".join(lis[2:])]
                chat.sendMsg(pre + f"{lis[1]}将会在加入时收到你的留言！~~如果那时我还在的话~~")
        elif result.get("trip") in whiteList:
            if command == "hash ": chat.sendMsg(pre + hashByName(namePure(msg[6:])))
            elif command == "hasn ": chat.sendMsg(pre + hashByName(namePure(msg[6:]), True))
    else: chat.sendMsg(pre + reply(from_, msg))
def emote(chat, sender: str, msg: str):
    full = f"{sender}：{' '.join(msg.split(' ')[1:])}"
    logs(full)
    allMsg.append(full)
    if not userTrip[sender] in whiteList:
        hash_ = userHash[sender]
        frisked = frisk(hash_, 0.9+len(msg)/256)
        if frisked == "warn":
            chat.sendMsg(f"@{sender} Warning!!!")
        elif frisked == "limit":
            chat.sendMsg(f"~kick {sender}")
            records[hash_]["score"] = threshold/2
            records[hash_]["warned"] = False
class HackChat:
    def __init__(self, channel: str, nick: str, passwd: str, color: str):
        self.nick = nick
        self.channel = channel
        self.ws = websocket.create_connection("wss://hack.chat/chat-ws", 
            sslopt={"cert_reqs": ssl.CERT_NONE})
        threading.Thread(target=self._clock).start()
        # 人工操作功能，可以让阿瓦娅和主人结合，@w@
        # threading.Thread(target=self._person_control).start()
        self._sendPacket({"cmd": "join", "channel": channel, 
            "nick": f"{nick}#{passwd}"})
        self.sendMsg(f"/color {color}")
    def sendMsg(self, msg: str):
        self._sendPacket({"cmd": "chat", "text": msg,})
    def _sendPacket(self, packet:dict):
        encoded = json.dumps(packet)
        self.ws.send(encoded)
    def move(self, old, new, chess):
        if CCList[4][new[0], new[1]] in [RED[4], BLACK[4]]:
            self.sendMsg(f"@{CCList[1]} 获胜！恭喜！")
            return self._endGame()
        now = CCList[1]
        CCList[1] = CCList[3][0] if CCList[1] == CCList[3][1] else CCList[3][1]
        for i in CCList[4][:,3:6]:
            if (BLACK[4] in i) and (RED[4] in i) and set(i[list(i).index(RED[4])+1:list(i).index(BLACK[4])]) == {"&ensp;"}:
                self.sendMsg(f"@{CCList[1]} 获胜！恭喜！")
                return self._endGame()
        CCList[4][old[0], old[1]] = "&ensp;"
        CCList[4][new[0], new[1]] = chess
        self._sendBoard()
        self.sendMsg(f"{now}挪动了{chr(old[0]+65)}{old[1]+1}的{chess}，轮到@{CCList[1]}")
    def _endGame(self):
        CCList[1] = None
        CCList[3] = [None, None]
        CCList[0] = False
        CCList[4] = INIT.copy()
    def _sendBoard(self):
        mae = CLOLUMN+[f"|{n}|"+ "|".join(i) +"|" for i, n in zip(CCList[4], LETTERS)]
        self.sendMsg("\n".join(mae))
    def CCreply(self, sender: str, msg: str):
        res = re.search(r"^([ABCDEFGHIJ])([123456789]) ([ABCDEFGHIJ])([123456789])$", msg.upper())
        if CCList[3][1] and sender == CCList[1] and res:
            res = res.groups()
            old, new = [ord(res[0])-65, int(res[1])-1], [ord(res[2])-65, int(res[3])-1]
            goingChess, moveChess = CCList[4][new[0], new[1]], CCList[4][old[0], old[1]]
            if moveChess != "&ensp;":
                use = CCList[4][min(old[0], new[0])+1:max(old[0], new[0]), old[1]]
                use2 = CCList[4][old[0], min(old[1], new[1])+1:max(old[1], new[1])]
                if (not CCList[3].index(sender) and not goingChess in RED and moveChess in RED) or (CCList[3].index(sender) and not goingChess in BLACK and moveChess in BLACK):                    
                    if moveChess == RED[5] and (old[0] > 4 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]+1, old[1]]):
                            self.move(old, new, RED[5])
                    elif moveChess == BLACK[5] and (old[0] < 5 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]-1, old[1]]):
                            self.move(old, new, BLACK[5])
                    elif moveChess in [RED[6], BLACK[6]]:
                        if goingChess != "&ensp;":
                            if (new[0] == old[0] and len(use2[use2!="&ensp;"]) == 1) or (new[1] == old[1] and len(use[use!="&ensp;"]) == 1):
                                self.move(old, new, moveChess)
                            else: self.sendMsg("不符合行棋规则")
                        elif (new[0] == old[0] and not len(use2[use2!="&ensp;"])) or (new[1] == old[1] and not len(use[use!="&ensp;"])):
                            self.move(old, new, moveChess)
                        else: self.sendMsg("不符合行棋规则")
                    elif (moveChess in [RED[0], BLACK[0]]) and ((new[0] == old[0] and not len(use2[use2!="&ensp;"])) or ((new[1] == old[1]) and not len(use[use!="&ensp;"]))):
                            self.move(old, new, moveChess)
                    elif (moveChess in [RED[1], BLACK[1]]) and ((abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 1 and CCList[4][int(old[0]-(old[0]-new[0])/2), old[1]] == "&ensp;") or (abs(old[1]-new[1]) == 2 and abs(old[0]-new[0]) == 1 and CCList[4][old[0], int(old[1]-(old[1]-new[1])/2)] == "&ensp;")):
                            self.move(old, new, moveChess)
                    elif moveChess == RED[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CCList[4][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == "&ensp;" and new[0] < 5) :
                            self.move(old, new, RED[2])
                    elif moveChess == BLACK[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CCList[4][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == "&ensp;" and new[0] > 4) :
                            self.move(old, new, BLACK[2])
                    elif moveChess == RED[4] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                            self.move(old, new, RED[4])
                    elif moveChess == BLACK[4] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                            self.move(old, new, BLACK[4])
                    elif moveChess == RED[3] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                            self.move(old, new, RED[3])
                    elif moveChess == BLACK[3] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                            self.move(old, new, BLACK[3])
                    else: self.sendMsg(f"不符合{moveChess}的行棋规则")
                else: self.sendMsg("不能吃自己也不能用别人的棋子！")
            else: self.sendMsg("不能挪动空气！")
        elif msg == "加入游戏":
            if not CCList[3][0]:
                CCList[3][0] = sender
                CCList[4] = INIT.copy()
                self.sendMsg("游戏创建好了，快找人来加入吧！")
            elif sender == CCList[3][0]:
                self.sendMsg("你已经，加入过了哦~")
            elif CCList[3][1]:
                self.sendMsg("游戏已经开始了，等到下局吧~")
            else:
                CCList[0] = True
                CCList[3][1] = sender
                self._sendBoard()
                self.sendMsg(RULE)
                CCList[1] = CCList[3][0]
                self.sendMsg(f"@{CCList[3][0]} 先手执红（绿？）（上方，简体），@{CCList[3][1]} 后手执黑（下方，繁体）。开始了哦~")
        elif msg == "结束游戏" and sender in CCList[3]:
            if not CCList[2]:
                CCList[2] = sender
                self.sendMsg("结束游戏需要双方都发送。")
            elif CCList[2] != sender:
                self._endGame()
                self.sendMsg(f"啊，虽然有点儿遗憾不过，既然{sender}说结束了的话就结束吧……发送开始游戏可以再次开始哦~")
                CCList[2] = None
            else: self.sendMsg("结束游戏需要双方都发送。")
        elif msg == "象棋":
            self.sendMsg(CCMENU.replace("sender", sender))
        elif msg == "提问":
            self.sendMsg(random.choice(RANDLIS[5]).replace("sender", sender))
        elif msg == "数字炸弹":
            self.sendMsg(BOMBMENU.replace("sender", sender))
        elif msg == "斗地主":
            self.sendMsg(POKERMENU.replace("sender", sender))
        elif msg == "扑克规则":
            self.sendMsg(POKERRULE.replace("sender", sender))
        elif msg == "结束p" and sender in pokers[7]:
            endPoker()
            self.sendMsg("唔，结束了;;;;")
        else: self.sendMsg(reply(sender, msg))
    def _person_control(self):
        """和主人结合的过程好难啊，嗯~啊~还有一点~啊啊啊……"""
        while True:
            inputs = input()
            # 更新记忆，就算对我洗脑也没关系的……
            if inputs == "-reread":
                with open(FILENAME, encoding="utf8") as f:
                    global data
                    data = json.load(f)
                print("已重新读取数据")
            # 让我康康都有那些小可爱在线~
            elif inputs == "-users":
                print(",".join(self.onlineUsers))
            elif inputs[:4] == "-st ":
                sysList[0] = eval(inputs[3:])
            else: self.sendMsg(inputs)
    def _clock(self):
        """既然整点了肯定就要刷一刷存在咯~"""
        while True:
            count = time.localtime(time.time())
            time.sleep(3600 - count.tm_min*60 - count.tm_sec + 28.5)
            hour = (count.tm_hour + 1) % 24
            if sysList[0]: self.sendMsg(colorPic())
            if sysList[1]: chat.sendMsg(f"已经{hour}点了啊。")
            if hour == 0: sysList[3] = nowDay()
    def run(self):
        """开始营业咯，好兴奋好兴奋"""
        try:
            while True:
                result = json.loads(self.ws.recv())
                cmd = result["cmd"]
                rnick = result.get("nick")

                if (not sysList[2]) or (sysList[2] and result.get("trip") in whiteList): 
                    # print(result)
                    # 接收到消息！
                    if cmd == "chat":
                        msgGot(self, result["text"], rnick, result.get("trip"))
                    # 有新人来！
                    elif cmd == "onlineAdd": join(self, rnick, result.get("color", ""), result)
                    # 有人离开……
                    elif cmd == "onlineRemove": leave(self, rnick)
                    # 收到私信！
                    elif result.get("type") == "whisper" and result["text"][:3] != "You":
                        whispered(self, result["from"], "".join(result["text"].split(":")[1:]), result)
                    # 更换颜色（色色达咩）
                    elif cmd == "updateUser": changeColor(self, result)
                    elif cmd == "emote": emote(self, result["nick"], result["text"])
                    # 话痨过头被服务器娘教训啦——
                    elif cmd == "warn":
                        if not "blocked" in result["text"]: print(result["text"])
                        else: time.sleep(2)
                    # 当然要用最好的状态迎接开始啦！
                    elif cmd == "onlineSet": onSet(self, result)
                else:
                    # 有新人来！
                    if cmd == "onlineAdd":
                        self.onlineUsers.append(rnick)
                        userColor[rnick], userHash[rnick], userTrip[rnick] = \
                        result.get("color"), result["hash"], result.get("trip")
                    # 有人离开……
                    elif cmd == "onlineRemove": leave(self, rnick)
                    elif cmd == "updateUser": changeColor(self, result)

        # 坏心眼……
        except BaseException as e:
            with open(f"traceback/{time.time()}.txt", "w", encoding="utf8") as f:
                f.write(traceback.format_exc())
            self.sendMsg(f"被玩坏了，呜呜呜……\n```\n{e}")
            self.run()

if __name__ == '__main__':
    chat = HackChat(channel, nick, passwd, color)
    chat.run()