using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class UIWorldPage : MonoBehaviour
{
	[SerializeField]
	private UINextWorldPopup _nextWorldPopup;

	[SerializeField]
	private UIGameButton _nextWorldButton;

	[SerializeField]
	private UIGameButton _prevWorldButton;

	[SerializeField]
	private UIGameButton _questButton;

	[SerializeField]
	private Image _questImage;

	[SerializeField]
	private UIBadge _questBadge;

	[SerializeField]
	private TextMeshProUGUI _nextWorldUnlockCompletionText;

	[SerializeField]
	private UIBadge _nextWorldBadge;

	[SerializeField]
	private UIChestsPanel _chestPanel;

	[SerializeField]
	private UIWorldRenderer _worldRenderer;

	[SerializeField]
	private Transform _target;

	private WorldData _worldData;

	private UIQuestPopup _questPopup;

	private Action _nextWorldButtonClicked;

	private Action _prevWorldButtonClicked;

	public UIGameButton NextButton => _nextWorldButton;

	public string WorldId => _worldData.Config.Id;

	/// <summary>
	/// 世界在配置里的序号（从 0 开始）。翻页一律按这个序号算，
	/// 不用页面列表下标——GetAllConfigs() 返回的是 Dictionary.Values，
	/// 顺序不保证与 Index 一致。
	/// </summary>
	public int WorldIndex => _worldData.Config.Index;

	public float TargetOffsetY
	{
		get
		{
			Vector2 anchoredPosition = _target.GetComponent<RectTransform>().anchoredPosition;
			return anchoredPosition.y;
		}
	}

	public UIWorldPage Init(WorldData worldData, Action nextWorldButtonClicked, Action prevWorldButtonClicked)
	{
		_worldData = worldData;
		_nextWorldButtonClicked = nextWorldButtonClicked;
		_prevWorldButtonClicked = prevWorldButtonClicked;
		string str = MonoSingleton<AdventureLevelConfigs>.Instance.GetMonsterIds(worldData.Config.Id)[0];
		_questImage.sprite = Resources.Load<Sprite>("Monsters/" + str);
		if (_questPopup == null)
		{
			_questPopup = UIQuestPopup.Create(_worldData.Config.Id);
		}
		if (!IsUnlocked())
		{
			_nextWorldPopup.Init(_worldData);
		}
		_nextWorldPopup.gameObject.SetActive(!IsUnlocked());
		_questButton.gameObject.SetActive(IsUnlocked());
		NextButton.OnClick(OnNextWorldButtonClicked);
		if (_prevWorldButton != null)
		{
			// 旧存档/旧场景里的 WorldPage 实例可能没有这个引用，判空避免空引用。
			_prevWorldButton.OnClick(OnPrevWorldButtonClicked);
			UpdatePrevWorldButtonState();
		}
		_questButton.OnClick(OnQuestButtonClicked);
		UpdateNextWorldButtonState();
		SetupBackground();
		_chestPanel.Init(App.Instance.Player.ChestManager);
		_chestPanel.gameObject.SetActive( false);
		UpdateNextWorldBadge();
		UpdateQuestBadge();
		App.Instance.Player.MonsterMissions.Events.MonsterRewardClaimedEvent += OnMonsterRewardClaimed;
		return this;
	}

	private void OnNextWorldButtonClicked()
	{
		_nextWorldBadge.SetVisible( false, false);
		if (_nextWorldButtonClicked != null)
		{
			_nextWorldButtonClicked();
		}
	}

	private void OnPrevWorldButtonClicked()
	{
		if (_prevWorldButtonClicked != null)
		{
			_prevWorldButtonClicked();
		}
	}

	private void UpdatePrevWorldButtonState()
	{
		if (_prevWorldButton == null)
		{
			return;
		}
		// 第一个世界没有上一页，隐藏即可。
		bool hasPreviousWorld = _worldData.Config.Index > 0;
		_prevWorldButton.gameObject.SetActive(hasPreviousWorld);
		if (!hasPreviousWorld)
		{
			return;
		}
		ApplyPrevWorldButtonLayout();
	}

	/// <summary>
	/// 「上一世界」按钮有两种落位：
	/// 1) 已解锁世界：右上角，紧挨「下一世界」左边；
	/// 2) 未解锁世界：整页被 UINextWorldPopup 的「解锁条件」卡片盖住，右上角正好落在卡片里，
	///    按钮会被压住点不到。此时挪到左上角（与标题同一行）—— 卡片是从标题下方开始的，
	///    左上角是空白区。配合 prefab 里把它排在 Panel 子节点的最后一位，
	///    保证玩家在任何页面上都退得回去，不会卡死在锁定世界。
	/// </summary>
	private void ApplyPrevWorldButtonLayout()
	{
		RectTransform rectTransform = _prevWorldButton.transform as RectTransform;
		if (rectTransform == null)
		{
			return;
		}
		if (IsUnlocked())
		{
			rectTransform.anchorMin = new Vector2(1f, 0.5f);
			rectTransform.anchorMax = new Vector2(1f, 0.5f);
			rectTransform.anchoredPosition = new Vector2(-415f, 189.65f);
		}
		else
		{
			rectTransform.anchorMin = new Vector2(0f, 0.5f);
			rectTransform.anchorMax = new Vector2(0f, 0.5f);
			rectTransform.anchoredPosition = new Vector2(111f, 410f);
		}
	}

	private void OnQuestButtonClicked()
	{
		_questBadge.SetVisible( false, false);
		_questPopup.Show();
	}

	private void UpdateQuestBadge()
	{
		bool isVisible = App.Instance.Player.MonsterMissions.CanClaimQuests(_worldData.Config.Id);
		_questBadge.SetVisible(isVisible, true);
	}

	public void OnPageEnter()
	{
		if (IsUnlocked())
		{
			_chestPanel.gameObject.SetActive( true);
		}
		// 每次进入这一页都重新判定「下一世界」按钮的显隐并刷新解锁百分比，
		// 否则通关/任务进度变化后，按钮上的百分比要等下一次世界解锁才更新。
		UpdateNextWorldButtonState();
		UpdatePrevWorldButtonState();
	}

	public void OnPageExit()
	{
		_chestPanel.gameObject.SetActive( false);
	}

	private void UpdateWorld(string worldId)
	{
	}

	private void UpdateNextWorldBadge()
	{
		_nextWorldBadge.SetVisible(CanShowNextWorldBadge(), true);
	}

	private bool CanShowNextWorldBadge()
	{
		return IsNextWorldLocked() && IsNextWorldReady();
	}

	private bool IsNextWorldReady()
	{
		WorldData nextLockedWorldData = App.Instance.Player.LevelManager.GetNextLockedWorldData();
		return nextLockedWorldData.Config.IsValid() && nextLockedWorldData.AreMissionsCompleted();
	}

	private void SetupBackground()
	{
		_worldRenderer.Init(_worldData.Config.Id);
	}

	public bool IsNextWorldLocked()
	{
		WorldData nextLockedWorldData = App.Instance.Player.LevelManager.GetNextLockedWorldData();
		string lastUnlockedWorldId = App.Instance.Player.LevelManager.LastUnlockedWorldId;
		return nextLockedWorldData.Config.IsValid() && _worldData.Config.Id == lastUnlockedWorldId;
	}

	public bool IsUnlocked()
	{
		return _worldData.IsUnlocked;
	}

	private void OnDestroy()
	{
		if (App.IsCreated())
		{
			App.Instance.Player.MonsterMissions.Events.MonsterRewardClaimedEvent -= OnMonsterRewardClaimed;
		}
	}

	private void OnMonsterRewardClaimed(MonsterMissionData data, List<Reward> rewards)
	{
		UpdateQuestBadge();
	}

	private void ShowNextWorldButton()
	{
		UpdateNextWorldButtonText();
		_nextWorldButton.gameObject.SetActive( true);
	}

	private void HideNextWorldButton()
	{
		_nextWorldButton.gameObject.SetActive( false);
	}

	private void UpdateNextWorldButtonText()
	{
		// 滑动翻页已关闭，「下一世界」按钮是唯一的翻页入口，
		// 所以这里取「下一个世界」而不是「下一个未解锁的世界」：
		// 下个世界若已解锁，它的解锁任务必然全部完成，GetUnlockCompletion01() 返回 1，显示 100%。
		WorldConfig nextWorld = MonoSingleton<WorldConfigs>.Instance.GetNextWorld(_worldData.Config.Id);
		if (!nextWorld.IsValid())
		{
			return;
		}
		WorldData nextWorldData = App.Instance.Player.LevelManager.GetWorldData(nextWorld.Id);
		_nextWorldUnlockCompletionText.text = Mathf.FloorToInt(nextWorldData.GetUnlockCompletion01() * 100f) + "%";
	}

	private void UpdateNextWorldButtonState()
	{
		// 后面还有世界、且当前世界已经解锁时才显示按钮。
		// 当前世界未解锁时整页被「解锁条件」卡片覆盖：按钮既看不见，
		// 也不该让玩家再往后跳（会连跳好几页锁定世界，彻底出不来）。
		WorldConfig nextWorld = MonoSingleton<WorldConfigs>.Instance.GetNextWorld(_worldData.Config.Id);
		if (nextWorld.IsValid() && IsUnlocked())
		{
			ShowNextWorldButton();
		}
		else
		{
			HideNextWorldButton();
		}
	}

	public void OnWorldUnlocked()
	{
		UpdateNextWorldButtonState();
		UpdatePrevWorldButtonState();
		_nextWorldPopup.gameObject.SetActive( false);
		_chestPanel.gameObject.SetActive( true);
		_questButton.gameObject.SetActive( true);
	}

	public void UpdateNextWorldPanel()
	{
		_nextWorldPopup.UpdateMainBox();
	}
}