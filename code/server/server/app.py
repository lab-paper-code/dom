# -- coding: utf-8 --
import os
os.environ["CUDA_VISIBLE_DEVICES"]=''

import logging
from flask import Flask, render_template, request, jsonify
from flask_restful import Api
from collections import OrderedDict
from flask import redirect, url_for
import json
import sys
import time
from flask import g
from operator import itemgetter
import werkzeug
from werkzeug.utils import secure_filename
import argparse
import datetime
import config
import tempfile
import zipfile
from apscheduler.schedulers.background import BackgroundScheduler
import psutil
from tensorflow.keras.applications import MobileNet
# from keras.applications.inception_v3 import InceptionV3
# from keras.applications.inception_v3 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from keras.applications import imagenet_utils
from tensorflow.python.keras.models import load_model
import tensorflow as tf
import numpy as np
import pandas as pd
import shlex
import requests
import subprocess
from subprocess import Popen, PIPE
import threading
from tqdm import tqdm
import keras
import keras.backend as K
import gc
import multiprocessing
import shlex
from collections import OrderedDict

UPLOAD_FOLDER = '/home/data/'
UPLOAD_LOG_FOLDER = UPLOAD_FOLDER + 'log/'
DOM_CONTAINER = config.IP['container_name']
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'zip', 'mpg'])

#configg = tf.compat.v1.ConfigProto()
#configg.gpu_options.allow_growth = True
#configg.gpu_options.per_process_gpu_memory_fraction = 0.0499
#session = tf.compat.v1.Session(config=configg)
model = MobileNet(alpha=0.25, weights="imagenet")
print('model loaded')
app = Flask(__name__)

nowdown_size = 0
isDownload = False
previous_filename = ''
current_filename = ''
filesize = 0

#scheduler
start_time = 0
my_scheduler = None

PI_QUANTITY = 20
IMAGE_PATH = '/home/data/'
container_name = ""
check_t = None
t = None

def _check_usage_of_cpu_and_memory():
    
    global check_t
    
    # pid = os.getpid()
    # py  = psutil.Process(pid)
    
    # cpu_usage   = os.popen("ps aux | grep " + str(pid) + " | grep -v grep | awk '{print $3}'").read()
    # cpu_usage   = cpu_usage.replace("\n","")
    
    # memory_usage  = round(py.memory_info()[0] /2.**30, 2)
    
    all_cpu_usage   = psutil.cpu_percent()    
    all_memory_usage  = psutil.virtual_memory().percent
    
    cpu_str = '[' + str(datetime.datetime.now())+ '] ' + str(all_cpu_usage)# + ' ' + str(cpu_usage)
    cpu_log(cpu_str)
    ram_str = '[' + str(datetime.datetime.now())+ '] '+  str(all_memory_usage)# + ' ' + str(memory_usage)
    #ram_log(ram_str)
    if check_t is not None:
        check_t.cancel()
        del check_t
    check_t = threading.Timer(1, _check_usage_of_cpu_and_memory)
    check_t.start()

def log_request(req: 'flask_request', time, size, status) -> None:
    container = req.form.get('domId')
    with open(UPLOAD_LOG_FOLDER + '_' + container + '_log.log', 'a+') as log:
        files = req.files
        for f in files:
            print('[' + str(time)+ '] ' + str(req.remote_addr) + ' received file ' + str(f) + ' ' + str(size) + 'MB, receive ' + status)
            print('[' + str(time)+ '] ' + str(req.remote_addr) + ' received file ' + str(f) + ' ' + str(size) + 'MB, receive ' + status ,file=log)
def cpu_log(string):
    global container_name
    with open(UPLOAD_LOG_FOLDER + "cpu_" + container_name + '_cpu.log', 'a+') as log:
        print(string)
        print(string,file=log)
def ram_log(string):
    global container_name
    with open("ram" + UPLOAD_LOG_FOLDER + "ram_" + container_name + '_ram.log', 'a+') as log:
        print(string)
        print(string,file=log)
@app.before_request
def before_request():
    #global t
    # print(request.remote_addr)
    #t = threading.Thread(target=_check_usage_of_cpu_and_memory)
    #t.start()
    g.start = time.time()
    

@app.after_request
def after_request(response):
    #global check_t
    #global t
    #check_t.cancel()
    #t.join()
    #del t
    diff = (time.time() - g.start) * 1000
    print('after_requese')
    if ((response.response) and
        (200 <= response.status_code < 300)):
        # print(request.content_length/1024.0/1024.0, 'MB')
        # print ("Exec time: %sms" % str(diff))
        # print('Throughput(MB/msec): ', request.content_length/1024.0/1024.0 / diff)
        response.set_data(response.get_data().replace(
            b'__EXECUTION_TIME__', bytes(str(diff), 'utf-8')))
    return response

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    try:
        
        global nowdown_size
        global isDownload
        global previous_filename
        global current_filename
        global start_time
        global filesize
        global container_name
        
        if container_name == "":
            container_name = request.form.get('domId')
        
        
            
        print("Uploade")
        if request.method == 'POST':
            files = request.files
            label = ''
            acc = ''
            isPredict = False
            for file in files:
                
                if files[file].filename == '':
                    resp = jsonify({'message' : 'No file selected for uploading'})
                    resp.status_code = 400
                    return resp
                #if files[file] and allowed_file(files[file].filename):
                current_filename = files[file].filename
                container = request.form.get('domId')  
                temp_name = 'tmp_' + container + '_' + current_filename
                print(UPLOAD_FOLDER + temp_name) 
                filesize = int(request.form.get('size'))                
                if not os.path.exists(UPLOAD_FOLDER + temp_name):
                    nowdown_size = 0
                    isDownload = True
                    log_request(request, request.form.get('time'), filesize / 1024.0 /1024.0, 'start')
                else:
                    nowdown_size = int(os.path.getsize(UPLOAD_FOLDER + temp_name))
                print('filesize: ', filesize)               
                downbuff_size = 60 * 1024.0 * 1024.0
                print("nowd=",nowdown_size)
                with open(UPLOAD_FOLDER + temp_name, 'ab') as f:   
                    print("with open")
                    print(filesize)
                    if nowdown_size < filesize:
                        print("if")
                        f.write(files[file].read())
                        f.flush()
                        
                        nowdown_size = int(os.path.getsize(UPLOAD_FOLDER + temp_name))
                        print(UPLOAD_FOLDER + temp_name)
                        print('nowdown_size: ', nowdown_size)
                        
                        if nowdown_size == filesize:
                            print("nowdonw == filesize")
                            filename = files[file].filename
                            if os.path.exists(UPLOAD_FOLDER + filename):
                                filename = container + '_' + filename
                            print("1")
                            os.replace(UPLOAD_FOLDER + temp_name, UPLOAD_FOLDER + filename)
                            print("2")
                            nowdown_size = 0
                            down_filesize = os.path.getsize(UPLOAD_FOLDER + filename)
                            print("3")
                            #압축 풀기
                            try:
                                if filename.endswith('.zip'):
                                    with zipfile.ZipFile(UPLOAD_FOLDER + filename, 'r') as zip_ref:
                                        print("extractall")
                                        zip_ref.extractall(UPLOAD_FOLDER)
                                        os.unlink(UPLOAD_FOLDER + filename)
                            except Exception as e:
                                print(e)
                            print("4")
                            
                            #영상 응용(압축 하기)
                            try:
                                if request.form.get('is_application') == 'T':
                                    file_name = UPLOAD_FOLDER + filename
                                print(file_name)
                                split = file_name.split(".")
                                output_file_name = split[0] + "_compressed."+split[1]
                                print(output_file_name)
                                command = "ffmpeg -i " + file_name +" "+output_file_name + " -y"
                                if request.form.get('is_gpu') == 'T':
                                    command = "ffmpeg -hwaccel cuda -i " + file_name +" "+output_file_name + " -y"
                                print(command)
                                command = shlex.split(command)
                                process = subprocess.Popen(command, stdout=subprocess.PIPE)
                                output, err = process.communicate()

                                print('finish compress file')
                            except Exception as e:
                                print(e)
                            #이미지 응용
                            if request.form.get('is_predict') == 'T':     
                                # test할 이미지
                                file = UPLOAD_FOLDER + filename
                                f = open("result.txt", "a+")
                                if file.endswith('.JPEG')or file.endswith('.JPG') or file.endswith('.PNG') :
                                    label, acc = predict_fu(file,f)
                                    isPredict = True
                        
                            
                            log_request(request, datetime.datetime.now(), down_filesize / 1024.0 / 1024.0, 'end')
                            isDownload = False
                            print('success upload')
                previous_filename = current_filename            
            if isPredict:
                resp = jsonify({'message' : label + ' ' + str(acc)})
                resp.status_code = 201
            else:
                resp = jsonify({'message' : 'File successfully uploaded'})
                resp.status_code = 201
            
            return resp
        else:
            resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
            resp.status_code = 400
            return resp
    except Exception as e:
        return {'error': str(e)}
        
#영상 응용
def is_not_blank(s):
    return bool(s and not s.isspace())


def isIntegrityVideos(file_name):
    # command
    command = "ffmpeg -v error -sseof -1 -i " + file_name + " -f null -"
    print(command)

    command = shlex.split(command)
    out = subprocess.run(command, capture_output=True, encoding="utf-8")
    print(out.stderr)

    if is_not_blank(out.stderr):
        return False
    return True






        
################## 이미지 인식 ###############################
def requestImageClassification1AllClients(ip, divide_cnt):
    try:
        print("Uploading {}".format(ip))
        parmas = {
            'img_cnt': divide_cnt
        }
        res = requests.post('http://59.27.74.76:' + ip + '/imagenet1_each', data=parmas)
    except Exception as e:
        print(str(e))
        
@app.route('/imagenet1', methods=['GET', 'POST'])
def requestImageClassification1():
    try:
        values = config.IP['clients']
        img_cnt = int(request.form.get('img_cnt'))

        divide_cnt = img_cnt / PI_QUANTITY
        divide_cnt = int(divide_cnt)

        start = time.time()

        threads = [threading.Thread(target=requestImageClassification1AllClients, args=(ip, divide_cnt)) for ip in values]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print("Elapsed Time : %s" % (time.time() - start))
        return 'imagenet1 succeed'
    except Exception as e:
        return str(e)

def getFilesByCnt(img_cnt):
    files = os.listdir(IMAGE_PATH)
    os.chdir(IMAGE_PATH)

    fileList = []


    for i in range(0, img_cnt):
        file_name = files[i]
        fileList.append(file_name)

    print("SEND FILE LIST LENGTH : {}".format(len(fileList)))

    return fileList
    
def getFiles(limit_size):
    files = os.listdir(IMAGE_PATH)
    os.chdir(IMAGE_PATH)
    cnt = 0
    fileList = []
    file_sizes = 0

    while True:
        file_name = files[cnt]
        next_file = files[cnt + 1]
        filesize = os.path.getsize(file_name) / (1024.0 * 1024.0 * 1024.0)
        next_file_size = os.path.getsize(next_file) / (1024.0 * 1024.0 * 1024.0)
        file_sizes += filesize

        fileList.append(file_name)


        if file_sizes + next_file_size > limit_size:
            print("total file size : ", file_sizes)
            break;
        cnt += 1
    print("SEND FILE LIST LENGTH : {}".format(len(fileList)))

    return fileList

def predict_fu(path, file):
    global model
    
    inputShape = (224, 224)
    img = load_img(path, target_size=inputShape)
    image = img_to_array(img)
    image = np.expand_dims(image, axis=0)
    
    
    #image = preprocess_input(image)
    print("before predict")
    tensor = tf.convert_to_tensor(image)
    predicts = model.predict_on_batch(tensor)
    #predicts = model.predict(image)
    #predicts = model.predict_on_batch(image)
    print("after predict")
    
    P = imagenet_utils.decode_predictions(predicts)

    for (i, (imagenetID, label, prob)) in enumerate(P[0]):
        file.write("{}: {:.2f}% \n".format(label, prob * 100))
        #print("{}: {:.2f}%".format(label, prob * 100))
        return label, prob * 100
        
@app.route('/imagenet1_each', methods=['GET', 'POST'])
def imageClassification1():
    try:
        print("=====imagenet1_each=======")
        
        
        configg = tf.compat.v1.ConfigProto()
        configg.gpu_options.allow_growth = True
        configg.gpu_options.per_process_gpu_memory_fraction = 0.049
        session = tf.compat.v1.Session(config=configg)
        
        from tensorflow.keras.applications import MobileNet
        os.chdir('/DOM/server/')
        #model = MobileNet(alpha=0.25, weights="imagenet")
        #model = load_model('imagenet.h5')
        print('model loaded')
                
        img_cnt = int(request.form.get('img_cnt'))
        print("Image Cnt : {}".format(img_cnt))

        if os.path.isfile("result.txt"):
            os.unlink("result.txt")

        f = open("result.txt", "w")


        fileList = getFilesByCnt(int(img_cnt))

        start = time.time()
        for file in tqdm(fileList):
            if file.endswith('.JPEG') or file.endswith('.JPG') or file.endswith('.PNG'):
                predict_fu(file, f)
        f.close()

        print("Elapsed Time : %s" % (time.time() - start))
        print("Run successfully")
        return "=========ImageNet Classification2 server success"
    except Exception as e:
        print(e)
        return str(e)
       

################## git 관련 ###############################
@app.route('/update', methods=['GET', 'POST'])
def requestUpdateCode():
    try:
        values = config.IP['clients']
        print(values)
        for port in values:
            print("git pull {}".format(port))
            res = requests.post('http://155.230.36.27:' + port + '/update_git')
        return 'update succeed\n'
    except Exception as e:
        return str(e)


@app.route('/update_git', methods=['GET', 'POST'])
def updateCodeFromGit():
    try:
        command = 'no command'
        print("============")
        os.chdir('/DOM')
        command = "git pull"
        print(command)

        print('Started executing command')
        command = shlex.split(command)
        print('asdf')
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        print("Run successfully")
        output, err = process.communicate()
        return output
    except Exception as e:
        return str(e)

        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-p', '--port', help='Port_number', required=True)
    args = vars(parser.parse_args())
    app.run(host='0.0.0.0', use_reloader=True, debug = True, port=args['port'], threaded=False, processes=1)
    #app.run(host='0.0.0.0', debug = True, port=args['port'], threaded=False, processes=1)

