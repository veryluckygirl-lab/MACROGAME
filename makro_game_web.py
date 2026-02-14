import time
import random
import matplotlib.pyplot as plt

# ---------------------------
# Funkcje pomocnicze
# ---------------------------
def slow_print(text, delay=0.02):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def show_economy(state, turn):
    slow_print(f"\n--- Rok {turn} ---")
    slow_print(f"PKB: {state['Y']:.2f}")
    slow_print(f"PKB potencjalny: {state['Y_pot']:.2f}")
    slow_print(f"Inflacja: {state['inflacja']:.2f}%")
    slow_print(f"Bezrobocie: {state['bezrobocie']:.2f}%")
    slow_print(f"Eksport: {state['export']:.2f}, Import: {state['import']:.2f}\n")

def apply_random_shocks(state):
    # Losowe wydarzenia w gospodarce
    shock_type = random.choice(["boom eksportowy", "kryzys", "szok energetyczny", "postęp technologiczny", None])
    if shock_type == "boom eksportowy":
        gain = random.uniform(20, 50)
        state['Y'] += gain
        slow_print(f"!!! Boom eksportowy: PKB wzrósł o {gain:.2f} !!!")
    elif shock_type == "kryzys":
        loss = random.uniform(30, 70)
        state['Y'] = max(0, state['Y'] - loss)
        slow_print(f"!!! Kryzys gospodarczy: PKB spadł o {loss:.2f} !!!")
    elif shock_type == "szok energetyczny":
        inflation_spike = random.uniform(1, 3)
        state['inflacja'] += inflation_spike
        slow_print(f"!!! Szok energetyczny: inflacja wzrosła o {inflation_spike:.2f}% !!!")
    elif shock_type == "postęp technologiczny":
        tech_gain = random.uniform(10, 30)
        state['Y_pot'] += tech_gain
        slow_print(f"!!! Postęp technologiczny: PKB potencjalny wzrósł o {tech_gain:.2f} !!!")
    # None = brak wstrząsu

# ---------------------------
# Symulacja IS-LM i Phillipsa
# ---------------------------
def update_state(state, decisions):
    # Konsumpcja zależna od PKB
    C = 0.6 * state['Y']
    # Inwestycje zależne od stopy procentowej
    I = max(0, 50 + 0.05 * (state['Y_pot'] - state['Y']) - 10 * decisions['r'])
    # Popyt krajowy = C + I + G + NX - T
    NX = state['export'] - state['import']
    Y_new = C + I + decisions['G'] + NX - decisions['T']

    # Aktualizacja stanu gospodarki
    state['Y'] = max(0, Y_new)

    # Phillips curve: inflacja zależy od przewyższenia PKB nad potencjałem
    state['inflacja'] = max(0, 2 + 0.03*(state['Y'] - state['Y_pot']))

    # Bezrobocie spada przy wzroście PKB powyżej potencjału
    state['bezrobocie'] = max(0, state['U_natural'] - 0.05*(state['Y'] - state['Y_pot']))

# ---------------------------
# Funkcja tur gracza
# ---------------------------
def player_turn(turn, state):
    show_economy(state, turn)
    slow_print("Podejmij decyzje polityki fiskalnej i pieniężnej oraz inwestycje strategiczne.")

    # Decyzje gracza
    try:
        G = float(input("Wydatki rządowe G: "))
        T = float(input("Podatki T: "))
        r = float(input("Stopa procentowa r (%): "))
        invest_tech = float(input("Inwestycje w technologię (punkty): "))
    except ValueError:
        slow_print("Błędne dane, używamy wartości domyślnych 0.")
        G, T, r, invest_tech = 0, 0, 0, 0

    decisions = {'G': G, 'T': T, 'r': r, 'invest_tech': invest_tech}

    # Inwestycje strategiczne zwiększają PKB potencjalny w przyszłości
    state['Y_pot'] += invest_tech * 0.5

    # Aktualizacja gospodarki
    update_state(state, decisions)
    apply_random_shocks(state)

    # Edukacja
    if state['Y'] > state['Y_pot']:
        slow_print("PKB > potencjał: boom gospodarczy, inflacja rośnie, bezrobocie spada.")
    elif state['Y'] < state['Y_pot']:
        slow_print("PKB < potencjał: recesja, bezrobocie rośnie, inflacja niska.")
    else:
        slow_print("Gospodarka w równowadze: stabilny wzrost.")

    # Punktacja za stabilność gospodarki
    score = max(0, 100 - abs(state['Y']-state['Y_pot']) - abs(state['inflacja']-2)*10 - state['bezrobocie']*5)
    return score

# ---------------------------
# Wizualizacja wyników
# ---------------------------
def plot_history(history):
    plt.figure(figsize=(12,6))
    plt.plot(history['Y'], label='PKB')
    plt.plot(history['Y_pot'], label='PKB potencjalny', linestyle='--')
    plt.plot(history['inflacja'], label='Inflacja (%)')
    plt.plot(history['bezrobocie'], label='Bezrobocie (%)')
    plt.xlabel('Rok')
    plt.ylabel('Wartość')
    plt.title('Symulacja gospodarcza - trendy')
    plt.legend()
    plt.grid(True)
    plt.show()

# ---------------------------
# Główna funkcja gry
# ---------------------------
def play_game():
    slow_print("Witaj w MakroSymulatorze MASTER! Nauczysz się makroekonomii poprzez decyzje strategiczne.\n")

    # Stan początkowy gospodarki
    state = {
        'Y': 1000,
        'Y_pot': 1000,
        'inflacja': 2.0,
        'bezrobocie': 5.0,
        'U_natural': 5.0,
        'export': 100,
        'import': 80
    }

    history = {'Y': [], 'Y_pot': [], 'inflacja': [], 'bezrobocie': []}
    total_score = 0
    turns = 10

    for turn in range(1, turns+1):
        score = player_turn(turn, state)
        total_score += score

        # Zapisywanie historii
        history['Y'].append(state['Y'])
        history['Y_pot'].append(state['Y_pot'])
        history['inflacja'].append(state['inflacja'])
        history['bezrobocie'].append(state['bezrobocie'])

    # Podsumowanie
    slow_print("\n=== KONIEC GRY ===")
    show_economy(state, turns)
    slow_print(f"Twój wynik punktowy: {total_score:.2f} / {turns*100}")
    slow_print("Gratulacje! Gra pokazuje pełne interakcje IS-LM, polityki fiskalnej i pieniężnej, cykle koniunkturalne i postęp technologiczny.\n")

    # Wizualizacja
    plot_history(history)

# ---------------------------
# Uruchomienie gry
# ---------------------------
if __name__ == "__main__":
    play_game()
