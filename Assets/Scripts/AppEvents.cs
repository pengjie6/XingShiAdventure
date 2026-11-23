using System;

public class AppEvents
{
	public event Action AppPausedEvent;

	public event Action AppResumedEvent;

	/// <summary>内购/兑换成功（抖音小游戏无 IAP，保留事件供后续自定义支付渠道使用）</summary>
	public event Action<Reward> InAppPurchaseDoneEvent;

	public void OnAppPaused()
	{
		if (this.AppPausedEvent != null)
		{
			this.AppPausedEvent();
		}
	}

	public void OnAppResumed()
	{
		if (this.AppResumedEvent != null)
		{
			this.AppResumedEvent();
		}
	}

	public void OnInAppPurchaseDone(Reward reward)
	{
		if (this.InAppPurchaseDoneEvent != null)
		{
			this.InAppPurchaseDoneEvent(reward);
		}
	}
}
