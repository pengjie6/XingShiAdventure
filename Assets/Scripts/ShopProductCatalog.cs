using System.Collections.Generic;

public static class ShopProductCatalog
{
    public const string WatchVideoRubiesProductId = "productRubiesVideo";

    // 说明：抖音小游戏没有内购通道，原来走 IAP 的红宝石礼包现在只能展示价格文本（PriceText），
    // 实际购买逻辑在 UIShopPanel.OnProductClicked 里走游戏内货币/广告，不再调起商店。
    private static Dictionary<string, ShopProductConfig> _products = new Dictionary<string, ShopProductConfig>
    {
        {
            "productRubies1",
            new ShopProductConfig("productRubies1", "rubies1a", "礼包 1", string.Empty, ShopProductType.Rubies, ShopPurchaseType.Consumable, 900, string.Empty, "lootCoin")
        },
        {
            "productRubies2",
            new ShopProductConfig("productRubies2", "rubies2", "礼包 2", string.Empty, ShopProductType.Rubies, ShopPurchaseType.Consumable, 2000, "+27%","lootCoin")
        },
        {
            "productRubies3",
            new ShopProductConfig("productRubies3", "rubies3", "礼包 3", string.Empty, ShopProductType.Rubies, ShopPurchaseType.Consumable, 5000, "+58%", "lootCoin")
        },
        {
            "productRubies4",
            new ShopProductConfig("productRubies4", "rubies4", "礼包 4", string.Empty, ShopProductType.Rubies, ShopPurchaseType.Consumable, 12000, "+90%", "lootCoin")
        },
        {
            "productRubies5",
            new ShopProductConfig("productRubies5", "rubies5", "礼包 5", string.Empty, ShopProductType.Rubies, ShopPurchaseType.Consumable, 35000, "+120%", "lootCoin")
        },
        {
            "productRubiesVideo",
            new ShopProductConfig("productRubiesVideo", string.Empty, "video", "观看视频", ShopProductType.Rubies, ShopPurchaseType.Consumable, 10, string.Empty, "lootCoin")
        }
    };

    public static List<ShopProductConfig> GetProductConfigs(ShopProductType iapType)
    {
        List<ShopProductConfig> list = new List<ShopProductConfig>();
        foreach (KeyValuePair<string, ShopProductConfig> product in _products)
        {
            if (product.Value.IAPType == iapType)
            {
                list.Add(product.Value);
            }
        }
        return list;
    }

    public static List<ShopProductConfig> GetAllConfigs()
    {
        return new List<ShopProductConfig>(_products.Values);
    }

    public static ShopProductConfig GetInAppConfig(string inAppId)
    {
        foreach (KeyValuePair<string, ShopProductConfig> product in _products)
        {
            if (product.Value.IAPId == inAppId)
            {
                return product.Value;
            }
        }
        return null;
    }
}
