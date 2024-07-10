import base64
import requests
import streamlit as st
from io import BytesIO
import time
from dotenv import load_dotenv
 
 
 
def main():
    st.set_page_config(page_title="Interactive PDF Q&A", page_icon="📄", layout="wide")
    st.title("Interactive PDF Q&A 📄")
    st.markdown("Welcome to the Interactive PDF Q&A app. Upload your PDF and ask questions to get insights!")
 
    # Upload PDF section
    st.sidebar.header("Upload your PDF")
    uploaded_file = st.sidebar.file_uploader('', type='pdf')
 
    if uploaded_file is not None:
        with st.spinner('Processing PDF...'):
            
            pdf_bytes = uploaded_file.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode()
 
            
            response = requests.post('http://localhost:5001/upload', json={'pdf_base64': pdf_base64})
 
            
            if response.status_code == 200:
                st.sidebar.success("PDF uploaded successfully!")
            else:
                st.sidebar.error("Failed to upload the PDF.")
 
    st.markdown("---")
 
   
    st.header("Ask a Question")
    query = st.text_input("Type your question about the uploaded PDF:")
 
    if query:
        with st.spinner('Getting your answer...'):
            
            url = "http://localhost:5001/answer"
            data = {'query': query}
            response = requests.post(url, data=data)
 
            if response.status_code == 200:
                st.write(response.json()['response'])
            else:
                st.error("Error getting the answer.")
 
  
    st.markdown("---")
   
if __name__ == "__main__":
    time.sleep(2)
    main()