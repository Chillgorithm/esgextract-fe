# ESG-Based Construction Company Data Dashboard (Streamlit)

This project visualizes the **ESG (safety/environmental) metrics** of major construction companies, allowing **yearly** and **company-wise** comparisons.  

- **Framework**: Streamlit  
- **Page Structure**: `main.py` + `pages/` (multi-page)  
- **Data Source**: `data.json` (local JSON)  

---

## 1. Data (`data.json`)

The `data.json` file contains ESG data for **Samsung, Hyundai, LG, Google, and Tesla** for the years **2023–2025**.  

Metrics included:  
- **Safety**:  
  - Incident Rate (‰, per 1,000 workers)  
  - Fatality Count (cases)  
  - Safety Audit Compliance (%)  
  - Industrial Insurance Claims (million KRW)  

- **Environment**:  
  - Total Carbon Emissions (tCO₂e)  
  - Energy Usage (kWh/㎡)  
  - Renewable Energy Ratio (%)  
  - Construction Waste Generated (ton)  
  - Recycling Rate (%)  

👉 Placeholder values are stored in the JSON file.  

---

## 2. Main Page (`main.py`)

- Contains a **toggle switch**:  
  - **Yearly Comparison Mode**  
  - **Company Comparison Mode**  

- Based on the toggle selection, either the `yearReport.py` or `companyReport.py` page becomes available.  

---

## 3. Pages (`pages/`)

### `yearReport.py`  
- Activated when **Yearly Comparison Mode** is selected.  
- Features:  
  - Displays a **dataframe containing the most recent year’s data for all companies**.  
  - When a company is selected, visualizations show the company’s metrics **across multiple years**.  
- Visualized in **two tabs**:  
  - **Safety**  
  - **Environment**  

---

### `companyReport.py`  
- Activated when **Company Comparison Mode** is selected.  
- Features:  
  - Displays a **dataframe containing the most recent year’s data for all companies**.  
  - From the dataframe, users can **select multiple companies** for comparison.  
- Visualized in **two tabs**:  
  - **Safety**  
  - **Environment**  
- Comparison is always based on the **most recent year’s data**.  

---

## 4. Workflow Summary

1. **Main Page**  
   - Choose comparison mode with toggle.  

2. **Yearly Report** (`yearReport.py`)  
   - Select a year → Compare companies.  
   - Select a company → See yearly trend visualizations (Safety/Environment).  

3. **Company Report** (`companyReport.py`)  
   - Select multiple companies → Compare their latest year’s data (Safety/Environment).  

---

## 5. Tech Notes

- **Charts**: Altair (interactive, tooltips enabled).  
- **Data Handling**: Pandas for dataframe operations.  
- **Caching**: Streamlit cache for loading JSON data efficiently.  
- **Scalability**: Additional metrics or filters (region, project size) can be added easily.  