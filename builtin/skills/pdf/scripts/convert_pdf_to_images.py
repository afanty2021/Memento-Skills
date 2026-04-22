#!/usr/bin/env python3
"""Convert PDF pages to PNG images using pypdfium2 (no system deps needed)."""
import os
import sys


def convert(pdf_path: str, output_dir: str, *, max_dim: int = 1600, scale: float = 2.0):
    try:
        import pypdfium2 as pdfium
    except ImportError:
        print(
            "Error: pypdfium2 is not installed. Install it with: pip install pypdfium2",
            file=sys.stderr,
        )
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    try:
        pdf = pdfium.PdfDocument(pdf_path)
    except Exception as e:
        print(f"Error: Failed to open PDF '{pdf_path}': {e}", file=sys.stderr)
        sys.exit(1)

    page_count = len(pdf)
    for i in range(page_count):
        page = pdf[i]
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()

        w, h = image.size
        if w > max_dim or h > max_dim:
            ratio = min(max_dim / w, max_dim / h)
            image = image.resize((int(w * ratio), int(h * ratio)))

        image_path = os.path.join(output_dir, f"page_{i + 1}.png")
        image.save(image_path)
        print(f"Saved page {i + 1} as {image_path} (size: {image.size})")

    print(f"Converted {page_count} pages to PNG images in {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: convert_pdf_to_images.py <input.pdf> <output_dir> [--scale 2.0] [--max-dim 1600]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_directory = sys.argv[2]

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("outdir")
    parser.add_argument("--scale", type=float, default=2.0)
    parser.add_argument("--max-dim", type=int, default=1600)
    args = parser.parse_args()

    convert(args.pdf, args.outdir, max_dim=args.max_dim, scale=args.scale)
