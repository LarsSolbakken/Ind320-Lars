# IND320 Compulsory Work – Lars Solbakken

This repository contains my project work for the course **IND320 – Data-Driven Digitalization**.  
It includes both a **Jupyter Notebook** (analysis and documentation) and a **Streamlit web app**.

---

## 📁 Contents
- `IND320_part3.ipynb` – Jupyter Notebook with full analysis, functions, and log  
- `utils.py` – Helper functions for STL, spectrogram, outlier and anomaly detection  
- `pages/` – Streamlit sub-pages (Table, Plot, STL & Spectrogram, Outliers & Anomalies, etc.)  
- `requirements.txt` – Dependencies for Streamlit Cloud  

---

## 🌐 Streamlit app  
👉 [https://ind320-lars-d2bn5njskcftffxrf9cvi9.streamlit.app](https://ind320-lars-d2bn5njskcftffxrf9cvi9.streamlit.app)

---

## 💻 GitHub repository  
👉 [https://github.com/LarsSolbakken/Ind320-Lars/tree/streamlit%2C-part3](https://github.com/LarsSolbakken/Ind320-Lars/tree/streamlit%2C-part3)

---

## 📓 Jupyter Notebook  
👉 [https://github.com/LarsSolbakken/Ind320-Lars/blob/streamlit%2C-part3/Project%20work%2C%20part%203/IND320ProjectWorkPart%203.ipynb](https://github.com/LarsSolbakken/Ind320-Lars/blob/streamlit%2C-part3/Project%20work%2C%20part%203/IND320ProjectWorkPart%203.ipynb) 

---

## 📜 Description
The project includes:
- API connection to **Open-Meteo (ERA5 reanalysis)** for live weather data  
- STL decomposition and spectrograms based on **Elhub production data**  
- Detection of **temperature outliers** (SPC + DCT) and **precipitation anomalies** (LOF)  
- A multi-page **Streamlit app**:
  1. 🏠 Home  
  2. 📊 Table (data preview)  
  3. 📈 Plot (time-series visualization)  
  4. ⚡ Electricity Production (Elhub 2021)  
  5. 🔍 STL & Spectrogram  
  6. 🌡️ Outliers & Anomalies  

---

## 🤖 AI usage
ChatGPT (GPT-5) was used for:
- Structuring the notebook and explaining formulas  
- Writing and documenting Python functions  
- Adding comments and Markdown formatting  
- Debugging and improving Streamlit page logic
