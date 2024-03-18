import streamlit as st

# Create a session state to store uploaded files
def init_session_state():
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

# Function to handle file upload
def upload_file():
    uploaded_file = st.file_uploader("Upload Files", type=["csv", "txt"])
    if uploaded_file is not None:
        st.session_state.uploaded_files.append(uploaded_file)

# Function to display list of uploaded files
def display_uploaded_files():
    st.write("### Uploaded Files:")
    if len(st.session_state.uploaded_files) == 0:
        st.write("No files uploaded yet.")
    else:
        for file in st.session_state.uploaded_files:
            st.write(f"- {file.name}")

def main():
    init_session_state()
    st.title("Uploaded Files List")
    upload_file()
    display_uploaded_files()

if __name__ == "__main__":
    main()
