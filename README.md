# Finance Backtesting and Historical Data Analysis

This python project enables backtesting of trading strategies based on historical data.

It provides the structure to implement your specific buy and sell strategy, and compare to a "buy and hold strategy". 

The period, equities, strategy, can all be configured in the code.

It also provides functions to perform historical data analysis, such as generating the distribution of an equity daily change over a given period of time.


## Getting Started



### Prerequisites

That project was built on Python 3.7.

It uses the following modules:
* numpy (for scientific computing, and array work)
* pandas (equities historical data is stored as pandas dataframes)
* yfinance (module used to get financial historical data)
* matplotlib (to plot results, either in an exported PDF, or interactive backend)

I suggest you use Anaconda to create a virtual environment where those modules will be available.

To include 'yfinance' in your virtual environment, you will have to run:
```
pip install yfinance
```

### Installing

Clone the present repository on your local machine, and run "app.py".


## Built With

* [Anaconda](https://www.anaconda.com/) - Access and Manage science libraries and packages
* [Yfinance](https://pypi.org/project/yfinance/) - Financial market data downloader


## Author

* **Joffrey Armellini** - *Initial work* - [MtlBerri](https://github.com/mtlberri)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

