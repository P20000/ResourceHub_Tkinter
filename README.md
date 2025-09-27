# 🧠 ResourceHub: Advanced Knowledge Manager

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square\&logo=python)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/Dependencies-5%20Libs-brightgreen?style=flat-square)](./requirements.txt)
[![UI](https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=flat-square)](https://customtkinter.tomschimansky.com/)

## 🌟 Overview

**ResourceHub** is a sophisticated desktop application built with Python that solves the problem of **information overload** by combining automated web scraping, full-text search, and **AI-powered summarization** into a clean, modern user interface.

It allows users to save links to articles, code snippets, or notes, automatically extracts the core content, generates a concise summary using the Gemini API, and stores everything in a local, searchable database.

---

|                                        1. Input & Summarization Trigger                                        |                                                  2. Results and AI Summary View                                                 |
| :------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------: |
| Enter the URL, Title, and Tags. Clicking the button triggers scraping, AI summarization, and data persistence. | The left panel shows filtered results. The right panel displays the **AI-Generated Summary** prominently above the raw content. |
|                             ![Input Form Screenshot](./docs/images/input-form.png)                             |                                 ![Search Results Screenshot](./docs/images/results-summary.png)                                 |

---

## ✨ Key Features

This project showcases advanced integration across multiple technologies:

* **Modern UI/UX (Phase 5):** Built using **CustomTkinter (CTk)** for a clean, modern, and natively dark/light mode compatible interface.
* **AI Summarization (Phase 6):** Integrates the **Google Gemini API** (`gemini-2.5-flash`) to generate concise, high-quality summaries of scraped articles.
* **Advanced Persistence (Phase 1):** Uses **SQLite3** for reliable local data storage.
* **Full-Text Search (Phase 3):** Implements fuzzy search across the resource **Title**, **Tags**, and the saved **Full Content**.
* **Automation (Phase 2):** Uses `requests` and `BeautifulSoup` for robust content capture.

---

## 🛠️ Installation and Setup

### Prerequisites

You must have **Python 3.8+** installed and obtain a **Gemini API Key** from Google AI Studio.

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/<YOUR_USERNAME>/ResourceHub_Tkinter.git
   cd ResourceHub_Tkinter
   ```

2. **Set up Virtual Environment:**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set API Key Environment Variable:**

   You must set your Gemini API key in your terminal session before running the app. Replace `YOUR_API_KEY_HERE` with your actual key.

   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="YOUR_API_KEY_HERE"

   # macOS/Linux
   export GEMINI_API_KEY="YOUR_API_KEY_HERE"
   ```

---

## 🚀 How to Run

Start the application from your active virtual environment:

```bash
python app.py
```

---

## 🧩 Troubleshooting Images (Access Denied / Not Loading)

1. **Use relative paths** to files committed in your repo (recommended for GitHub README):

   * Put files under `docs/images/` and reference as `./docs/images/<file>.png`.
2. **Avoid private asset hosts** (e.g., `user-images.githubusercontent.com` from a private repo). Those links can return **403 Access Denied** to others.
3. **Keep file names simple** (no spaces, lowercase, use `-` or `_`).
4. If hosting outside GitHub (PyPI, npm, docs sites), use **absolute raw URLs**:

   * `https://raw.githubusercontent.com/<YOUR_USERNAME>/ResourceHub_Tkinter/main/docs/images/<file>.png`
5. If using Git LFS, ensure bandwidth quotas aren’t exceeded; otherwise PNGs/JPGs usually don’t need LFS.

**Quick add & commit:**

```bash
mkdir -p docs/images
# copy your screenshots into docs/images
git add docs/images/input-form.png docs/images/results-summary.png README.md
git commit -m "docs: fix README images via repo-relative paths"
git push origin main
```


