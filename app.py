import threading
from flask import Flask
from flask_cors import CORS
from database.config import SECRET_KEY
from routes.auth import auth_bp
from messaging.consumer import consume_events, login_events_callback

app = Flask(__name__)

# Настройка CORS: Разрешить все источники (для разработки)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config['SECRET_KEY'] = SECRET_KEY

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    threading.Thread(target=lambda: consume_events('login_events', login_events_callback), daemon=True).start()
    app.run(host='0.0.0.0', port=3000)
