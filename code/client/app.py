from flask import Flask
import socket
import logging.config
import datetime

from update_device import updateDevice_api
from client.client_app_image import appImage_api
from client.client_combine import combinedData_api
from client.client_image import image_api
from client.client_mqtt import mqtt_api
from client.client_socket import socket_api
from client.client_text import text_api
from client.client_video import video_api


from silence_tensorflow import silence_tensorflow
silence_tensorflow()


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})
logging.basicConfig(format='%(message)s', filename="logs/client_REST.log", level=logging.INFO, filemode='w')

app = Flask(__name__)
app.register_blueprint(updateDevice_api)
app.register_blueprint(appImage_api)
app.register_blueprint(combinedData_api)
app.register_blueprint(image_api)
app.register_blueprint(mqtt_api)
app.register_blueprint(socket_api)
app.register_blueprint(text_api)
app.register_blueprint(video_api)
# app.register_blueprint(account_api, url_prefix='/accounts')


if __name__ == '__main__':
    my_ip = socket.gethostbyname(socket.getfqdn())
    print(my_ip)
    app.run(host=my_ip, port=60000, debug=True)


