import numpy as np
import scipy.stats as norm
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, render_template_string, request, jsonify
import matplotlib

# Use 'Agg' backend to avoid GUI issues when running a server
matplotlib.use('Agg')

app = Flask(__name__)

def generate_risk_data(s0, mu, sigma, n_days, conf_level):
    """Generates price paths, risk metrics, and base64 plots."""
    
    # 1. Simulate Price Path (GBM)
    dt = 1 / 252 # Daily steps
    returns = np.random.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), n_days)
    prices = s0 * np.exp(np.cumsum(returns))
    
    # Calculate daily parameters
    mu_daily = mu / 252
    sigma_daily = sigma / np.sqrt(252)
    
    # 2. Parametric Risk Metrics
    z_score = norm.norm.ppf(1 - conf_level)
    var_param = -(mu_daily + z_score * sigma_daily)
    # Expected Shortfall (Parametric)
    es_param = sigma_daily * norm.norm.pdf(norm.norm.ppf(1 - conf_level)) / (1 - conf_level) - mu_daily
    
    # 3. Historical Risk Metrics
    var_hist = -np.percentile(returns, (1 - conf_level) * 100)
    tail_losses = returns[returns < -var_hist]
    es_hist = -np.mean(tail_losses) if len(tail_losses) > 0 else var_hist

    # 4. Generate Plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Panel 1: Price
    ax1.plot(prices, color='#2980b9', linewidth=1.5)
    # Using 'rf' to prevent ParseException with LaTeX symbols
    ax1.set_title(rf"Simulated Price Path ($S_0$={s0}, $\mu$={mu:.2f}, $\sigma$={sigma:.2f})")
    ax1.set_ylabel("Price")
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Distribution
    ax2.hist(returns, bins=50, density=True, alpha=0.5, color='#34495e')
    ax2.axvline(-var_param, color='#e74c3c', linestyle='--', linewidth=2, label=f'Parametric VaR: {var_param:.2%}')
    ax2.axvline(-es_param, color='#c0392b', linestyle='-', linewidth=2, label=f'Parametric ES: {es_param:.2%}')
    ax2.axvline(-var_hist, color='#f39c12', linestyle='--', linewidth=2, label=f'Historical VaR: {var_hist:.2%}')
    ax2.axvline(-es_hist, color='#f39c12', linestyle='-', linewidth=2, label=f'Historical ES: {es_hist:.2%}')
    # Using 'rf' to prevent ParseException with LaTeX symbols
    ax2.set_title(rf"Returns Distribution ($N$={n_days} days, Confidence={conf_level:.0%})")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 5. Convert Plot to Base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return {
        'plot_url': plot_url,
        'var_param': f"{var_param:.2%}",
        'es_param': f"{es_param:.2%}",
        'var_hist': f"{var_hist:.2%}",
        'es_hist': f"{es_hist:.2%}"
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Risk Analysis Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; display: flex; color: #333; }
        .sidebar { width: 300px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .main-content { flex-grow: 1; margin-left: 20px; display: flex; flex-direction: column; }
        h2 { color: #2c3e50; font-size: 1.2em; margin-top: 0; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .control-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; color: #555; font-size: 0.9em; }
        input[type="range"] { width: 100%; cursor: pointer; }
        .val-display { float: right; font-weight: normal; color: #3498db; background: #ecf0f1; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; }
        .btn { display: block; width: 100%; padding: 10px; background: #3498db; color: white; border: none; border-radius: 5px; font-size: 1em; cursor: pointer; transition: background 0.3s; margin-top: 20px;}
        .btn:hover { background: #2980b9; }
        .metrics-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th, td { padding: 12px; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; color: #2c3e50; }
        .plot-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        img { max-width: 100%; height: auto; border-radius: 4px; }
    </style>
</head>
<body>

    <div class="sidebar">
        <h2>Risk Parameters</h2>
        
        <div class="control-group">
            <!-- Using HTML entities instead of LaTeX -->
            <label>Initial Price (S<sub>0</sub>) <span id="s0_val" class="val-display">100</span></label>
            <input type="range" id="s0" min="10" max="500" step="10" value="100" oninput="updateDashboard()">
        </div>
        
        <div class="control-group">
            <label>Trend / Drift (&mu;) <span id="mu_val" class="val-display">0.05</span></label>
            <input type="range" id="mu" min="-0.5" max="0.5" step="0.01" value="0.05" oninput="updateDashboard()">
        </div>
        
        <div class="control-group">
            <label>Volatility (&sigma;) <span id="sigma_val" class="val-display">0.20</span></label>
            <input type="range" id="sigma" min="0.05" max="0.80" step="0.01" value="0.20" oninput="updateDashboard()">
        </div>
        
        <div class="control-group">
            <label>Time Horizon (Days) <span id="n_days_val" class="val-display">252</span></label>
            <input type="range" id="n_days" min="50" max="1000" step="10" value="252" oninput="updateDashboard()">
        </div>

        <div class="control-group">
            <label>Confidence Level <span id="conf_val" class="val-display">0.95</span></label>
            <input type="range" id="conf_level" min="0.90" max="0.99" step="0.01" value="0.95" oninput="updateDashboard()">
        </div>

        <button class="btn" onclick="updateDashboard()">🎲 Resimulate Random Path</button>
    </div>

    <div class="main-content">
        <div class="metrics-card">
            <table>
                <tr>
                    <th>Method</th>
                    <th>Value at Risk (VaR)</th>
                    <th>Expected Shortfall (ES)</th>
                </tr>
                <tr>
                    <td><strong>Parametric (Normal)</strong></td>
                    <td id="var_param_td" style="color:#e74c3c; font-weight:bold;">--</td>
                    <td id="es_param_td" style="color:#c0392b; font-weight:bold;">--</td>
                </tr>
                <tr>
                    <td><strong>Historical</strong></td>
                    <td id="var_hist_td" style="color:#f39c12; font-weight:bold;">--</td>
                    <td id="es_hist_td" style="color:#d35400; font-weight:bold;">--</td>
                </tr>
            </table>
        </div>

        <div class="plot-container">
            <img id="risk_plot" src="" alt="Risk Analysis Plots will appear here">
        </div>
    </div>

    <script>
        function updateDashboard() {
            // Get values from sliders
            const s0 = document.getElementById('s0').value;
            const mu = document.getElementById('mu').value;
            const sigma = document.getElementById('sigma').value;
            const n_days = document.getElementById('n_days').value;
            const conf_level = document.getElementById('conf_level').value;

            // Update display values next to sliders
            document.getElementById('s0_val').innerText = s0;
            document.getElementById('mu_val').innerText = mu;
            document.getElementById('sigma_val').innerText = sigma;
            document.getElementById('n_days_val').innerText = n_days;
            document.getElementById('conf_val').innerText = conf_level;

            // Send POST request to backend
            fetch('/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    s0: parseFloat(s0),
                    mu: parseFloat(mu),
                    sigma: parseFloat(sigma),
                    n_days: parseInt(n_days),
                    conf_level: parseFloat(conf_level)
                })
            })
            .then(response => response.json())
            .then(data => {
                // Update Image
                document.getElementById('risk_plot').src = 'data:image/png;base64,' + data.plot_url;
                
                // Update Table Data
                document.getElementById('var_param_td').innerText = data.var_param;
                document.getElementById('es_param_td').innerText = data.es_param;
                document.getElementById('var_hist_td').innerText = data.var_hist;
                document.getElementById('es_hist_td').innerText = data.es_hist;
            })
            .catch(error => console.error('Error:', error));
        }

        // Trigger initial load
        window.onload = updateDashboard;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/update', methods=['POST'])
def update():
    req = request.get_json()
    data = generate_risk_data(
        s0=req['s0'],
        mu=req['mu'],
        sigma=req['sigma'],
        n_days=req['n_days'],
        conf_level=req['conf_level']
    )
    return jsonify(data)

if __name__ == '__main__':
    print("Starting Offline Risk Dashboard...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
