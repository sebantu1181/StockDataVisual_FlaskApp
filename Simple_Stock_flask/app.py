
from flask import Flask, render_template, request
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    stocks_df = pd.read_csv('stocks.csv')
    stock_symbols = list(stocks_df['symbol'])

    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        chart_type = request.form['chart_type']
        time_series = request.form['time_series']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Send user input to Alpha Vantage API
        base_url = "https://www.alphavantage.co/query?"
        api_key = 'CRF5E6TEAFQOQWZY'

        params = {
            "function": "TIME_SERIES_DAILY",  # Adjust the function based on time_series selection
            "symbol": stock_symbol,
            "apikey": api_key,
            "interval": "5min" if time_series == "1" else None,  # Intraday interval
            "outputsize": "full",
            "datatype": "json",
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()

            # Extract and process data from the Alpha Vantage API response
            time_series_data = data.get("Time Series (Daily)")
            if time_series_data is None:
                return render_template('index.html', error_message="No data available for the selected stock symbol.", stock_symbols=stock_symbols)

            dates = list(time_series_data.keys())
            prices = [float(time_series_data[date]["4. close"]) for date in dates]

            # Visualize the data using matplotlib
            plt.figure(figsize=(10, 6))
            if chart_type == "1":
                plt.bar(dates, prices, label="Stock Price", color="g")
            else:
                plt.plot(dates, prices, label="Stock Price", color="b")

            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.title(f"Stock Price Chart ({'Bar' if chart_type == '1' else 'Line'})")
            plt.xticks(rotation=45)
            plt.legend()

            # Save the plot to a BytesIO object
            img_io = BytesIO()
            plt.savefig(img_io, format='png')
            img_io.seek(0)
            plt.close()

            # Encode the image to base64 for embedding in HTML
            img_base64 = base64.b64encode(img_io.read()).decode('utf-8')

            return render_template('index.html', chart_data=img_base64, stock_symbols=stock_symbols, start_date=start_date, end_date=end_date)

        else:
            return render_template('index.html', error_message="Failed to retrieve data from Alpha Vantage API.", stock_symbols=stock_symbols)

    return render_template('index.html', error_message=None, stock_symbols=stock_symbols)



if __name__ == '__main__':
    app.run(debug=True, port=5009)






