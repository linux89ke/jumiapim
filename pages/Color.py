import pandas as pd
import re
import os
from datetime import datetime
import streamlit as st

def check_for_color(cell_text):
    common_colors = ["navy", "black", "yellow", "red", "blue", "green", "orange", "purple", 
                     "pink", "brown", "white", "gray", "grey", "khaki", "coffee", "gold", 
                     "silver", "beige", "burgundy", "multi", "turquoise", "violet", "indigo", 
                     "maroon", "olive", "lime", "teal", "aqua", "apricot", "wine", "mocha", 
                     "multicolor", "multi", "plaid", "rose", "lily", "violet", "daisy", 
                     "tulip", "sunflower", "iris", "orchid", "lavender", "marigold", 
                     "poppy", "jasmine", "peony", "camellia", "hyacinth", "magnolia", 
                     "daffodil", "chrysanthemum", "geranium", "dahlia", "transparent", 
                     "clear", "rainbow", "caramel", "milk", "bronze", "argent", "chocolate", 
                     "stawberry", "colorful", "peach", "magenta", "carbon", "Camouflage", 
                     "camo", "stripes", "polka dot", "floral", "geometric", "animal print", 
                     "tie-dye", "chevron", "camouflage", "herringbone", "paisley", 
                     "checkered", "gingham", "tartan", "abstract", "batik", "ikat", "ombre", 
                     "checked", "cyan", "ivory", "periwinkle", "chartreuse", "fandango", 
                     "wisteria", "mauve", "vermilion", "viridian", "tangerine", "cerulean", 
                     "heliotrope", "gamboge", "xanadu", "byzantium", "caput mortuum", 
                     "persimmon", "coquelicot", "falu red", "zaffre", "wood", "mahogany", 
                     "Auburn", "turmeric", "lemon", "skin", "nude", "walnut", "copper", 
                     "chrome", "watermelon", "leopard", "lemon", "print", "tan", "Amber", 
                     "Smoky", "Smoked", "coral", "tomato", "rusty", "rust", "steel", 
                     "cream", "Champagne", "matte", "blossom", "graffiti", "sapphire",
                     "velvet", "translucent", "metal", "metallic", "iridium", "chroma", "coral",
                     "scarlet", "crimson", "ruby", "cherry", "burgundy", "vermilion", "maroon", 
                     "carmine", "raspberry", "blue", "navy", "azure", "cobalt", "cerulean", 
                     "indigo", "teal", "sky blue", "sapphire", "cyan", "green", "emerald", "lime", 
                     "olive", "jade", "mint", "sage", "forest green", "hunter green", "kelly green", 
                     "yellow", "lemon", "gold", "canary", "maize", "amber", "buttercup", "mustard", 
                     "dandelion", "honey", "orange", "tangerine", "apricot", "peach", "iron", 
                     "pumpkin", "terracotta", "rust", "salmon", "purple", "lavender", "lilac", "violet", 
                     "mauve", "plum", "grape", "amethyst", "orchid", "magenta", "pink", "blush", "rose", 
                     "bubblegum", "salmon pink", "coral pink", "fuchsia", "neon", "carnation", "peony", 
                     "brown", "chocolate", "tan", "beige", "auburn", "chestnut", "coffee", "mahogany", "sienna", 
                     "umber", "gray", "charcoal", "slate", "silver", "ash", "steel", "dove", "graphite", "pearl", 
                     "smoke", "white", "ivory", "cream", "snow", "pearl white", "off-white", "vanilla", "alabaster", 
                     "bone", "chiffon", "black", "jet", "onyx", "ebony", "charcoal black", "coal", "midnight", 
                     "obsidian", "raven", "soot"]

   
    if pd.isna(cell_text):
        return "No"
    
    for color in common_colors:
        if re.search(re.escape(color), cell_text, flags=re.IGNORECASE):
            return "Yes"

    return "No"

def main():
    st.title("Upload Excel Files and Process")

    uploaded_files = st.file_uploader("Upload your Excel files", type=['xlsx'], accept_multiple_files=True)
    category_file = st.file_uploader("Upload category FAS.xlsx", type=['xlsx'])

    if uploaded_files and category_file:
        try:
            category_fas_df = pd.read_excel(category_file, engine='openpyxl')
            combined_df = pd.DataFrame()

            for uploaded_file in uploaded_files:
                try:
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                    if 'COLOR' in df.columns:
                        df['Check'] = df['COLOR'].apply(lambda x: check_for_color(str(x)))
                    
                    if 'URL_COLUMN_NAME' in df.columns:
                        df.drop(columns=['URL_COLUMN_NAME'], inplace=True)

                    df['Check_brand'] = df['ID'].apply(lambda id_value: "No" if category_fas_df['CATEGORY_CODE'].isin([id_value]).any() and category_fas_df.loc[category_fas_df['CATEGORY_CODE'] == id_value, 'BRAND'].iloc[0] == "Generic" else ("Yes" if category_fas_df['CATEGORY_CODE'].isin([id_value]).any() else "Not Found"))

                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                except Exception as e:
                    st.error(f"Error processing file '{uploaded_file.name}': {e}")

            current_date = datetime.now().strftime('%Y-%m-%d')
            output_file_name = f"Output_PIM_{current_date}.csv"
            output_file_path = os.path.join(os.getcwd(), output_file_name)

            while os.path.exists(output_file_path):
                output_file_name = output_file_name[:-4] + chr(ord(output_file_name[-5]) + 1) + ".csv"
                output_file_path = os.path.join(os.getcwd(), output_file_name)

            combined_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

            st.success(f"Output file '{output_file_name}' created.")

            st.download_button(
                label="Download Output File",
                data=open(output_file_path, 'rb').read(),
                file_name=output_file_name,
                mime='text/csv'
            )
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
