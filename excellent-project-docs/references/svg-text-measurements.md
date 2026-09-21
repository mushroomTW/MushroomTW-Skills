# SVG Text Measurements

The fitting table and the pinning rules in [visual-readme](visual-readme.md) are measured facts, not conventions, and one of them is easy to get wrong in a way no DOM query reveals. This file records the numbers, the decisive test behind each, and how to re-measure. Read it before changing those rules, or when a banner's text does not land where the recipe says it should.

## How these were measured

Headless Chrome, a probe page that references the SVG through `<img>` and a script that writes measurements into a `<pre>`; the probe page and the command are under **Re-measuring** below.

`getComputedTextLength()` **does not report the adjustment `textLength` applies.** It returns the natural advance even when the rendered line is a different width, and it cannot tell whether the glyphs were scaled. So the tables below carry two columns: `DOM`, from the script, and `Rendered`, read off a screenshot. The `DOM` column alone is incomplete, and where the two disagree the screenshot is right.

The decisive test for glyph scaling is a **single character** with a `textLength` larger than its natural advance: one glyph has no inter-glyph gaps, so any change in its width can only have come from the glyph itself.

## Per-character advances

Latin, Chrome, `Segoe UI`, font-size 20, the string `Handcrafted Documents` (21 characters):

| Sample | Measured advance | Per character | Coefficient |
| --- | --- | --- | --- |
| regular | 215.2 units | 10.25 | 0.512 × font-size |
| weight 800 | 240.0 units | 11.43 | 0.571 × font-size |
| `Arial` fallback, regular | 215.7 units | 10.27 | 0.514 × font-size |

The recipe uses 0.48 and 0.58. Both sit at or below the measurement — 0.48 is about 6 % under Segoe UI regular — which is the intended direction: the coefficients are a floor for a font the writer has not seen, not a description of one.

`DejaVu Sans`, `Liberation Sans`, and `Noto Sans` are the fallbacks on the Linux readers where a banner most often overflows, and none of them was installed on the machine these numbers came from, so their width is **not measured here**. Treat a banner whose text sits within 5 % of its column edge as unverified until it has been rendered.

CJK advances one em per glyph in every font, which makes it the one script whose width is arithmetic:

| Sample | Measured | Per glyph |
| --- | --- | --- |
| `測試文字`, font-size 20, `system-ui` stack | 80.0 units | 1.000 × font-size |
| `專案文件產生器`, font-size 64, explicit CJK stack | 448.0 units | 1.000 × font-size |

## What `textLength` does to a line

CJK, font-size 64, `專案文件產生器` (7 glyphs, natural advance 448):

| `textLength` | `lengthAdjust` | DOM | Rendered |
| --- | --- | --- | --- |
| — | — | 448.0 | square glyphs, 448 wide |
| 896 | `spacingAndGlyphs` | 896.0 | glyphs stretched horizontally — no longer square |
| 896 | `spacing` | **448.0** | square glyphs, tracking opened to the full 896 |
| 224 | `spacingAndGlyphs` | 224.0 | glyphs squeezed horizontally |
| 128 on one glyph `專` (natural 64) | `spacingAndGlyphs` | 128.0 | that single glyph drawn 2× wide |
| 128 on one glyph `專` (natural 64) | `spacing` | 64.0 | untouched |

Latin, font-size 40, `Handcrafted Documents` (natural advance 430.3):

| `textLength` | `lengthAdjust` | DOM | Rendered |
| --- | --- | --- | --- |
| — | — | 430.3 | normal |
| 700 | `spacing` | **430.4** | glyphs intact, tracking opened to 700 |
| 700 | `spacingAndGlyphs` | 700.0 | glyphs stretched wider |
| 280 | `spacing` | **430.4** | the word space collapsed (`HandcraftedDocuments`) and the line stayed 430 wide — it never reached 280 |
| 280 | `spacingAndGlyphs` | 280.0 | glyphs condensed |

Two facts follow, and they are the whole reason the recipe splits Latin from CJK:

- **`spacing` can only widen.** Given a target narrower than the string it removes the inter-glyph space — including the word space, which runs two words together — and then stops, so the line still overflows. It is safe for glyphs and useless as a guarantee against overflow.
- **`spacingAndGlyphs` always reaches the target, by scaling the glyphs.** That is what makes it the only pin that guarantees a too-wide line fits, and what makes it wrong for CJK, where a scaled square glyph is visibly wrong.

The DOM reports `448.0` and `430.4` for the two `spacing` rows, which is the same number as no pin at all. Reading only the DOM is how a writer concludes that `spacing` is ignored and reaches for `spacingAndGlyphs` — which is exactly the mistake that squeezes a Chinese tagline.

The four cases, as markup — render it and look at the glyphs, because the DOM will not tell you:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320">
  <rect width="1200" height="320" fill="#0f0f0f"/>
  <!-- natural: correct for CJK, 7 x 32 = 224 units -->
  <text x="60" y="60" font-size="32" fill="#fff">專案文件產生器</text>
  <!-- widened without touching the glyphs: lengthAdjust="spacing" -->
  <text x="60" y="140" font-size="32" fill="#fff" textLength="448" lengthAdjust="spacing">專案文件產生器</text>
  <!-- WRONG: the glyphs are stretched horizontally -->
  <text x="60" y="220" font-size="32" fill="#fff" textLength="448" lengthAdjust="spacingAndGlyphs">專案文件產生器</text>
  <!-- WRONG: the glyphs are squeezed, and the square is gone -->
  <text x="60" y="300" font-size="32" fill="#fff" textLength="160" lengthAdjust="spacingAndGlyphs">專案文件產生器</text>
</svg>
```

The same four cases with Latin text read as stretched and condensed letterforms rather than broken squares, which is why the recipe allows `spacingAndGlyphs` there and forbids it here.

## Re-measuring

Probe page: reference the SVG through `<img>` inside a container of the width under test, apply `img { max-width: 100% }`, and write the results on load. An SVG loaded through `<img>` has no DOM to query, so a text advance has to be measured from a second copy of the same `<text>` inlined in the page:

```html
<img id="a" src="banner.svg" alt="banner">
<svg viewBox="0 0 1200 400" width="1200" height="400">
  <text id="t" x="0" y="40" font-size="20" font-family="'Segoe UI', sans-serif">Handcrafted Documents</text>
</svg>
<pre id="out">pending</pre>
<script>
  window.addEventListener('load', () => requestAnimationFrame(() => {
    const el = document.getElementById('a');
    const r = el.getBoundingClientRect();
    document.getElementById('out').textContent =
      `img box=${r.width.toFixed(1)}x${r.height.toFixed(1)}` +
      ` natural=${el.naturalWidth}x${el.naturalHeight}` +
      ` text advance=${document.getElementById('t').getComputedTextLength().toFixed(1)}`;
  }));
</script>
```

```bash
chrome --headless=new --disable-gpu --no-sandbox \
  --run-all-compositor-stages-before-draw --virtual-time-budget=5000 \
  --dump-dom <page.html> | sed -n '/<pre id="out">/,/<\/pre>/p'
```

Traps:

- Without `--virtual-time-budget` and a measurement that runs after load, the images are not loaded yet and every size reads `0×0`.
- A relative `<img>` under `file://` may not load at all; embedding the SVG as `data:image/svg+xml,...` is reliable (`#` must be written `%23`).
- `--screenshot=` takes an absolute path only; a relative one silently produces no file.
- An inline `<text>` measures the same advances as one inside an `<img>`, but the inline copy has no `textLength` context unless you give it one — copy the attributes you are testing, not just the string.
- For anything about glyph shape, take the screenshot. The DOM cannot answer it.

## When a render disagrees with this file

Trust the render. Record the new measurement here with the browser, the font, and the font-size it came from, and note which readers the font represents — the table is only as good as the machine it was measured on, and a coefficient that has never been checked against a Linux fallback is the likeliest source of an overflow.
