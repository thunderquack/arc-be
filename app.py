import threading
from flask import Flask
from flask_cors import CORS
import ptvsd
from database.config import SECRET_KEY
from routes.auth import auth_bp
from routes.document import document_bp
from messaging.consumer import consume_events, login_events_callback

app = Flask(__name__)

ptvsd.enable_attach(address=('0.0.0.0', 5678))
print("ptvsd enabled and waiting for attach...")

# Настройка CORS: Разрешить все источники (для разработки)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config['SECRET_KEY'] = SECRET_KEY

# Увеличение размера загружаемого файла до 16 мегабайт
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.register_blueprint(auth_bp)
app.register_blueprint(document_bp)

if __name__ == '__main__':
    threading.Thread(target=lambda: consume_events('login_events', login_events_callback), daemon=True).start()
    app.run(host='0.0.0.0', port=3000)
