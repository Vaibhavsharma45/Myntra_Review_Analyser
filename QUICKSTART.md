# 🚀 Quick Start Guide - Myntra Review Scraper Pro

## Setup in 5 Minutes! ⏱️

### Step 1: Install Python (if not installed)
Download Python 3.10+ from: https://www.python.org/downloads/

### Step 2: Open Terminal/Command Prompt
- **Windows**: Press `Win + R`, type `cmd`, press Enter
- **Mac/Linux**: Press `Cmd + Space`, type `terminal`, press Enter

### Step 3: Navigate to Project Folder
```bash
cd path/to/myntra-scraper-improved
```

### Step 4: Create Virtual Environment
```bash
# Using Conda (Recommended)
conda create -p ./env python=3.10 -y
conda activate ./env

# OR Using Python venv
python -m venv env
# Activate:
# Windows: env\Scripts\activate
# Mac/Linux: source env/bin/activate
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .
```

### Step 6: Run the App! 🎉
```bash
streamlit run app.py
```

The app will automatically open in your browser!

---

## How to Use 📖

### 1️⃣ Enter Product Name
- In the sidebar, type product name (e.g., "Nike shoes")

### 2️⃣ Choose Settings
- Number of products: 1-10
- Headless mode: ✅ (recommended)

### 3️⃣ Click "Start Scraping"
- Wait for scraping to complete
- View progress in real-time

### 4️⃣ Explore Results
- **Analytics Tab**: View charts and graphs
- **Reviews Tab**: Read individual reviews
- **Advanced Tab**: Word clouds and keywords

### 5️⃣ Export Data
- Click download buttons
- Choose Excel, CSV, or Summary Report

---

## Common Issues & Fixes 🔧

### ❌ "Chrome not found"
**Fix**: Install Google Chrome browser
- Download: https://www.google.com/chrome/

### ❌ "Module not found"
**Fix**: Install dependencies again
```bash
pip install -r requirements.txt --force-reinstall
```

### ❌ "No reviews found"
**Fix**: Try these:
- Use a different product name
- Increase number of products
- Check if product has reviews on Myntra

### ❌ App not opening
**Fix**: Check if port is available
```bash
streamlit run app.py --server.port 8502
```

---

## Pro Tips 💡

### ⚡ For Faster Scraping
- Enable "Headless Mode" ✅
- Start with fewer products (3-5)
- Use good internet connection

### 📊 For Better Analysis
- Scrape multiple products for comparison
- Use filters to find specific reviews
- Export data for further analysis

### 🎯 For Best Results
- Use specific product names
- Check product exists on Myntra first
- Run during off-peak hours

---

## Need Help? 🆘

1. **Check README.md** for detailed documentation
2. **Look at error messages** - they often tell you what's wrong
3. **Google the error** - chances are someone else had it too
4. **Open an issue** on GitHub with:
   - Error message
   - Screenshot
   - Steps you tried

---

## Example Usage 📝

### Good Product Names:
✅ "Levis jeans"
✅ "Nike running shoes"
✅ "Puma t-shirt"
✅ "HRX shorts"

### Bad Product Names:
❌ "clothes" (too generic)
❌ "xyz123" (doesn't exist)
❌ "" (empty)

---

## What You'll Get 🎁

After scraping, you'll see:
- Total number of reviews
- Sentiment breakdown (Positive/Negative/Neutral)
- Average ratings
- Interactive charts
- Word clouds
- Top keywords
- Individual reviews with filters

---

## Export Options 💾

1. **Excel**: 
   - Multiple sheets
   - Formatted data
   - Statistics included

2. **CSV**:
   - Simple format
   - Easy to open in Excel
   - Good for data analysis

3. **Summary Report**:
   - Text format
   - Key insights
   - Quick overview

---

**That's it! You're ready to go! 🚀**

Happy scraping! 🛍️
