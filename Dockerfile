# pull official base image
FROM python:3.10.4

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/

# CMD python manage.py makemigrations

CMD python manage.py migrate
#CMD python manage.py runserver 0.0.0.0:8000

#EXPOSE 8000