from builtins import str
import numpy as np
import pandas as pd
import re
import datetime
import matplotlib.pyplot as plt
# Close all figure windows
plt.close('all')

# Global Parameters ####################################################################
# Names of the files to import (Yahoo Finance csv files)
data_files_names = ['SPY.csv',
                    'TSLA.csv'
                    ]

# List of columns from data source being days 
columns_being_prices = ['Open', 'High', 'Low', 'Close']
# Time horizon used (in open trading days)
time_horizon = 10
# Setting what is considered to be a SPY large move in one day = -0.5%
spy_large_move = -0.5
# Setting the target profit for TSLA when taking a position = + 5%
target_profit_taking = 5.0
# Starting capital to invest: $10,000
starting_capital = 10000.0
#####################################################################################

# Read the CSV file  & Prepare data #######################################################
def read_data_source_csv(file_name):
    df0 = pd.read_csv(file_name)
    # Set the date as the index
    df0 = df0.set_index('Date')
    # Apply the function on the index to convert the string date into a proper date
    df0.index = df0.index.map(dstring_to_date)
    # Add a column named 'Change' giving the percentage of change between today's Close and previous Close
    df0 = generate_change_column(df0)
    # Take a sub-set of the data (for the time horizon) and make it clear it is a copy
    df1 = df0.tail(time_horizon).copy()
    return df1
############################################################################

# TRANSFORM DATE STRING INTO DATE ##########################################
def dstring_to_date(dstr):
    ''' Method that returns a date based on the date string  '''
    # Set the format as it is originally (as a string in the Data Frame read from the CSV)
    format_of_date_string = '%Y-%m-%d'
    # Convert into a datetime object and return it
    return datetime.datetime.strptime(dstr, format_of_date_string)
#########################################################################

# Calculate Change from Day to Day ########################################
def generate_change_column(df0):
    # Be n the length of the data frame
    n = df0.__len__()
    # Iterating over the data frame rows
    for r in range(1, n):
        previous_close = df0.iloc[r-1]['Close']
        close = df0.iloc[r]['Close']
        try:
            change = ((close - previous_close) / previous_close)*100
            df0.at[df0.index[r], 'Change'] = change
        except ZeroDivisionError:
            print('Previous Close = 0, Cannot calculate change. ZeroDivisionError.')
    return df0
##########################################################

# Method adding the relative stregth signal column ##########
def add_relative_stregth_column(rs_df):
    # Initiate a list to store the signals
    rs_signal_list = []
    # Iterate over the rows to calculate if signal or not
    for i,j in rs_df.iterrows():
        spy_change = j['SPY Change']
        stock_change = j['TSLA Change']
        if is_showing_rstrength(spy_change,stock_change, spy_large_move) == True:
            rs_signal_list.append(True)
        else:
            rs_signal_list.append(False)
    # Add the column to the dataset
    rs_df['RS Signal'] = rs_signal_list
    return rs_df
############################################################

# STRATEGY BUY SELL ####################################################
def add_strategy_columns(rs_df):
    # Buying when getting the signal, selling at the profit target

    # Init my tracking variables
    in_out_status = 'OUT'
    position_qty = 0
    entry_point_position_value = 0
    position_value = 0
    cash_at_hands = starting_capital
    total_equity = position_value + cash_at_hands

    # Initialize strategy columns
    buy_sell_actions_list = []
    buy_sell_qty_list = []
    position_value_list = []
    cash_at_hands_list = []
    total_equity_list = []

    # Iterate over rows
    for i,j in rs_df.iterrows():

        # WAIT AND DO NOTHING
        if in_out_status == 'OUT' and j['RS Signal'] == False :
            # NO ACTION
            buy_sell_actions_list.append('-')
            # QTY
            buy_sell_qty_list.append(position_qty)
            # POSITION VALUE
            position_value_list.append(position_value)
            # CASH AT HANDS
            cash_at_hands_list.append(cash_at_hands)
            # TOTAL EQUITY
            total_equity = cash_at_hands + position_value
            total_equity_list.append(total_equity)

        # ENTRY POINT (BUY)
        elif in_out_status == 'OUT' and j['RS Signal'] == True :
            # BUY ACTION
            in_out_status = 'IN'
            buy_sell_actions_list.append('BUY')
            # QTY
            position_qty = int(cash_at_hands / j['TSLA Close'])
            buy_sell_qty_list.append(position_qty)
            # POSITION VALUE
            position_value = position_qty * j['TSLA Close']
            entry_point_position_value = position_value
            position_value_list.append(position_value)
            # CASH AT HANDS
            cash_at_hands = cash_at_hands - position_value
            cash_at_hands_list.append(cash_at_hands)
            # TOTAL EQUITY
            total_equity = cash_at_hands + position_value
            total_equity_list.append(total_equity)

        # HOLD
        elif in_out_status =='IN' and (position_value - entry_point_position_value) < 1000:
            # HOLD ACTION
            buy_sell_actions_list.append('HOLD')
            # QTY
            buy_sell_qty_list.append(position_qty)
            # POSITION VALUE
            position_value = position_qty * j['TSLA Close']
            position_value_list.append(position_value)
            # CASH AT HANDS
            cash_at_hands_list.append(cash_at_hands)
            # TOTAL EQUITY
            total_equity = cash_at_hands + position_value
            total_equity_list.append(total_equity)

        # SELL (EXIT POINT)
        elif in_out_status == 'IN' and (position_value - entry_point_position_value) >= 1000:
            # SELL ACTION
            in_out_status = 'OUT'
            buy_sell_actions_list.append('SELL')
            # CASH AT HANDS
            cash_at_hands = cash_at_hands + (position_qty * j['TSLA Close'])
            cash_at_hands_list.append(cash_at_hands)
            # QTY
            position_qty = 0
            buy_sell_qty_list.append(position_qty)
            # POSITION VALUE
            position_value = 0
            position_value_list.append(position_value)
            # TOTAL EQUITY
            total_equity = cash_at_hands + position_value
            total_equity_list.append(total_equity)

    # Add new columns to the DataFrame
    rs_df['Action'] = buy_sell_actions_list
    rs_df['Qty'] = buy_sell_qty_list
    rs_df['Position Value'] = position_value_list
    rs_df['Cash at hands'] = cash_at_hands_list
    rs_df['Total Equity'] = total_equity_list

    return rs_df

######################################################################

# Methods determining if stock showing relative strength ############
def is_showing_rstrength(spy_change, stock_change, spy_large_move):
    ''' Method returning True if stock showing relative strength versus a SPY large move '''
    # If the SPY is doing a large move down
    if spy_change <= spy_large_move and stock_change >= 0:
        return True
    else:
        return False
#####################################################################

# MAIN ################################################################################################3
# Read and prepare data
spy_df = read_data_source_csv(data_files_names[0])
tsla_df = read_data_source_csv(data_files_names[1])


'''
# Initial position taken - max possible with capital to invest
initial_position_qty = int(starting_capital / tsla_df['Close'][0])

# Create dataframe for my relative strength signal
# Initiate my relative strength Data Frame with the spy change Series of data
rs_df = pd.DataFrame({'SPY Close': spy_df['Close'],
                      'TSLA Close': tsla_df['Close'],
                      'SPY Change': spy_df['Change'],
                      'TSLA Change': tsla_df['Change'],
                      'TSLA Buy and Hold Value': tsla_df['Close'] * initial_position_qty
                      })
# Add column with relative strength signal column
rs_df = add_relative_stregth_column(rs_df)
# Add strategy BUY SELL actions column
rs_df = add_strategy_columns(rs_df)

# PLOT
# Plot the selected columns
rs_df.loc[ : , ['TSLA Buy and Hold Value', 'Total Equity'] ].plot()
'''
#######################################################################################################3