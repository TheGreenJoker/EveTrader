from flask import Flask, render_template, request
from manage import analyse_data

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        min_profit_percent = float(request.form['min_profit_percent'])
        min_volume_per_day = int(request.form['min_volume_per_day'])
        min_daily_sold = int(request.form['min_daily_sold'])
        min_daily_bought = int(request.form['min_daily_bought'])
        region_id = int(request.form['region_id'])
        station_id = int(request.form['station_id'])
        top_n = int(request.form['top_n'])
        fetch_web = request.form.get('fetch_web') == 'on'

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
