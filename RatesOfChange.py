import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_rate_of_change(group):
    """Calculate rate of change for a group of rows."""
    if len(group) < 2:
        return 0
    total_value_change = group['Value'].iloc[-1] - group['Value'].iloc[0]
    time_periods = len(group)
    return total_value_change / (15 * time_periods)

def identify_sustained_periods(df, time_threshold=timedelta(minutes=16)):  # Increased threshold slightly
    """Identify sustained decline periods based on time difference."""
    df = df.copy()
    df['TimeDiff'] = df['Date'].diff()
    # Consider a break only if the time difference is significantly more than 15 minutes
    df['PeriodStart'] = (df['TimeDiff'] > time_threshold) | (df['TimeDiff'].isna())
    df['PeriodID'] = df['PeriodStart'].cumsum()
    return df

def process_sheet(df, output_suffix, group_by_column=None):
    """Process a single sheet with optional grouping column."""
    # Check if the group_by_column exists
    if group_by_column and group_by_column not in df.columns:
        print(f"Warning: Column '{group_by_column}' not found in sheet. Available columns: {df.columns.tolist()}")
        return None
    
    # Identify sustained periods
    df_processed = identify_sustained_periods(df)
    
    # If there's a group_by_column, we need to split periods when that column changes
    if group_by_column:
        # Instead of using diff(), directly compare consecutive values
        df_processed['ValueChange'] = (df_processed[group_by_column] != 
                                     df_processed[group_by_column].shift()).fillna(False)
        df_processed['PeriodID'] = (df_processed['PeriodStart'] | 
                                  df_processed['ValueChange']).cumsum()
    
    # Calculate rate of change for each period
    results = []
    for period_id, group in df_processed.groupby('PeriodID'):
        # Only process groups with at least 2 points
        if len(group) >= 2:
            rate = calculate_rate_of_change(group)
            
            # Create a row for each period
            result_row = {
                'PeriodStart': group['Date'].iloc[0],
                'PeriodEnd': group['Date'].iloc[-1],
                'InitialValue': group['Value'].iloc[0],
                'FinalValue': group['Value'].iloc[-1],
                'NumberOfPoints': len(group),
                'RateOfChange': rate
            }
            
            if group_by_column:
                result_row[group_by_column] = group[group_by_column].iloc[0]
                
            results.append(result_row)
    
    return pd.DataFrame(results)

def process_excel_file(file_path):
    """Process all sheets in the Excel file."""
    # Read the Excel file
    excel_file = pd.ExcelFile(file_path)
    
    # Create a new Excel writer object
    with pd.ExcelWriter(f'processed_{file_path}', engine='openpyxl') as writer:
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\nProcessing sheet: {sheet_name}")
            
            # Read the original sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Convert Date column to datetime if it's not already
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Process with different conditions
            # 1. Basic rate of change
            basic_roc = process_sheet(df, '_basic')
            if basic_roc is not None:
                basic_roc.to_excel(writer, sheet_name=f'{sheet_name}_BasicROC', index=False)
            
            # 2. Rate of change with DemandLimit breaks
            demand_limit_roc = process_sheet(df, '_demand_limit', 'DemandLimit')
            if demand_limit_roc is not None:
                demand_limit_roc.to_excel(writer, sheet_name=f'{sheet_name}_DemandLimitROC', index=False)
            
            # 3. Rate of change with SyncedDemandLimit breaks
            synced_demand_roc = process_sheet(df, '_synced_demand', 'SyncedDemandLimit')
            if synced_demand_roc is not None:
                synced_demand_roc.to_excel(writer, sheet_name=f'{sheet_name}_SyncedDemandROC', index=False)

# Usage
if __name__ == "__main__":
    file_path = "sustained_decline_periods.xlsx"
    process_excel_file(file_path)
