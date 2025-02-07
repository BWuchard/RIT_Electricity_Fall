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

# Now continue with your existing analysis
# Get the rows where demand limit is not D0
df_exceeded_d0 = df[df['DemandLimit'] != 'D0']

# Initialize a list to store report data
report_lines = []

# Function to calculate the duration for each period above D0
def calculate_duration_above_d0(group):
    above_d0_periods = []
    current_period_start = None

    for i in range(len(group)):
        if group['DemandLimit'].iloc[i] != 'D0':
            if current_period_start is None:
                current_period_start = group['Date'].iloc[i]
        else:
            if current_period_start is not None:
                period_end = group['Date'].iloc[i]
                duration = period_end - current_period_start
                above_d0_periods.append((current_period_start, period_end, duration))
                current_period_start = None

    if current_period_start is not None:
        period_end = group['Date'].iloc[-1]
        duration = period_end - current_period_start
        above_d0_periods.append((current_period_start, period_end, duration))

    return above_d0_periods

# Generate the report for exceeding D0 and durations
grouped_dates = df.groupby(['DateOnly'])
for date, group in grouped_dates:
    if not group[group['DemandLimit'] != 'D0'].empty:
        circuits = group.groupby('Circuit')
        
        for circuit, circuit_group in circuits:
            max_limit_reached = circuit_group['DemandLimit'].max()
            report_lines.append(f"Date: {date}, Circuit: {circuit}, Maximum Demand Limit Reached: {max_limit_reached}")

            periods_above_d0 = calculate_duration_above_d0(circuit_group)

            for start, end, duration in periods_above_d0:
                report_lines.append(f"    Demand exceeded D0 from {start} to {end}, duration: {duration}")

if report_lines:
    with open('DemandLimitReportWithDuration.txt', 'w') as report_file:
        for line in report_lines:
            report_file.write(line + '\n')

    print("Report generated and saved as 'DemandLimitReportWithDuration.txt'")
else:
    print("No days exceeded D0. No report generated.")

# Generate the report for exceeding D0 and durations
grouped_dates = df.groupby(['DateOnly'])
for date, group in grouped_dates:
    # Check if either circuit exceeded D0
    if not group[group['DemandLimit'] != 'D0'].empty:  # If there's any DemandLimit != 'D0' for this date
        circuits = group.groupby('Circuit')
        
        for circuit, circuit_group in circuits:
            max_limit_reached = circuit_group['DemandLimit'].max()  # Find the highest demand limit reached on that day
            report_lines.append(f"Date: {date}, Circuit: {circuit}, Maximum Demand Limit Reached: {max_limit_reached}")

            # Now calculate the duration of periods where DemandLimit was above D0
            periods_above_d0 = calculate_duration_above_d0(circuit_group)

            for start, end, duration in periods_above_d0:
                report_lines.append(f"    Demand exceeded D0 from {start} to {end}, duration: {duration}")

# Write the report to a text file (only if there's data to report)
if report_lines:
    with open('DemandLimitReportWithDuration.txt', 'w') as report_file:
        for line in report_lines:
            report_file.write(line + '\n')

    print("Report generated and saved as 'DemandLimitReportWithDuration.txt'")
else:
    print("No days exceeded D0. No report generated.")

# Step 1: Convert 'Date' to just the date part for day-based analysis
df['DateOnly'] = df['Date'].dt.date

# Step 2: Filter rows where DemandLimit is not 'D0'
df_exceeded_d0 = df[df['DemandLimit'] != 'D0']

# Step 3: Identify cases where only Circuit A, only Circuit B, or both exceeded D0
# Group by date and circuit to check for exceedances per circuit
grouped_dates = df_exceeded_d0.groupby(['DateOnly', 'Circuit'])['DemandLimit'].max()

# Convert to a DataFrame for easier manipulation
grouped_df = grouped_dates.reset_index()

# Count unique days for Circuit A and Circuit B exceedances
only_a_exceeded = grouped_df[grouped_df['Circuit'] == 'A']['DateOnly'].unique()
only_b_exceeded = grouped_df[grouped_df['Circuit'] == 'B']['DateOnly'].unique()

# Count cases where both circuits exceeded D0 on the same date
both_exceeded = grouped_df.groupby('DateOnly').filter(lambda x: len(x) > 1)

# Unique counts for the final report
unique_days_a = len(set(only_a_exceeded))
unique_days_b = len(set(only_b_exceeded))
unique_days_both = len(set(both_exceeded['DateOnly']))

# Step 4: Count by month for individual circuits with specific dates
grouped_by_month = df_exceeded_d0.groupby([df['Date'].dt.month, 'Circuit'])['DateOnly'].apply(list)

# Step 5: Count months where both circuits exceeded D0
both_exceeded_by_month = both_exceeded.groupby(both_exceeded['DateOnly'].map(lambda d: d.month))['DateOnly'].apply(list)

# Write results to a text file
with open('exceeded_d0_report.txt', 'w') as f:
    # Total unique days that exceeded D0
    total_unique_days = df_exceeded_d0['DateOnly'].nunique()
    f.write(f"Total unique days exceeding D0: {total_unique_days}\n\n")

    # Count for each circuit
    f.write(f"Unique days where only Circuit A exceeded D0: {unique_days_a}\n")
    f.write(f"Unique days where only Circuit B exceeded D0: {unique_days_b}\n")
    f.write(f"Unique days where both circuits exceeded D0: {unique_days_both}\n\n")

    # Count by month with specific dates
    f.write("Monthly exceedance report (by Circuit A and B):\n")
    for (month, circuit), dates in grouped_by_month.items():
        unique_dates = set(dates)
        f.write(f"Month {month}, Circuit {circuit}: {len(unique_dates)} unique days (Dates: {', '.join(map(str, unique_dates))})\n")

    # Count for both circuits exceeding D0 by month with specific dates
    f.write("\nMonthly count where both circuits exceeded D0:\n")
    for month, dates in both_exceeded_by_month.items():
        unique_dates = set(dates)
        f.write(f"Month {month}: {len(unique_dates)} unique days (Dates: {', '.join(map(str, unique_dates))})\n")

print("Report saved to 'exceeded_d0_report.txt'")

# Get unique months present in the DataFrame
unique_months = df['Month'].unique()

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

    # Create a figure and axes for the plots
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 10))

    # Plot for Circuit A
    circuit_a = monthly_data[monthly_data['Circuit'] == 'A']
    axes[0].set_title(f'Circuit A: Value in Month {month}')
    axes[0].set_xlabel('Date and Time')
    axes[0].set_ylabel('kW')


    # Assign colors based on the DemandLimit values
    for index, row in circuit_a.iterrows():
        if row['DemandLimit'] == 'D3':
            axes[0].scatter(row['Date'], row['Value'], color=colors['D3'], label='D3 Limit' if 'D3 Limit' not in axes[0].get_legend_handles_labels()[1] else "")
        elif row['DemandLimit'] == 'D2':
            axes[0].scatter(row['Date'], row['Value'], color=colors['D2'], label='D2 Limit' if 'D2 Limit' not in axes[0].get_legend_handles_labels()[1] else "")
        elif row['DemandLimit'] == 'D1':
            axes[0].scatter(row['Date'], row['Value'], color=colors['D1'], label='D1 Limit' if 'D1 Limit' not in axes[0].get_legend_handles_labels()[1] else "")
        else:
            axes[0].scatter(row['Date'], row['Value'], color=colors['D0'], label='D0 Limit' if 'D0 Limit' not in axes[0].get_legend_handles_labels()[1] else "")
    
    # Add reference lines for D1Limit, D2Limit, and D3Limit
    if not circuit_a.empty:
        d1_limit_a = circuit_a['D1Limit'].iloc[0] if 'D1Limit' in circuit_a.columns else np.nan
        d2_limit_a = circuit_a['D2Limit'].iloc[0] if 'D2Limit' in circuit_a.columns else np.nan
        d3_limit_a = circuit_a['D3Limit'].iloc[0] if 'D3Limit' in circuit_a.columns else np.nan

        if pd.notna(d1_limit_a):
            axes[0].axhline(y=d1_limit_a, color='red', linestyle='--', label='D1Limit')
        if pd.notna(d2_limit_a):
            axes[0].axhline(y=d2_limit_a, color='green', linestyle='--', label='D2Limit')
        if pd.notna(d3_limit_a):
            axes[0].axhline(y=d3_limit_a, color='purple', linestyle='--', label='D3Limit')

        # Set the lower Y-limit
        axes[0].set_ylim(bottom=d1_limit_a - 500)

    axes[0].legend()
    axes[0].grid(True, which='both', axis='both')  # Enable grid lines for both axes

    # Plot for Circuit B
    circuit_b = monthly_data[monthly_data['Circuit'] == 'B']
    axes[1].set_title(f'Circuit B: Value in Month {month}')
    axes[1].set_xlabel('Date and Time')
    axes[1].set_ylabel('kW')


    # Assign colors based on the DemandLimit values
    for index, row in circuit_b.iterrows():
        if row['DemandLimit'] == 'D3':
            axes[1].scatter(row['Date'], row['Value'], color=colors['D3'], label='D3 Limit' if 'D3 Limit' not in axes[1].get_legend_handles_labels()[1] else "")
        elif row['DemandLimit'] == 'D2':
            axes[1].scatter(row['Date'], row['Value'], color=colors['D2'], label='D2 Limit' if 'D2 Limit' not in axes[1].get_legend_handles_labels()[1] else "")
        elif row['DemandLimit'] == 'D1':
            axes[1].scatter(row['Date'], row['Value'], color=colors['D1'], label='D1 Limit' if 'D1 Limit' not in axes[1].get_legend_handles_labels()[1] else "")
        else:
            axes[1].scatter(row['Date'], row['Value'], color=colors['D0'], label='D0 Limit' if 'D0 Limit' not in axes[1].get_legend_handles_labels()[1] else "")

    # Add reference lines for D1Limit, D2Limit, and D3Limit
    if not circuit_b.empty:
        d1_limit_b = circuit_b['D1Limit'].iloc[0] if 'D1Limit' in circuit_b.columns else np.nan
        d2_limit_b = circuit_b['D2Limit'].iloc[0] if 'D2Limit' in circuit_b.columns else np.nan
        d3_limit_b = circuit_b['D3Limit'].iloc[0] if 'D3Limit' in circuit_b.columns else np.nan

        if pd.notna(d1_limit_b):
            axes[1].axhline(y=d1_limit_b, color='red', linestyle='--', label='D1Limit')
        if pd.notna(d2_limit_b):
            axes[1].axhline(y=d2_limit_b, color='green', linestyle='--', label='D2Limit')
        if pd.notna(d3_limit_b):
            axes[1].axhline(y=d3_limit_b, color='purple', linestyle='--', label='D3Limit')

        # Set the lower Y-limit
        axes[1].set_ylim(bottom=d1_limit_b - 500)

    axes[1].legend()
    axes[1].grid(True, which='both', axis='both')  # Enable grid lines for both axes

    # Format x-axis date ticks to show every week (major) and every day (minor)
    for ax in axes:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))  # Major ticks every week
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))  # Format major ticks to show day only
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))  # Minor ticks every day
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))  # Format minor ticks for daily grid lines
        ax.grid(which='both', axis='x', linestyle='--', alpha=0.7)  # Enable vertical grid lines for major and minor ticks

    # Adjust layout
    plt.tight_layout()
    
    # Show the plots for the current month
    plt.show()


