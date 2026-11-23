using System;
using UnityEngine;

public class ConfigLoader : MonoBehaviour
{
	public void LoadAll(Action<ConfigsData> onConfigAllUpdated)
	{
		ConfigsData configsDataFromDisk = LoadFromDisk();
		// 全量中文化：远程配置表（Google Sheets）里的 Title/Name 是英文，会把本地中文名覆盖掉，
		// 因此固定使用本地内置配置（本地配置里已经是中文）。如需恢复联网配置，删除下一行即可。
		onConfigAllUpdated(configsDataFromDisk);
	}

	private ConfigsData LoadFromDisk()
	{
		ConfigsData configsData = MonoSingleton<ConfigsManager>.Instance.LoadFromDiskBuiltIn();
		if (configsData == null)
		{
			UnityEngine.Debug.LogWarning("Major fail. Can't load built-in configurations!");
		}
		// 全量中文化：不再读取 persistentDataPath 下的旧缓存（旧缓存里是英文名称，
		// 且版本号可能更高，会覆盖掉内置的中文配置）。如需恢复缓存逻辑，把下面三行取消注释即可。
		// ConfigsData configsData2 = MonoSingleton<ConfigsManager>.Instance.LoadFromDiskCached();
		// if (configsData2 != null && configsData != null && configsData2.Version > configsData.Version)
		// {
		// 	return configsData2;
		// }
		return configsData;
	}

	private void CheckWebVersion(int currentVersion, Action onNoUpdatedNeeded, Action onConfigUpdateNeeded)
	{
		Action<int> onVersionDownloaded = delegate(int webVersion)
		{
			if (webVersion > currentVersion)
			{
				onConfigUpdateNeeded();
			}
			else
			{
				onNoUpdatedNeeded();
			}
		};
		Action<string> onError = delegate
		{
			onNoUpdatedNeeded();
		};
		MonoSingleton<ConfigsManager>.Instance.DownloadConfigsVersion(onVersionDownloaded, onError);
	}

	private void LoadFromWeb(Action<ConfigsData> onConfigAllUpdated, Action<string> onErrorContinue)
	{
		MonoSingleton<ConfigsManager>.Instance.DownloadConfigs(onConfigAllUpdated, onErrorContinue);
	}
}