# Educational_Risk_Dashboard

An interactive, fully offline web application built with Python and Flask. This dashboard is designed for educational purposes to simulate asset price paths and calculate key financial risk metrics in real-time.

## 🚀 Features

* **Fully Offline & Standalone:** Requires no internet connection or external CDNs. All HTML, CSS, JavaScript, and visualizations are generated and served directly from a single Python script.
* **Real-time Interactivity:** Features interactive sliders for adjusting simulation parameters. Uses AJAX (`fetch` API) to update plots and data dynamically without reloading the page.
* **Financial Modeling:** 
  * Simulates asset price paths using **Geometric Brownian Motion (GBM)**.
  * Calculates **Value at Risk (VaR)** and **Expected Shortfall (ES)**.
* **Multiple Risk Methodologies:** Compares risk metrics using both **Historical** and **Parametric (Normal Distribution)** approaches.
* **Dynamic Visualization:** Server-side Matplotlib plots are encoded in Base64 and injected directly into the frontend, displaying both price trajectories and return distributions with highlighted risk thresholds.

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Math & Stats:** NumPy, SciPy
* **Data Visualization:** Matplotlib
* **Frontend:** Vanilla JavaScript, HTML5, CSS3 (Inline)

## 📊 Parameters Explained

You can control the following variables via the dashboard sliders:
* **$S_0$ (Initial Price):** The starting price of the simulated asset.
* **$\mu$ (Drift/Trend):** The expected return of the asset over time.
* **$\sigma$ (Volatility):** The standard deviation of the asset's returns (risk/fluctuation).
* **Time Horizon ($N$):** Number of simulated time steps (days).
* **Confidence Level:** The statistical probability level for VaR and ES calculations (e.g., $95\%$ or $99\%$).

## 📝 License

This project is licensed under the MIT License.

## ⚙️ Installation & Usage

1. **Clone the repository:**
```bash
   git clone https://github.com/DrSavalan/Educational_Risk_Dashboard.git
   cd Educational_Risk_Dashboard
   
