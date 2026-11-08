# RimWorld SmashTools 框架架構與功能整合

[English](rimworld-smashtools.md) | **繁體中文**

> 本文件位於 `docs/`。Skill 本體位於 [`rimworld-smashtools/SKILL.md`](../rimworld-smashtools/SKILL.md)。

全方位支援 RimWorld 知名高效能 C# 基礎框架 [SmashTools](https://github.com/SmashPhil/SmashTools) 的整合與開發指引。本 Skill 協助開發者與 AI Agent 選用 SmashTools 現成功能、規劃模組架構，並妥善處理生命週期、組件載入、發布打包與相容性等複雜問題。

SmashTools 為複雜大型模組提供了歷經考驗的底層設施——包含多格大型實體尋路、執行緒安全物件池、自訂 UI 渲染管線與 XML 深度序列化。本 Skill 能精準將模組的功能需求對應至 SmashTools 的最佳化原生 API，避免不必要的重複造輪子。

## 觸發時機

當需要為 RimWorld 模組規劃架構、整合 SmashTools 各項功能、最佳化執行效能或打包發布模組時觸發。

若專案中已設定或引用 SmashTools，Agent 可自動選用本 Skill，亦可透過自然語言直接叫用：

```text
使用 $rimworld-smashtools，將 SmashTools 整合至這個 RimWorld 模組。
```

針對已完成基礎接入的專案：

```text
使用 $rimworld-smashtools，先查現成功能，再實作這個模組需要的 UI 與資料儲存邏輯。
```

## 模組架構導覽

SmashTools 劃分為多個專業子系統，並分別由專屬參考文件提供詳細規範：

| 子系統領域 | 參考文件 | 範疇與核心功能 |
| --- | --- | --- |
| **核心基底設施** | [`core.md`](../rimworld-smashtools/references/core.md) | 高效能原生集合、2D/3D 幾何運算、執行緒安全物件池（Object Pooling）、背景工作調度器（Job Dispatching）與動態委派。 |
| **多格實體尋路** | [`pathfinding.md`](../rimworld-smashtools/references/pathfinding.md) | 佔據多網格大型實體的尋路導航演算法、空間啟發式搜尋與匈牙利最佳指派演算法（Hungarian Algorithm）。 |
| **UI 與自訂渲染** | [`ui-rendering.md`](../rimworld-smashtools/references/ui-rendering.md) | 視窗管理框架、GUI 狀態快取、自訂 Mesh 與 Shader 渲染管線，以及動畫曲線內插評估。 |
| **資料儲存與 XML** | [`data.md`](../rimworld-smashtools/references/data.md) | 深度 XML 序列化、結構化遊戲存檔持久化、高效率集合擴充方法與序列化契約介面。 |
| **事件與修補擴充** | [`events-patching.md`](../rimworld-smashtools/references/events-patching.md) | 自訂目標選取處理器（Targeting）、高吞吐量事件匯流排系統，以及 Patch 擴充契約。 |
| **診斷與效能分析** | [`diagnostics.md`](../rimworld-smashtools/references/diagnostics.md) | 高效能日誌記錄、LRU 記憶體快取、執行耗時 Profiling 與編譯期 Roslyn 程式碼分析器。 |
| **建置與發布打包** | [`integration.md`](../rimworld-smashtools/references/integration.md) | 多版本編譯矩陣配置、相依提供者管理、組件身分（Assembly Identity）驗證、發布打包與過期產物清理。 |
| **模組生命週期** | [`lifecycle.md`](../rimworld-smashtools/references/lifecycle.md) | 嚴格規範靜態建構子、`Mod` 實例化與遊戲啟動各階段的執行順序；Patch 擁有權隔離、背景執行緒安全關閉與啟動故障排查。 |
| **功能快速索引** | [`features.md`](../rimworld-smashtools/references/features.md) | 依照業務功能需求快速查找對應參考文件的總索引。 |

## 關鍵整合規範

- **優先使用本機來源**：優先查找本機 SmashTools 原始碼或編譯完成的 DLL，僅在首次導入且本機完全缺失時才連網下載；日常程式碼查核與 API 瀏覽維持完全離線運作。
- **嚴守生命週期載入順序**：確保程式碼遵循 RimWorld 引擎各載入階段的界線（例如：嚴禁在靜態建構子階段過早存取未初始化的 `DefDatabase`）。
- **背景執行緒優雅清理**：確保背景 Worker、執行緒池與 Job 任務在場景切換或遊戲退出時皆能優雅終止，防止記憶體洩漏與孤兒執行緒。
- **維護組件獨立性**：嚴格隔離模組組件與 SmashTools 相依庫，避免因重複定義引發 Type 碰撞或跨組件載入異常。

## 環境需求與先決條件

- **遊戲本體**：RimWorld 1.6+ 執行環境。
- **開發工具**：.NET SDK 與 RimWorld 遊戲核心參考組件。
- **SmashTools 組件**：相容版本之 `SmashTools.dll` 及其相依程式集。

## 安裝方式

請於儲存庫根目錄下，透過 `skills` CLI 自動偵測相容 Agent 並安裝本 Skill：

```bash
npx skills add . --skill rimworld-smashtools
```

加上 `--global` 可安裝至個人使用者層級；未加時預設為專案層級。若採用手動安裝，請將 `rimworld-smashtools/` 目錄複製至 Agent 主機所指定的 Skills 目錄中。

> [!NOTE]
> 首次執行 `npx` 可能需要下載 CLI。若 Agent 主機僅在啟動對話階段載入 Skills，安裝完成後請重新載入或重啟主機環境。
