# -- coding: utf-8 --
import socket
import argparse
import glob
import os
import sys
import tempfile
import datetime
import config
import zipfile
import time 
import threading

UPLOAD_FOLDER = '/home/data/'
UPLOAD_LOG_FOLDER = UPLOAD_FOLDER + 'log/'
DOM_CONTAINER = config.IP['container_name']

def log_request(addr, time, f, size, status) -> None:
    with open(UPLOAD_LOG_FOLDER + DOM_CONTAINER + '_socket_log.log', 'a+') as log:
        print('[' + str(time)+ '] ' + str(addr[0]) + ' received file ' + str(f) + ' ' + str(size) + 'MB, receive ' + status ,file=log)

def run_tcp_server(port, root_dir):
    host = ''
    before_packet = ''
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            s.listen(10000)
        except:
            print("Error: cannot run server")
            return

        while True:
            try:
                print("\nWaiting for connection...")

                conn, addr = s.accept()
                
                
                
                file_count = conn.recv(4096).decode()
                while True:
                    if file_count and file_count != before_packet:
                        break
                    else:
                        file_count = conn.recv(4096).decode()
                before_packet = file_count
                
                print("file_count: ", file_count)
                
                conn.sendall('file_count'.encode())
                
                for i in range(int(file_count)):
                    print('connect')
                    time.sleep(0.001)
                    file_name = conn.recv(4096).decode()
                    while True:
                        if file_name and file_name != before_packet:
                            break
                        else:
                            file_name = conn.recv(4096).decode()
                    before_packet = file_name
                    print('file: ', file_name)
                    
                    time.sleep(0.0001)
                    conn.sendall('done'.encode())
                    
                    time.sleep(0.001)
                    file_size = conn.recv(4096).decode()
                    while True:
                        if file_size and file_size != before_packet:
                            break
                        else:
                            file_size = conn.recv(4096).decode()
                    before_packet = file_size
                    print('file size: ', file_size)
                    
                    filesize = int(file_size)
                    
                    if filesize == 0:
                        print("Error: file size 0")
                        return
                    print("Get file: '" + file_name)
                
                    nowdown_size = 0
                    downbuff_size = 60 * 1024.0 * 1024.0
                    log_request(addr, datetime.datetime.now(), file_name, int(file_size) / 1024.0 / 1024.0, 'start')
                    with tempfile.NamedTemporaryFile(delete=False, dir="/home/data/") as f:
                        temp_name = f.name
                        while True:
                            if nowdown_size < filesize:
                                time.sleep(0.001)
                                resp = conn.recv(min(downbuff_size, filesize - nowdown_size))
                                if not resp: 
                                    print('not resp!!!!!!!!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                                    continue
                                nowdown_size += len(resp)
                                f.write(resp)
                                #print("Download %.4f%%" % min(100, nowdown_size / filesize * 100))
                                sys.stdout.flush()
                            else:
                                print("Finish!\n")
                                break
                    print('end while loop')
                    
                    if os.path.exists(UPLOAD_FOLDER + file_name):
                        file_name = DOM_CONTAINER + '_' + file_name
                        
                    os.replace(temp_name, UPLOAD_FOLDER + file_name)
                    download_filesize = os.path.getsize(UPLOAD_FOLDER + file_name)
                    print('success save')
                    if file_name.endswith('.zip'):
                        with zipfile.ZipFile(UPLOAD_FOLDER + file_name, 'r') as zip_ref:
                            zip_ref.extractall(UPLOAD_FOLDER)
                            os.remove(UPLOAD_FOLDER + file_name)
                            
                    log_request(addr, datetime.datetime.now(), file_name, download_filesize / 1024.0 / 1024.0, 'end')
                    time.sleep(0.0001)
                    conn.sendall('Finish send'.encode())
                
            except ConnectionError as error:
                print(error)
            except OSError as error:
                print(error)
            except Exception as e:
                print(e)
            finally:
                try: conn.close()
                except: pass

def run_udp_server(port, root_dir):
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
        host = ''
        try:
            s.bind((host, port))
        except:
            print("Error: cannot run server")
            return

        while True:
            try:
                print("\nWaiting for connection...")
                try:
                    file_count, addr = s.recvfrom(4096)
                except socket.timeout:
                    continue
                file_count = file_count.decode()
                print("file_count: ", file_count)
                
                s.sendto('file_count'.encode(), addr)
                
                for i in range(int(file_count)):
                    check = False
                    print('connect')
                    try:
                        file_name, addr = s.recvfrom(4096)
                    except socket.timeout:
                        continue
                    file_name = file_name.decode()
                    print('file: ', file_name)
                    
                    s.sendto('done'.encode(), addr)                    
                    try:
                        file_size, addr = s.recvfrom(4096)
                    except socket.timeout:
                        continue
                    file_size = file_size.decode()
                    print('file size: ', file_size)
                    
                    filesize = int(file_size)
                    
                    if filesize == 0:
                        print("Error: file size 0")
                        return
                    print("Get file: '" + file_name)
                
                    nowdown_size = 0
                    downbuff_size = 60 * 1024.0
                    log_request(addr, datetime.datetime.now(), file_name, int(file_size) / 1024.0 / 1024.0, 'start')
                    with tempfile.NamedTemporaryFile(delete=False, dir="/home/data/") as f:
                        temp_name = f.name
                        while True:
                            if nowdown_size < filesize:
                                try:
                                    resp, addr = s.recvfrom(min(downbuff_size, filesize - nowdown_size))
                                except socket.timeout:
                                    continue
                                try:
                                    resp.decode()
                                    check = True
                                    break
                                except:
                                    nowdown_size += len(resp)
                                f.write(resp)
                                #print("Download %.4f%%" % min(100, nowdown_size / filesize * 100))
                                sys.stdout.flush()
                            else:
                                try:
                                    resp, addr = s.recvfrom(min(downbuff_size, filesize - nowdown_size))
                                except socket.timeout:
                                    continue
                                print("Finish!\n")
                                break
                    print('end while loop')
                    if check:
                        try:
                            resp, addr = s.recvfrom(min(downbuff_size, filesize - nowdown_size))
                        except socket.timeout:
                            continue
                    if os.path.exists(UPLOAD_FOLDER + file_name):
                        file_name = DOM_CONTAINER + '_' + file_name
                        
                    os.replace(temp_name, UPLOAD_FOLDER + file_name)
                    print('success save')
                    
                    log_request(addr, datetime.datetime.now(), file_name, os.path.getsize(UPLOAD_FOLDER + file_name) / 1024.0 / 1024.0, 'end')
                    
                    s.sendto('Finish send'.encode(), addr)
                
            except ConnectionError as error:
                print(error)
            except OSError as error:
                print(error)
            except Exception as e:
                print(e)
            finally:
                try: conn.close()
                except: pass
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run file server")
    parser.add_argument('-p', metavar="<port>", help="port_number", required=True)
    parser.add_argument('-d', metavar="<dir>", help="root_directory", required=True)
    parser.add_argument('-t', metavar="<type>", help="server_type", required=True)
    
    args = parser.parse_args()
    
    print(args.t)
    
    if args.t == 'tcp':
        run_tcp_server(port=int(args.p), root_dir=args.d)
    else:
        run_udp_server(port=int(args.p), root_dir=args.d)