---
name: patent-drawing
description: >
  Draw patent figures by writing code. Use it whenever the user wants a patent drawing or figure: flowcharts, block
  or system diagrams, mechanical line drawings, perspective, section or exploded views, reference numerals and lead
  lines, a figure set for a US or Chinese application, or fixing a figure that already exists; 画专利附图、流程图、框图、
  结构图、爆炸图、标附图标记. You write the drawing program for each figure yourself, render it, look at the result and
  correct it. No drawing templates and no image generation.
---

# Patent drawing: write the code, look at the picture, fix it

You draw each figure by writing your own program for it. There is no drawing engine to call and no template to fill in:
choose the geometry, layout and libraries that suit this invention. Code is used because a figure must match the
specification exactly and be regenerated when the claims change. Do not generate figures with an image model: it adds
structure nobody disclosed, which can be new matter, and it gets text and numerals wrong.

## 1. Before drawing

- Work out which figures the claims and description need. Each one must show something the text relies on: every claimed
  feature appears in some figure (37 CFR 1.83(a)). Do not fill out a set of six views: rear and side views rarely show a feature.
- Draw only what the material discloses. A dimension, rib, hole or connection you cannot source is a question for the user,
  not a guess. If the shape is unknown, draw it schematically and say so.
- When sources conflict, use the version the user settled or the newest evidence, and list the conflict. A feature disclosed but undecided (an option, a Pro model): draw it or leave it out, and flag that choice, since matter left out at filing cannot be added later.
- A part the text implies but never names (a shaft between blade and motor): draw the simplest form so nothing floats, and list it as an assumption to confirm.
- A section view needs a parent view for its cutting line. If none was requested, add a minimal one and say why.
- Keep one numeral register for the case, `drawings/numerals.json`: part or step name, numeral, where the text defines it (the source material until a specification exists). One part
  has one numeral across all figures and two parts never share one. US practice often uses even numbers (10, 12, 14) so
  parts can be added later; Chinese practice often uses 1, 2, 3. Method steps use S101 or 202 style.
- Design patents follow different rules, and the figures are the claim. Views must agree exactly, so draw them from one 3D model,
  not separately in 2D. No numerals. Unclaimed environment is dashed in the US. Tell the user an attorney must review the views.

## 2. Write the program

Put each figure's source in `drawings/src/` and its output in `drawings/out/`. Rerunning the source must reproduce the figure.

Pick what fits; these are starting points, not rules:

| Input | Suits |
|---|---|
| Method steps, system blocks | Graphviz or hand-placed SVG. Hand placement often gives a calmer sheet. |
| Text and sketches of a structure | A small parametric model of your own in Python or JS: parts as shapes, drawn back to front so nearer parts hide farther ones. For 3D, cadquery or build123d, then project. |
| STEP or other CAD | `pip install cadquery-ocp` and project with OpenCascade `HLRBRep_Algo`. Geometry stays exact and views agree. |
| Photo | Use it as a reference to measure and to overlay against. Redraw the outline in code; do not trace shadows and reflections. |

Check what is installed first, and install what you need into a virtual environment. `rsvg-convert` or `cairosvg` turns SVG into PNG and PDF.

What the output must obey, whatever you write it in (US 37 CFR 1.84; check the national rule for other offices):

- Black lines on white. No color, gray fill, shading washes or photographs.
- A4 or Letter. A4 margins at least 2.5 cm top, 2.5 left, 1.5 right, 1.0 bottom. No frame, title block, dimensions or scale.
- Solid lines of even weight, about 0.35 mm for outlines. Dashed only where it means something, such as hidden or phantom parts.
- Numbers and letters at least 3.2 mm high, box text included. That usually means capitals and spelled-out units, since a lowercase "ms" falls short. Numerals are plain: no circle, brackets or quotes. They sit off hatching and lines; a lead line may cross hatching to reach its part.
- Lead lines short and not crossing each other, ending on the part they name. An underlined numeral marks a surface; a freestanding arrow marks a whole assembly.
- `FIG. 1` labels larger than the numerals; in China `图1`. Several figures may share a sheet if clearly separated. Sheets numbered `1/3` at top center, inside the margins.
- Text only where needed: short labels in flowchart and block boxes, in English for a US filing. All of it must match the specification word for word. A long flowchart barely fits A4 at this text size: drop START and END terminals or split it across sheets.
- A figure must stay readable when reduced to two thirds.
- A landscape figure in the US has its top toward the right edge of the sheet.

Lessons from drawing real assemblies:

- Exploded views: move parts along the assembly axis, one after another, keeping coaxial parts aligned and no parts overlapping. Do not push parts radially out from the center: coaxial parts lose alignment and small parts collide. Long pins slide out along their own axis. In the US, a bracket groups separated parts of one assembly (1.84(h)(1)).
- Filleted parts: a CAD outline is often a tangent edge. Parts that hide each other in assembly show gaps once exploded, so draw tangent edges in exploded views and check every outline closes.
- Section views: mark the cutting line as a broken line with arrows for the direction of sight, and put the section's view number at each end (`3B`), per 1.84(h)(3). Hatch different parts in different directions, and keep hatching sparse.
- Place numerals in columns or around the outside of the figure, then route lead lines inward. It is the easiest way to avoid crossings.

## 3. Look at it and correct it

Rendering without error proves nothing. After every render:

1. Open the PNG and actually look at it. Check each of: a line missing or an outline not closed; parts overlapping or floating; text clipped or touching a line; a lead line crossing another or ending on the wrong part; a flowchart arrow pointing the wrong way or a branch left unlabeled; proportions contradicting the material. Zoom into crowded areas.
2. Write a check script and run it on every figure, using coordinates your program logs: no color and no gray region thicker than antialiasing (thresholding first would let a gray fill pass), nothing inside the margins, text height measured on pixels, text not touching lines or other text, lead lines not crossing and each one landing on its named part, flow lines not crossing, every numeral on the sheet in the register and every register entry in some figure. The script finds only what it tests, so it does not replace looking.
3. Fix the source, not the output. Then render and look again. Keep going until a careful reviewer would have nothing to point at. Do not hand over a first render.

When the specification exists, cross-check: every numeral in the figures appears in the text and the reverse, the name matches each time, and every figure is in the brief description of the drawings in order.

## 4. Hand over

Give the user the figures (PNG to view; SVG and PDF to file or edit), the source, the register and a short note: what each figure shows and which claim feature it supports, anything drawn schematically or assumed, and what you could not confirm. For a portable SVG and a PDF that will not depend on installed fonts, convert text to outlines or embed the fonts, then confirm with `pdffonts`. Pass on anything legally significant you notice in the material, such as a public disclosure date. If they want a change, change the program and regenerate, keeping numerals stable. The figures are a draft for an attorney's review, not a formal filing.
