# -*- coding: utf-8 -*-
import os, re, sys

ROOT = r"E:/unitystudy/project/Unity2018_小小RPG_MicroRPG/Unity2018_小小RPG_MicroRPG/Unity2018_小小RPG_MicroRPG"
os.chdir(ROOT)

E = []  # (file, old, new, min_count)


def add(f, old, new, n=1):
    E.append((f, old, new, n))


# ---------- 配置表：关卡 / 世界 / 武器 / 怪物 / 英雄 / 宝箱 / 商店 ----------
add("Assets/Scripts/AdventureLevelConfigs.cs", r'Title = "Level (\d+)"', r'Title = "第\1关"', 15)
add("Assets/Scripts/WorldConfigs.cs", 'Title = "ENCHANTED FOREST"', 'Title = "魔法森林"')
add("Assets/Scripts/WorldConfigs.cs", 'Title = "THE DUNGEON"', 'Title = "地牢"')
add("Assets/Scripts/WorldConfigs.cs", 'Title = "THE SWAMP"', 'Title = "沼泽"')

weapons = {
    "SWORD": "剑", "HAMMER": "铁锤", "BOW": "弓", "IRON GLOVE": "铁拳套",
    "AXE": "斧", "LANCE": "长矛", "HATCHET": "短柄斧", "MACE": "钉头锤", "KUNAI": "苦无",
}
for en, cn in weapons.items():
    add("Assets/Scripts/WeaponConfigs.cs", 'Title = "%s"' % en, 'Title = "%s"' % cn)

monsters = {
    "MAGIC MUSHROOM": "魔法蘑菇", "WOODLOG": "木头", "ACORN": "橡果", "CHEST": "宝箱",
    "STRAWBERRY": "草莓", "DRAGON": "龙", "SKELETON": "骷髅", "SNAKE": "蛇",
    "SPIDER": "蜘蛛", "GHOST": "幽灵", "EYE": "眼球", "FISHMAN": "鱼人",
    "LEECH": "水蛭", "TOXIC MUSHROOM": "毒蘑菇", "SALAMANDER": "火蜥蜴", "FROG": "青蛙",
}
for en, cn in monsters.items():
    add("Assets/Scripts/MonsterConfigs.cs", 'Name = "%s"' % en, 'Name = "%s"' % cn, 1)

add("Assets/Scripts/HeroConfigs.cs", 'Name = "THEOBALD"', 'Name = "提奥巴德"')
add("Assets/Scripts/ChestConfigs.cs", 'Name = "ADS CHEST"', 'Name = "广告宝箱"')
add("Assets/Scripts/ChestConfigs.cs", 'Name = "FREE CHEST"', 'Name = "免费宝箱"')
add("Assets/Scripts/ChestConfigs.cs", 'Name = "PREMIUM CHEST"', 'Name = "高级宝箱"', 2)
add("Assets/Scripts/ShopProductCatalog.cs", '"Pack 1"', '"礼包 1"')
add("Assets/Scripts/ShopProductCatalog.cs", '"Pack 2"', '"礼包 2"')
add("Assets/Scripts/ShopProductCatalog.cs", '"Pack 3"', '"礼包 3"')
add("Assets/Scripts/ShopProductCatalog.cs", '"Pack 4"', '"礼包 4"')
add("Assets/Scripts/ShopProductCatalog.cs", '"Pack 5"', '"礼包 5"')
add("Assets/Scripts/ShopProductCatalog.cs", '"Watch a video"', '"观看视频"')

# ---------- 任务描述 ----------
add("Assets/Scripts/MissionKillMonsters.cs",
    'return $"Beat {base.Objective} {name} with the {title}";',
    'return $"用{title}击败{base.Objective}只{name}";')
add("Assets/Scripts/MissionKillMonsters.cs",
    'return $"Beat <color=#FF4364>{base.Objective}</color> with the {title}";',
    'return $"用{title}击败<color=#FF4364>{base.Objective}</color>只怪物";')
add("Assets/Scripts/MissionKillMonsters.cs",
    'return $"Beat {base.Objective} monsters";',
    'return $"击杀{base.Objective}只怪物";', 2)

# ---------- 流程与浮动文字 ----------
add("Assets/Scripts/EndGameFlow.cs", '"LEVEL\\nCOMPLETED!"', '"关卡完成！"')
add("Assets/Scripts/EndGameFlow.cs", '"GAME OVER"', '"游戏结束"')
add("Assets/Scripts/GameController.cs", '"TURN LOST!"', '"回合失败！"')
add("Assets/Scripts/FloatingTextManager.cs",
    '$"{_gameState.GetWaveRemainingCount()} waves remaining!"',
    '$"剩余 {_gameState.GetWaveRemainingCount()} 波！"')

# ---------- UI 文案 ----------
add("Assets/Scripts/UIGameIntroPanel.cs", 'waveCount + " WAVES"', 'waveCount + " 波"')
add("Assets/Scripts/UIGameHUD.cs", '"Combo x" + comboCount', '"连击 x" + comboCount')
add("Assets/Scripts/UIMonsterCard.cs", '("LVL " + (_museumData.Level + 1))', '("等级 " + (_museumData.Level + 1))')
add("Assets/Scripts/UIMonsterCard.cs", ': "MAX")', ': "满级")')

add("Assets/Scripts/UICurrentHeroBox.cs", '"You don\'t have enough coins"', '"金币不足"')
add("Assets/Scripts/UIChestBox.cs", '"You don\'t have enough rubies"', '"红宝石不足"')
add("Assets/Scripts/UIChestBox.cs", '"You have reached the limit for now."', '"暂时已达上限。"')
add("Assets/Scripts/UIGameWeapon.cs", '"You don\'t have enough coins"', '"金币不足"')

add("Assets/Scripts/UIHeroDetailsPopup.cs", '_buttonUpgradeText.text = "UPGRADE";', '_buttonUpgradeText.text = "升级";')
add("Assets/Scripts/UIHeroDetailsPopup.cs", '_buttonEquipText.text = "SELECT";', '_buttonEquipText.text = "选择";')
add("Assets/Scripts/UIHeroDetailsPopup.cs", '_buttonUpgradePriceText.text = "MAXED";', '_buttonUpgradePriceText.text = "满级";')
add("Assets/Scripts/UIHeroDetailsPopup.cs", '"Max level reached!"', '"已达最高等级！"')
add("Assets/Scripts/UIHeroDetailsPopup.cs", '"You need more cards"', '"需要更多卡牌"')
add("Assets/Scripts/UIHeroDetailsPopup.cs", '"You don\'t have enough coins!"', '"金币不足！"')

add("Assets/Scripts/UIWeaponsDetailsPopup.cs", '_buttonUpgradeText.text = "UPGRADE";', '_buttonUpgradeText.text = "升级";')
add("Assets/Scripts/UIWeaponsDetailsPopup.cs", '_buttonEquipText.text = "EQUIP";', '_buttonEquipText.text = "装备";')
add("Assets/Scripts/UIWeaponsDetailsPopup.cs", '_buttonUpgradePriceText.text = "MAXED";', '_buttonUpgradePriceText.text = "满级";')
add("Assets/Scripts/UIWeaponsDetailsPopup.cs", '"Max level reached!"', '"已达最高等级！"')
add("Assets/Scripts/UIWeaponsDetailsPopup.cs", '"You need more cards"', '"需要更多卡牌"')
add("Assets/Scripts/UIWeaponsDetailsPopup.cs", '"You don\'t have enough coins!"', '"金币不足！"')
add("Assets/Scripts/UIWeaponsDetailsPopup.cs",
    '_weaponShapeText.text = _weaponConfig.RangeType + " Range";',
    '_weaponShapeText.text = _weaponConfig.RangeType.ToChinese();')

add("Assets/Scripts/UIWeaponUnlockedPanel.cs",
    '_weaponRangeText.text = copyWeaponBox.WeaponConfig.RangeType + " range";',
    '_weaponRangeText.text = copyWeaponBox.WeaponConfig.RangeType.ToChinese();')
add("Assets/Scripts/UIRewardPanel.cs", '_itemText.text = config2.RangeType + " Range";',
    '_itemText.text = config2.RangeType.ToChinese();')
add("Assets/Scripts/UIRewardPanel.cs", '_itemText.text = "Hero";', '_itemText.text = "英雄";')
add("Assets/Scripts/UIWeaponsPanel.cs", '"You haven\'t found this card yet"', '"你还没有找到这张卡牌"')
add("Assets/Scripts/UIWeaponStatusPanel.cs", '"BROKEN!"', '"损坏！"')
add("Assets/Scripts/UIWeaponStatusPanel.cs", '"REPAIRED!"', '"已修复！"')

add("Assets/Scripts/UIHomePanel.cs", '"You need to complete the missions first!"', '"需要先完成任务！"')
add("Assets/Scripts/UIHomePanel.cs", '"You must unlock previous worlds"', '"需要先解锁之前的世界"')

add("Assets/Scripts/UIShopPanelBox.cs", '"Please come back tomorrow!"', '"明天再来吧！"')
add("Assets/Scripts/UIShopPanelBoxChest.cs", '_claimText.text = "CLAIM!";', '_claimText.text = "领取！";')
add("Assets/Scripts/UIShopPanelBoxChest.cs", '"Come back later!"', '"稍后再来！"')
add("Assets/Scripts/UIShopPanelBoxChest.cs", '"You don\'t have enough rubies"', '"红宝石不足"')

add("Assets/Scripts/UIMenuGameOverContinue.cs", ' CONTINUE";', ' 继续";')
add("Assets/Scripts/UIMenuGameOverContinue.cs", '$"Hero HP: +{25}%"', '$"英雄生命: +{25}%"')
add("Assets/Scripts/UIMenuGameOverContinue.cs", '"You don\'t have enough rubies"', '"红宝石不足"')

add("Assets/Scripts/UINextWorldPopup.cs",
    '$"WORLD {_worldToUnlock.Config.Index + 1} - {_worldToUnlock.Config.Title}"',
    '$"世界 {_worldToUnlock.Config.Index + 1} - {_worldToUnlock.Config.Title}"')
add("Assets/Scripts/UINotEnoughLootPopup.cs",
    'string.Format("MISSING {0}".ToUpper(), LootIdToString(lootId))',
    'string.Format("缺少{0}", LootIdToString(lootId))')
add("Assets/Scripts/UINotEnoughLootPopup.cs",
    '$"Want more {LootIdToString(lootId)}?\\nVisit the shop!"',
    '$"需要更多{LootIdToString(lootId)}？\\n前往商店！"')

add("Assets/Scripts/UIMenuCheat.cs", '"SHOW DEBUG HUD"', '"显示调试信息"')
add("Assets/Scripts/UIMenuCheat.cs", '"HIDE DEBUG HUD"', '"隐藏调试信息"')

add("Assets/Scripts/UIMenuSettingsPanel.cs", '"Version: "', '"版本: "')
add("Assets/Scripts/UIMenuSettingsPanel.cs",
    '"Please enter the word <color=red>RESET</color> to reset your progress."',
    '"请输入 <color=red>RESET</color> 来重置你的进度。"')
add("Assets/Scripts/UIMenuSettingsPanel.cs",
    '_inputPopup.Init("RESET GAME", ', '_inputPopup.Init("重置游戏", ')
add("Assets/Scripts/UIMenuSettingsPanel.cs", '"RESET", onContinue', '"确认重置", onContinue')
add("Assets/Scripts/UIMenuSettingsPanel.cs", '_inputPopup.Init("CODE", "Enter your code:", "DONE"',
    '_inputPopup.Init("兑换码", "输入兑换码：", "完成"')
add("Assets/Scripts/UIMenuSettingsPanel.cs", '"Performance reduced!"', '"性能已降低！"')

# ---------- 动态字体材质名 ----------
add("Assets/Scripts/GameConstant.cs", '"FiraSansExtraCondensed-ExtraBold SDF - Default"', '"DroidSans SDF - Default"')
add("Assets/Scripts/GameConstant.cs", '"FiraSansExtraCondensed-ExtraBold SDF - Button"', '"DroidSans SDF - Button"')
add("Assets/Scripts/GameConstant.cs", '"FiraSansExtraCondensed-ExtraBold SDF - Negative"', '"DroidSans SDF - Negative"')
add("Assets/Scripts/UIShopPanel.cs",
    'SetPriceFont("Fonts & Materials/FiraSansExtraCondensed-ExtraBold SDF", "Fonts & Materials/FiraSansExtraCondensed-ExtraBold SDF - NoOutline")',
    'SetPriceFont("Fonts & Materials/DroidSansFallback SDF", "Fonts & Materials/DroidSans SDF - NoOutline")')

# ---------- 执行 ----------
fails = 0
for f, old, new, n in E:
    if not os.path.exists(f):
        print("!! 文件缺失", f); fails += 1; continue
    s = open(f, encoding="utf-8").read()
    if old.startswith('Title = "Level (') or "(\\d+)" in old:
        cnt = len(re.findall(old, s))
        s2 = re.sub(old, new, s)
    else:
        cnt = s.count(old)
        s2 = s.replace(old, new)
    if cnt < n:
        print("!! 未匹配 [%s] 期望>=%d 实际=%d : %s" % (f, n, cnt, old[:70])); fails += 1
        continue
    if s2 != s:
        open(f, "w", encoding="utf-8", newline="").write(s2)
        print("OK %-58s %d 处  %s" % (os.path.basename(f), cnt, old[:45]))

# "Lv. " 统一替换
for f in ["HeroBoxCard.cs", "UICurrentHeroBox.cs", "UIHeroDetailsPopup.cs", "UIWeaponsDetailsPopup.cs",
          "UIWeaponsPanelBox.cs", "UIStatusBarCharacter.cs"]:
    p = "Assets/Scripts/" + f
    s = open(p, encoding="utf-8").read()
    s2 = s.replace('"Lv. ', '"等级 ')
    if s2 != s:
        open(p, "w", encoding="utf-8", newline="").write(s2)
        print("OK %-58s Lv. -> 等级" % f)

print("失败项:", fails)
