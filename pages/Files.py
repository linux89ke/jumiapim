import streamlit as st

def display_files():
    st.title("Uploaded and Downloaded Files")
    
    # Display uploaded files
    uploaded_files = st.session_state.get("uploaded_files", [])
    if uploaded_files:
        st.subheader("Uploaded Files:")
        for file in uploaded_files:
            st.write(file)
    
    # Display downloaded files
    downloaded_files = st.session_state.get("downloaded_files", [])
    if downloaded_files:
        st.subheader("Downloaded Files:")
        for file in downloaded_files:
            st.write(file)

def main():
    st.set_page_config(page_title="File Explorer", layout="wide")
    display_files()

if __name__ == "__main__":
    main()
