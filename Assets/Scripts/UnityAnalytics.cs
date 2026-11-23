using System.Collections.Generic;

/// <summary>
/// 原实现调用 UnityEngine.Analytics.Analytics.CustomEvent 上报 Unity 云分析，
/// 但抖音小游戏会拦截未进白名单的 unity3d.com 域名，启动日志里会刷
/// "url not in domain list"。这里改为空实现，埋点仍会走 GameAnalytics / PlayFab。
/// </summary>
public static class UnityAnalytics
{
	public static void OnEvent(RPGAnalytics.EventType type, RPGAnalytics.EventAction action, Dictionary<string, object> parameters)
	{
		// 抖音小游戏环境：不上报 Unity Analytics，避免域名白名单报错与额外流量
	}
}
