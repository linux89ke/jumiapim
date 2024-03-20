import pandas as pd
import streamlit as st
from streamlit.components.v1 import components
from datetime import datetime
import os

def load_colors_from_txt(file_path):
    with open(file_path, 'r') as file:
        colors = {line.strip().lower() for line in file.readlines()}
    return colors

def check_for_color(cell_text, common_colors):
    if pd.isna(cell_text):
        return "No"

    cell_text_lower = cell_text.lower()
    for color in common_colors:
        if color in cell_text_lower:
            return "Yes"
    return "No"

def main():
    st.title("Process Excel Files")

    # Load common colors from text file
    common_colors_file = "common_colors.txt"
    common_colors = load_colors_from_txt(common_colors_file)

    # Read category file
    category_file = "category FAS.xlsx"
    category_fas_df = pd.read_excel(category_file, engine='openpyxl')

    uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx'])

    if uploaded_file:
        try:
            # Read the uploaded file
            df = pd.read_excel(uploaded_file, engine='openpyxl')

            # Check if 'BRAND' column exists in the uploaded file
            if 'BRAND' in df.columns:
                # Check if any value in 'BRAND' column is 'Generic'
                if df['BRAND'].str.lower().eq('generic').any():
                    # Create a new column 'check_Brand' in the output file
                    df['check_Brand'] = df.apply(lambda row:
                        'No' if row['BRAND'].lower() == 'generic' and row['CATEGORY_CODE'] in category_fas_df['ID'].values else 'Yes',
                        axis=1
                    )
                else:
                    st.error("Error: No value 'Generic' found in 'BRAND' column of the uploaded file.")
            else:
                st.error("Error: 'BRAND' column not found in the uploaded file.")

            # Now, let's check for colors
            if 'COLOR' in df.columns:
                progress_bar = st.progress(0)
                total_rows = df.shape[0]
                processed_rows = 0
                for index, row in df.iterrows():
                    df.at[index, 'Check_Color'] = check_for_color(str(row['COLOR']), common_colors)
                    processed_rows += 1
                    progress_bar.progress(processed_rows / total_rows)

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

            # Next button for navigation to Pivot_table.py
            if st.button("Next"):
                components.iframe("http://localhost:8501/Pivot_table.py", width=1200, height=800)

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
