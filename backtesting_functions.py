from builtins import str
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt

# FUNCTIONS DEFINITION ################################################################
def create_master_data_df(data_files_names):
    '''Function returning a Data Frame with metadata about the source files'''
    # Create a list of Equity names based on files names
    # Create a lambda function extracting the string name of equity
    extract_name = lambda x: x[0:x.find('.')]
    # Create the list of equities
    equities_list = list(map(extract_name, data_files_names))
    # Create the Data Frame with all that metadata
    meta_data_df = pd.DataFrame({'Equity': equities_list, 'File Name': data_files_names})
    return meta_data_df


def read_data_source_csv(file_name, time_horizon):
    ''' Read the CSV file  & returns corresponding Data Frame '''
    df0 = pd.read_csv('data/' + file_name)
    # Set the date as the index
    df0 = df0.set_index('Date')
    # Apply the function on the index to convert the string date into a proper date
    df0.index = df0.index.map(dstring_to_date)
    # Add a column named 'Change' giving the percentage of change between today's Close and previous Close
    df0 = add_change_column(df0)
    # Take a sub-set of the data (for the time horizon) and make it clear it is a copy
    df1 = df0.tail(time_horizon).copy()
    return df1


def dstring_to_date(dstr):
    ''' Method that returns a date object based on the date string  '''
    # Set the format as it is originally (as a string in the Data Frame read from the CSV)
    format_of_date_string = '%Y-%m-%d'
    # Convert into a datetime object and return it
    return datetime.datetime.strptime(dstr, format_of_date_string)


def create_df_list(metadata_df, time_horizon):
    '''Method that creates the list of Data Frames, one per Equity'''
    # Initialize an empty list to store the Data Frames
    df_list = []
    # Iterate over the equity list
    for index, equity_row in metadata_df.iterrows():
        # create Data Frame from reading the csv file
        df0 = read_data_source_csv(equity_row['File Name'], time_horizon=time_horizon)
        # Insert a column with Equity name in the first position
        df0.insert(0, 'Equity', equity_row['Equity'])
        # Add the Data Frame to the list
        df_list.append(df0)
    return df_list


def add_change_column(df):
    ''' Calculate the Change from Day Close to Day Close and returns Data Frame with corresponding column added '''
    # Be n the length of the data frame
    n = df.__len__()
    # Iterating over the data frame rows
    for r in range(1, n):
        previous_close = df.iloc[r - 1]['Close']
        close = df.iloc[r]['Close']
        try:
            change = ((close - previous_close) / previous_close) * 100
            df.at[df.index[r], 'Change'] = change
        except ZeroDivisionError:
            print('Previous Close = 0, Cannot calculate change. ZeroDivisionError.')
    return df


def add_SPY_change(df_list, metadata_df):
    '''Add the SPY Change column to each Data Frame and return the list'''
    # Get the index of the SPY Data Frame in the list
    index_of_SPY = find_index_of_equity('SPY', metadata_df)
    # Get the SPY data frame, only the SPY change column
    spy_df = df_list[index_of_SPY]
    # Extract the Chhange column of SPY and rename the column
    spy_df_extract = spy_df['Change'].rename('SPY Change')
    # Iterate over all the dataframes and Merge the SPY columns into each of the Equity Data Frames
    for i in range(len(df_list)):
        df_list[i] = pd.merge(df_list[i], spy_df_extract, on='Date')
    return df_list


def find_index_of_equity(equity_str, metadata_df):
    '''Finds the index of an equity based on its name'''
    # Get a Series of boolean indicating where SPY equity is found
    where_is_equity_boolean_series = metadata_df['Equity'] == equity_str
    # Extract the Series indexes where equity was found
    indexes_where_found = metadata_df[where_is_equity_boolean_series].index
    # Return the int index where the first occurence was found
    index_found = indexes_where_found[0]
    return index_found


def generate_relative_strength_column(df_list, spy_large_move):
    ''' Method calculating the relative strength signal and returns the list of Data Frames with corresponding column added '''
    for df in df_list:
        # Initiate a list to store the signals
        rs_signal_list = []
        # Iterate over the rows to calculate if signal or not
        for i, j in df.iterrows():
            spy_change = j['SPY Change']
            stock_change = j['Change']
            if is_showing_rstrength(spy_change, stock_change, spy_large_move) == True:
                rs_signal_list.append(True)
            else:
                rs_signal_list.append(False)
        # Add the column to the dataset
        df['RS Signal'] = rs_signal_list
    return df_list


def is_showing_rstrength(spy_change, stock_change, spy_large_move):
    ''' Method returning True if stock showing relative strength versus a SPY large move '''
    # If the SPY is doing a large move down
    if spy_change <= spy_large_move and stock_change >= 0:
        return True
    else:
        return False


def generate_strategy_columns(df_list, starting_capital):
    ''' Method calculating the strategy columns (action, equity, ...) and returns Data Frame with corresponding columns added '''
    for df in df_list:
        # Buying when getting the signal, selling at the profit target

        # Init my tracking variables
        in_out_status = 'OUT'
        position_qty = 0
        entry_point_position_value = 0
        position_value = 0
        # Adjusting the starting capital in order to compare apples to apples between "Buy and Hold" and "Strategy"
        buy_and_hold_initial_qty = int(starting_capital / df['Close'][0])
        adjusted_starting_capital = buy_and_hold_initial_qty * df['Close'][0]
        cash_at_hands = adjusted_starting_capital
        total_equity = position_value + cash_at_hands

        # Initialize strategy columns
        buy_sell_actions_list = []
        buy_sell_qty_list = []
        position_value_list = []
        cash_at_hands_list = []
        total_equity_list = []

        # Iterate over rows
        for i, row in df.iterrows():

            # Evaluate positon value that day (for condition testing in if's below)
            position_value = position_qty * row['Close']

            # WAIT AND DO NOTHING
            if in_out_status == 'OUT' and row['RS Signal'] == False:
                # NO ACTION
                buy_sell_actions_list.append('-')
                # QTY
                buy_sell_qty_list.append(position_qty)
                # POSITION VALUE
                position_value_list.append(position_value)
                # CASH AT HANDS
                cash_at_hands_list.append(cash_at_hands)
                # Strategy Equity
                total_equity = cash_at_hands + position_value
                total_equity_list.append(total_equity)

            # ENTRY POINT (BUY)
            elif in_out_status == 'OUT' and row['RS Signal'] == True:
                # BUY ACTION
                in_out_status = 'IN'
                buy_sell_actions_list.append('BUY')
                # QTY
                position_qty = int(cash_at_hands / row['Close'])
                buy_sell_qty_list.append(position_qty)
                # POSITION VALUE
                position_value = position_qty * row['Close']
                entry_point_position_value = position_value
                position_value_list.append(position_value)
                # CASH AT HANDS
                cash_at_hands = cash_at_hands - position_value
                cash_at_hands_list.append(cash_at_hands)
                # Strategy Equity
                total_equity = cash_at_hands + position_value
                total_equity_list.append(total_equity)

            # HOLD
            elif in_out_status == 'IN' and (position_value - entry_point_position_value) < 1000:
                # HOLD ACTION
                buy_sell_actions_list.append('HOLD')
                # QTY
                buy_sell_qty_list.append(position_qty)
                # POSITION VALUE
                position_value = position_qty * row['Close']
                position_value_list.append(position_value)
                # CASH AT HANDS
                cash_at_hands_list.append(cash_at_hands)
                # Strategy Equity
                total_equity = cash_at_hands + position_value
                total_equity_list.append(total_equity)

            # SELL (EXIT POINT)
            elif in_out_status == 'IN' and (position_value - entry_point_position_value) >= 1000:
                # SELL ACTION
                in_out_status = 'OUT'
                buy_sell_actions_list.append('SELL')
                # CASH AT HANDS
                cash_at_hands = cash_at_hands + (position_qty * row['Close'])
                cash_at_hands_list.append(cash_at_hands)
                # QTY
                position_qty = 0
                buy_sell_qty_list.append(position_qty)
                # POSITION VALUE
                position_value = 0
                position_value_list.append(position_value)
                # Strategy Equity
                total_equity = cash_at_hands + position_value
                total_equity_list.append(total_equity)

        # Add new columns to the DataFrame
        df['Action'] = buy_sell_actions_list
        df['Qty'] = buy_sell_qty_list
        df['Position Value'] = position_value_list
        df['Cash at hands'] = cash_at_hands_list
        df['Strategy Equity'] = total_equity_list

    return df_list


def generate_buy_and_hold_column(df_list, starting_capital):
    '''Methods that adds the Buy and Hold Equity column based on starting capital '''
    for df in df_list:
        position_qty = int(starting_capital / df['Close'][0])
        df['Buy and Hold Equity'] = position_qty * df['Close']
    return df_list
