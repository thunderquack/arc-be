import json

from langdetect import detect
import pycountry
from database.base import Page
from database.config import DATABASE_URL
from database.setup import setup_database
from messaging.utils import get_rabbitmq_connection, declare_queues, TESSERACT_URL
import requests
import io

Session = setup_database(DATABASE_URL)
session = Session()


def consume_events(queue_name, callback):
    connection, channel = get_rabbitmq_connection()
    declare_queues(channel)
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(f'Waiting for {queue_name} events. To exit press CTRL+C')
    channel.start_consuming()


def login_events_callback(ch, method, properties, body):
    print(f"Received login event: {body}")


def page_update_events_callback(ch, method, properties, body):
    page_id = body.decode('utf-8')
    page = session.query(Page).filter_by(id=page_id).first()

    if page and page.image_data:
        try:
            file_like_object = io.BytesIO(page.image_data)
            file_like_object.name = 'image.png'
            options = {}
            options_json = json.dumps(options)
            files = {
                'options': (None, options_json),
                'file': ('image.png', file_like_object, 'image/png')
            }
            response = requests.post(TESSERACT_URL, files=files)
            if response.ok:
                recognized = json.loads(response.text)
                recognized_text = str(
                    recognized['data']['stdout']).replace('\\\\n', '\n')
                page.language = detect(recognized_text)

                # Second run: with detected language
                lang = pycountry.languages.get(iso639_1_code=page.language)
                options = {"languages": [lang]}
                options_json = json.dumps(options)
                files = {
                    'options': (None, options_json),
                    'file': ('image.png', file_like_object, 'image/png')
                }
                response = requests.post(TESSERACT_URL, files=files)
                recognized = json.loads(response.text)
                recognized_text = str(
                    recognized['data']['stdout']).replace('\\\\n', '\n')
                page.recognized_text = recognized_text

            session.commit()
            print(f"Thumbnail for page {page_id} updated successfully.")
        except Exception as e:
            print(f"Failed to update thumbnail for page {page_id}: {str(e)}")
            session.rollback()
    else:
        print(f"Page {page_id} not found or has no image data.")
