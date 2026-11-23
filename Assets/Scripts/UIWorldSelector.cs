using DG.Tweening;
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.UI.Extensions;

public class UIWorldSelector : MonoBehaviour
{
	private const string PageNameKey = "PageName";

	[SerializeField]
	private HorizontalScrollSnap _selector;

	[SerializeField]
	private GameController _gameController;

	private Dictionary<string, UIWorldPage> _pagesByIds = new Dictionary<string, UIWorldPage>();

	private List<UIWorldPage> _pages = new List<UIWorldPage>();

	private int _currentPageIndex;

	private UIWorldPage _currentPage;

	private UIWorldPage _latestUnlockedPage;

	private Hero _hero;

	private Sequence _heroTween;

	private string _lastWorldIdSeen;

	public string WorldId => _currentPage.WorldId;

	public event Action<string> WorldSelectedEvent;

	private void Start()
	{
		DisableSwipeNavigation();
		List<WorldConfig> allConfigs = MonoSingleton<WorldConfigs>.Instance.GetAllConfigs();
		_currentPageIndex = 0;
		string @string = PlayerPrefs.GetString("PageName", "w00");
		for (int i = 0; i < allConfigs.Count; i++)
		{
			string id = allConfigs[i].Id;
			WorldData worldData = App.Instance.Player.LevelManager.GetWorldData(id);
			UIWorldPage uIWorldPage = CreateWorldPage(worldData);
			_selector.AddChild(uIWorldPage.gameObject);
			if (uIWorldPage.IsNextWorldLocked())
			{
				_latestUnlockedPage = uIWorldPage;
			}
			if (id == @string)
			{
				_currentPageIndex = i;
				_currentPage = uIWorldPage;
			}
		}
		HeroData currentHeroData = App.Instance.Player.HeroManager.GetCurrentHeroData();
		SetHero(currentHeroData);
		_selector.GoToScreen(_currentPageIndex);
		_selector.StartingScreen = _currentPageIndex;
		App.Instance.MenuEvents.OnWorldSelectorReady();
	}

	/// <summary>
	/// 关闭左右滑动翻页，翻页只保留页面里的「下一世界」按钮。
	///
	/// 这里禁用的是同物体上的 ScrollRect 组件，而不是 HorizontalScrollSnap：
	/// 拖拽、惯性、滚轮全部由 ScrollRect 处理，禁用后它不再接收任何输入事件；
	/// 而 HorizontalScrollSnap 的翻页是自己在 Update 里对 content.localPosition 做
	/// Lerp 实现的（GoToScreen → _lerp_target），不依赖 ScrollRect，所以按钮跳页照常工作。
	///
	/// 注意不要改成 scrollRect.horizontal = false：那会让 ScrollRect 的
	/// UpdateBounds 换一条分支计算 content 边界，SetScrollContainerPosition 里
	/// 用 horizontalNormalizedPosition 定位初始页时会算偏。
	/// </summary>
	private void DisableSwipeNavigation()
	{
		if (_selector == null)
		{
			return;
		}
		ScrollRect scrollRect = _selector.GetComponent<ScrollRect>();
		if (scrollRect != null)
		{
			scrollRect.enabled = false;
		}
	}

	private void OnEnable()
	{
		RegisterEvents();
	}

	private void OnDisable()
	{
		UnRegisterEvents();
	}

	private void OnDestroy()
	{
		if (_heroTween != null)
		{
			_heroTween.Kill( true);
			_heroTween = null;
		}
	}

	private void RegisterEvents()
	{
		App.Instance.Player.LevelManager.Events.WorldUnlockedEvent += OnWorldUnlocked;
		App.Instance.Player.HeroManager.Events.HeroSelectedEvent += OnHeroSelected;
		App.Instance.Player.HeroManager.Events.WeaponsUpdatedEvent += OnWeaponsUpdated;
		_selector.OnSelectionPageChangedEvent.AddListener(OnSelectionPageChanged);
		_selector.OnSelectionChangeEndEvent.AddListener(OnSelectionChangeEnded);
	}

	private void UnRegisterEvents()
	{
		if (App.IsCreated())
		{
			App.Instance.Player.LevelManager.Events.WorldUnlockedEvent -= OnWorldUnlocked;
			App.Instance.Player.HeroManager.Events.HeroSelectedEvent -= OnHeroSelected;
			App.Instance.Player.HeroManager.Events.WeaponsUpdatedEvent -= OnWeaponsUpdated;
		}
		if (_selector != null)
		{
			_selector.OnSelectionPageChangedEvent.RemoveListener(OnSelectionPageChanged);
			_selector.OnSelectionChangeEndEvent.RemoveListener(OnSelectionChangeEnded);
		}
	}

	private void OnWeaponsUpdated(List<WeaponData> equippedWeapons)
	{
		if (_hero != null)
		{
			_hero.UpdateEquippedWeapons(equippedWeapons);
		}
	}

	public void OnFocusLost()
	{
		if (_hero != null)
		{
			_hero.Visual.SetColor(new Color(1f, 1f, 1f, 0f));
		}
	}

	public void OnFocusGained()
	{
	}

	public void OnFocusGaining()
	{
		if (_currentPage != null && _currentPage.IsUnlocked() && _hero != null && _hero.Visual != null)
		{
			_hero.Visual.SetColor(new Color(1f, 1f, 1f, 1f), 0.15f);
		}
	}

	private void SetHero(HeroData heroData)
	{
		if (_hero != null)
		{
			UnityEngine.Object.Destroy(_hero.gameObject);
		}
		_hero = Hero.Create(heroData, App.Instance.Player.WeaponManager.Events, new CharacterEvents());
		_hero.transform.position = Vector3.zero;
		_hero.SetPosition(_hero.transform.position);
		_hero.SetTag("Hero");
		_hero.SetCollisionLayer(9);
		_hero.gameObject.AddComponent<RectTransform>();
		_hero.gameObject.SetSortingOrder(102);
		_hero.Visual.WeaponPivot.SetSortingOrder(101);
		UpdateHeroParent();
	}

	private void UpdateHeroParent()
	{
		_hero.transform.SetParent(_currentPage.transform, true);
		RectTransform component = _hero.GetComponent<RectTransform>();
		component.anchoredPosition = new Vector2(0f, _currentPage.TargetOffsetY);
		component.localScale = Vector3.one * 110f;
		_hero.Visual.SetColor((!_currentPage.IsUnlocked()) ? new Color(1f, 1f, 1f, 0f) : Color.white);
		if (_currentPage.IsUnlocked() && _currentPage.WorldId != _lastWorldIdSeen && !string.IsNullOrEmpty(_lastWorldIdSeen))
		{
			AnimateHero();
		}
		_lastWorldIdSeen = _currentPage.WorldId;
	}

	private void AnimateHero()
	{
		if (_heroTween != null)
		{
			_heroTween.Complete( true);
			_heroTween = null;
		}
		if (!(_hero == null) && !(_hero.Visual == null))
		{
			_hero.Visual.SetColor(new Color(1f, 1f, 1f, 1f));
			_hero.Visual.MovingPivot.localScale = Vector3.zero;
			_heroTween = DOTween.Sequence();
			_heroTween.Insert(0f, _hero.Visual.MovingPivot.DOScaleX(0.6f, 0.3f).SetEase(Ease.Linear).OnComplete(delegate
			{
			}));
			_heroTween.Insert(0f, _hero.Visual.MovingPivot.DOScaleX(1f, 0.2f).SetDelay(0.3f).SetEase(Ease.OutBack)
				.OnComplete(delegate
				{
				}));
			_heroTween.Insert(0f, _hero.Visual.MovingPivot.DOScaleY(1f, 0.5f).SetEase(Ease.OutBack).OnComplete(delegate
			{
			}));
			_heroTween.OnComplete(delegate
			{
				if (_hero != null && _hero.Visual != null)
				{
					_hero.Visual.MovingPivot.localScale = Vector3.one;
				}
			});
		}
	}

	private void OnHeroSelected(HeroData heroData)
	{
		SetHero(heroData);
	}

	private UIWorldPage CreateWorldPage(WorldData worldData)
	{
		UIWorldPage uIWorldPage = UnityEngine.Object.Instantiate(Resources.Load<UIWorldPage>("UI/WorldPage"));
		_pagesByIds[worldData.Config.Id] = uIWorldPage;
		_pages.Add(uIWorldPage);
		return uIWorldPage.Init(worldData, GoToNextWorldPage, GoToPreviousWorldPage);
	}

	private float _lastPageChangeTime = -1f;

	/// <summary>
	/// 「下一世界」按钮的点击入口。
	/// 不使用 HorizontalScrollSnap.NextScreen()：它依赖内部 _lerp 状态，
	/// 过渡进行中调用会被静默忽略（表现为"点了没反应"），
	/// 这里改为按世界序号显式跳转，并对边界做判断。
	/// </summary>
	private void GoToNextWorldPage()
	{
		NavigateToWorldIndex(_currentPage.WorldIndex + 1);
	}

	/// <summary>
	/// 「上一世界」按钮的点击入口。滑动翻页已关闭，这是唯一的后退方式。
	/// </summary>
	private void GoToPreviousWorldPage()
	{
		NavigateToWorldIndex(_currentPage.WorldIndex - 1);
	}

	/// <summary>
	/// 按 WorldConfig.Index 跳页。
	///
	/// 不用 _pages 的下标直接加减：_pages 的顺序来自
	/// MonoSingleton&lt;WorldConfigs&gt;.GetAllConfigs()，那是 Dictionary.Values，
	/// 顺序不保证等于 Index 顺序。所以先按 Index 找到目标世界配置，
	/// 再用 WorldId 反查页面下标。
	/// </summary>
	private void NavigateToWorldIndex(int worldIndex)
	{
		if (Time.unscaledTime - _lastPageChangeTime < 0.35f)
		{
			return;
		}
		if (worldIndex < 0)
		{
			return;
		}
		WorldConfig targetConfig = MonoSingleton<WorldConfigs>.Instance.GetAllConfigs().Find((WorldConfig c) => c.Index == worldIndex);
		if (targetConfig == null)
		{
			return;
		}
		UIWorldPage targetPage;
		if (!_pagesByIds.TryGetValue(targetConfig.Id, out targetPage))
		{
			return;
		}
		int pageIndex = _pages.IndexOf(targetPage);
		if (pageIndex < 0 || pageIndex == _currentPageIndex)
		{
			return;
		}
		_lastPageChangeTime = Time.unscaledTime;
		_selector.GoToScreen(pageIndex);
	}

	private void OnSelectionChangeEnded(int pageIndex)
	{
		OnPageChanged(pageIndex);
	}

	private void OnSelectionPageChanged(int pageIndex)
	{
		OnPageChanged(pageIndex);
	}

	private void OnPageChanged(int pageIndex)
	{
		if (_currentPageIndex != pageIndex)
		{
			_currentPageIndex = pageIndex;
			if (_currentPage != null)
			{
				_currentPage.OnPageExit();
			}
			_currentPage = _pages[pageIndex];
			_currentPage.OnPageEnter();
			UpdateHeroParent();
			if (App.Instance.Player.LevelManager.GetWorldData(_currentPage.WorldId).IsUnlocked)
			{
				PlayerPrefs.SetString("PageName", _currentPage.WorldId);
			}
			App.Instance.Player.LevelManager.LastSelectedWorldId = _currentPage.WorldId;
			if (this.WorldSelectedEvent != null)
			{
				this.WorldSelectedEvent(_currentPage.WorldId);
			}
		}
	}

	private void OnWorldUnlocked(string worldId)
	{
		if (_pagesByIds.ContainsKey(worldId))
		{
			UIWorldPage uIWorldPage = _pagesByIds[worldId];
			_latestUnlockedPage.OnWorldUnlocked();
			_latestUnlockedPage = uIWorldPage;
			uIWorldPage.OnWorldUnlocked();
			WorldConfig nextWorld = MonoSingleton<WorldConfigs>.Instance.GetNextWorld(worldId);
			if (nextWorld.IsValid() && _pagesByIds.ContainsKey(nextWorld.Id))
			{
				_pagesByIds[nextWorld.Id].UpdateNextWorldPanel();
			}
			AnimateHero();
		}
	}
}