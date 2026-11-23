using System.IO;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

/// <summary>
/// 游戏缓存 / 存档清理工具。新增的独立文件，不改动任何现有脚本。
///
/// 编辑器：菜单 Tools/清除缓存/...
/// 运行时：GameCacheCleaner.ClearAll() / ClearProfile() / ClearDailyReward()
///
/// 注意：清理后 PlayerProfile 仍在内存里（Player.Awake 时构建），
/// 必须先停止 Play 再清，或者清完重进游戏；否则退出时会把旧存档再写回去。
/// </summary>
public static class GameCacheCleaner
{
    /// <summary>主存档键（Player.cs 中 new PlayerProfile("profile-v12-00")）</summary>
    public const string ProfileKey = "profile-v12-00";

    /// <summary>存档类：等级、英雄、武器、宝箱、图鉴、限购次数等</summary>
    public static readonly string[] SaveKeys = { ProfileKey, "data", "hash", "version" };

    /// <summary>进度类：每日免费红宝石、广告计数、上次所在世界页</summary>
    public static readonly string[] ProgressKeys = { "FreeRubiesKey", "AdsWatchedKey", "PageName" };

    /// <summary>账号类：PlayFab 登录缓存</summary>
    public static readonly string[] AccountKeys = { "PLAYFABID", "CURRENTUSER", "VENDORID" };

    /// <summary>配置缓存目录（ConfigsManager 写入的 master.bytes）</summary>
    public static string ConfigCacheDir
    {
        get { return Path.Combine(Application.persistentDataPath, "Cache"); }
    }

    // ---------------------------------------------------------------- 清理动作

    /// <summary>全部清空：PlayerPrefs + 配置缓存 + AssetBundle 缓存</summary>
    public static void ClearAll()
    {
        PlayerPrefs.DeleteAll();
        PlayerPrefs.Save();
        ClearConfigCache();
        ClearAssetBundleCache();
        Debug.Log("[缓存] 已清空 PlayerPrefs、配置缓存、Bundle 缓存");
    }

    /// <summary>只清存档（保留配置缓存，省一次远端拉取）</summary>
    public static void ClearProfile()
    {
        DeleteKeys(SaveKeys);
        DeleteKeys(ProgressKeys);
        Debug.Log("[缓存] 已清空玩家存档与进度");
    }

    /// <summary>只重置每日奖励/广告计数，用于反复测试激励视频</summary>
    public static void ClearDailyReward()
    {
        DeleteKeys(new[] { "FreeRubiesKey", "AdsWatchedKey" });
        Debug.Log("[缓存] 已重置每日免费红宝石与广告计数");
    }

    /// <summary>只清 PlayFab 登录缓存（换号测试用）</summary>
    public static void ClearAccount()
    {
        DeleteKeys(AccountKeys);
        Debug.Log("[缓存] 已清空 PlayFab 登录缓存");
    }

    /// <summary>删除 persistentDataPath/Cache（远端配置的本地缓存）</summary>
    public static void ClearConfigCache()
    {
        string dir = ConfigCacheDir;
        if (!Directory.Exists(dir))
        {
            return;
        }

        try
        {
            Directory.Delete(dir, true);
            Debug.Log("[缓存] 已删除配置缓存: " + dir);
        }
        catch (System.Exception e)
        {
            Debug.LogWarning("[缓存] 删除配置缓存失败: " + e.Message);
        }
    }

    /// <summary>清 UnityWebRequestAssetBundle / WWW 的下载缓存</summary>
    public static void ClearAssetBundleCache()
    {
        try
        {
            if (Caching.ClearCache())
            {
                Debug.Log("[缓存] 已清空 AssetBundle 下载缓存");
            }
        }
        catch (System.Exception e)
        {
            Debug.LogWarning("[缓存] 清空 Bundle 缓存失败: " + e.Message);
        }
    }

    public static void DeleteKeys(string[] keys)
    {
        for (int i = 0; i < keys.Length; i++)
        {
            if (PlayerPrefs.HasKey(keys[i]))
            {
                PlayerPrefs.DeleteKey(keys[i]);
            }
        }
        PlayerPrefs.Save();
    }

#if UNITY_EDITOR
    // ------------------------------------------------------------ 编辑器菜单

    [MenuItem("Tools/清除缓存/清空全部（存档 + 配置 + Bundle）", false, 1)]
    public static void MenuClearAll()
    {
        if (!EditorUtility.DisplayDialog("清空全部缓存",
            "将删除 PlayerPrefs 全部键、" + ConfigCacheDir + " 目录、AssetBundle 下载缓存。\n\n" +
            "请先停止 Play 模式，否则运行中的 Player 会把旧存档写回去。\n\n继续吗？",
            "清空", "取消"))
        {
            return;
        }

        ClearAll();
    }

    [MenuItem("Tools/清除缓存/仅清存档（保留配置缓存）", false, 2)]
    public static void MenuClearProfile()
    {
        if (!EditorUtility.DisplayDialog("清空存档",
            "将删除主存档（" + ProfileKey + "）与每日奖励/广告计数，保留配置缓存。\n\n继续吗？",
            "清空", "取消"))
        {
            return;
        }

        ClearProfile();
    }

    [MenuItem("Tools/清除缓存/仅重置每日奖励与广告计数", false, 3)]
    public static void MenuClearDaily()
    {
        ClearDailyReward();
    }

    [MenuItem("Tools/清除缓存/清 PlayFab 登录缓存", false, 4)]
    public static void MenuClearAccount()
    {
        ClearAccount();
    }

    [MenuItem("Tools/清除缓存/打印当前缓存路径", false, 20)]
    public static void MenuPrintPaths()
    {
        Debug.Log("[缓存] persistentDataPath = " + Application.persistentDataPath
            + "\n[缓存] 配置缓存目录 = " + ConfigCacheDir
            + "\n[缓存] 编辑器 PlayerPrefs 注册表 = HKCU\\Software\\Unity\\UnityEditor\\"
            + PlayerSettings.companyName + "\\" + PlayerSettings.productName);
    }
#endif
}
