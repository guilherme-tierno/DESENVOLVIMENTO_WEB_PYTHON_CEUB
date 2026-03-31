from dotenv import load_dotenv
load_dotenv()

from src.helpdesk import create_app

app = create_app()

if __name__ == "__main__":
    # Forçamos a porta 5005 para evitar o conflito comum do Windows
    app.run(debug=True, port=5005)