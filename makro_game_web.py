# plik: makro_game_web.py
from flask import Flask, render_template, request, redirect, url_for
import random
import plotly
import plotly.graph_objs as go
import json

app = Flask(__name__)

# --- Stan gry (w prostym modelu) ---
game_state = {
    'Y': 1000,
    'Y_pot': 1000,
    'inflacja': 2.0,
    'bezrobocie': 5.0,
    'U_natural': 5.0,
    'export': 100,
    'import': 80,
    'turn': 1,
    'history': {'Y': [], 'Y_pot': [], 'inflacja': [], 'bezrobocie': []},
    'score': 0
}

# --- Aktualizacja gospodarki ---
def update_state(G, T, r, invest_tech):
    state = game_state
    # Konsumpcja i inwestycje (prosty IS-LM)
    C = 0.6 * state['Y']
    I = max(0, 50 + 0.05*(state['Y_pot']-state['Y']) - 10*r)
    NX = state['export'] - state['import']
    Y_new = C + I + G + NX - T
    state['Y'] = max(0, Y_new)
    # Postęp technologiczny
    state['Y_pot'] += invest_tech * 0.5
    # Phillips curve
    state['inflacja'] = max(0, 2 + 0.03*(state['Y']-state['Y_pot']))
    # Bezrobocie
    state['bezrobocie'] = max(0, state['U_natural'] - 0.05*(state['Y']-state['Y_pot']))
    # Losowe wstrząsy
    shock_type = random.choice(["boom", "kryzys", "energia", "tech", None])
    if shock_type == "boom":
        state['Y'] += random.uniform(20,50)
    elif shock_type == "kryzys":
        state['Y'] = max(0, state['Y'] - random.uniform(30,70))
    elif shock_type == "energia":
        state['inflacja'] += random.uniform(1,3)
    elif shock_type == "tech":
        state['Y_pot'] += random.uniform(10,30)
    # Historia i punktacja
    state['history']['Y'].append(state['Y'])
    state['history']['Y_pot'].append(state['Y_pot'])
    state['history']['inflacja'].append(state['inflacja'])
    state['history']['bezrobocie'].append(state['bezrobocie'])
    score = max(0, 100 - abs(state['Y']-state['Y_pot']) - abs(state['inflacja']-2)*10 - state['bezrobocie']*5)
    state['score'] += score
    state['turn'] += 1

# --- Wykresy z Plotly ---
def get_plot():
    state = game_state
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=state['history']['Y'], mode='lines+markers', name='PKB'))
    fig.add_trace(go.Scatter(y=state['history']['Y_pot'], mode='lines+markers', name='PKB potencjalny'))
    fig.add_trace(go.Scatter(y=state['history']['inflacja'], mode='lines+markers', name='Inflacja (%)'))
    fig.add_trace(go.Scatter(y=state['history']['bezrobocie'], mode='lines+markers', name='Bezrobocie (%)'))
    fig.update_layout(title="Trendy gospodarcze", xaxis_title="Tura", yaxis_title="Wartość")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

# --- Strony web ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            G = float(request.form["G"])
            T = float(request.form["T"])
            r = float(request.form["r"])
            invest_tech = float(request.form["invest_tech"])
        except:
            G = T = r = invest_tech = 0
        update_state(G, T, r, invest_tech)
        return redirect(url_for("index"))
    graphJSON = get_plot()
    return render_template("index.html", state=game_state, graphJSON=graphJSON)

@app.route("/reset")
def reset():
    global game_state
    game_state = {
        'Y': 1000,
        'Y_pot': 1000,
        'inflacja': 2.0,
        'bezrobocie': 5.0,
        'U_natural': 5.0,
        'export': 100,
        'import': 80,
        'turn': 1,
        'history': {'Y': [], 'Y_pot': [], 'inflacja': [], 'bezrobocie': []},
        'score': 0
    }
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
