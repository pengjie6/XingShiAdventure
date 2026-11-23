using System;
using System.Reflection;
using UnityEngine;

/// <summary>
/// 抖音小游戏（WebGL）环境下彻底关掉 Unity 云服务的运行时上报。
///
/// 背景：工程里已经没有 com.unity.purchasing / com.unity.services.core 了，
/// config.uca.cloud.unity3d.com 与 cdp.cloud.unity.cn/config 的请求也随之消失；
/// 但引擎自带的 UnityConnect（Unity 服务心跳 / 旧版 Analytics 派发器）仍会
/// POST https://cdp.cloud.unity3d.com/v1/events，被抖音的域名白名单拦下刷屏。
///
/// 处理方式：
/// 1) ProjectSettings/UnityConnectSettings.asset 里 m_Enabled 与
///    UnityAnalyticsSettings.m_InitializeOnStartup 置 0（这是根本开关，编辑器
///    打开时可能被回写，所以再用这里的运行时兜底）；
/// 2) 本脚本在 SubsystemRegistration（比首个场景还早）把旧版 Analytics 关掉。
///
/// 用反射而不是直接 using UnityEngine.Analytics：这样即使以后把
/// com.unity.modules.unityanalytics 模块删掉，本文件也不会编译报错。
/// </summary>
public static class RuntimeCloudSilencer
{
	private const string AnalyticsTypeName = "UnityEngine.Analytics.Analytics, UnityEngine.UnityAnalyticsModule";

	private static bool _applied;

	[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
	private static void Apply()
	{
		if (_applied)
		{
			return;
		}
		_applied = true;

		// 启动即初始化 = 0：不自动起会话，自然不会发 cdp/v1/events
		SetStaticBool("initializeOnStartup", false);
		// 关闭上报总开关
		SetStaticBool("enabled", false);
	}

	private static void SetStaticBool(string propertyName, bool value)
	{
		try
		{
			Type type = Type.GetType(AnalyticsTypeName, false);
			if (type == null)
			{
				return;
			}

			PropertyInfo property = type.GetProperty(propertyName, BindingFlags.Public | BindingFlags.Static);
			if (property == null || !property.CanWrite)
			{
				return;
			}

			property.SetValue(null, value, null);
		}
		catch (Exception)
		{
			// 关不掉也不能影响游戏启动
		}
	}
}
