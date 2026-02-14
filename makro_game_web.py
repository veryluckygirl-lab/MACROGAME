from flask import Flask, render_template, request, redirect, url_for
import json, random
import plotly
import plotly.graph_objs as go

app = Flask(__name__)

# --- Dane historyczne Polski (1990-2010) ---
historical_data = {
    "1990": {"GDP": 195.1, "inflation": 94.4, "unemployment": 6.6},
    "1995": {"GDP": 219.3, "inflation": 27.8, "unemployment": 14.0},
    "2000": {"GDP": 283.17, "inflation": 10.1, "unemployment": 15.1},
    "2008": {"GDP": 469.0, "inflation": 4.0, "unemployment": 7.1},
    "2010": {"GDP": 411.2, "inflation": 2.6, "unemployment": 9.6}
}

# --- Stan gry startowy ---
def init_state(year="2000"):
    data = historical_data[year]
    return {
        'year': int(year),
        'Y': data['GDP'],
        'Y_pot': data['GDP']*1.05,
        'inflacja': data['inflation'],
        'bezrobocie': data['unemployment'],
        'U_natural': 12.0,
        'export': data['GDP']*0.28,
        'import': data['GDP']*0.25,
        'turn': 1,
        'score': 0,
        'history': {'Y': [], 'Y_pot': [], 'inflacja': [], 'bezrobocie': []},
        'achievements': []
    }

state = init_state()

# --- Funkcja aktualizacji stanu gry ---
def update_state(state, decisions):
    data = historical_data.get(str(state['year']), state)
    
    # Parametry podręcznikowe
    c1 = 0.6          # krańcowa skłonność do konsumpcji
    I0 = 50           # inwestycje bazowe
    b = 5             # wrażliwość inwestycji na r
    alpha = 0.03      # Phillips slope
    tech_factor = 0.5
    export_factor = 0.1

    # Konsumpcja
    C = c1 * (state['Y'] - decisions['T'])
    # Inwestycje
    I = max(0, I0 - b*decisions['r'] + decisions.get('invest_tech',0))
    # Eksport-import (globalizacja)
    NX = (state['export']*(1+decisions.get('export_boost',0.0))) - state['import']
    # PKB – IS
    Y_new = C + I + decisions['G'] + NX
    state['Y'] = Y_new

    # Phillips – inflacja
    state['inflacja'] = data['inflation'] + alpha * (state['Y'] - state['Y_pot'])

    # Bezrobocie
    state['bezrobocie'] = max(0, data['unemployment'] - 0.05*(state['Y']-state['Y_pot']))

    # PKB potencjalny rośnie dzięki technologii
    state['Y_pot'] += decisions.get('invest_tech',0)*tech_factor

    # Wstrząsy losowe
    shock = random.choice([None, "boom", "kryzys"])
    if shock=="boom":
        state['Y'] += random.uniform(10,50)
        state['achievements'].append("Boom gospodarczy!")
    elif shock=="kryzys":
        state['Y'] -= random.uniform(20,60)
        state['achievements'].append("Kryzys gospodarczy!")

    # Historia i punktacja edukacyjna
    state['history']['Y'].append(state['Y'])
    state['history']['Y_pot'].append(state['Y_pot'])
    state['history']['inflacja'].append(state['inflacja'])
    state['history']['bezrobocie'].append(state['bezrobocie'])

    score = max(0, 100 - abs(state['Y']-state['Y_pot']) - abs(state['inflacja']-2)*5 - state['bezrobocie']*2)
    state['score'] += score

    # Osiągnięcia za stabilną gospodarkę
    if abs(state['Y']-state['Y_pot'])<10 and state['inflacja']<5 and state['bezrobocie']<10:
        if "Stabilna gospodarka" not in state['achievements']:
            state['achievements'].append("Stabilna gospodarka")

    state['turn'] += 1
    state['year'] += 1
    return state

# --- Generowanie wykresów ---
def get_plot(state):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=state['history']['Y'], mode='lines+markers', name='PKB'))
    fig.add_trace(go.Scatter(y=state['history']['Y_pot'], mode='lines+markers', name='PKB potencjalny'))
    fig.add_trace(go.Scatter(y=state['history']['inflacja'], mode='lines+markers', name='Inflacja (%)'))
    fig.add_trace(go.Scatter(y=state['history']['bezrobocie'], mode='lines+markers', name='Bezrobocie (%)'))
    fig.update_layout(title="Trendy gospodarcze", xaxis_title="Tura", yaxis_title="Wartość")
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# --- Strona główna ---
@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="POST":
        G = float(request.form.get("G",0))
        T = float(request.form.get("T",0))
        r = float(request.form.get("r",0))
        invest_tech = float(request.form.get("invest_tech",0))
        export_boost = float(request.form.get("export_boost",0.0))
        decisions = {'G':G,'T':T,'r':r,'invest_tech':invest_tech,'export_boost':export_boost}
        update_state(state, decisions)
        return redirect(url_for("index"))
    graphJSON = get_plot(state)
    return render_template("index.html", state=state, graphJSON=graphJSON)

# --- Reset gry ---
@app.route("/reset")
def reset():
    global state
    state = init_state()
    return redirect(url_for("index"))

if __name__=="__main__":
    app.run(debug=True)
