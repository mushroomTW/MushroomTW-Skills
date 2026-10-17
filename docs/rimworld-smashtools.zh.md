# RimWorld SmashTools 整合與使用

[English](rimworld-smashtools.md) | **繁體中文**

協助選用 SmashTools 現成功能開發 RimWorld 模組，並處理接入、發布、初始化與載入問題。技能入口：[`rimworld-smashtools/SKILL.md`](../rimworld-smashtools/SKILL.md)。

功能導覽涵蓋 CoreLib 原生集合、執行緒與物件池，以及搜尋與多格尋路、目標選取、遊戲事件、UI／視窗、渲染、存檔與 XML、動畫曲線、快取、效能分析、日誌、擴充方法與編譯期分析器。依使用目的查找代表 API、限制與來源位置。

安裝後可自動選用，或直接叫用：

```text
使用 $rimworld-smashtools，將 SmashTools 整合至這個 RimWorld 模組。
```

已接入的專案也可要求：

```text
使用 $rimworld-smashtools，先查現成功能，再實作這個模組需要的 UI 與資料儲存邏輯。
```

優先使用本機來源與 DLL。建置需要相容工具及遊戲參考組件；遊戲內驗證需要實際啟動遊戲。

## 內容

- `references/features.md`：功能索引，依用途選讀以下文件。
- `references/core.md`：集合、幾何、執行緒、工作派發、物件池與動態委派。
- `references/pathfinding.md`：搜尋、最佳指派與多格尋路。
- `references/ui-rendering.md`：UI、視窗、GUI 狀態、渲染與動畫曲線。
- `references/data.md`：存檔、XML、資料結構、擴充方法與輔助介面。
- `references/events-patching.md`：目標選取、事件與修補擴充契約。
- `references/diagnostics.md`：日誌、快取、效能分析、除錯與編譯期分析器。
- `references/integration.md`：相依提供者、專案參考、輸出與發布、組件身分及更新殘留。
- `references/lifecycle.md`：初始化、修補擁有者、背景工作、遊戲驗證與故障定位。
