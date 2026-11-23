using System;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 激励广告弹窗
/// </summary>
public class AdConfirm : MonoBehaviour
{
    private static AdConfirm instance;

    [SerializeField] private Button btnClose;
    [SerializeField] private Button btnConfirm;
    private Action onCompleted;

    [Header("没有传入回调时发放的默认奖励（金币）")]
    [Tooltip("弹窗上写的是「看广告获得奖励 100」，jiliBtn 走 Show(null) 打开时就用这个数量兜底。")]
    [SerializeField] private int defaultCoinsReward = 100;

    public static void Show(Action callBack)
    {
        if (instance == null)
        {
            // 加载 AdConfirm 预制体
            GameObject prefab = Resources.Load<GameObject>("AdConfirm");
            if (prefab == null)
            {
                Debug.LogError("AdConfirm 预制体未找到，请确保其位于 Resources 文件夹中。");
                return;
            }

            // 实例化 AdConfirm
            GameObject adConfirmInstance = Instantiate(prefab);
            instance = adConfirmInstance.GetComponent<AdConfirm>();

            if (instance == null)
            {
                Debug.LogError("AdConfirm 脚本未附加到预制体上，请检查预制体设置。");
                Destroy(adConfirmInstance);
                return;
            }
        }

        // 设置回调并显示弹窗
        instance.onCompleted = callBack;
        instance.gameObject.SetActive(true);
    }

    private void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }

        instance = this;
        //gameObject.SetActive(false);
        btnClose?.onClick.AddListener(this.OnClose);
        btnConfirm?.onClick.AddListener(this.OnConfirm);
    }


    private void OnClose()
    {
        // 清掉回调，避免下次被别的入口（例如直接 SetActive）打开时误触发上一次的奖励。
        onCompleted = null;
        this.gameObject.SetActive(false);
    }

    void OnConfirm()
    {
#if UNITY_EDITOR
        // 编辑器里 TT 是 mock，直接按「看完」处理，方便验证奖励链路
        if (onCompleted != null)
        {
            onCompleted();
        }
        else
        {
            GiveDefaultReward();
        }
        this.OnClose();
#else
        if (AdManager.Instance == null)
        {
            Debug.LogError("[广告] 场景里没有 AdManager，无法播放广告");
            OnAdError("广告服务未初始化");
            return;
        }
        AdManager.Instance.ShowRewardedVideoAd(OnAdWatched, OnAdError);
#endif
    }

    private void OnAdWatched()
    {
        Debug.Log("广告观看完成");
        if (onCompleted != null)
        {
            onCompleted();
        }
        else
        {
            GiveDefaultReward();
        }

        OnClose();
    }

    /// <summary>
    /// 没有外部回调时发放默认金币奖励。
    /// 主界面 jiliBtn 走的是 AdConfirm.Show(null)，只想要「看广告换奖励」，
    /// 这里按弹窗上写的「添加金币 100」兜底发放，避免看完广告什么都拿不到。
    /// </summary>
    private void GiveDefaultReward()
    {
        if (defaultCoinsReward <= 0)
        {
            return;
        }

        if (App.Instance == null || App.Instance.Player == null)
        {
            Debug.LogWarning("[广告] Player 未初始化，默认奖励未发放");
            return;
        }

        App.Instance.Player.LootManager.Add("lootCoin", defaultCoinsReward, CurrencyReason.adsRewardFreeChest);
        App.Instance.MenuEvents.OnTextOverlayRequested("+" + defaultCoinsReward + " 金币", new Vector3(0f, 300f, 0f));
        Debug.Log("[广告] 已发放默认奖励：" + defaultCoinsReward + " 金币");
    }

    private void OnAdError(string errorMessage)
    {
        Debug.LogError($"广告播放失败: {errorMessage}");
        // 加载 AdError 预制体
        GameObject adErrorPrefab = Resources.Load<GameObject>("AdError");
        if (adErrorPrefab != null)
        {
            // 实例化 AdError
            GameObject adErrorInstance = Instantiate(adErrorPrefab, transform.position, Quaternion.identity);
            // 1 秒后销毁实例
            Destroy(adErrorInstance, 1.5f);
        }
        else
        {
            Debug.LogError("AdError 预制体未找到，请确保其位于 Resources 文件夹中。");
        }
    }
}
