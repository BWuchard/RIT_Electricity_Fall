import pandas as pd
import numpy as np

def process_transitions(file_path):
    # Read sheets
    demand_df = pd.read_excel(file_path, sheet_name='Demand Transitions')
    synced_df = pd.read_excel(file_path, sheet_name='Synced Transitions')
    
    def calculate_rates(df):
        # Initialize lists for results
        rates = []
        circuits = []
        months = []
        contexts = []
        
        # Process in groups of 4 rows
        for i in range(0, len(df), 4):
            group = df.iloc[i:i+4]
            if len(group) < 4:  # Skip incomplete groups
                continue
                
            # Calculate rates for the sequence CB->TB->TA->CA
            cb_to_tb = (group.iloc[1]['Value'] - group.iloc[0]['Value']) / 15
            tb_to_ta = (group.iloc[2]['Value'] - group.iloc[1]['Value']) / 15
            ta_to_ca = (group.iloc[3]['Value'] - group.iloc[2]['Value']) / 15
            
            # Append rates and metadata
            rates.extend([cb_to_tb, tb_to_ta, ta_to_ca])
            circuits.extend([group.iloc[0]['Circuit']] * 3)
            months.extend([group.iloc[0]['Month']] * 3)
            
            # Create context labels
            contexts.extend([
                f"({group.iloc[0]['TransitionType']})CB-TB",
                f"({group.iloc[1]['TransitionType']})TB-TA",
                f"({group.iloc[2]['TransitionType']})TA-CA"
            ])
        
        # Create result dataframe
        result_df = pd.DataFrame({
            'Circuit': circuits,
            'Month': months,
            'Combined_Context': contexts,
            'Rate_of_Change': rates
        })
        
        return result_df
    
    # Process both sheets
    demand_rates = calculate_rates(demand_df)
    synced_rates = calculate_rates(synced_df)
    
    # Write to new Excel file
    with pd.ExcelWriter('TransitionRates.xlsx') as writer:
        demand_rates.to_excel(writer, sheet_name='Demand_Rates', index=False)
        synced_rates.to_excel(writer, sheet_name='Synced_Rates', index=False)
    
    return demand_rates, synced_rates

# Usage
rates_demand, rates_synced = process_transitions('DemandTransitions.xlsx')
