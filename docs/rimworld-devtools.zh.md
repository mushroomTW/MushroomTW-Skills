# RimWorld 模組測試

[English](rimworld-devtools.md) | **繁體中文**

本 skill 協助 agent 接入 SmashPhil DevTools、撰寫並執行 RimWorld 遊戲內測試及讀取結果。也提供 Smoke Test、子程序 Test Plan 與效能基準測試的使用指引。

技能入口：[`rimworld-devtools/SKILL.md`](../rimworld-devtools/SKILL.md)。

## 使用

在 skills host 安裝本儲存庫的 `rimworld-devtools/` 後，可直接叫用：

```text
使用 $rimworld-devtools，替這個已接入 DevTools 的模組新增地圖內測試，執行指定 fixture 並回報結果。
```

其他適用請求：調查 fixture 未被發現、設定 Test.log 與報告，或為指定方法比較基準效能。技能允許自動選用，適用於明確選用或已接入 DevTools 的專案。

接入需要 DevTools 來源／DLL、.NET 10 SDK 與遊戲參考組件；測試在 RimWorld 內執行。

優先使用本機 DevTools；只有首次導入且本機缺少時，才從 GitHub 的 `SmashPhil/DevTools` 下載。日常使用與 API 查核不需連網。

## 內容

- `references/testing.md`：組件載入、fixture、非拋例外式斷言、參數化、協程與狀態清理。
- `references/running.md`：UI／CLI、設定、結果新鮮度、完成證據、計數與故障判讀。
- `references/advanced.md`：Smoke Test 宿主、Test Plan 資料還原、Benchmark 限制。
