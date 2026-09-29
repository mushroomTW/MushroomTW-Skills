# RimTest Redux Integrate

[English](rimtest-redux-integrate.md) | **繁體中文**

> 本文件位於 `docs/`。skill 本體位於 [`rimtest-redux-integrate/SKILL.md`](../rimtest-redux-integrate/SKILL.md)。

一個用 [RimTest Redux](https://steamcommunity.com/sharedfiles/filedetails/?id=3762405308) 在遊戲執行中測試 RimWorld 模組的 skill，同時避開那些讓測試因錯誤原因通過或失敗的時序與 Harmony 陷阱。

headless 單元測試把 Unity stub 掉，所以看不到 Harmony patch 是否真的套用、延遲的啟動工作何時完成、圖集與注入的翻譯最後長什麼樣子。遊戲內測試補的正是這一塊——前提是它等對時機、比對對的基準。

## 觸發時機

只要是撰寫或除錯 RimWorld 模組的測試，包括確認 Harmony patch 真的套用、追查啟動時序造成的失敗。請求不需要提到 RimTest Redux。

skill 會先**詢問**要不要用 RimTest Redux；倉庫裡已經有依賴它的 companion 測試 mod 時就略過這一問。你選了別的做法，skill 其餘部分就不介入。

## 涵蓋內容

1. **專案結構**——測試放在獨立的開發用 companion mod，載入順序排在被測 mod 之前，參考被測 mod 建置出的 DLL，且不隨它發布。
2. **撰寫測試**——`[TestSuite]`／`[Test]` 類別，失敗先收集再一次列出；前置條件（地圖、相容 mod）不存在時，記下略過原因後提早 `return`。
3. **原版對照組**——以 Harmony reverse patch 取回未被改寫的原版方法，逐項比對被測 mod 的結果，內容與順序都比；只比對經過原版入口產生的物件，因為其他 mod 會直接寫入快取欄位。
4. **探針**——記錄狀態的 `[HarmonyPatch]` 類別，涵蓋目標的每個多載，找不到任何目標時由 `Prepare()` 停用自己。
5. **時序**——RimTest Redux 的啟動時執行會等排入的長事件跑完，但不會等 Task、執行緒或跨多幀分批處理的工作；遇到這類 mod，就由自訂 driver 等待被測 mod 提供的完成訊號。
6. **回報**——每種設定組合各跑一次並記錄通過、失敗、略過數，每個失敗都歸類為被測 mod 的問題、原版行為或 RimTest Redux 自身行為。

skill 另附 [`references/rimtest-redux-api.md`](../rimtest-redux-integrate/references/rimtest-redux-api.md)：改寫自 RimTest Redux README 的框架規則、attribute 與斷言 API，自訂 driver 需透過反射呼叫的 internal 成員，以及三個範例——基本 suite、收集失敗並記錄略過、自訂 driver。

## Harmony 陷阱

| 陷阱 | 做法 |
| --- | --- |
| 含 `catch … when` 篩選器的方法無法被 patch（"Incorrect code generation for exception block"） | 要被 patch 的方法改用獨立的多個 `catch` |
| `Harmony.PatchCategory(string)` 取呼叫端組件，在測試裡呼叫會讓 Mono 崩潰 | 明確傳入被測 mod 的組件 |

## 需求

執行測試需要 RimWorld 1.6，並安裝 `brrainz.harmony`、`ilyvion.Laboratory`、`ilyvion.rimtestredux` 三個 mod；測試組件目標為 net481。

## 安裝

請在倉庫根目錄讓 `skills` CLI 自動偵測相容 agent，並安裝此 skill：

```bash
npx skills add . --skill rimtest-redux-integrate
```

若要安裝到個人層級，請加上 `--global`；未加時為專案層級。若採手動安裝，請把 `rimtest-redux-integrate/` 複製到 host 文件指定的 skills 目錄，不要假設特定 runtime 路徑。

> [!NOTE]
> 第一次執行 `npx` 可能會下載 CLI。若 host 只在 session 啟動時偵測 skill，安裝後請重新載入或重啟。
