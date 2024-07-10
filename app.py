import subprocess
import time
import os
from dotenv import load_dotenv
import sys
from chatprocess import app
 
 
os.environ['FLASK_APP'] = 'chatprocess.py'
 
def run_flask_app():
    # Run Flask backend
    subprocess.Popen([sys.executable, '-m', 'flask', 'run', '--no-debugger', '--no-reload', '--port', '5001'])
 
 
def run_streamlit_app():
    # Run Streamlit frontend
    subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'frontend.py', '--server.port', '8501', '--', '--port', '8501'])
 
if __name__ == '__main__':
    # Load environment variables
    load_dotenv()
 
    run_flask_app()
    # Give some time for the Flask app to start
    time.sleep(2)
 
    # Run Streamlit frontend
    run_streamlit_app()