using UnityEngine;

/// <summary>
/// 插屏广告的统一入口。
///
/// 抖音小游戏对插屏有硬性频控，这些都已在 TikTokPlatform.ShowInterstitialAd 里处理：
///   1. 广告模块启动 15 秒内不允许展示；
///   2. 两次展示间隔必须 ≥ 30 秒；
///   3. 插屏实例必须先 Load 完成才能 Show（首次调用通常只是触发加载，本次不展示）。
/// 所以这里不再叠加冷却，只做三件事：判空、统一日志、方便以后换平台。
/// </summary>
public static class AdInterstitial
{
	/// <summary>
	/// 请求播放一次插屏广告。
	/// </summary>
	/// <param name="reason">触发来源，仅用于日志排查，例如「游戏胜利」「设置」。</param>
	public static void Show(string reason)
	{
		if (AdManager.Instance == null)
		{
			Debug.LogWarning("[插屏] 场景里没有 AdManager，跳过本次展示（来源：" + reason + "）");
			return;
		}

		Debug.Log("[插屏] 请求展示（来源：" + reason + "）");
		AdManager.Instance.ShowInterstitialAd();
	}
}
