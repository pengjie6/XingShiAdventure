using UnityEngine;
using UnityEngine.UI;

namespace TMPro
{
	// Unity 2021 的 uGUI 1.0.0 中 Graphic 不再 RequireComponent(CanvasRenderer)，
	// 运行时 AddComponent 出来的 Graphic 不会自动带 CanvasRenderer，这里显式声明。
	[RequireComponent(typeof(CanvasRenderer))]
	public class TMP_SelectionCaret : MaskableGraphic
	{
		public override void Cull(Rect clipRect, bool validRect)
		{
		}
	}
}