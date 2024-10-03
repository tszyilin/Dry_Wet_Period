# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 14:20:37 2024

@author: Safin.Lin
"""

import pandas as pd
import time

start_time = time.time()

# User input
dry_threshold = 760
dry_wet = 'Wet'
pool = 'PoolB'
read_file = pool + '.xlsx'

''' Main '''
sheetName = ['No', '2.6', '2.6GW']

bins = [0, 10, 20, 30, 50, 75, 100, 150, 200, 300, float('inf')]  # Define your bin edges
labels = []
for i in range(0, 10):
    if i == 0:
        string = "<" + str(bins[i+1])
        labels.append(string)
    elif i == 9:
        string = ">" + str(bins[i])
        labels.append(string)
    else:
        string = str(bins[i]) + "-" + str(bins[i+1])
        labels.append(string)

df_output = pd.DataFrame()
df_output['Duration'] = labels


for i in range(3):
# Create a DataFrame
    df = pd.read_excel(read_file, sheet_name=sheetName[i])
    
    # Define dry threshold
   
    
    # Create a column to indicate if the day is dry (storage < dry_threshold) change for wet
    if dry_wet == 'Dry':
        df[dry_wet] = df['Storage'] < dry_threshold
    else:
        df[dry_wet] = df['Storage'] > dry_threshold
    
    # Calculate the duration of dry periods
    dry_periods = []
    dry_start = None
    dry_duration = 0
    
    for index, row in df.iterrows():
        if row[dry_wet]:
            if dry_start is None:
                dry_start = row['Date']  # Start of a dry period
            dry_duration += 1  # Increment duration
        else:
            if dry_start is not None:  # If we were in a dry period and now it's over
                dry_periods.append({'Start': dry_start, 'End': row['Date'] - pd.Timedelta(days=1), 'Duration': dry_duration})
                dry_start = None
                dry_duration = 0
    
    # Add the final dry period if it ended on the last day
    if dry_start is not None:
        dry_periods.append({'Start': dry_start, 'End': df.iloc[-1]['Date'], 'Duration': dry_duration})
    
    # Convert dry periods to a DataFrame for better presentation
    dry_periods_df = pd.DataFrame(dry_periods)
    dry_periods_df['Duration'] = dry_periods_df['Duration']-1
    
    print(dry_periods_df)
    
    
    

    
    # Create a new column that categorizes the durations into the specified bins
    dry_periods_df['Duration Group'] = pd.cut(dry_periods_df['Duration'], bins=bins, labels=labels, right=False)
    
    # Count the number of occurrences for each duration group
    duration_group_counts = dry_periods_df['Duration Group'].value_counts().sort_index()
    duration_group_df = pd.DataFrame(duration_group_counts).reset_index()
    duration_group_df.columns = ['Duration Group', 'A']
    
    df_output[sheetName[i]] = duration_group_df['A']

file_name = pool + "_" + dry_wet + ".xlsx"
df_output.to_excel(file_name, index=False)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds")