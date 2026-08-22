import os
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF

def combine_pngs(dir_path, file1, file2, out_file):
    path1 = os.path.join(dir_path, file1)
    path2 = os.path.join(dir_path, file2)
    out_path = os.path.join(dir_path, out_file)

    # Load images
    img1 = Image.open(path1)
    img2 = Image.open(path2)

    # Calculate combined dimensions
    new_width = max(img1.width, img2.width)
    new_height = img1.height + img2.height

    # Create new blank image (white background)
    combined_img = Image.new('RGB', (new_width, new_height), 'white')

    # Paste images vertically
    combined_img.paste(img1, (0, 0))
    combined_img.paste(img2, (0, img1.height))

    # Add (a) and (b) annotations
    draw = ImageDraw.Draw(combined_img)
    
    # Attempt to load a scalable default font (requires Pillow >= 10.1.0)
    # If using an older version, fallback to the standard small default font
    try:
        font = ImageFont.load_default(size=36)
    except TypeError:
        font = ImageFont.load_default()

    # Position text slightly offset from the top-left of each image
    text_color = (0, 0, 0) # Black
    draw.text((15, 15), "(a)", font=font, fill=text_color)
    draw.text((15, img1.height + 15), "(b)", font=font, fill=text_color)

    # Save
    combined_img.save(out_path)
    print(f"Successfully saved combined PNG: {out_path}")

def combine_pdfs(dir_path, file1, file2, out_file):
    path1 = os.path.join(dir_path, file1)
    path2 = os.path.join(dir_path, file2)
    out_path = os.path.join(dir_path, out_file)

    # Open source PDFs
    doc1 = fitz.open(path1)
    doc2 = fitz.open(path2)
    
    page1 = doc1[0]
    page2 = doc2[0]

    # Calculate combined dimensions
    r1 = page1.rect
    r2 = page2.rect
    new_width = max(r1.width, r2.width)
    new_height = r1.height + r2.height

    # Create output PDF and a new blank page
    out_doc = fitz.open()
    new_page = out_doc.new_page(width=new_width, height=new_height)

    # Overlay the source PDFs onto the new page
    new_page.show_pdf_page(fitz.Rect(0, 0, r1.width, r1.height), doc1, 0)
    new_page.show_pdf_page(fitz.Rect(0, r1.height, r2.width, new_height), doc2, 0)

    # Add (a) and (b) annotations higher up
    # Changed Y from 25 to 14 to move the text up to the top edge
    new_page.insert_text(fitz.Point(15, 14), "(a)", fontsize=14, color=(0, 0, 0))
    new_page.insert_text(fitz.Point(15, r1.height + 14), "(b)", fontsize=14, color=(0, 0, 0))

    # Save
    out_doc.save(out_path)
    print(f"Successfully saved combined PDF: {out_path}")

if __name__ == "__main__":
    # Define paths and filenames
    target_dir = "results/extendedTestSetFaceCounterfactual"
    
    base_name_top = "trafficLights_facePain_1.0"
    base_name_bot = "trafficLights_facePain_0.65"
    base_name_out = "trafficLights_facePain_combined"

    # 1. Process PNGs
    combine_pngs(
        target_dir, 
        f"{base_name_top}.png", 
        f"{base_name_bot}.png", 
        f"{base_name_out}.png"
    )

    # 2. Process PDFs
    combine_pdfs(
        target_dir, 
        f"{base_name_top}.pdf", 
        f"{base_name_bot}.pdf", 
        f"{base_name_out}.pdf"
    )