import requests
import config
import subprocess
import shlex
from flask import Blueprint

updateDevice_api = Blueprint('updateDevice_api', __name__)
@updateDevice_api.route('/update', methods=['GET', 'POST'])
def requestUpdateCode():
    try:
        values = config.IP['clients']

        for ip in values:
            print("git pull {}".format(ip))
            res = requests.post('http://' + ip + ':60000/update_git')
        return 'update succeed'
    except Exception as e:
        return str(e)


@updateDevice_api.route('/update_git', methods=['GET', 'POST'])
def updateCodeFromGit():
    try:
        command = 'no command'
        print("============")
        command = "git pull origin master"
        print(command)

        print('Started executing command')
        command = shlex.split(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        print("Run successfully")
        output, err = process.communicate()
        return output
    except Exception as e:
        return str(e)

# @app.route('/run', methods=['POST', 'GET'])
# def execute():
#     command = 'no command'
#     print("============")
#     print(request.form.get("command"))
#     # command = (request.form.get("command")).decode("utf-8")
#     command = request.form.get("command")
#     print(command)
#     if request.method == 'POST':
#         print('Started executing command')
#         command = shlex.split(command)
#         process = subprocess.Popen(command, stdout=subprocess.PIPE)
#         print("Run successfully")
#         output, err = process.communicate()
#         return output
#     return "not executed"
