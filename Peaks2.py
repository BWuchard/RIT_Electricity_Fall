import pandas as pd
from datetime import datetime, timedelta
import os

def process_excel_file(input_file, output_file):
    # List of months to process
    months = ['April', 'May', 'June', 'July', 'August', 'September']
    
    # Create Excel writer object for output file
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        for month in months:
            try:
                # Read the sheet for current month
                df = pd.read_excel(input_file, sheet_name=month)
                
                # Create a list to store all filtered data
                all_filtered_rows = []
                
                # Get unique circuits
                unique_circuits = df['Circuit'].unique()
                
                # Process each circuit separately
                for circuit in unique_circuits:
                    # Filter data for this circuit
                    circuit_data = df[df['Circuit'] == circuit].copy()
                    
                    # Get unique days
                    unique_days = circuit_data['Day'].unique()
                    
                    # For each day, find the peak and surrounding hours
                    for day in unique_days:
                        # Get data for this day and circuit
                        day_data = circuit_data[circuit_data['Day'] == day]
                        
                        # Find the row with maximum Value
                        peak_row = day_data.loc[day_data['Value'].idxmax()]
                        peak_date = peak_row['Date']
                        
                        # Find rows within ±2 hours of the peak time for this circuit and day
                        matching_rows = df[
                            (df['Circuit'] == circuit) &
                            (df['Day'] == day) &
                            (df['Date'] >= peak_date - timedelta(hours=2)) &
                            (df['Date'] <= peak_date + timedelta(hours=2))
                        ]
                        
                        all_filtered_rows.append(matching_rows)
                
                # Combine all filtered rows
                if all_filtered_rows:
                    filtered_df = pd.concat(all_filtered_rows)
                    
                    # Sort by Circuit, Day, and Date
                    filtered_df = filtered_df.sort_values(['Circuit', 'Day', 'Date'])
                    
                    # Remove any duplicates while keeping all columns
                    filtered_df = filtered_df.drop_duplicates()
                    
                    # Write to new Excel file, maintaining all original columns
                    filtered_df.to_excel(writer, sheet_name=month, index=False)
                else:
                    print(f"No data found for {month}")
                
            except Exception as e:
                print(f"Error processing {month} sheet: {str(e)}")
                raise  # This will show the full error for debugging

    print(f"Processing complete. Output saved to {output_file}")

# Example usage
input_file = "ATestByMonth.xlsx"
output_file = "ATestByMonth_Processed.xlsx"

process_excel_file(input_file, output_file)
