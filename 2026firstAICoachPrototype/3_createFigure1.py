"""
Stack baseline traffic-light panels (face → knee → arm) into one publication PDF and PNG.

Reads, in order:
  results/baseline/bestHyperparametersSetResults/trafficLights_facePain.{pdf|png}
  results/baseline/bestHyperparametersSetResults/trafficLights_kneePain.{pdf|png}
  results/baseline/bestHyperparametersSetResults/trafficLights_armPain.{pdf|png}

If all three PDFs exist, they are merged vertically on a single page (vector graphics
preserved). Otherwise, if all three PNGs exist, they are stacked at 300 dpi with the
same matplotlib PDF settings used elsewhere (embeds Type 42 fonts / editable text where
matplotlib applies).

Output:
  results/combinedAnalysis/figure1.pdf
  results/combinedAnalysis/figure1.png

Requires PyMuPDF (``pip install pymupdf``) when combining PDF sources. For PNG-only,
matplotlib and Pillow are sufficient.
"""

from __future__ import annotations

from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
RESULTS_ROOT = SCRIPT_ROOT / "results"
TRAFFIC_DIR = RESULTS_ROOT / "baseline" / "bestHyperparametersSetResults"
OUT_PDF = RESULTS_ROOT / "combinedAnalysis" / "figure1.pdf"
OUT_PNG = RESULTS_ROOT / "combinedAnalysis" / "figure1.png"

STEMS_IN_ORDER = (
    "trafficLights_facePain",
    "trafficLights_kneePain",
    "trafficLights_armPain",
)


def _resolve_inputs() -> tuple[list[Path], str]:
    pdfs = [TRAFFIC_DIR / f"{s}.pdf" for s in STEMS_IN_ORDER]
    pngs = [TRAFFIC_DIR / f"{s}.png" for s in STEMS_IN_ORDER]
    if all(p.is_file() for p in pdfs):
        return pdfs, "pdf"
    if all(p.is_file() for p in pngs):
        return pngs, "png"
    missing_pdf = [str(p) for p in pdfs if not p.is_file()]
    missing_png = [str(p) for p in pngs if not p.is_file()]
    raise FileNotFoundError(
        "Need either all three PDFs or all three PNGs under "
        f"{TRAFFIC_DIR}.\n"
        f"Missing PDFs: {missing_pdf}\n"
        f"Missing PNGs: {missing_png}"
    )


def _stack_pdfs_fitz(paths: list[Path], out_pdf: Path, out_png: Path) -> None:
    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise SystemExit(
            "Combining PDF inputs requires PyMuPDF. Install with: pip install pymupdf"
        ) from e

    src_docs = [fitz.open(p) for p in paths]
    try:
        rects = [d[0].rect for d in src_docs]
        w = max(r.width for r in rects)
        total_h = sum(r.height for r in rects)
        out = fitz.open()
        page = out.new_page(width=w, height=total_h)
        y = 0.0
        for doc, r in zip(src_docs, rects):
            h = r.height
            x_off = (w - r.width) / 2.0
            rect = fitz.Rect(x_off, y, x_off + r.width, y + h)
            page.show_pdf_page(rect, doc, 0)
            y += h
        
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        
        # Save PDF
        out.save(out_pdf)
        
        # Render and save PNG at 300 DPI
        pix = page.get_pixmap(dpi=300)
        pix.save(out_png)
        
        out.close()
    finally:
        for d in src_docs:
            d.close()


def _stack_pngs_matplotlib(paths: list[Path], out_pdf: Path, out_png: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    pil_images = [Image.open(p).convert("RGB") for p in paths]
    w = max(im.width for im in pil_images)
    resized: list[Image.Image] = []
    for im in pil_images:
        if im.width != w:
            new_h = int(round(im.height * (w / im.width)))
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS  # type: ignore[attr-defined]
            im = im.resize((w, new_h), resample)
        resized.append(im)
    total_h = sum(im.height for im in resized)
    combined = Image.new("RGB", (w, total_h), (255, 255, 255))
    y = 0
    for im in resized:
        combined.paste(im, (0, y))
        y += im.height

    # Single-panel width matches publication traffic-light PDF (183 mm single column)
    width_in = 183 / 25.4
    height_in = width_in * (total_h / w)
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.imshow(np.asarray(combined))
    ax.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    
    # Save both PDF and PNG formats
    fig.savefig(out_pdf, format="pdf", bbox_inches="tight", pad_inches=0, dpi=300)
    fig.savefig(out_png, format="png", bbox_inches="tight", pad_inches=0, dpi=300)
    
    plt.close(fig)


def main() -> None:
    paths, kind = _resolve_inputs()
    if kind == "pdf":
        _stack_pdfs_fitz(paths, OUT_PDF, OUT_PNG)
    else:
        _stack_pngs_matplotlib(paths, OUT_PDF, OUT_PNG)
    print(f"Wrote:\n  - {OUT_PDF}\n  - {OUT_PNG}")


if __name__ == "__main__":
    main()