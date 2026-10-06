
# Docx to Canvas Page Converter

Automates the conversion of Microsoft Word (`.docx`) documents into accessible, natively formatted Canvas Pages.

## Important Notes & Warnings
* **General Warning:** This script uses the Canvas API which may make irreversible changes to your Canvas course. The authors of this script are not responsible for any harms caused.
* **Canvas API Token:** These instructions ask you to create a Canvas API token. This API token is all powerful and anyone who posses it can make changes to any Canvas course attached to your account. You should give this token a expiration date that forces it to expire after a short period of time (1 or 2 days) and keep it in a safe place that no one else has access to. You can delete this token in your Canvas account settings at anytime.
* **Image Overwrite Warning:** To prevent image collisions, the script prefixes uploaded images with the Word document's filename. **If you convert two different `.docx` files that have the exact same filename, the images from the second document will overwrite the images from the first document in Canvas**, breaking the first Canvas page. Always ensure your `.docx` files have unique names before running the script.
* **Canvas Image File Cleanup:** When images are uploaded during execution, they are saved directly to the Canvas course's **Files** directory. If a generated Canvas Page is deleted, the HTML page reference is removed, but the uploaded image files remain stored in the Canvas Files repository. Unused images must be deleted manually from the Canvas **Files** tab if storage cleanup is required.


## Core Features

* **Math Handling:** Word equations are processed via Pandoc's `--mathjax` flag and converted to standard LaTeX wrapped in delimiters (`\(` and `\)`). Canvas renders these automatically using MathJax, preserving screen-reader accessibility, braille compatibility, and clean vector scaling.
* **Image Uploads:** Local images are extracted from the Word document, uploaded to the target Canvas course's Files repository, and updated in the page HTML with their live Canvas URLs.
* **Long Alt Text Handling:** If an image's `alt` text exceeds 120 characters, the script sets the image `alt` attribute to a concise fallback and appends an HTML5 `<details>`/`<summary>` dropdown block directly beneath the image containing the complete description.
* **Heading Hierarchy Normalization:** Detects `<h1>` elements in the document and shifts the heading hierarchy down (capping at `<h4>`) to prevent conflicts with Canvas's reserved page title `<h1>`.

---

## Prerequisites & Tool Installation

This script requires **Pandoc** (to parse Word documents) and **uv** (to automatically manage Python and script dependencies). 

Use [Pixi](https://pixi.sh) to install both tools easily across any operating system.

### 1. Install Pixi
* **macOS / Linux / WSL:**
  ```bash
  curl -fsSL [https://pixi.sh/install.sh](https://pixi.sh/install.sh) | bash
  ```
* **Windows (PowerShell):**
  ```powershell
  iwr -useb [https://pixi.sh/install.ps1](https://pixi.sh/install.ps1) | iex
  ```

### 2. Install Pandoc and uv
Restart your terminal, then run:
```bash
pixi global install pandoc uv
```
*(If you already have Pandoc and `uv` installed via Homebrew, Winget, or Chocolatey, skip this step).*

---

## Setup Instructions

1. **Clone or Download** this repository.
2. **Create the Environment File:**
   Copy the template file to create your local credentials file.
   * **macOS / Linux / WSL:**
     ```bash
     cp .env.example .env
     ```
   * **Windows (PowerShell):**
     ```powershell
     Copy-Item .env.example .env
     ```
3. **Generate a Canvas API Token:**
   * Log into Canvas > **Account** > **Settings**.
   * Under **Approved Integrations**, click **+ New Access Token**.
   * Enter a purpose name and click **Generate Token**.
4. **Configure Credentials:**
   Open the `.env` file in a text editor and fill in your details:
   ```text
   CANVAS_API_URL="https://canvas.yourinstitution.edu"
   CANVAS_API_KEY="your_actual_access_token_here"
   CANVAS_COURSE_ID="123456"
   ```

---

## Usage

The `uv` tool automatically downloads the required Python packages and executes the script in an isolated environment. No manual Python virtual environment setup is required. 

Run the command from your terminal, replacing the path with the location of your specific document.

### macOS / Linux / WSL
```bash
uv run canvas_script.py "/path/to/assignment.docx"
```

### Windows (PowerShell or Command Prompt)
```powershell
uv run canvas_script.py "C:\path\to\assignment.docx"
```

The script will convert the document, upload all embedded images, format accessibility structures, generate a new Canvas Page using the document filename as the title, and print the output page URL.

