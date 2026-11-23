public static class WeaponRangeTypeExtensions
{
	// 武器射程在 UI 上直接显示中文，避免出现 "Short Range" 之类的英文
	public static string ToChinese(this WeaponRangeType range)
	{
		switch (range)
		{
		case WeaponRangeType.Short:
			return "短距离";
		case WeaponRangeType.Medium:
			return "中距离";
		case WeaponRangeType.Long:
			return "远距离";
		default:
			return "未知";
		}
	}
}
