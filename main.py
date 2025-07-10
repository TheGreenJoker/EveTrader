from flask import Flask, render_template, request, flash
import json
from manage import analyse_data

app = Flask(__name__)
app.secret_key = 'une_clef_secrete_pour_flash'  # nécessaire pour flash messages

# Charger et inverser le JSON stations (nom → id)
with open('data/staStations.json', 'r', encoding='utf-8') as f:
    station_dict = json.load(f)

# Inverse dict : nom → id (pour lookup rapide)
station_name_to_id = {name: int(station_id) for station_id, name in station_dict.items()}


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    error = None
    if request.method == 'POST':
        min_profit_percent = float(request.form['min_profit_percent'])
        min_volume_per_day = int(request.form['min_volume_per_day'])
        min_daily_sold = int(request.form['min_daily_sold'])
        min_daily_bought = int(request.form['min_daily_bought'])
        region_id = int(request.form['region_id'])
        station_name = request.form['station_name'].strip()
        top_n = int(request.form['top_n'])
        fetch_web = request.form.get('fetch_web') == 'on'

        # Trouver l'ID de station via le nom
        station_id = station_name_to_id.get(station_name)
        if station_id is None:
            error = f"Nom de station inconnu : {station_name}"
            flash(error)
        else:
            results = analyse_data(
                min_profit_percent,
                min_volume_per_day,
                min_daily_sold,
                min_daily_bought,
                region_id,
                station_id,
                top_n,
                fetch_web
            )

    return render_template('index.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
