# RimWorld DevTools 遊戲內測試與效能診斷

[English](rimworld-devtools.md) | **繁體中文**

> 本文件位於 `docs/`。Skill 本體位於 [`rimworld-devtools/SKILL.md`](../rimworld-devtools/SKILL.md)。

協助 AI Agent 接入 SmashPhil DevTools 測試工具套件，於 RimWorld 遊戲執行期內進行自動化測試執行、多程序測試計畫（Test Plan）、冒煙測試（Smoke Test）、智慧日誌診斷與微基準效能測試（Benchmark）。

脫機（Headless）單元測試無法捕捉 Unity 引擎狀態、自訂圖形渲染上下文或複雜的多模組載入相依性。SmashPhil DevTools 提供真實遊戲環境下的測試執行能力，並在斷言失敗時避免遊戲程序崩潰，確保測試流程穩定跑完。

## 觸發時機

當需要為採用 SmashPhil DevTools 的 RimWorld 模組編寫、執行或排查遊戲內測試與效能基準測試時觸發。

若專案中已設定或引用 DevTools，Agent 可自動選用本 Skill，亦可透過自然語言直接叫用：

```text
使用 $rimworld-devtools，替這個已接入 DevTools 的模組新增地圖測試，執行指定 fixture 並回報結果。
```

## 核心功能

1. **遊戲內測試夾具（Fixture）與斷言**：
   - 採用結構化測試夾具與非拋出式斷言（`Test.Assert`），允許測試套件在遭遇單一錯誤時持續執行，一次收集並回報所有失敗點，而非中途崩潰中斷。
   - 完整支援參數化測試、Unity 協程（`IEnumerator`）非同步測試，以及嚴謹的測試後狀態清理機制，避免殘留資料污染後續測試。

2. **自動化冒煙測試（Smoke Tests）**：
   - 透過 `SmokeTestManager` 執行 `--smoke-test` 命令列模式，自動監控遊戲啟動、場景切換與初始化日誌，無需逐一撰寫業務斷言即可迅速驗證穩定性。
   - 支援經由 `Configs/SmokeTestConfig.xml` 自訂警告與錯誤等級門檻，提早攔截例外。

3. **子程序矩陣測試計畫（Test Plans）**：
   - 使用 `--test-plan <name>` 針對不同的模組清單啟動獨立子程序進行矩陣式整合測試。
   - 具備設定保護機制：執行前自動備份玩家的 `ModsConfig.xml`，並於子程序結束後自動還原，防範測試過程損壞日常存檔環境。

4. **智慧日誌解析與失敗歸因**：
   - 自動解析 `Test.log` 與遊戲即時主控台輸出，過濾無關的引擎環境雜訊與原版無害警告，將問題精確分類為：
     - **Mod 程式缺陷**：被測模組本身的邏輯錯誤。
     - **原版行為特性**：原版遊戲既有機制或已知引擎限制。
     - **環境配置問題**：測試夾具未載入、相依組件遺失或設定檔損壞。

5. **微基準效能測試（Performance Benchmarks）**：
   - 運用 `DevTools.Benchmarking`（`[BenchmarkClass]`、`[Benchmark]`）精確測量特定方法的執行耗時、記憶體分配與幀率表現。
   - 支援自訂統計表格（平均值、中位數、標準差、取樣次數），並內建防範 JIT 編譯器死碼消除（Dead-code Elimination）與常數折疊（Constant Folding）的測量保護機制。

## 參考資料

- [`references/testing.md`](../rimworld-devtools/references/testing.md)——組件載入機制、測試夾具撰寫、非拋出式斷言、參數化、協程支援與測試狀態還原。
- [`references/running.md`](../rimworld-devtools/references/running.md)——UI 與 CLI 執行方式、執行期設定、日誌新鮮度驗證、完成標記與故障診斷。
- [`references/advanced.md`](../rimworld-devtools/references/advanced.md)——Smoke Test 宿主設定、Test Plan 狀態防護與 Benchmark 進階限制。

## 環境需求與先決條件

- **遊戲本體**：RimWorld 1.6+ 執行環境（執行測試時需啟動遊戲）。
- **開發工具**：.NET SDK 與 RimWorld 遊戲核心參考組件。
- **DevTools 組件**：相容版本之 SmashPhil DevTools 組件（`DevTools.dll`）。優先採用本機現有來源；僅在首次導入且本機缺少時才自 `SmashPhil/DevTools` 下載。

## 安裝方式

請於儲存庫根目錄下，透過 `skills` CLI 自動偵測相容 Agent 並安裝本 Skill：

```bash
npx skills add . --skill rimworld-devtools
```

加上 `--global` 可安裝至個人使用者層級；未加時預設為專案層級。若採用手動安裝，請將 `rimworld-devtools/` 目錄複製至 Agent 主機所指定的 Skills 目錄中。

> [!NOTE]
> 首次執行 `npx` 可能需要下載 CLI。若 Agent 主機僅在啟動對話階段載入 Skills，安裝完成後請重新載入或重啟主機環境。
