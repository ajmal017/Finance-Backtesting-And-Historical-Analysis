import pandas as pd
from financeclasses import fclasses as fc

# Global parameters
equities_list = ['SPY', 'AMD', 'AAPL', 'NVDA', 'MSFT', 'SNAP', 'FNV',
                 'MU', 'NFLX', 'BA', 'AMZN', 'INTC', 'GLD', 'TSLA', 'BABA', 'FB']
period = '1y' # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
interval = '1d' # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
# spy_large_move = -2.0
# starting_capital = 10000

if __name__ == '__main__':

    # df = fc.run_backtesting(equities_list, period, interval, spy_large_move, starting_capital)
    # fc.plot_and_export_to_pdf(df, 3, 3, 'output.pdf')
    # fc.get_csv_files_for_equities(equities_list, period, interval)
    df_list = fc.create_df_list(equities_list, 'csv')
