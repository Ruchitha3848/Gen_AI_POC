from io import BytesIO
 
import base64
import tempfile
from flask import Flask, request, jsonify
from openai import AzureOpenAI
import os
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from langchain.vectorstores.chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
 
 
app = Flask(__name__)
 
load_dotenv()
print("""""""""""""""""""""""""")
AZURE_OPENAI_ENDPOINT = os.environ['AZURE_OPENAI_ENDPOINT']
AZURE_OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]
AZURE_OPENAI_EMBED_DEPLOYEMENT = os.environ["AZURE_OPENAI_EMBED_DEPLOYEMENT"]
EMBEDDING_MODEL_NAME = os.environ['EMBEDDING_MODEL_NAME']
CHAT_COMPLETIONS_DEPLOYMENT_NAME = os.environ['CHAT_COMPLETIONS_DEPLOYMENT_NAME']
 
if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set")
 
persist_directory = 'db'
 
embeddings = AzureOpenAIEmbeddings(
    api_key=AZURE_OPENAI_API_KEY,
    model=EMBEDDING_MODEL_NAME,
    azure_deployment=AZURE_OPENAI_EMBED_DEPLOYEMENT
)
 
@app.route('/upload', methods=['POST'])
def upload_file():
    
   
    data = request.get_json()
 
    pdf_base64 = data.get('pdf_base64')
 
    
    pdfbytes = base64.b64decode(pdf_base64)
   
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdfbytes)
        tempfile_path = temp_file.name
           
    if tempfile_path:
        loader = PyPDFLoader(tempfile_path)
        documents = loader.load_and_split()
        os.remove(tempfile_path)
 
        
        text_splitter = CharacterTextSplitter(
            separator='\n',
            chunk_size=4000,
            chunk_overlap=128
        )
        texts = text_splitter.split_documents(documents)
 
 
       
        try:
            vectordb = Chroma.from_documents(
                documents=texts,
                embedding=embeddings,
                persist_directory=persist_directory
            )
            vectordb.persist()
        except Exception as e:
            print(f"An error occurred: {e}")
       
   
        return jsonify({'message': 'File uploaded and processed successfully.'})
    else:
        return jsonify({'error': 'No file uploaded.'}), 400
 
@app.route('/answer', methods=['POST'])
def answer_question():
    load_dotenv()
    client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2023-03-15-preview",
    azure_deployment=os.getenv('CHAT_COMPLETIONS_DEPLOYMENT_NAME')
)
 
    vectordb = Chroma(persist_directory=persist_directory,
                    embedding_function=embeddings)
   
 
    query = request.form['query']
    response = answer_question(query, vectordb , client)
    return jsonify({'response': response})
 
def answer_question(query, vectordb ,client):
    results = vectordb.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in results])
 
    msg = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"}
    ]
 
  
    response = client.chat.completions.create(
        model=CHAT_COMPLETIONS_DEPLOYMENT_NAME,
        messages=msg,
        max_tokens=500,
        temperature=0.7
    )
 
   
    return response.choices[0].message.content
 
if __name__ == '__main__':
        app.run(port=5001)