docker run -it -d -v /home/palisade2/dom/share:/home/ -p 50011:50011 --name dom1 dom:latest /bin/bash /DOM/server/start_server.sh 50011
docker run -it -d -v /home/palisade2/dom/share:/home/ -p 50012:50012 --name dom2 dom:latest /bin/bash /DOM/server/start_server.sh 50012
docker run -it -d -v /home/palisade2/dom/share:/home/ -p 50013:50013 --name dom3 dom:latest /bin/bash /DOM/server/start_server.sh 50013
docker run -it -d -v /home/palisade2/dom/share:/home/ -p 50014:50014 --name dom4 dom:latest /bin/bash /DOM/server/start_server.sh 50014

docker run -it -d -v /home/palisade2/dom/share:/home/ -p 50021:50021 --name dom1_socket dom:latest /bin/bash /DOM/server_socket/start_server.sh 50021 /home/data/
docker run -it -d -v /home/palisade2/dom/share:/home/ -p 50022:50022 --name dom2_socket dom:latest /bin/bash /DOM/server_socket/start_server.sh 50022 /home/data/
docker run -it -d -v /home/palisade2/dom/share:/home/ -p 50023:50023 --name dom3_socket dom:latest /bin/bash /DOM/server_socket/start_server.sh 50023 /home/data/
docker run -it -d -v /home/palisade2/dom/share:/home/ -p 50024:50024 --name dom4_socket dom:latest /bin/bash /DOM/server_socket/start_server.sh 50024 /home/data/
