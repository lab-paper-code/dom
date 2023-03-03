# @app.route('/upload_batch_img_zip', methods=['GET', 'POST'])
# def upload_batch_img_zip():
#     try:
#         if request.method == 'POST':
#             img_cnt = int(request.form.get('img_cnt'))
#             print("limit count : ", img_cnt)
#             batch = int(request.form.get('batch'))
#             print("batch : {}".format(batch))
#
#             if batch <= 0:
#                 raise ValueError
#
#             values = config.IP['clients']
#             start = time.time()
#             divide_cnt = int(img_cnt / len(values))
#
#             threads = [threading.Thread(target=cr.requestToAllClients_image_zip_batch, args=(ip, divide_cnt, batch)) for ip in values]
#
#             for thread in threads:
#                 thread.start()
#             for thread in threads:
#                 thread.join()
#             print("Elapsed Time : %s" % (time.time() - start))
#
#             return 'uploaded'
#     except Exception as e:
#         print(str(e))
#         return str(e)
#     except ValueError:
#         log("wrong batch number")
#         return "wrong batch number"
#
# @app.route('/upload_img_zip_batch', methods=['GET', 'POST'])
# def upload_img_zip_batch():
#     try:
#         img_cnt = int(request.form.get('img_cnt'))
#         print("limit count : ", img_cnt)
#         batch = int(request.form.get('batch'))
#
#         if batch <= 0:
#             raise ValueError
#
#         batch_images = int(img_cnt / batch)
#         print("batch_images : {}".format(batch_images))
#         threads = []
#
#         for i in range(0, batch):
#             start_index = i * batch_images
#             end_index = start_index + batch_images
#             print("index : {}, start_index : {}, end index : {}".format(i, start_index, end_index))
#             fileList = utils.getFileByCntWithIndex(start_index, end_index)
#             print("batch images length : {}".format(len(fileList)))
#             thread = threading.Thread(target=batch_threads, args=(i, fileList,))
#             threads.append(thread)
#         #threads = [threading.Thread(target=batch_threads, args=(i, batch_images, fileList,)) for i in range(0, batch)]
#         print("thread assignment completed :{}".format(len(threads)))
#         for thread in threads:
#             thread.start()
#         for thread in threads:
#             thread.join()
#
#         return "upload"
#
#
#     except Exception as e:
#         log(e)
#         return str(e)
#     except ValueError:
#         print("wrong batch number")
#         return "wrong batch number"
#
#
# def batch_threads(i, fileList):
#     try:
#         owd = os.getcwd()
#         os.chdir(img_path)
#         zip_start = time.time()
#
#         zip_file_name = 'compressed_' + i + '.zip'
#         print("Compressed file name : {}".format(zip_file_name))
#         zip_file = zipfile.ZipFile(zip_file_name, 'w')
#
#         for file in fileList:
#             zip_file.write(file)
#         zip_file.close()
#         log("Compressed Time : %s" % (time.time() - zip_start))
#
#         os.chdir(owd)
#
#         zip_file_path = img_path + zip_file_name
#         zip_file_size = os.path.getsize(zip_file_path)
#
#         start_time = log("{} send file {} {}byte, send START".format(my_ip, zip_file_name, zip_file_size))
#
#         index = 0
#         offset = 0
#
#         params = {
#             'time': start_time,
#             'size': int(zip_file_size),
#             'domId': my_ip
#         }
#
#         f = open(zip_file_path, 'rb')
#
#         for chunk in utils.read_in_chunks(f, CHUNK_SIZE):
#
#             offset = index + len(chunk)
#             index = offset
#
#             print("{} send file {} {}byte, send START".format(my_ip, zip_file_name, zip_file_size))
#             res = requests.post('http://' + server_add + '/upload', files={zip_file_name: chunk},
#                                 data=params)
#             # log("END {} FILE_SIZE : {}MB SEND".format(zip_file_name, zip_file_size))
#             log("{} send file {} {}byte, send END".format(my_ip, zip_file_name, zip_file_size))
#             if res.ok:
#                 print("Upload completed successfully! : {}".format(zip_file_name))
#                 print(res.text)
#             else:
#                 print("Something Wrong!")
#         f.close()
#
#         # 압축 파일 삭제
#         if os.path.exists(zip_file_path):
#             os.unlink(zip_file_path)
#         else:
#             print("Compressed File not existed")
#
#         return "UPLOAD COMPRESSED"
#     except Exception as e:
#         log(str(e))
#         return str(e)
