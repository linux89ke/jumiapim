import pandas as pd
import os
from datetime import datetime
import streamlit as st
import re

def load_colors_from_txt(file_path):
    with open(file_path, 'r') as file:
        colors = [line.strip() for line in file.readlines()]
    return colors

def check_for_color(cell_text, common_colors):
    if pd.isna(cell_text):
        return "No"
    
    for color in common_colors:
        if re.search(re.escape(color), cell_text, flags=re.IGNORECASE):
            return "Yes"

    return "No"

def main():
    st.title("Upload Excel Files and Process")
    common_colors_file = "common_colors.txt"
    common_colors = load_colors_from_txt(common_colors_file)

    uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx'])
    category_file = st.file_uploader("Upload category FAS.xlsx", type=['xlsx'])

    if uploaded_file and category_file:
        try:
            # Read the uploaded file
            df = pd.read_excel(uploaded_file, engine='openpyxl')

            # Read the category file
            category_fas_df = pd.read_excel(category_file, engine='openpyxl')

            # Check if 'BRAND' column exists in the uploaded file
            if 'BRAND' in df.columns:
                # Check if any value in 'BRAND' column is 'Generic'
                if (df['BRAND'] == 'Generic').any():
                    # Check if 'ID' column exists in the category file
                    if 'ID' in category_fas_df.columns:
                        # Create a new column 'check_Brand' in the output file
                        df['check_Brand'] = df.apply(lambda row:
                            'No' if row['BRAND'] == 'Generic' and row['CATEGORY_CODE'] in category_fas_df['ID'].values else 'Yes',
                            axis=1
                        )
                    else:
                        st.error("Error: 'ID' column not found in the category file.")
                else:
                    st.error("Error: No value 'Generic' found in 'BRAND' column of the uploaded file.")
            else:
                st.error("Error: 'BRAND' column not found in the uploaded file.")

            # Now, let's check for colors
            if 'COLOR' in df.columns:
                df['Check_Color'] = df['COLOR'].apply(lambda x: check_for_color(str(x), common_colors))

            # Save the output file as Excel
            current_date = datetime.now().strftime('%Y-%m-%d')
            output_file_name = f"Output_PIM_{current_date}.xlsx"
            output_file_path = os.path.join(os.getcwd(), output_file_name)
            df.to_excel(output_file_path, index=False)

            # Display success message and provide download link
            st.success(f"Output file '{output_file_name}' created.")
            st.download_button(
                label="Download Output File",
                data=open(output_file_path, 'rb').read(),
                file_name=output_file_name,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
