
from flask import request, Blueprint
import threading
import subprocess
import shlex


import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import client_request as cr
import config
import utils


socket_api = Blueprint('socket_api', __name__)

@socket_api.route('/socket/hello', methods=['GET', 'POST'])
def appImageHello():
    print("Socket Hello")
    return "Hello"


@socket_api.route('/upload_all_socket', methods=['GET', 'POST'])
def SocketUploadAll():
    try:
        values = config.IP['clients']
        limit_size = request.form.get('limit')
        protocol = request.form.get('protocol')
        isZip = request.form.get('isZip')

        print("limit size : ", limit_size)
        print("protocol : ", protocol)
        print("isZip : ", isZip)

        threads_socket = [threading.Thread(target=cr.requestToAllClients_socket, args=(ip, limit_size, protocol, isZip))
                          for ip
                          in
                          values]

        for thread in threads_socket:
            thread.start()
        for thread in threads_socket:
            thread.join()
        return 'Success SocketUploadAll'

    except Exception as e:
        utils.log(str(e))
        return str(e)


@socket_api.route('/upload_socket', methods=['GET', 'POST'])
def SocketUpload():
    try:
        socket_host = config.IP['socket_host']
        socker_port = config.IP['socket_post']
        limit = request.form.get("limit")
        protocol = request.form.get('protocol')
        # isZip = reqeust.form.get('isZip')

        command = 'no command'
        print("Socket Protocol : {}".format(protocol))

        command = "python3 socket_client.py -i {} -p {} -l {} -t {}".format(socket_host, socker_port, limit, protocol)
        # command = "python3 socket_client.py -i {} -p {} -l {} -t {} -z {}".format(socket_host, socker_port, limit, protocol,
        # isZip)
        print(command)

        print('Started executing command')
        command = shlex.split(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        print("Run successfully")
        output, err = process.communicate()

        return output
    except Exception as e:
        return str(e)
