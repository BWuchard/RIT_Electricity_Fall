import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

def identify_sustained_declines(df):
    """
    Identifies periods of sustained decline in the value column.
    A sustained decline is defined as a period where the overall trend is negative,
    from a peak until the values start increasing again.
    """
    if 'Value' not in df.columns:
        print("Warning: Value column not found. Available columns:", df.columns.tolist())
        return pd.DataFrame()
    
    # Initialize lists to store decline periods
    decline_periods = []
    in_decline = False
    decline_start_idx = None
    previous_value = None
    min_decline_length = 3  # Minimum number of points to consider it a real decline
    
    values = df['Value'].values
    
    for i in range(len(values)):
        current_value = values[i]
        
        if previous_value is not None:
            if not in_decline:
                # Check if this could be the start of a decline
                if current_value < previous_value:
                    # Look ahead to confirm it's a real decline trend
                    if i < len(values) - 2:  # Ensure we have points to look ahead
                        next_few_points = values[i:i+3]  # Look at next few points
                        if all(next_few_points[j] <= next_few_points[j-1] for j in range(1, len(next_few_points))):
                            in_decline = True
                            decline_start_idx = i - 1  # Include the peak
            else:
                # We're in a decline period, check if it's ending
                if current_value > previous_value:
                    # Look ahead to confirm the trend is really reversing
                    if i < len(values) - 2:  # Ensure we have points to look ahead
                        next_few_points = values[i:i+3]  # Look at next few points
                        if all(next_few_points[j] >= next_few_points[j-1] for j in range(1, len(next_few_points))):
                            # End of decline period
                            if i - decline_start_idx >= min_decline_length:
                                decline_period = df.iloc[decline_start_idx:i+1].copy()
                                decline_period['decline_start_time'] = df.iloc[decline_start_idx]['DateTime']
                                decline_period['decline_end_time'] = df.iloc[i]['DateTime']
                                decline_period['peak_value'] = values[decline_start_idx]
                                decline_period['trough_value'] = values[i]
                                decline_period['total_decline'] = values[decline_start_idx] - values[i]
                                decline_period['decline_duration'] = i - decline_start_idx
                                decline_periods.append(decline_period)
                            in_decline = False
                            decline_start_idx = None
        
        previous_value = current_value
    
    # Handle case where decline continues to the end of the dataset
    if in_decline and (len(values) - decline_start_idx >= min_decline_length):
        decline_period = df.iloc[decline_start_idx:].copy()
        decline_period['decline_start_time'] = df.iloc[decline_start_idx]['DateTime']
        decline_period['decline_end_time'] = df.iloc[-1]['DateTime']
        decline_period['peak_value'] = values[decline_start_idx]
        decline_period['trough_value'] = values[-1]
        decline_period['total_decline'] = values[decline_start_idx] - values[-1]
        decline_period['decline_duration'] = len(values) - decline_start_idx
        decline_periods.append(decline_period)
    
    if decline_periods:
        return pd.concat(decline_periods)
    return pd.DataFrame()

def process_monthly_circuits(excel_file):
    """
    Process each month's sheet for both circuits and identify sustained decline periods.
    """
    months = ['April', 'May', 'June', 'July', 'August', 'September']
    results = {}
    
    for month in months:
        try:
            print(f"Processing sheet: {month}")
            df = pd.read_excel(excel_file, sheet_name=month)
            
            for circuit in ['A', 'B']:
                circuit_data = df[df['Circuit'] == circuit].copy()
                
                if len(circuit_data) == 0:
                    print(f"No data found for Circuit {circuit} in sheet {month}")
                    continue
                
                try:
                    circuit_data['Date'] = pd.to_datetime(circuit_data['Date'])
                    circuit_data['Hour'] = circuit_data['Hour'].astype(str).str.zfill(2)
                    circuit_data['Minute'] = circuit_data['Minute'].astype(str).str.zfill(2)
                    circuit_data['DateTime'] = pd.to_datetime(
                        circuit_data['Date'].dt.strftime('%Y-%m-%d') + ' ' + 
                        circuit_data['Hour'] + ':' + 
                        circuit_data['Minute']
                    )
                except Exception as e:
                    print(f"Error creating DateTime for sheet {month}, Circuit {circuit}: {str(e)}")
                    continue
                
                circuit_data = circuit_data.sort_values('DateTime')
                
                # Find sustained decline periods
                decline_periods = identify_sustained_declines(circuit_data)
                
                if not decline_periods.empty:
                    results[f"{month}_Circuit_{circuit}"] = decline_periods
                    print(f"Found {len(decline_periods)} decline periods for {month} Circuit {circuit}")
                else:
                    print(f"No sustained decline periods found for {month} Circuit {circuit}")
                    
        except Exception as e:
            print(f"Error processing {month}: {str(e)}")
            
    return results

def plot_circuit_declines(df, decline_df, circuit, month):
    """
    Creates a plot showing original data and sustained decline periods for a specific circuit.
    """
    plt.figure(figsize=(15, 8))
    
    # Plot original data
    plt.plot(df['Date'], df['Value'], label='Original Data', alpha=0.6)
    
    # Plot decline periods with different colors
    for i, group in enumerate(decline_df.groupby('decline_start_time')):
        period_data = group[1]
        plt.plot(period_data['Date'], period_data['Value'], 
                'r-', linewidth=2, alpha=0.8)
    
    if decline_df.empty:
        plt.title(f'{month} - Circuit {circuit} (No Sustained Declines Found)')
    else:
        plt.title(f'{month} - Circuit {circuit} Sustained Decline Periods')
    
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def analyze_all_circuits(excel_file):
    """
    Analyze and visualize sustained decline periods for all months and circuits.
    """
    print(f"Starting analysis of {excel_file}")
    results = process_monthly_circuits(excel_file)
    
    if not results:
        print("No results were generated. Please check the error messages above.")
        return results
    
    output_file = 'sustained_decline_periods.xlsx'
    print(f"Saving results to {output_file}")
    with pd.ExcelWriter(output_file) as writer:
        for key, df in results.items():
            sheet_name = key[:31]
            df.to_excel(writer, sheet_name=sheet_name)
            print(f"Saved sheet: {sheet_name}")
    
    return results# Run the analysis with your specific filename
decline_results = analyze_all_circuits('ATestByMonth.xlsx')

# Then for each month and circuit, create the plot
months = ['April', 'May', 'June', 'July', 'August', 'September']
for month in months:
    for circuit in ['A', 'B']:
        # Read original data
        df = pd.read_excel('ATestByMonth.xlsx', sheet_name=month)
        circuit_data = df[df['Circuit'] == circuit].copy()
        
        # Get decline periods for this month/circuit
        decline_key = f"{month}_Circuit_{circuit}"
        if decline_key in decline_results:
            decline_df = decline_results[decline_key]
            plot_circuit_declines(circuit_data, decline_df, circuit, month)
