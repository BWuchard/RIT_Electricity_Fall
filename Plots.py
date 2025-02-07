import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read the CSV file and ensure all columns are loaded correctly
df = pd.read_csv('C:\\Users\\steak\\Downloads\\DrKatie\\ATest.csv', low_memory=False)

# Convert the 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Drop rows where the 'Date' conversion failed (if any)
df = df.dropna(subset=['Date'])

# Extract the date part for grouping (creating the 'DateOnly' column)
df['DateOnly'] = df['Date'].dt.date
# Get unique months present in the DataFrame
unique_months = df['Month'].unique()

# Get unique circuits present in the DataFrame
unique_circuits = df['Circuit'].unique()

# Set colors for different D limits
colors = {
    'D1': 'blue',   # Color for D1
    'D2': 'green',  # Color for D2
    'D3': 'purple', # Color for D3
    'D0': 'orange'  # Color for D0
}

# Iterate over each unique month
for month in unique_months:
    # Filter data for the current month
    monthly_data = df[df['Month'] == month]
    
    if monthly_data.empty:
        continue  # Skip if there is no data for the month

    # Iterate over each unique circuit
    for circuit in unique_circuits:
        circuit_data = monthly_data[monthly_data['Circuit'] == circuit]
        
        if circuit_data.empty:
            continue  # Skip if there is no data for the circuit

        # Create a new figure for each circuit
        fig, ax = plt.subplots(figsize=(15, 5))
        ax.set_title(f'Circuit {circuit}: Value in Month {month}')
        ax.set_xlabel('Date and Time')
        ax.set_ylabel('kW')

        # Assign colors based on the DemandLimit values
        for index, row in circuit_data.iterrows():
            if row['DemandLimit'] == 'D3':
                ax.scatter(row['Date'], row['Value'], color=colors['D3'], label='D3 Limit' if 'D3 Limit' not in ax.get_legend_handles_labels()[1] else "")
            elif row['DemandLimit'] == 'D2':
                ax.scatter(row['Date'], row['Value'], color=colors['D2'], label='D2 Limit' if 'D2 Limit' not in ax.get_legend_handles_labels()[1] else "")
            elif row['DemandLimit'] == 'D1':
                ax.scatter(row['Date'], row['Value'], color=colors['D1'], label='D1 Limit' if 'D1 Limit' not in ax.get_legend_handles_labels()[1] else "")
            else:
                ax.scatter(row['Date'], row['Value'], color=colors['D0'], label='D0 Limit' if 'D0 Limit' not in ax.get_legend_handles_labels()[1] else "")

        # Add reference lines for D1Limit, D2Limit, and D3Limit
        d1_limit = circuit_data['D1Limit'].iloc[0] if 'D1Limit' in circuit_data.columns else np.nan
        d2_limit = circuit_data['D2Limit'].iloc[0] if 'D2Limit' in circuit_data.columns else np.nan
        d3_limit = circuit_data['D3Limit'].iloc[0] if 'D3Limit' in circuit_data.columns else np.nan

        if pd.notna(d1_limit):
            ax.axhline(y=d1_limit, color='red', linestyle='--', label='D1Limit')
        if pd.notna(d2_limit):
            ax.axhline(y=d2_limit, color='green', linestyle='--', label='D2Limit')
        if pd.notna(d3_limit):
            ax.axhline(y=d3_limit, color='purple', linestyle='--', label='D3Limit')

        ax.legend()
        ax.grid(True, which='both', axis='both')

        # Set the lower Y-limit
        if pd.notna(d1_limit):
            ax.set_ylim(bottom=d1_limit - 3000)

        # Format x-axis date ticks
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
        ax.grid(which='both', axis='x', linestyle='--', alpha=0.7)

        # Adjust layout and show the plot for the current circuit
        plt.tight_layout()
        plt.show()
