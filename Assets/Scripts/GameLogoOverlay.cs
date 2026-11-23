using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

/// <summary>
/// 游戏 Logo 展示（独立脚本，不改动场景 YAML，也不依赖任何现有脚本的改动）。
///
/// 两处使用：
///   1) Boot 场景：Resources/Branding/GameLogo.png，居中大图，压在“加载中...”上方。
///   2) Game 场景主页：Resources/Branding/GameLogoHome.png（透明底，可融入背景），
///      以“播放键”为基准贴在它上方，位置由运行时实测的按钮矩形算出来，
///      所以换机型 / 换分辨率都不会压到播放键，也不会掉到英雄脚下。
///
/// 主页另外做了“只在主页显示”的处理：UIMenuStack 栈顶不是主页（打开了商店、任务弹窗等）时，
/// logo 自动淡出，避免压在弹窗内容上。
///
/// 换图只需替换对应的 PNG，不用动代码。
/// </summary>
public class GameLogoOverlay : MonoBehaviour
{
    // ---------------- Boot 场景 ----------------
    private const string BootResourcePath = "Branding/GameLogo";
    private const string BootOverlayName = "GameLogoOverlay";
    private const float BootSizeRatio = 0.62f;
    private const float BootOffsetRatio = 0.26f;

    // ---------------- Game 场景主页 ----------------
    private const string HomeResourcePath = "Branding/GameLogoHome";
    private const string HomePanelName = "HomePanel";
    private const string HomeBadgeName = "GameLogoHomeBadge";
    private const string HomeWatcherName = "~GameLogoWatcher";
    private const string PlayButtonName = "ButtonPlay";

    /// <summary>Logo 高度占画布高度的比例（画布按高度匹配，所以这个比例跨机型稳定）。</summary>
    private const float HomeHeightRatio = 0.175f;

    /// <summary>Logo 底边与播放键顶边之间留的空隙（占画布高度）。</summary>
    private const float HomeGapRatio = 0.018f;

    /// <summary>Logo 顶边最多上探到中心线以下这么多，再往上就会压到英雄。</summary>
    private const float HomeCeilingRatio = 0.06f;

    /// <summary>找不到播放键时的兜底：Logo 底边距画布底部的比例。</summary>
    private const float HomeFallbackBottomRatio = 0.205f;

    /// <summary>空间被挤压时允许的最小高度，避免缩成一条线。</summary>
    private const float HomeMinHeightRatio = 0.10f;

    /// <summary>图片本身的宽高比（784x700），用来校验贴图有没有被 NPOT 缩放拉变形。</summary>
    private const float HomeDesignAspect = 784f / 700f;

    private const float HomeRiseDistance = 14f;
    private const float FadeInDuration = 0.35f;
    private const float VisibilityCheckInterval = 0.2f;
    private const float VisibilityFadeSpeed = 6f;

    private static Sprite _bootSprite;
    private static Sprite _homeSprite;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void Bootstrap()
    {
        SceneManager.sceneLoaded -= OnSceneLoaded;
        SceneManager.sceneLoaded += OnSceneLoaded;
        HandleScene(SceneManager.GetActiveScene());
    }

    private static void OnSceneLoaded(Scene scene, LoadSceneMode mode)
    {
        HandleScene(scene);
    }

    private static void HandleScene(Scene scene)
    {
        if (!scene.IsValid())
        {
            return;
        }

        if (scene.name == "Boot")
        {
            ShowBootLogo();
        }
        else if (scene.name == "Game")
        {
            WatchHomePanel();
        }
    }

    // ------------------------------------------------------------------ Boot

    private static void ShowBootLogo()
    {
        if (GameObject.Find(BootOverlayName) != null)
        {
            return;
        }

        Sprite sprite = LoadSprite(BootResourcePath, ref _bootSprite);
        if (sprite == null)
        {
            return;
        }

        Canvas canvas = FindUiCanvas();
        if (canvas == null)
        {
            return;
        }

        RectTransform canvasRect = canvas.rootCanvas.transform as RectTransform;
        float canvasWidth = canvasRect != null && canvasRect.rect.width > 1f ? canvasRect.rect.width : 755f;
        float canvasHeight = canvasRect != null && canvasRect.rect.height > 1f ? canvasRect.rect.height : 1334f;
        float size = Mathf.Min(canvasWidth, canvasHeight) * BootSizeRatio;

        GameObject go = new GameObject(BootOverlayName, typeof(RectTransform), typeof(CanvasGroup), typeof(Image));
        go.transform.SetParent(canvas.transform, false);
        go.transform.SetAsLastSibling();

        RectTransform rect = (RectTransform)go.transform;
        rect.anchorMin = new Vector2(0.5f, 0.5f);
        rect.anchorMax = new Vector2(0.5f, 0.5f);
        rect.pivot = new Vector2(0.5f, 0.5f);
        rect.sizeDelta = new Vector2(size, size);
        rect.anchoredPosition = new Vector2(0f, canvasHeight * BootOffsetRatio);
        rect.localScale = Vector3.one;

        ApplySprite(go, sprite);

        GameLogoOverlay overlay = go.AddComponent<GameLogoOverlay>();
        overlay.StartCoroutine(overlay.FadeIn(go.GetComponent<CanvasGroup>()));
    }

    private static Canvas FindUiCanvas()
    {
        Canvas[] canvases = Object.FindObjectsOfType<Canvas>();

        Canvas fallback = null;
        for (int i = 0; i < canvases.Length; i++)
        {
            Canvas canvas = canvases[i];
            if (canvas == null || !canvas.isActiveAndEnabled)
            {
                continue;
            }

            if (canvas.name == "AppCanvas")
            {
                return canvas;
            }

            if (fallback == null)
            {
                fallback = canvas;
            }
        }

        return fallback;
    }

    // ------------------------------------------------------------------ Game / 主页

    /// <summary>HomePanel 初始是 inactive，只能在进入 Game 场景后边走边找。</summary>
    private static void WatchHomePanel()
    {
        if (GameObject.Find(HomeWatcherName) != null)
        {
            return;
        }

        GameObject host = new GameObject(HomeWatcherName);
        Object.DontDestroyOnLoad(host);
        GameLogoOverlay watcher = host.AddComponent<GameLogoOverlay>();
        watcher.StartCoroutine(watcher.AttachHomeBadgeCR());
    }

    private IEnumerator AttachHomeBadgeCR()
    {
        // 最多等 30 秒；HomePanel 由 UIMenuStack 打开，通常在 1 秒内出现。
        float waited = 0f;
        while (waited < 30f)
        {
            Scene scene = SceneManager.GetActiveScene();
            if (scene.name != "Game")
            {
                break;
            }

            Transform home = FindHomePanel(scene);
            if (home != null)
            {
                AttachBadge(home);
                break;
            }

            yield return new WaitForSecondsRealtime(0.25f);
            waited += 0.25f;
        }

        // 角标已挂到 HomePanel 上，中继对象没用了。
        Destroy(gameObject);
    }

    private static Transform FindHomePanel(Scene scene)
    {
        GameObject[] roots = scene.GetRootGameObjects();
        for (int i = 0; i < roots.Length; i++)
        {
            Transform[] all = roots[i].GetComponentsInChildren<Transform>(true);
            for (int j = 0; j < all.Length; j++)
            {
                if (all[j] != null && all[j].name == HomePanelName)
                {
                    return all[j];
                }
            }
        }

        return null;
    }

    private static void AttachBadge(Transform home)
    {
        if (home.Find(HomeBadgeName) != null)
        {
            return;
        }

        Sprite sprite = LoadSprite(HomeResourcePath, ref _homeSprite);
        if (sprite == null)
        {
            return;
        }

        RectTransform homeRect = home as RectTransform;
        if (homeRect == null)
        {
            return;
        }

        float aspect = sprite.rect.height > 0.01f ? sprite.rect.width / sprite.rect.height : HomeDesignAspect;
        if (Mathf.Abs(aspect - HomeDesignAspect) > 0.08f)
        {
            // 贴图被 NPOT 缩放过（786x705 -> 1024x512），logo 会被横向拉扁。
            Debug.LogWarning("[Logo] GameLogoHome.png 宽高比异常：" + aspect.ToString("0.00")
                + "（应为 " + HomeDesignAspect.ToString("0.00") + "），请在 Inspector 里关掉 NPOT Scale 后 Reimport。");
        }

        GameObject go = new GameObject(HomeBadgeName, typeof(RectTransform), typeof(CanvasGroup), typeof(Image));
        go.transform.SetParent(home, false);
        // 放在最上层，避免被主页顶部的暗色渐变（ShadowTop）压住。
        go.transform.SetAsLastSibling();

        RectTransform rect = (RectTransform)go.transform;
        rect.anchorMin = new Vector2(0.5f, 0f);
        rect.anchorMax = new Vector2(0.5f, 0f);
        rect.pivot = new Vector2(0.5f, 0f);
        rect.localScale = Vector3.one;

        CanvasGroup group = go.GetComponent<CanvasGroup>();
        group.alpha = 0f;
        group.blocksRaycasts = false;
        group.interactable = false;

        ApplySprite(go, sprite);

        RectTransform playRect = FindDeep(home, PlayButtonName) as RectTransform;

        GameLogoOverlay badge = go.AddComponent<GameLogoOverlay>();
        badge.StartCoroutine(badge.RunHomeBadge(homeRect, playRect, rect, group, aspect));
    }

    private static Transform FindDeep(Transform root, string name)
    {
        if (root.name == name)
        {
            return root;
        }

        Transform[] all = root.GetComponentsInChildren<Transform>(true);
        for (int i = 0; i < all.Length; i++)
        {
            if (all[i] != null && all[i].name == name)
            {
                return all[i];
            }
        }

        return null;
    }

    /// <summary>
    /// 主页角标的常驻驱动：每帧摆放位置，每 0.2 秒判断一次“当前是不是还在主页”，
    /// 不在主页（商店、任务弹窗、设置等压在上面）就淡出。
    /// </summary>
    private IEnumerator RunHomeBadge(RectTransform homeRect, RectTransform playRect, RectTransform badge, CanvasGroup group, float aspect)
    {
        float riseTime = 0f;
        float nextCheck = 0f;
        bool visible = true;

        while (true)
        {
            if (homeRect == null || badge == null || group == null)
            {
                yield break;
            }

            // 面板还没激活时矩形算不准，等它显示出来再摆位置、再开始淡入。
            if (!homeRect.gameObject.activeInHierarchy)
            {
                group.alpha = 0f;
                yield return null;
                continue;
            }

            if (Time.unscaledTime >= nextCheck)
            {
                nextCheck = Time.unscaledTime + VisibilityCheckInterval;
                visible = IsHomeOnTop(homeRect);
            }

            float homeHeight = homeRect.rect.height;
            if (homeHeight < 1f)
            {
                homeHeight = 1334f;
            }

            float rise = HomeRiseDistance * (1f - Mathf.Clamp01(riseTime / FadeInDuration));
            LayoutBadge(homeRect, playRect, badge, homeHeight, aspect, rise);

            riseTime += Time.unscaledDeltaTime;
            float entrance = Mathf.Clamp01(riseTime / FadeInDuration);
            float targetAlpha = visible ? entrance : 0f;
            group.alpha = Mathf.MoveTowards(group.alpha, targetAlpha, Time.unscaledDeltaTime * VisibilityFadeSpeed);

            yield return null;
        }
    }

    private static void LayoutBadge(RectTransform homeRect, RectTransform playRect, RectTransform badge, float homeHeight, float aspect, float rise)
    {
        float bottom;
        if (playRect != null)
        {
            // 用播放键实测的顶边作为基准，跨机型都不会压到按钮。
            Bounds bounds = RectTransformUtility.CalculateRelativeRectTransformBounds(homeRect, playRect);
            bottom = bounds.max.y + homeHeight * HomeGapRatio;
        }
        else
        {
            bottom = -homeHeight * 0.5f + homeHeight * HomeFallbackBottomRatio;
        }

        float height = homeHeight * HomeHeightRatio;

        // 顶边不许越过中心线以下的警戒线，否则会压到英雄。
        float room = -homeHeight * HomeCeilingRatio - bottom;
        if (room > 0f && height > room)
        {
            height = room;
        }

        float minHeight = homeHeight * HomeMinHeightRatio;
        if (height < minHeight)
        {
            height = minHeight;
        }

        badge.sizeDelta = new Vector2(height * aspect, height);
        badge.anchoredPosition = new Vector2(0f, bottom + homeHeight * 0.5f - rise);
    }

    /// <summary>当前主页是否还在最上层 —— 有任何菜单/弹窗压在上面就返回 false。</summary>
    private static bool IsHomeOnTop(RectTransform homeRect)
    {
        if (!homeRect.gameObject.activeInHierarchy)
        {
            return false;
        }

        if (!MonoSingleton<UIMenuStack>.IsCreated())
        {
            return true;
        }

        UIMenu top = MonoSingleton<UIMenuStack>.Instance.Peek();
        if (top == null)
        {
            return true;
        }

        Transform topTransform = top.transform;
        return topTransform == homeRect || topTransform.IsChildOf(homeRect);
    }

    // ------------------------------------------------------------------ 公共

    private static void ApplySprite(GameObject go, Sprite sprite)
    {
        Image image = go.GetComponent<Image>();
        image.sprite = sprite;
        image.preserveAspect = true;
        image.raycastTarget = false;
    }

    private static Sprite LoadSprite(string path, ref Sprite cache)
    {
        if (cache != null)
        {
            return cache;
        }

        Sprite sprite = Resources.Load<Sprite>(path);
        if (sprite != null)
        {
            cache = sprite;
            return cache;
        }

        Texture2D texture = Resources.Load<Texture2D>(path);
        if (texture == null)
        {
            Debug.LogWarning("[Logo] 没找到 Resources/" + path + ".png");
            return null;
        }

        cache = Sprite.Create(
            texture,
            new Rect(0f, 0f, texture.width, texture.height),
            new Vector2(0.5f, 0.5f),
            100f);
        cache.name = "GameLogo_" + path;
        return cache;
    }

    private IEnumerator FadeIn(CanvasGroup group)
    {
        if (group == null)
        {
            yield break;
        }

        float time = 0f;
        group.alpha = 0f;
        while (time < FadeInDuration)
        {
            time += Time.unscaledDeltaTime;
            group.alpha = Mathf.Clamp01(time / FadeInDuration);
            yield return null;
        }

        group.alpha = 1f;
    }
}
