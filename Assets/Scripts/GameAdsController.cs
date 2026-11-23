using System.Collections.Generic;
using UnityEngine;
using Utils;

/// <summary>
/// 游戏内唯一的广告总控。
///
/// 现在只对接抖音小游戏：AdManager → TikTokPlatform → TTSDK 的激励视频 / 插屏。
/// 之所以保留 PlayRewardedVideo / Events / AreRewardedVideoReady 这几个原有接口，
/// 是为了让 UIChestsPanel、UIShopPanel 这些已经写好的界面一行都不用改，
/// 内部实现从「假广告直接发奖」换成了真正的抖音激励视频回调。
/// </summary>
public class GameAdsController : MonoSingleton<GameAdsController>
{
    public GameAdsEvents Events;

    /// <summary>本次看的是哪个广告位（决定发什么奖励）。</summary>
    private GameAdsPlacement _fullyWatchedPlacement = GameAdsPlacement.None;

    private RewardContext _rewardContext;

    /// <summary>true 表示当前没有广告在播；与 _fullyWatchedPlacement 配合避免重复发奖。</summary>
    private bool _isVideoClosed = true;

    /// <summary>防止连点导致同时拉起两个激励视频。</summary>
    private bool _isPlaying;

    /// <summary>拉起广告的时刻，用于兜底解锁（极端情况下平台不回调也不会永久卡死）。</summary>
    private float _adStartTime;

    /// <summary>超过这个时长还没收到抖音回调，就认为上一次广告已经丢了。</summary>
    private const float AdTimeoutSeconds = 180f;

    protected override void Init()
    {
        base.Init();
        Events = new GameAdsEvents();
    }

    /// <summary>
    /// 抖音激励视频是「点击时才创建并 Show」，没有独立的预加载就绪状态。
    /// 这里固定返回 true，让「看广告得金币」的宝箱按钮始终显示；
    /// 真的拉不起来时 PlayRewardedVideo 会走 OnVideoPlayFailed 弹「暂无广告」。
    /// </summary>
    public bool AreRewardedVideoReady()
    {
        return true;
    }

    /// <summary>抖音侧的频控在 AdManager / TikTokPlatform 里做，这里不额外限制。</summary>
    public bool IsPlacementCapped(GameAdsPlacement placement)
    {
        return false;
    }

    /// <summary>
    /// 播放一次抖音激励视频。
    /// 看完（onClose 的 ended = true）才发奖，中途关掉不发奖并通知界面。
    /// </summary>
    public bool PlayRewardedVideo(GameAdsPlacement placement, RewardContext rewardContext = null)
    {
#if UNITY_EDITOR
        // 编辑器里 TTSDK 是 mock，弹不出真实抖音广告。
        // 和 AdConfirm 的编辑器分支保持一致：直接按「看完」处理，方便验证发奖链路。
        // 真正的广告只在抖音开发者工具 / 真机（UNITY_WEBGL 且非编辑器）里才会走下面的分支。
        Debug.LogWarning("[广告] 编辑器模式：跳过真实广告，直接发奖（广告位：" + placement + "）");
        _rewardContext = rewardContext;
        GiveRewards(placement);
        _rewardContext = null;
        return true;
#else
        if (_isPlaying)
        {
            // 兜底：如果平台一直没回调，超过 3 分钟就强制解锁，否则玩家会永久点不动广告
            // 注意必须写 UnityEngine.Time：文件顶部 using Utils 带进来了 Utils.Time，直接写 Time 会 CS0104 二义性
            if (UnityEngine.Time.realtimeSinceStartup - _adStartTime < AdTimeoutSeconds)
            {
                Debug.LogWarning("[广告] 上一个激励视频还没结束，忽略这次点击");
                return false;
            }
            Debug.LogWarning("[广告] 上一次激励视频超时没有回调，强制重置状态");
            ResetPlayState();
        }

        if (AdManager.Instance == null)
        {
            Debug.LogError("[广告] 场景里没有 AdManager（抖音广告组件），无法播放激励视频");
            Events.OnVideoPlayFailed();
            return false;
        }

        _rewardContext = rewardContext;
        _fullyWatchedPlacement = placement;
        _isPlaying = true;
        _isVideoClosed = false;
        _adStartTime = UnityEngine.Time.realtimeSinceStartup;

        PauseMusic();
        Events.OnVideoOpened();

        bool started = AdManager.Instance.ShowRewardedVideoAd(OnRewardedVideoCompleted, OnRewardedVideoFailed);
        if (!started)
        {
            // 平台未就绪 / 抛异常时 AdManager 可能已经同步调过 onFail 了，
            // 只有还停在「播放中」才说明没人收尾，这里补上，避免重复触发失败事件。
            if (_isPlaying)
            {
                ResetPlayState();
                ResumeMusic();
                Events.OnVideoClosed();
                Events.OnVideoPlayFailed();
            }
            return false;
        }

        Debug.Log("[广告] 抖音激励视频已拉起，广告位：" + placement);
        return true;
#endif
    }

    /// <summary>抖音回调：完整看完，发奖。</summary>
    private void OnRewardedVideoCompleted()
    {
        GameAdsPlacement placement = _fullyWatchedPlacement;

        _isPlaying = false;
        _isVideoClosed = true;
        ResumeMusic();
        Events.OnVideoClosed();

        Debug.Log("[广告] 抖音激励视频看完，发放奖励：" + placement);
        // 注意顺序：RewardContext 要在 GiveRewards 之后才能清空
        GiveRewards(placement);

        _fullyWatchedPlacement = GameAdsPlacement.None;
        _rewardContext = null;
    }

    /// <summary>
    /// 抖音回调：加载失败 / 中途关闭 / 播放异常。
    ///
    /// 这里必须把两种情况分开，否则「玩家自己关掉广告」会被当成「没有广告」，
    /// 界面上就会误弹「暂无广告」（UIShopPanel / UIChestsPanel 的 VideoPlayFailedEvent）。
    /// </summary>
    private void OnRewardedVideoFailed(string errorMessage)
    {
        bool closedByUser = errorMessage == AdManager.RewardAdClosedWithoutReward;

        ResetPlayState();
        _isVideoClosed = true;
        ResumeMusic();
        Events.OnVideoClosed();

        if (closedByUser)
        {
            // 中途关闭：不发奖，也不弹「暂无广告」，只轻提示一下
            Debug.Log("[广告] 玩家中途关闭了激励视频，本次不发奖励");
            ShowTip("广告未看完，未获得奖励");
            return;
        }

        Debug.LogWarning("[广告] 抖音激励视频未完成，不发奖励：" + errorMessage);
        Events.OnVideoPlayFailed();
    }

    private void ResetPlayState()
    {
        _isPlaying = false;
        _fullyWatchedPlacement = GameAdsPlacement.None;
        _rewardContext = null;
    }

    /// <summary>顶部飘字提示，走的是游戏里已有的 UITextOverlayPanel。</summary>
    private void ShowTip(string text)
    {
        if (App.Instance == null || App.Instance.MenuEvents == null)
        {
            return;
        }

        App.Instance.MenuEvents.OnTextOverlayRequested(text, new Vector3(0f, 300f, 0f));
    }

    #region 兼容旧接口（外部如果还按事件回调调用，走的还是这一套）

    public void OnVideoPlayFailed()
    {
        _fullyWatchedPlacement = GameAdsPlacement.None;
        Events.OnVideoPlayFailed();
    }

    public void OnVideoRewardCompleted(string placementId)
    {
        GameAdsPlacement placement = Enum.TryParse(placementId, GameAdsPlacement.None);
        _fullyWatchedPlacement = placement;
        if (_isVideoClosed)
        {
            GiveRewards(placement);
        }
    }

    public void OnVideoOpened()
    {
        _isVideoClosed = false;
        _fullyWatchedPlacement = GameAdsPlacement.None;
        PauseMusic();
        Events.OnVideoOpened();
    }

    public void OnVideoClosed()
    {
        _isVideoClosed = true;
        ResumeMusic();
        Events.OnVideoClosed();
        if (_fullyWatchedPlacement != GameAdsPlacement.None)
        {
            GiveRewards(_fullyWatchedPlacement);
        }
    }

    public void OnVideoAvailabilityChanged(bool isAvailable)
    {
        Events.OnVideoAvailabilityChanged(isAvailable);
    }

    #endregion

    private void GiveRewards(GameAdsPlacement placement)
    {
        if (placement == GameAdsPlacement.None)
        {
            return;
        }

        if (App.Instance == null || App.Instance.Player == null)
        {
            Debug.LogWarning("[广告] App/Player 还没初始化好，本次奖励未发放");
            return;
        }

        // 奖励配置在 RewardConfigs / ChestConfigs 里按「reward + 广告位」的命名注册，
        // 例如 rewardFreeCoins（金币，按博物馆产出浮动）和 rewardFreeRubies（红宝石）。
        List<Reward> rewards = new List<Reward>();
        Reward reward = null;
        int index = 1;
        do
        {
            string rewardId = "reward" + placement + ((index <= 1) ? string.Empty : index.ToString());
            reward = App.Instance.RewardFactory.Create(rewardId, _rewardContext);
            if (reward != null)
            {
                CurrencyReason currencyReason = Enum.TryParse("adsReward" + placement, CurrencyReason.unknown);
                if (currencyReason == CurrencyReason.unknown && placement == GameAdsPlacement.FreeCoins)
                {
                    // 枚举里没有 adsRewardFreeCoins，金币宝箱统一记到 adsRewardFreeChest 下
                    currencyReason = CurrencyReason.adsRewardFreeChest;
                }
                App.Instance.Player.RewardManager.Redeem(reward, currencyReason);
                rewards.Add(reward);
                Debug.Log("[广告] 已发放 " + rewardId + "（" + currencyReason + "）");
            }
            index++;
        }
        while (reward != null);

        Events.OnVideoRewardCompleted(placement.ToString(), rewards);
    }

    private void PauseMusic()
    {
        if (MonoSingleton<GameMusicManager>.IsCreated())
        {
            MonoSingleton<GameMusicManager>.Instance.PauseMusic();
        }
    }

    private void ResumeMusic()
    {
        if (MonoSingleton<GameMusicManager>.IsCreated())
        {
            MonoSingleton<GameMusicManager>.Instance.ResumeMusic();
        }
    }
}
