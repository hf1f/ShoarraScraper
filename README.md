# 📊 Arabic Poetry Data Pipeline & Analytics Dashboard

An end-to-end Data Engineering and NLP pipeline that scrapes, cleans, and visualizes Arabic poetry data from web sources. This project handles data inconsistencies, eliminates scaling duplicates, and provides interactive analytics insights.

🔗 **Live Dashboard Link:** [View Live Streamlit Dashboard](https://shoarrascraper-mqycreebauwcy5zqcas3at.streamlit.app/)

---

## 🚀 Key Features

* **Multi-Threaded Scraper**: Fast and concurrent scraping using python's concurrency pool with automated data safety backups.
* **Smart Data Cleaning**: Resolves real-world data anomalies (e.g., identity merging based on normalized names, duplicate poem removal via unique identifiers).
* **Advanced Analytics Dashboard**: Built using `Streamlit` and `Plotly` featuring dynamic Middle East geographical heatmaps (using Logarithmic scaling to handle high data skewness).
* **NLP Exploratory Analysis**: Contextual top-word extraction filtered dynamically by historical eras or country boundaries.

---

## 📂 Project Structure

Based on the official repository structure (as seen in `image_7f9464.png`), the project consists of the following components:

```text
├── scrapperCooP.py       # Multi-threaded web scraper for Arabic poetry data
├── extract_poets.py      # Script dedicated to extracting and parsing specific poet entities
├── Cleaning.py           # Data verification, deduplication, and parsing pipeline
├── ML.ipynb              # Jupyter Notebook for machine learning models & initial EDA
├── app.py                # Streamlit Dashboard application connected to Google Drive
├── requirements.txt      # List of dependencies required to deploy the dashboard
├── .gitignore            # Excludes large raw JSON databases from Git tracking
└── README.md             # Documentation (This file)