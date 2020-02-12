import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# Setting Seaborn style via set()
sns.set()

# Read the CSV file #######################################################
def read_nasdaq_csv(file_name):
    df0 = pd.read_csv(file_name)
    # Re-order from oldest to newest, and re-indexing
    df0 = df0.sort_index(ascending=False)
    df0 = df0.reset_index(drop=True)
    # Rename the Close/Last column to Close
    df0 = df0.rename(columns={'Close/Last': 'Close'})
    # Take a sub-set of the data and make it clear it is a copy
    df1 = df0.tail(10).copy()
    return df1
############################################################################

# Calculate Change from Day to Day ########################################
def add_change_column(df0):
    # Column initiated to calculate the % Change column
    changes_list = []
    # Initiating previous close
    previous_close = df0.iloc[0]['Close']
    # Iterate through rows to calculate changes from day to day
    for i, j in df0.iterrows():
        day_close = j['Close']
        day_change = ((day_close - previous_close) / previous_close) * 100
        changes_list.append(day_change)
        # Get ready for next iteration
        previous_close = day_close
    df0['Change'] = changes_list
    return df0
##########################################################

# PLOT ############################################
def plot_my_df(df0):
    # Plot on ax1
    ax1 = sns.lineplot(x='Date', y='Close', data=df0)
    # Creating a new axis sharing the same x
    ax2 = ax1.twinx()
    # Creating a Custom Palette
    custom_palette = []
    for change in df0['Change']:
        if change <= 0:
            custom_palette.append('r')
        else:
            custom_palette.append('g')
    # Plot on ax2
    sns.barplot(x='Date', y='Change', data=df0, ax=ax2, palette=custom_palette)
    # Redefine y axis for ax2
    ax2.set(ylim=(-3, 3))
    # Hide the grid on ax2
    ax2.grid(False)
##############################################################

# MAIN #######################################################
spy_df = read_nasdaq_csv('HistoricalQuotes_SPY_5Y_02112020.csv')
df = add_change_column(df)
plot_my_df(df)
