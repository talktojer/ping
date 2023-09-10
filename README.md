# ping


docker run -it -v ~/ping_db:/usr/app/src/db ping python app.py --setup
docker run -itd -v ~/ping_db:/usr/app/src/db -p 8092:8092 --name=ping ping:latest


docker stop ping && docker container rm ping && docker build . -t ping:latest && docker run -itd -v ~/ping_db:/usr/app/src/db -p 8092:8092 --name=ping ping:latest && curl -d "build done" ntfy.jersweb.net/test


