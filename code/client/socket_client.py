import socket
import argparse
import os
import sys
import tempfile
import logging
from datetime import datetime
import config
import zipfile
import time

logging.basicConfig(filename="logs/client_SOCKET.log", level=logging.INFO)

CHUNK_SIZE = 60 * 1024
img_path = config.IP['img_path']

#path = config.IP['video_path']
path = config.IP['img_path']

def read_in_chunks(file_object, CHUNK_SIZE):
    print('2')
    while True:
        data = file_object.read(CHUNK_SIZE)
        if not data:
            break
        yield data


def log(message):
    log_date, raw_data = get_log_date()
    log_message = "[{0}] {1}".format(log_date, message)
    print(log_message)
    logging.info(log_message)
    return raw_data


def get_log_date():
    raw_data = datetime.now()
    log_date = raw_data.strftime('%Y-%m-%d %H:%M:%S.%f')
    return log_date, raw_data


def get_files(limit):
    path = config.IP['video_path']
    files = os.listdir(path)
    fileList = dict()
    cnt = 0
    file_sizes = 0
    limit_size = limit

    while True:
        # print(cnt)
        file_name = files[cnt]
        next_file = files[cnt + 1]
        filesize = os.path.getsize(path + file_name) / (1024.0 * 1024.0 * 1024.0)
        next_file_size = os.path.getsize(path + next_file) / (1024.0 * 1024.0 * 1024.0)
        file_sizes += filesize

        f = open(path + file_name, 'rb')
        fileList[file_name] = {file_name: f}
        f.close()

        if file_sizes + next_file_size > limit_size:
            print("total file size : ", file_sizes)
            break;
        cnt += 1
    return fileList


def getFileName(file):
    files = file.split(".")
    return files[0]


def returnFile(file, isZip):
    file_size = 0
    print("IsZip : {}".format(isZip))
    if isZip == "T":
        owd = os.getcwd()
        os.chdir(path)

        file_name = getFileName(file)
        zip_file_path = path + file_name + '.zip'
        zip_file_name = file_name + '.zip'

        zip_start = time.time()
        zip_file = zipfile.ZipFile(zip_file_name, 'w')
        zip_file.write(file)
        zip_file.close()

        os.chdir(owd)
        log("Compressed Time : %s" % (time.time() - zip_start))
        file_size = os.path.getsize(zip_file_path) / (1024.0 * 1024.0)
        file = zip_file_name
    else:
        file_size = os.path.getsize(path + file)

    return file, file_size


def getFilesByCnt(img_cnt):
    files = os.listdir(img_path)

    fileList = []
    file_sizes = 0
    fileList = files[0:img_cnt]

    print("SEND FILE LIST LENGTH : {}".format(len(fileList)))

    return fileList

# TODO : 이미지, 영상 분리 할 것
def tcp(host, port, limit, isZip):
    log("===================== new request(tcp) start ===================")
    print("isZip_tcp: {}".format(isZip))
    sleep = 0.0001
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except:
            print("Error: cannot connect to server")
            return

        try:
            #path = config.IP['video_path']
            # fileList = get_files(limit)

            path = img_path
            fileList = getFilesByCnt(limit)

            file_length = len(fileList)
            time.sleep(sleep)
            s.sendall(str(file_length).encode())

            time.sleep(sleep)
            s.recv(4090).decode()

            for file in fileList:
                file_name, file_size = returnFile(file, isZip)
                time.sleep(sleep)
                s.sendall(file_name.encode())

                time.sleep(sleep)
                isDone = s.recv(4090).decode()
                print("file name send done: ", isDone)

                #file_size = os.path.getsize(path + file_name)
                print("Find the file (%d bytes)" % file_size)
                time.sleep(sleep)
                s.sendall(str(file_size).encode())
                log(str(file_size))
                # s.sendall((file_size).to_bytes(length=8, byteorder="big"))
                print("Start sending ' " + file_name + "'")
                log("Start FILE_SIZE : {}MB SEND".format(file_size / (1024.0 * 1024.0)))
                f = open(path + file_name, 'rb')

                index = 0
                offset = 0

                for chunk in read_in_chunks(f, CHUNK_SIZE):
                    offset = index + len(chunk)
                    index = offset

                    time.sleep(sleep)
                    s.sendall(chunk)

                print("Finish sending'" + file_name + "'")
                f.close()
                log("END FILE_SIZE : {}MB SEND".format(file_size / (1024.0 * 1024.0)))
                time.sleep(sleep)
                isFinish = s.recv(4096).decode()
            log("FINISH REQUEST")
            s.close()



        except ConnectionError as e:
            log(str(e))
            print("Error: connection closed")
        except OSError as e:
            log(str(e))
            print("Error: cannot write file")
        except Exception as e:
            print(str(e))
            log(str(e))
            print("Error: bad response")



def udp(host, port, limit, isZip):
    log("=====================new request(udp) start ===================")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            path = config.IP['video_path']
            fileList = get_files(limit)

            file_length = len(fileList)
            s.sendto(str(file_length).encode(), (host, port))

            try:
                s.recv(4090).decode()
            except socket.timeout as e:
                print(e)
                log(str(e))

            for file in fileList:
                file_name, file_size = returnFile(file, isZip)
                s.sendto(file_name.encode(), (host, port))
                try:
                    isDone = s.recv(4090).decode()
                except socket.timeout:
                    continue
                print("file name send done: ", isDone)

               # file_size = os.path.getsize(path + file_name)
                print("Find the file (%d bytes)" % file_size)
                s.sendto(str(file_size).encode(), (host, port))
                # s.sendall((file_size).to_bytes(length=8, byteorder="big"))
                print("Start sendizxng ' " + file_name + "'")
                log("Start FILE_SIZE : {}MB SEND".format(file_size / (1024.0 * 1024.0)))
                print(path + file_name)
                f = open(path + file_name, 'rb')

                index = 0
                offset = 0

                for chunk in read_in_chunks(f, CHUNK_SIZE):
                    offset = index + len(chunk)
                    index = offset
                    s.sendto(chunk, (host, port))
                s.sendto("finish".encode(), (host, port))
                print("Finish sending'" + file_name + "'")
                f.close()
                log("END FILE_SIZE : {}MB SEND".format(file_size / (1024.0 * 1024.0)))
                try:
                    isFinish = s.recv(4096).decode()
                except socket.timeout:
                    continue

            log("FINISH REQUEST")
            s.close()

        except ConnectionError as e:
            log(str(e))
            print("Error: connection closed")
        except OSError as e:
            log(str(e))
            print("Error: cannot write file")
        except Exception as e:
            print(str(e))
            log(str(e))
            print("Error: bad response")


def run(host, port, limit, protocol, isZip):
    try:
        if protocol == "tcp":
            tcp(host, port, limit,isZip)
        elif protocol == "udp":
            udp(host, port, limit, isZip)
    except Exception as e:
        log(str(e))
        print(str(e))


# def run(host, port):
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# try:
# s.connect((host, port))
# except:
# print("Error: cannot connect to server")
# return

# try:
# path = config.IP['video_path']
# fileList = os.listdir(path)
# print(fileList)
# file_length = len(fileList)
# print(file_length)
# s.sendall(str(file_length).encode())

# for file in fileList:
# s.sendall(file.encode())

# isDone = s.recv(4090).decode()
# print("file name send done: ", isDone)

# file_size = os.path.getsize(path + file)
# print("Find the file (%d bytes)" % file_size)
# s.sendall(str(file_size).encode())
# #s.sendall((file_size).to_bytes(length=8, byteorder="big"))
# print("Start sending ' " + file + "'")
# log("Start FILE_SIZE : {}MB SEND".format(file_size / (1024.0 * 1024.0)))
# print(path+file)
# f = open(path+file, 'rb')
# l = f.read()
# s.sendall(l)
# print("Finish sending'" + file + "'")
# log("END FILE_SIZE : {}MB SEND".format(file_size / (1024.0 * 1024.0)))

# isFinish = s.recv(4096).decode()
# print("finish str : " + isFinish)


# except ConnectionError as e:
# log(str(e))
# print("Error: connection closed")
# except OSError as e:
# log(str(e))
# print("Error: cannot write file")
# except Exception as e:
# print(str(e))
# log(str(e))
# print("Error: bad response")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Connect to server and download server's file")
    parser.add_argument('-i', metavar="<ip>", help="host_name", required=True)
    parser.add_argument('-p', metavar="<port>", help="port_number", required=True)
    parser.add_argument('-l', metavar="<limit>", help="file_limit_size", required=True)
    parser.add_argument('-t', metavar="<protocol>", help="protocol type", required=True)
    parser.add_argument('-z', metavar="<isZip>", help="is Zip file", required=False)

    args = parser.parse_args()
    run(host=args.i, port=int(args.p), limit=int(args.l), protocol=str(args.t), isZip=str(args.z))
