# -*- coding: utf-8 -*-
import os, re, json, sys

ROOT = r"E:/unitystudy/project/Unity2018_小小RPG_MicroRPG/Unity2018_小小RPG_MicroRPG/Unity2018_小小RPG_MicroRPG"
os.chdir(ROOT)

T = {
    "EMPTY": "空",
    "HAMMER": "铁锤",
    "REPAIR": "修理",
    "Lv. 10 ": "等级 10 ",
    "NOT FOUND": "未找到",
    "Kill 30 monsters with the hammer.": "用铁锤击杀30只怪物。",
    "THEOBALD": "提奥巴德",
    "UPGRADE": "升级",
    "Reward": "奖励",
    "SHOP": "商店",
    "Next world!": "下一世界！",
    "QUIT": "退出",
    "RUBIES": "红宝石",
    "COINS": "金币",
    "ROYAL CHESTS": "皇家宝箱",
    "BEST: 888": "最高: 888",
    "SCORE: 888": "得分: 888",
    "ROUND #1": "第1回合",
    "Option A": "选项 A",
    "Button": "按钮",
    "Lv. 17": "等级 17",
    "Beat 10 with the Axe": "用斧击杀10只",
    "Quest done": "任务完成",
    "CLAIM REWARDS": "领取奖励",
    "Beat the monster to unlock this quest": "击败怪物以解锁此任务",
    "Medium Range": "中距离",
    "Tap to continue": "点击继续",
    "Short range": "短距离",
    "Complete these missions to unlock the next world!": "完成这些任务即可解锁下一世界！",
    "UNLOCK ": "解锁 ",
    "WORLD 2 - THE DUNGEON": "世界 2 - 地牢",
    "Unlock previous worlds to access this one.": "需要先解锁之前的世界才能进入。",
    "QUIT?": "退出？",
    "Lv. 5": "等级 5",
    "Sword": "剑",
    "Are you sure that you want to quit?": "确定要退出吗？",
    "MUSIC": "音乐",
    "Lv. 1": "等级 1",
    "Short Range": "短距离",
    "PROMO CODE": "兑换码",
    "SOUND FX": "音效",
    "EQUIP": "装备",
    "HEROES": "英雄",
    "LEVEL\nCOMPLETED": "关卡完成！",
    "New Text": "新文本",
    "Watch a short video ad and receive rewards!": "观看短视频广告即可获得奖励！",
    "ADS": "广告",
    "WATCH AD": "观看广告",
    "No ads are available right now.\n\nPlease try again later!": "暂时没有可用的广告。\n\n请稍后再试！",
    "NO ADS": "暂无广告",
    "MISSING COINS": "缺少金币",
    "Want more coins?\\nVisit the shop!": "需要更多金币？\n前往商店！",
    "LVL 1": "等级 1",
    "New quests in: ": "新任务倒计时: ",
    "DAILY QUESTS": "每日任务",
    "SELECTED": "已选择",
    "Lvl": "等级",
    "WELCOME BACK": "欢迎回来",
    "While you where away you earned": "你离开期间获得了",
    "PREMIUM": "高级",
    "FREE!": "免费！",
    "Quests": "任务",
    "Loading...": "加载中...",
    "Hero HP: +25%": "英雄生命: +25%",
    "DONE": "完成",
    "Combo x2": "连击 x2",
    "Kill 200 monsters": "击杀200只怪物",
    "ADD WEAPON/HEROES CARDS": "添加武器/英雄卡牌",
    "SETTINGS": "设置",
    "New Weapon Unlocked!": "新武器已解锁！",
    "LOCKED WEAPON": "未解锁武器",
    "'Welcome to MicroRPG!": "欢迎来到微型RPG！",
    "Enter your code:": "输入兑换码：",
    "ENGLISH": "简体中文",
    "Dominic Hamelin-Blais": "多米尼克·哈梅林-布莱斯",
    "UNLOCK NEXT LEVEL": "解锁下一关",
    "MagicFred": "魔法弗雷德",
    "CONTINUE?": "继续？",
    "CHOOSE LANGUAGE": "选择语言",
    "Quest completed!": "任务完成！",
    "FRANÇAIS": "法语",
    "SWORD": "剑",
    "UPGRADE ": "升级 ",
    "SHOW DEBUG INFO": "显示调试信息",
    "How to unlock": "如何解锁",
    "'BATTERY": "电池",
    "BROKEN!": "损坏！",
    "ADD RUBIES": "添加红宝石",
    "CONTACT US": "联系我们",
    "Weapons": "武器",
    "HEAL": "治疗",
    "RESET GAME": "重置游戏",
    "NO THANKS": "不用了",
    "You have to wait until you can request cards": "请稍后再请求卡牌",
    "INCREASE MONSTER LEVEL": "提升怪物等级",
    "PAUSE": "暂停",
    "LEVEL 1": "第1关",
    "LANGUAGE": "语言",
    "GAME OVER": "游戏结束",
    "Design / Art": "设计 / 美术",
    "INCREASE QUESTS PROGRESS (+25%)": "提升任务进度 (+25%)",
    "Version: 0.3.11": "版本: 0.3.11",
    "Free coins!": "免费金币！",
    "PASS": "跳过",
    "CHEATS": "作弊",
    "OF MONSTERS": "怪物",
    "3 WAVES": "3 波",
    "ADD COINS": "添加金币",
    "Long Range": "远距离",
    "UNLOCK NEXT WORLD": "解锁下一世界",
    "ID: 1234rty6": "ID: 1234rty6",
    "FORCE QUESTS EXPIRATION": "强制任务过期",
    "Code": "兑换码",
    "WEAPONS": "武器",
    "MICRO RPG - BETA": "微型RPG - 测试版",
}


def decode(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == "'" and v[-1] == "'":
        return v[1:-1].replace("''", "'")
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        body = v[1:-1]
        out = []
        i = 0
        while i < len(body):
            c = body[i]
            if c == "\\" and i + 1 < len(body):
                n = body[i + 1]
                if n == "x":
                    try:
                        out.append(chr(int(body[i + 2:i + 4], 16))); i += 4; continue
                    except Exception:
                        pass
                if n == "u":
                    try:
                        out.append(chr(int(body[i + 2:i + 6], 16))); i += 6; continue
                    except Exception:
                        pass
                mp = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "0": "\0", "/": "/"}
                out.append(mp.get(n, n)); i += 2; continue
            out.append(c); i += 1
        return "".join(out)
    return v


def encode(s):
    out = ['"']
    for ch in s:
        o = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif 32 <= o < 127:
            out.append(ch)
        elif o <= 0xFFFF:
            out.append("\\u%04X" % o)
        else:
            o -= 0x10000
            out.append("\\u%04X\\u%04X" % (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF)))
    out.append('"')
    return "".join(out)


pat = re.compile(r"^(  m_text|  m_Text): (.*)$", re.M)
missing = {}
applied = 0

for dp, dn, fn in os.walk("Assets"):
    for f in fn:
        if not (f.endswith(".unity") or f.endswith(".prefab")):
            continue
        p = os.path.join(dp, f)
        txt = open(p, encoding="utf-8").read()

        def repl(m):
            global applied
            raw = m.group(2)
            val = decode(raw)
            if val in T:
                applied += 1
                return m.group(1) + ": " + encode(T[val])
            if re.search(r"[A-Za-z]{2,}", val):
                missing[val] = missing.get(val, 0) + 1
            return m.group(0)

        new = pat.sub(repl, txt)
        if new != txt:
            open(p, "w", encoding="utf-8", newline="").write(new)

print("替换文本条目:", applied)
print("仍未翻译（含字母）:", len(missing))
for k, v in sorted(missing.items(), key=lambda x: -x[1]):
    print("   ", v, repr(k))
