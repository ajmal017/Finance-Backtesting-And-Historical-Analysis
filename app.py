import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# Setting seaborn style via set()
sns.set()

print("Hello SPY by Seaborn")

# Reading the CSV file
df = pd.read_csv('HistoricalQuotes.csv')
# Re-ordering from oldest to newest, and re-indexing
df = df.sort_index(ascending=False)
df = df.reset_index(drop=True)
# Rename the Close/Last column to Close
df = df.rename(columns={'Close/Last':'Close'})

# Take a sub-set of the data just on a week
df0 = df.head(30)

# Column initiated to calculate the % Change column
changes_list = []
# Initiating previous close
previous_close = df0.iloc[0]['Close']
# Iterate through rows to calculate changes from day to day
for i,j in df0.iterrows():
    #print(i,j)
    #print()
    day_close = j['Close']
    day_change = ((day_close - previous_close) / previous_close) * 100
    changes_list.append(day_change)
    #print(changes_list)
    # Get ready for next iteration
    previous_close = day_close
    #print()

df0['Change'] = changes_list

# Seaborn Plot
# Plot on ax1
ax1 = sns.lineplot(x='Date', y='Close', data=df0)
'''
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
ax2.set(ylim=(-3,3))
# Hide the grid on ax2
ax2.grid(False)
'''