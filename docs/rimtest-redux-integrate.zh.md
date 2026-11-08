# RimTest Redux Integrate

[English](rimtest-redux-integrate.md) | **繁體中文**

> 本文件位於 `docs/`。Skill 本體位於 [`rimtest-redux-integrate/SKILL.md`](../rimtest-redux-integrate/SKILL.md)。

專為在 RimWorld 遊戲執行期透過 [RimTest Redux](https://steamcommunity.com/sharedfiles/filedetails/?id=3762405308) 進行模組測試而設計的 Skill，協助建立高可靠度的遊戲內整合測試，並避開因啟動時序競爭或 Harmony 陷阱所導致的假性通過或誤報失敗。

脫機（Headless）單元測試通常以 Stub 替代 Unity 引擎與遊戲子系統，因此無法驗證 Harmony Patch 是否真實注入生效、延遲的啟動任務（Deferred Startup Tasks）何時完成，也無法確認材質圖集（Atlas）與動態注入的字串翻譯在實際環境中的最終狀態。遊戲內整合測試精準填補了此項關鍵盲區——但前提是測試必須等待精確的啟動時序，並以正確的原版基準（Baseline）進行比對。

## 觸發時機

適用於撰寫或除錯 RimWorld 模組的測試流程，包含確認 Harmony Patch 實際生效、排查啟動時序競爭等情境。使用者的提問無需明確指明 RimTest Redux。

Skill 在介入前會先**主動詢問**開發者是否採用 RimTest Redux 作為測試框架；若儲存庫中已存在依賴 RimTest Redux 的伴隨測試 Mod，則會自動略過此詢問。若開發者選擇其他測試架構，Skill 其餘流程將不會強行介入。

## 涵蓋內容

1. **獨立伴隨測試 Mod（Companion Mod）**：測試程式碼獨立收納於專為開發環境設計的伴隨測試 Mod 中，其載入順序排在被測 Mod 之前，直接參考其編譯完成的 DLL，且絕對不會隨正式版本打包發布。
2. **撰寫遊戲內測試**：使用 `[TestSuite]` 與 `[Test]` 標註測試類別與方法，採集批次失敗報告一次呈現；當前置環境（如特定地圖或相容 Mod）缺失時，測試會記錄明確的略過原因並提早結束。
3. **Harmony 原版對照組（Reverse Patch）**：運用 Harmony Reverse Patch 動態還原未被竄改的原版方法，逐項嚴格比對被測 Mod 的輸出內容與集合順序；比對範圍僅限於原版入口建立的物件，防範其他外部 Mod 直寫快取欄位的干擾。
4. **狀態探針（Probes）**：以 `[HarmonyPatch]` 類別記錄執行期狀態，涵蓋目標方法的所有多載（Overload）；若找不到目標方法，則由 `Prepare()` 主動自我停用以防遊戲崩潰。
5. **啟動時序防護**：RimTest Redux 原生啟動機制會等待排程長任務（`LongEvent`），但無法自動等待非同步 `Task`、背景工作執行緒或跨多幀分散的非同步操作；針對此類 Mod，自訂測試驅動器（Driver）會等待被測 Mod 明確發布的就緒訊號。
6. **細緻回報分類**：針對各類設定組合個別執行測試並統計通過、失敗與略過數量；所有失敗項目皆精確分類為「被測 Mod 程式錯誤」、「原版既有行為」或「RimTest Redux 框架行為」。

本 Skill 亦隨附 [`references/rimtest-redux-api.md`](../rimtest-redux-integrate/references/rimtest-redux-api.md)，詳細整理了 RimTest Redux 框架規範、Attribute 宣告、斷言 API、自訂 Driver 專用的反射內部成員，以及三套完整範例（基礎測試套件、含略過說明的收集式斷言、自訂測試驅動器）。

## Harmony 與 Mono 陷阱防護

| 陷阱問題 | 成因與錯誤診斷 | 解決方案 |
| --- | --- | --- |
| **`catch … when` 例外篩選器** | Mono 編譯器重大限制：對包含例外篩選器的方法進行 Patch 時會報錯「Incorrect code generation for exception block」。 | 在任何需要被 Patch 注入的方法中，將 `catch … when` 改寫為標準的循序 `catch` 區塊。 |
| **`Harmony.PatchCategory(string)`** | `PatchCategory` 預設依賴呼叫端組件（Calling Assembly）；若自測試組件中直接呼叫，會引發 Mono 執行期崩潰。 | 呼叫分類 Patch 時，務必明確傳入目標 Mod 的 Assembly 參考。 |

## 環境需求與先決條件

執行遊戲內測試需要 RimWorld 1.6，並於模組載入清單中依序啟用下列模組：
- `brrainz.harmony`（Harmony 函式庫）
- `ilyvion.Laboratory`（測試前置框架）
- `ilyvion.rimtestredux`（RimTest Redux 測試執行器）

伴隨測試專案之編譯目標必須為 `.NET Framework 4.8.1` (`net481`)。

## 安裝方式

請於儲存庫根目錄下，透過 `skills` CLI 自動偵測相容 Agent 並安裝本 Skill：

```bash
npx skills add . --skill rimtest-redux-integrate
```

加上 `--global` 可安裝至個人使用者層級；未加時預設為專案層級。若採用手動安裝，請將 `rimtest-redux-integrate/` 目錄複製至 Agent 主機所指定的 Skills 目錄中。

> [!NOTE]
> 首次執行 `npx` 可能需要下載 CLI。若 Agent 主機僅在啟動對話階段載入 Skills，安裝完成後請重新載入或重啟主機環境。
