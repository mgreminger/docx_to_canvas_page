# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "beautifulsoup4",
#     "canvasapi",
#     "python-dotenv",
# ]
# ///

import os
import re
from typing import cast
import argparse
import subprocess
import tempfile
from bs4 import BeautifulSoup
from canvasapi import Canvas
from dotenv import load_dotenv

def main():
    # Load environment variables from the .env file
    load_dotenv()

    # --- Command Line Arguments ---
    parser = argparse.ArgumentParser(description="Convert a Word DOCX file into a Canvas Page.")
    parser.add_argument("docx_file", help="Path to the .docx file to convert")
    args = parser.parse_args()

    docx_path = args.docx_file
    if not os.path.exists(docx_path):
        print(f"Error: File '{docx_path}' not found.")
        return

    # Use the filename (without extension) as the Canvas Page Title
    page_title = os.path.splitext(os.path.basename(docx_path))[0]

    # --- Configuration ---
    API_URL = os.getenv("CANVAS_API_URL")
    API_KEY = os.getenv("CANVAS_API_KEY")
    COURSE_ID = os.getenv("CANVAS_COURSE_ID")

    if not API_KEY or not COURSE_ID:
        print("Error: Canvas API Key or Course ID missing. Please check your .env file.")
        return

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(COURSE_ID)

    # --- Temporary Environment ---
    # The 'with' block ensures the folder and all its contents are cleanly deleted upon exit
    with tempfile.TemporaryDirectory() as temp_dir:
        html_file = os.path.join(temp_dir, "output.html")
        
        print(f"Converting '{docx_path}'...")
        print(f"Using temporary directory: {temp_dir}")
        
        # --- Step 1: Run Pandoc ---
        # --extract-media is pointed to the temp_dir. Pandoc will place images there 
        # and automatically link to them in the generated HTML.
        subprocess.run([
            "pandoc", docx_path, 
            "-o", html_file, 
            f"--extract-media={temp_dir}", 
            "--mathjax"
        ], check=True)

        # --- Step 2: Parse HTML ---
        print("Parsing HTML and checking for alt text...")
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        # Remove Blockquotes
        for bq in soup.find_all("blockquote"):
            bq.name = "div" 
            bq["style"] = "margin-left: 40px;"

        # Find all heading tags (h1 through h6)
        for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            # If the header contains an image, convert the header tag to a standard div
            if header.find('img'):
                header.name = 'div'
            # If the header is completely empty, remove it to clean up spacing
            elif not header.get_text(strip=True):
                header.decompose()

        # Shift heading hierarchy if an h1 is present
        if soup.find('h1'):
            # find_all generates a static list, so changing names mid-loop won't cause double-processing
            for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                if header.name == 'h1':
                    header.name = 'h2'
                elif header.name == 'h2':
                    header.name = 'h3'
                elif header.name in ['h3', 'h4', 'h5', 'h6']:
                    header.name = 'h4'

        # --- Step 3: Upload images and update HTML links ---
        # Create a clean prefix from the page title (removes spaces/special chars) to prevent Canvas overwrites
        safe_prefix = re.sub(r'[^A-Za-z0-9]', '_', page_title)

        for img in soup.find_all("img"):
            local_image_path = img.get("src")
            
            if isinstance(local_image_path, str) and os.path.exists(local_image_path):
                # Rename the file locally to namespace it before uploading
                original_name = os.path.basename(local_image_path)
                unique_name = f"{safe_prefix}_{original_name}"
                unique_local_path = os.path.join(os.path.dirname(local_image_path), unique_name)
                
                os.rename(local_image_path, unique_local_path)
                
                print(f"Uploading {unique_name}...")
                success, response = course.upload(unique_local_path)
                
                if success:
                    # Update to the live Canvas URL
                    img["src"] = response["url"]
                    
                    # Handle Alt Text length limits
                    alt_text = cast(str, img.get("alt", ""))
                    if not alt_text:
                        img["alt"] = "NEEDS ALT TEXT"
                    elif len(alt_text) > 120:
                        # 1. Create the default-styled details HTML structure
                        details = soup.new_tag("details")
                        
                        summary = soup.new_tag("summary")
                        summary.string = "Detailed image description"
                        
                        desc_p = soup.new_tag("p")
                        desc_p.string = alt_text
                        
                        details.append(summary)
                        details.append(desc_p)
                        
                        # 2. Apply generic short alt text
                        img["alt"] = "Image with detailed description below."
                        
                        # 3. Safely insert the details block after the image's container
                        parent_fig = img.find_parent("figure")
                        
                        if parent_fig:
                            parent_fig.append(details)
                        else:
                            img.insert_after(details)

                else:
                    print(f"Failed to upload {unique_local_path}")

        # --- Step 4: Create the Canvas Page ---
        print(f"Creating Canvas page: '{page_title}'...")
        new_page = course.create_page(wiki_page={
            'title': page_title,
            'body': str(soup) 
        })

        print(f"Success! Page created at: {new_page.html_url}")

if __name__ == "__main__":
    main()