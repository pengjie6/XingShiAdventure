/// <summary>
/// 商品购买类型。抖音小游戏没有内购通道，这里仅保留"一次性消耗品"概念，
/// 用于标记商品是否可重复购买，不再依赖 com.unity.purchasing。
/// </summary>
public enum ShopPurchaseType
{
	Consumable,
	NonConsumable
}

public class ShopProductConfig
{
	public string Id;

	/// <summary>历史内购 ID（已废弃，抖音小游戏无 IAP 通道，仅保留作标识）</summary>
	public string IAPId;

	public string Title;

	public string Description;

	public string RewardId;

	public string ImagePath;

	public string PriceLootId;

	public int PriceLootAmount;

	/// <summary>人民币展示价，例如 "¥6"。留空则不显示价格。</summary>
	public string PriceText;

	public string Bonus;

	public ShopPurchaseType PurchaseType;

	public ShopProductType IAPType;

	public int Amount;

	public ShopProductConfig(string productId, string iapId, string title, string description, ShopProductType type, ShopPurchaseType purchaseType, int amount, string bonus, string lootPriceId = "", int lootPriceAmount = 0, string priceText = "")
	{
		Id = productId;
		if (string.IsNullOrEmpty(iapId))
		{
			IAPId = string.Empty;
		}
		else
		{
			IAPId = "com.dhb.microrpg." + iapId;
		}
		Title = title;
		Description = description;
		IAPType = type;
		PurchaseType = purchaseType;
		PriceLootId = lootPriceId;
		PriceLootAmount = lootPriceAmount;
		PriceText = priceText;
		Bonus = bonus;
		RewardId = "reward" + productId.ToUpperFirst();
		ImagePath = "UI/shop" + productId.ToUpperFirst();
		Amount = amount;
	}

	public bool IsInApp()
	{
		return !string.IsNullOrEmpty(IAPId);
	}
}
