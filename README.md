# Finance Backtesting and Historical Data Analysis

This python project enables backtesting of trading strategies based on historical data.

It provides the structure to implement your specific buy and sell strategy, and compare to a "buy and hold strategy". 

The period, equities, strategy, can all be configured in the code.

![Backtesting](https://mtlberriawsbucket.s3.us-east-2.amazonaws.com/Backtesting_Example.png)

It also provides functions to perform historical data analysis, such as generating the distribution of an equity daily change over a given period of time.

Example:
![Distribution](https://mtlberriawsbucket.s3.us-east-2.amazonaws.com/SP500_Probability_Density_10y_vs_corona_period.png)


## Getting Started



### Prerequisites

That project was built on Python 3.7.

It uses the following modules:
* numpy       (for scientific computing, and array work)
* pandas      (equities historical data is stored as pandas dataframes)
* [yfinance](https://pypi.org/project/yfinance/)    (module used to get financial historical data)
* matplotlib  (to plot results, either in an exported PDF, or interactive backend)

I suggest you use [Anaconda](https://www.anaconda.com/) to create a virtual environment where those modules will be available.

To include 'yfinance' in your virtual environment, you will have to run:
```
pip install yfinance
```

### Installing

Clone the present repository on your local machine, and run "app.py".



## Using



### Backtesting

In the 'app.py' file:

1. Set the Global parameters for equities subject to Backtesting:
```
equities_list = ['SPY', 'AMD', 'SNAP', 'INTC', 'MSFT', 'TSLA', 'AAPL', 'MU', 'NVDA'] # List of equities that are going to be used for backtesting
period = '1y' # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
interval = '1d' #valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
prepost = False # download pre/post regular market hours data
```

2. Define the parameters to be used by your strategy, for example:
```
spy_large_move = -0.5 # Setting what is considered to be a SPY large move in one day = -0.5%
target_profit_taking = 5.0 # Setting the target profit for stock when taking a position = + 5%
starting_capital = 10000.0 # Starting capital to invest: $10,000
```

3. Customize your strategy function implementation (in the file 'functions.py'):
```
def generate_strategy_columns(df_list, starting_capital):
```

4. Run backtesting:
```
df_list = run_backtesting(equities_list, period, interval, prepost, spy_large_move, starting_capital) # run the backtesting
```

5. Plot and export the results (PDF):
```
plot_and_export_to_pdf(df_list, 3, 3, name_of_output_pdf) # plot the list of dataframes and export to pdf, columns, rows per page
```

An output PDF file will be created with the result of your backtesting:
![Backtesting](https://mtlberriawsbucket.s3.us-east-2.amazonaws.com/Backtesting_Example.png)



### Historical Data Analysis

1. Customize the equity dristribution function to fit the need of your use case (in the 'functions.py' file):
```
def plot_equity_change_distribution(equity, period):
```

2. Plot the equity change distribution over the period (in the 'app.py' file):
```
plot_equity_change_distribution(equity='^GSPC', period='10y') # plot the S&P distribution
```

An output figure will be created in the interactive backend (macosx):
![Distribution](https://mtlberriawsbucket.s3.us-east-2.amazonaws.com/SP500_Probability_Density_10y_vs_corona_period.png)





## Built With

* [Anaconda](https://www.anaconda.com/) - Access and Manage science libraries and packages
* [Yfinance](https://pypi.org/project/yfinance/) - Financial market data downloader

## Author

* **Joffrey Armellini** - *Initial work* - [MtlBerri](https://github.com/mtlberri)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
