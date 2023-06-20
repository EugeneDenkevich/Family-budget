from dotenv import load_dotenv
import os


load_dotenv()


DB_PASS = os.getenv('DB_PASS')
DB_USER = os.getenv('DB_USER')
TOKEN = os.getenv('TOKEN')
