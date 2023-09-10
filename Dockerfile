#Deriving the latest base image
FROM python:latest


#Labels as key value pair
#LABEL Maintainer="roushan.me17"


# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
COPY . /usr/app/

# Create the db directory
RUN mkdir -p /usr/app/db
RUN pip install flask
RUN pip install flask-session
RUN pip install requests
#RUN pip install logging
RUN pip install flask_sqlalchemy
#to COPY the remote file at working directory in container
COPY . /usr/app/

# Now the structure looks like this '/usr/app/src/test.py'


#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

CMD [ "python", "run.py"]
