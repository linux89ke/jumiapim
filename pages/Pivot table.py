import pandas as pd
from datetime import datetime
import os
import streamlit as st
import base64

# Define a function to process the input and generate output files
def process_files(input_file):
    # Define the output folder
    output_folder = f'PIM_output_{datetime.now().strftime("%Y-%m-%d_%H-%M")}'
    os.makedirs(output_folder, exist_ok=True)
    
    # Check for existing files and generate unique filenames for Pivot and PIM output
    base_output_file = 'Pivot_Date'
    pivot_output_file = f'{base_output_file}_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.csv'
    counter = 1
    while os.path.exists(os.path.join(output_folder, pivot_output_file)):
        pivot_output_file = f'{base_output_file}_{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{counter}.csv'
        counter += 1
    
    # Read the file into a DataFrame (handle both Excel and CSV files)
    if input_file.name.endswith('.xlsx') or input_file.name.endswith('.xls'):
        df = pd.read_excel(input_file)
    elif input_file.name.endswith('.csv'):
        try:
            df = pd.read_csv(input_file, encoding='utf-8')
        except UnicodeDecodeError:
            # If UTF-8 encoding fails, try 'latin-1' encoding
            df = pd.read_csv(input_file, encoding='latin-1')
    else:
        st.error("Unsupported file format. Please upload an Excel (.xls, .xlsx) or CSV file.")
        return False
    
 
    # Specify the column names
    seller_name_col = 'SELLER_NAME'
    category_col = 'CATEGORY'
    app_col = 'app'
    rej_col = 'rej'
    reason_col = 'reason'
    
    # Replace blank values in the 'reason' column with ''
    df[reason_col] = df[reason_col].fillna('')
    
    # Map values under 'reason' to the desired replacements
    reason_mapping = {
        'col': 'Wrong Color',
        'cat': 'Wrong Category',
        'var': 'Wrong Variation - Size Only',
        'bra': 'Wrong Brand',
        'Wrong Variation - means size only': 'Wrong Variation - means size only'
    }
    
    # Update the reason mapping as per your requirement
    reason_mapping.update({'col': 'Wrong Color'})
    
    # Create a pivot table without totals
    pivot_table = pd.pivot_table(df,
                                 values=[app_col, rej_col],
                                 index=[seller_name_col, category_col, reason_col],
                                 aggfunc='count',
                                 fill_value=0)
    
    # Reset index to create a DataFrame from the pivot table
    table_df = pivot_table.reset_index()
    
    # Melt the DataFrame to convert it to the desired format
    melted_df = pd.melt(table_df, id_vars=[seller_name_col, category_col, reason_col],
                        var_name='type', value_name='count')
    
    # Filter rows with non-empty 'count' values
    melted_df = melted_df[melted_df['count'] != 0]
    
    # Pivot the melted DataFrame to get separate columns for app and rej counts
    final_df = melted_df.pivot_table(index=['SELLER_NAME', 'CATEGORY', 'reason'],
                                     columns='type', values='count', fill_value='').reset_index()
    
    # Custom sorting function to keep the original case for 'Wrong Variation - means size only'
    def custom_sort(x):
        return ('' if x == '' else x.lower(), x)
    
    # Sort 'reason' column with blanks first and then alphabetically using the custom sorting function
    final_df['reason'] = final_df['reason'].apply(lambda x: '' if x == '' else x)
    final_df.sort_values(by='reason', inplace=True, key=lambda x: x.map(custom_sort) if x.dtype == 'O' else x)
    
    # Apply the updated reason mapping to the 'reason' column
    final_df['reason'] = final_df['reason'].map(reason_mapping)
    
    # Create a new datetime column
    final_df['Date_Column'] = datetime.now().strftime('%Y-%m-%d')
    
    # Add two columns before 'SELLER_NAME' with week number and formatted date
    final_df.insert(0, 'Week_Number', pd.to_datetime(final_df['Date_Column']).dt.isocalendar().week)
    final_df.insert(1, 'Formatted_Date', pd.to_datetime(final_df['Date_Column']).dt.strftime('%m/%d/%Y'))
    
    # Add two columns after 'rej' with 'KE' and 'Charles'
    final_df.insert(final_df.columns.get_loc('rej') + 1, 'new_col_1', 'KE')
    final_df.insert(final_df.columns.get_loc('rej') + 2, 'new_col_2', 'Charles')
    
    # Add a blank column after 'rej'
    final_df.insert(final_df.columns.get_loc('rej') + 3, 'Blank_Column', '')
    
    # Reorder the columns, placing 'reason' at the end
    final_df = final_df[['Week_Number', 'Formatted_Date', 'SELLER_NAME', 'CATEGORY', 'app', 'rej', 'Blank_Column', 'new_col_1', 'new_col_2', 'reason']]
    
    # Save the Pivot DataFrame to a CSV file
    pivot_output_path = os.path.join(output_folder, pivot_output_file)
    final_df.to_csv(pivot_output_path, index=False, encoding='utf-8-sig')  # Specify encoding as utf-8-sig to preserve non-English characters
    
    # Display success message with downloadable link for Pivot file
    st.markdown(get_download_link(pivot_output_path, "Download Pivot File"), unsafe_allow_html=True)
    
    # Display the data from the Pivot file
    st.subheader("Data from Pivot File")
    st.write(final_df)
    
    # Define the base output file name for PIM file
    pim_output_file = f'PIM_Date_Time_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.xlsx'
    counter = 1
    while os.path.exists(os.path.join(output_folder, pim_output_file)):
        pim_output_file = f'PIM_Date_Time_{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{counter}.xlsx'
        counter += 1
    
    # Create the PIM DataFrame
    pim_df = df[['PRODUCT_SET_SID', 'PARENTSKU']].copy()  # Use the correct column names from the input file
    pim_df.columns = ['ProductSetSid', 'ParentSKU']  # Rename columns for consistency
    
    # Apply mapping for 'reason' to generate 'Status' and 'Reason' columns
    pim_df['Status'] = df['reason'].apply(lambda x: 'Approved' if pd.isna(x) or x == '' else 'Rejected')
    pim_df['Reason'] = df['reason'].map(reason_mapping).fillna('Approved')  # Fill blank reasons with 'Approved'
    pim_df.loc[pim_df['
