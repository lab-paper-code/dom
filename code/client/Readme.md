DOM Client Readme
* client 폴더
    * client_app_image.py : 이미지 추론 관련 api 및 함수
    * client_batch_zip.py : 이미지 압축을 batch로 나누어 압축 후 전송(실험 하려 했으나 무산, 코드가 제대로 작동하는지는 확인 해봐야함.)
    * client_combine.py : 영상 데이터와 이미지 데이터를 같이 전송하는 실험 관련 api 및 함수
    * client image.py : 이미지 전송 관련 api 및 함수 
    * client_mqtt.py : mqtt 전송 관련 api 및 함수
    * client_socket.py : socket을 이용한 전송 관련 api 및 함수 
    * client_text.py : text 데이터 전송 관련 api 및 함수
    * client_video.py : 영상 데이터 전송 관련 api 및 함수 
* app.py : main (실행)
* client_request.py : request 관련 코드 
* config.py : device 별 config 값 세팅(git ignore)
    ```
    IP = {
    'video_path': '/home/dom/dom/videos/',  # 영상 데이터가 저장된 위치
    'img_path' : '/home/dom/dom/images/',   # 이미지 데이터가 저장된 위치
    'server': '155.230.36.27:50011', # DOM: 데이터를 보낼 서버 주소, 현재 DOM 구조 상 각 디바이스 별로 주소가 다르므로 디바이스 별로 따로 세팅 해줘야함. KSV 에서는 사용하지 않아서 신경쓸 필요 X
    'clients':['155.230.36.58','155.230.36.220','155.230.36.221','155.230.36.222','155.230.36.241','155.230.36.248','155.230.36.250','155.230.36.244','155.230.36.249','155.230.36.242','155.230.36.243','155.230.36.245','155.230.36.246','155.230.36.247','155.230.36.251','155.230.36.252','155.230.36.253'],# DOM: control(?)할 device에만 전체 IP를 작성해주고 나머지 device에서는 따로 신경쓰지 않아도 된다.  KSV 에서는 사용하지 않아서 신경쓸 필요 X
    'socket_host': '59.27.74.76', # socket 전송 시 서버 IP, 기기별로 변경
    'socket_post' : '50025',  # socket 전송시 사용한  port, 기기별로 변경
    'webdav' : '/home/dom/webdav/',  # KSV : webdav 공유 폴더 , 이미지 추론 결과 저장
    'volumeID': 'pod1' # KSV 데모시 사용
    }
    ```
* image_classification.py : 이미지 추론 코드
* videoCompress.py : 영상 압축 코드 -> zip으로 압축 아닌 ffmpeg로 영상 압축, 영상 자체의 용량을 줄여줌
* socket_client.py : socket 전송(udp, tcp)
* update_device.py : 전체 pi기기 코드 업데이트(git)


* upload.py 전체 코드 (합쳐져 있는 코드)

## server와 client의 구조
![구조](image/structure.PNG)


## 이외의 TIP
---
* IP 변경되면 PI 기기의 /etc/hosts/ 의 dom IP변경 해주기


* 일반 계정 git pull 권한 해결
sudo chmod a+rwx .git/FETCH_HEAD

* gitlab id/password 저장
git config --global credential.helper store

* API Curl 명령어 예시

```
모든 디바에스에게 (비디오) 
curl -d "limit=16&is_zip=T" -X POST http://ip:port/upload_all_video
한 디바이스에게 (비디오)
curl -d "limit=16" -X POST http:ip:port/upload_video
한 디바이스에게(비디오 압축)
curl -d "limit=16" -X POST http:ip:port/upload_video_zip

모든 디바이스에게(비디오 전체 한번에 압축) limit 그대로 (40)
curl -d "limit=16" -X POSt http:ip:port/upload_all_video_zip
한 디바이스에게(이미지 전체 한번에 압축)
curl -d "limit=16" -X POST http:ip:port/upload_zip_all

모든 디바이스에게 (이미지)
curl -d "img_cnt=10000&is_predict=F&is_zip=F" -X POST http:ip:port/upload_all_img
한 디바이스에게 (이미지)
curl -d "img_cnt=10000&is_predict=T" -X POST http:ip:port/upload_image
한 디바이스에게(이미지 압축)
curl -d "img_cnt=10000&is_predict=T" -X POST http:ip:port/upload_image_zip

모든 디바이스에게(이미지 전체 한번에 압축)
curl -d "img_cnt=10000" -X POSt http:ip:port/upload_all_img_zip
한 디바이스에게(이미지 전체 한번에 압축)
curl -d "img_cnt=10000" -X POST http:ip:port/upload_img_zip_all

모든 디바이스에게(이미지 batch 압축)
curl -d "img_cnt=10000&batch=2" -X POST http://ip:port/upload_batch_img_zip
curl -d "img_cnt=10000&batch=2" -X POST http://ip:port/upload_img_zip_batch

모든 디바이스에게 데이터 이질성 : 
img_cnt == 0 일경우 video 100%
limit == 0 일 경우 img 100%
curl -d "img_cnt=80000&limit=16" -X POST http://ip:port/upload_hetero

모든 디바이스에게(mqtt, 비디오)
curl -d "limit=16" -X POST http://ip:port/upload_all_video_mqtt
한 디바이스에게 (mqtt, 비디오)
curl -d "limit=16" -X POST http:ip:port/upload_video_mqtt

모든 디바이스에게(mqtt, 이미지)
curl -d "img_cnt=10000" -X POST http://ip:port/upload_all_image_mqtt
한 디바이스에게 (mqtt, 이미지)
curl -d "img_cnt=10000" -X POST http:ip:port/upload_image_mqtt

jupyter notebook --ip=155.230.34.159 --port=50000

모든 디바이스에게 (mqtt, text)
curl -d "limit=16" -X POST http://ip:60000/upload_all_txt_mqtt
한 디바이스에게 (mqtt, text)
curl -d "limit=16" -X POST http://ip:60000/upload_txt_mqtt


모든 디바이스에게 이미지 인식 딥러닝 처리1 요청(디바이스 내에서 처리)
curl -d "img_cnt=10000" -X POST http://ip:port/image/app/device
한 디바이스에게 이미지 인식 딥러닝 처리1 요청
curl -d "img_cnt=10000" -X POST http://ip:port/imagenet1_each

모든 디바이스에게 이미지 인식 딥러닝 처리 2 요청(50 + 50)
curl -d "img_cnt=10000" -X POST http://ip:port/image/app/offloading/half/each

모든 디바이스에게 이미지 인식 딥러닝처리 3 요청 100%서버 오프로딩
curl -d "img_cnt=10000" -X POST http://ip:port/image/app/offloading/full


모든 디바이스 영상 모션 인식 딥러닝 처리1 요청
curl -d "limit=16" -X POST http://ip:60000/video1
모든 디바이스 영상 모션 인식 딥러닝 처리2 (50 + 50)
curl -d "limit=16" -X POST http://ip:60000/video2
모든 디바이스 영상 모션 인식 딥러닝처리3 100% 서버 오프로딩
curl -d "limit=16" -X POST http://ip:60000/video3

모든 디바이스에게 비디오 압축 요청 1
curl -d "limit=16" -X POST http://ip:port/video_compress1
한 디바이스에게 비디오 압축 요청2
curl -d "limit=2" -X POST http://ip:port/video_compress1_each

모든 디바이스에게 비디오 압축 요청 2
curl -d "limit=16" -X POST http://ip:port/video_compress2

모든 디바이스 socket tcp 
#curl -d "limit=2&protocol=tcp&isZip=F" -X POST http://ip:port/upload_all_socket
curl -d "limit=2&protocol=tcp" -X POST http://ip:port/upload_all_socket : 일단 isZip 막아놓음

모든 디바이스 socket udp
curl -d "limit=2&protocol=udp" -X POST http://ip:port/upload_all_socket : 일단 isZip 막아놓음

모든 디바이스에게 텍스트 nGB 보내기
curl -d "limit=5" -X POST http://ip:60000/upload_all_text 
한 디바이스 서버에게 텍스트 nGB 보내기
curl -d "limit=5" -X POST http://ip:60000/upload_text

모든 파이에게 (비디오 압축 ) 
curl -d "limit=4" -X POST http://ip:port/video1
파이 반 서버 반  파이에게 (비디오 압축 ) 
curl -d "limit=5" -X POST http://ip:port/video2
서버  서버에게 (비디오 압축 ) 
curl -d "limit=5" -X POST http://ip:port/video3

```

