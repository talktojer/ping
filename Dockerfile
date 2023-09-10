#Deriving the latest base image
FROM python:latest


#Labels as key value pair
#LABEL Maintainer="roushan.me17"


# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /usr/app/src
# Create the db directory
RUN mkdir -p /usr/app/src/db
RUN pip install flask
RUN pip install flask-session
RUN pip install requests
#RUN pip install logging
RUN pip install flask_sqlalchemy
#to COPY the remote file at working directory in container
COPY app.py ./
COPY run.py ./
ADD my_app .
COPY admin.html ./
COPY index.html ./
COPY register.html ./
COPY login.html ./
COPY add_user.html ./

# Now the structure looks like this '/usr/app/src/test.py'


#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

CMD [ "python", "./run.py"]
