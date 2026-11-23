using UnityEngine;

public class UIMenuChooseLanguagePanel : UIMenuPopup
{
	[SerializeField]
	private UIGameButton _buttonClose;

	[SerializeField]
	private UIGameButton _englishButton;

	[SerializeField]
	private UIGameButton _frenchButton;

	protected override void Awake()
	{
		base.Awake();
		_buttonClose.OnClick(OnCloseButtonClicked);
		_buttonClose.ActivateOnBackKey();
		// 项目已全量中文化，法文按钮没有对应内容，隐藏以避免两个一样的选项
		_frenchButton.gameObject.SetActive(false);
		_englishButton.OnClick(delegate
		{
			OnLanguageSelected(SystemLanguage.English);
		});
		_frenchButton.OnClick(delegate
		{
			OnLanguageSelected(SystemLanguage.French);
		});
	}

	private void OnLanguageSelected(SystemLanguage language)
	{
		App.Instance.Player.SettingsManager.Language = language.ToString();
		OnCloseButtonClicked();
	}

	private void OnCloseButtonClicked()
	{
		if (MonoSingleton<UIMenuStack>.Instance.Peek() == this)
		{
			Hide();
		}
	}
}