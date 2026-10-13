"""檢查常見 GFM 呈現問題，僅使用 Python 標準函式庫。

這是啟發式檢查，不是完整的 GFM 解析器或合規認證。
未閉合圍欄本身是合法語法，但常會意外吞掉後續內容，因此仍提出警告。
僅檢查頂層區塊；容器內的清單、引言與原始 HTML 不在檢查範圍。
規範來源：https://github.github.com/gfm/
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
DELIMITER = re.compile(r":?-+:?")


def table_cells(line: str) -> list[str]:
    """分割表格欄位；GFM 要求程式碼內的管線符號同樣使用反斜線跳脫。"""
    cells = [""]
    escaped = False
    for char in line.strip():
        if char == "|" and not escaped:
            cells.append("")
        else:
            cells[-1] += char
        escaped = char == "\\" and not escaped
    if len(cells) > 1 and not cells[0].strip():
        cells.pop(0)
    if len(cells) > 1 and not cells[-1].strip():
        cells.pop()
    return [cell.strip() for cell in cells]


def check_gfm(text: str) -> list[str]:
    """回傳含原始行號的警告，不修改輸入文字。

為避免把範例誤認為正文，略過圍欄、縮排程式碼與 HTML 區塊。
複雜容器語法保留給 GFM 解析器與 GitHub 預覽判斷。
"""
    warnings: list[str] = []
    fence: tuple[str, int, int] | None = None
    previous = ""
    html_end: str | None = None
    for number, line in enumerate(text.splitlines(), 1):
        if fence:
            char, length, _ = fence
            if re.fullmatch(r" {0,3}" + re.escape(char) + "{" + str(length) + r",}[ \t]*", line):
                fence = None
            continue
        if html_end:
            if (html_end == "blank" and not line.strip()) or (
                html_end != "blank" and html_end in line.lower()
            ):
                html_end = None
            previous = ""
            continue
        stripped = line.lstrip()
        if stripped.startswith("<"):
            lower = stripped.lower()
            if lower.startswith("<!--"):
                html_end = None if "-->" in lower else "-->"
            elif re.match(r"<(script|pre|style|textarea)(?:\s|>|$)", lower):
                tag = re.match(r"<(\w+)", lower).group(1)
                html_end = None if f"</{tag}>" in lower else f"</{tag}>"
            else:
                html_end = "blank"
            previous = ""
            continue
        # 這些行可能屬於容器或縮排程式碼，不在頂層檢查範圍。
        if line.startswith(("    ", "\t")) or re.match(r" {0,3}(?:>|[-+*]\s|\d+[.)]\s)", line):
            previous = ""
            continue
        match = FENCE.match(line)
        if match:
            marker, info = match.groups()
            if marker[0] == "`" and "`" in info:
                warnings.append(f"L{number} [GFM001] 反引號圍欄的資訊字串含反引號，無法作為開啟圍欄。")
            else:
                fence = (marker[0], len(marker), number)
            previous = ""
            continue
        if re.match(r"^ {0,3}#{1,6}[^#\s]", line):
            warnings.append(f"L{number} [GFM002] 疑似標題的 # 後缺少空白，會呈現為一般文字；若本來就是文字可忽略。")
        if "|" in line:
            cells = table_cells(line)
            if cells and all(DELIMITER.fullmatch(cell) for cell in cells) and previous.strip():
                if len(table_cells(previous)) != len(cells):
                    warnings.append(f"L{number} [GFM003] 表頭與分隔列欄數不同，無法形成 GFM 表格。")
        previous = line
    if fence:
        warnings.append(f"L{fence[2]} [GFM004] 圍欄未閉合；GFM 允許延伸至檔尾，請確認是否意外包含後續內容。")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("documents", nargs="+", type=Path, help="欲檢查的 UTF-8 Markdown 文件")
    args = parser.parse_args()
    result = 0
    for document in args.documents:
        try:
            warnings = check_gfm(document.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError) as error:
            print(f"{document}: 無法讀取文件：{error}")
            result = 2
            continue
        for warning in warnings:
            print(f"{document}:{warning}")
        if warnings:
            result = max(result, 1)
        else:
            print(f"{document}: 未發現涵蓋範圍內的 GFM 問題（非完整合規認證）。")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
