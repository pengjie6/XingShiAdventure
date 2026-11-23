using UnityEngine;
using System.Collections;
using UnityEditor;
using UnityEngine.UI;
using System.IO;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System;
using System.Linq;

// 注意：本类只是 MenuItem 工具集合，并非 Inspector 绘制器。
// 之前这里误加了 [CustomEditor(typeof(PrefabsTools))]，但类继承的是 ScriptableWizard 而不是 Editor，
// Unity 会持续报 "uses the CustomEditor attribute but does not inherit from Editor"，故移除。
public class PrefabsTools : ScriptableWizard
{
    [UnityEditor.MenuItem("Tools/Apply Selected Prefabs")]
    static void ApplySelectedPrefabs()
    {
        //获取选中的gameobject对象
        GameObject[] selectedsGameobject = Selection.gameObjects;

        // 旧版 PrefabType / GetPrefabParent / ReplacePrefab 在 2018.3 之后已被移除，改用新 Prefab API
        foreach (GameObject obj in selectedsGameobject)
        {
            // 是否为预设（预制体）实例
            GameObject instanceRoot = PrefabUtility.GetOutermostPrefabInstanceRoot(obj);
            if (instanceRoot == null)
            {
                continue;
            }

            // 对应旧的 GetPrefabObject / GetPrefabParent：拿到源预制体资源的路径
            string assetPath = PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(instanceRoot);
            if (string.IsNullOrEmpty(assetPath))
            {
                continue;
            }

            // 对应旧的 ReplacePrefab(obj, parent, ReplacePrefabOptions.ConnectToPrefab)：写回源预制体并保持连接
            PrefabUtility.SaveAsPrefabAssetAndConnect(instanceRoot, assetPath, InteractionMode.UserAction);
        }

        //刷新
        AssetDatabase.Refresh();
    }
    [UnityEditor.MenuItem("Tools/SetAllChild")]
    static void SetAllChild()
    {
        GameObject terrain = GameObject.Find("StaticEnvironment");
        SetAllChild(terrain.transform);
    }

    static void SetAllChild(Transform tf)
    {
        foreach (var mc in tf.GetComponentsInChildren<MeshCollider>(true))
        {
            MeshFilter mf = mc.GetComponent<MeshFilter>();
            if (mc.transform.localScale.x < 0 && mc.transform.localScale.y < 0 && mc.transform.localScale.z < 0)
            {
                mc.transform.localScale = new Vector3(-mc.transform.localScale.x, -mc.transform.localScale.y, -mc.transform.localScale.z);

                GameObject go = new GameObject("SetAllChildSetAllChild");
                go.transform.parent = mc.transform;
                go.transform.localPosition = Vector3.zero;
                go.transform.localEulerAngles = Vector3.zero;
                go.transform.localScale = new Vector3(-1, -1, -1);
                go.layer = mc.gameObject.layer;
                UnityEditorInternal.ComponentUtility.CopyComponent(mc);
                UnityEditorInternal.ComponentUtility.PasteComponentAsNew(go);
                GameObject.DestroyImmediate(mc);
            }
        }
    }


    [UnityEditor.MenuItem("Tools/SetAllChild222222")]
    static void SetAllChild2222222222()
    {
        GameObject terrain = GameObject.Find("StaticEnvironment");
        SetAllChild2222222222(terrain.transform);
    }

    static void SetAllChild2222222222(Transform tf)
    {
        foreach (var mc in tf.GetComponentsInChildren<MeshCollider>(true))
        {
            MeshFilter mf = mc.GetComponent<MeshFilter>();
            if (mf == null)
            {
                continue;
            }
            if (mc.transform.localScale.x < 0 && mc.transform.localScale.y < 0 && mc.transform.localScale.z < 0)
            {
                Debug.LogError( mc.name);
            }
        }
    }
}
