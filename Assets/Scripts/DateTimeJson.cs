using System;
using System.Globalization;
using Newtonsoft.Json;

/// <summary>
/// 存档里用来包装 DateTime 的类型（JSON 形态始终是 {"ss":"2026-11-21T10:00:00.0000000Z"}）。
///
/// 为什么不再用 [OnSerializing] / [OnDeserialized] 回调：
/// 开启 OPS 混淆后，这个类型里会生成多个带 [OnDeserialized] 的方法
/// （构建产物符号表里 DateTimeJson 上就有 oow / jjw / obw / cpb / cpc / czy / euw / faf / hyf 一堆），
/// Newtonsoft 在解析类型契约时直接抛：
///   JsonException: Invalid attribute. Both 'Void oow(...)' and 'Void jjw(...)'
///   in type 'DateTimeJson' have 'System.Runtime.Serialization.OnDeserializedAttribute'.
/// 只要序列化到 PlayerProfile / FreeRubiesProfile 里任何一个带 DateTimeJson 的字段就会炸，
/// 表现就是「看完激励视频 → 发奖 → 存 FreeRubiesProfile」抛异常，奖励弹窗也不弹，
/// 顺带整个本地存档的保存/读取都失效。
///
/// 现在改成「用公开属性直接映射 ss 字段」，完全不依赖任何序列化回调特性，
/// 混淆无论怎么改方法名都不会再触发；JSON 格式与旧版 [JsonProperty("ss")] private string _time 完全一致，
/// 老 PlayerPrefs 存档、PlayFab 云存档都能直接读。
/// </summary>
[Serializable]
public class DateTimeJson
{
	private DateTime _time;

	/// <summary>存档里真正落盘的字段，key 固定为 "ss"。</summary>
	[JsonProperty("ss")]
	public string SerializedTime
	{
		get
		{
			return _time.ToString("o", CultureInfo.InvariantCulture);
		}
		set
		{
			DateTime parsed;
			if (DateTime.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind, out parsed))
			{
				_time = parsed;
			}
		}
	}

	/// <summary>业务代码用的时间值，不参与 JSON。</summary>
	[JsonIgnore]
	public DateTime Time
	{
		get
		{
			return _time;
		}
		set
		{
			_time = value;
		}
	}

	public override string ToString()
	{
		return _time.ToString();
	}
}
