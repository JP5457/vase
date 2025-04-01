# start by pulling the python image
FROM python:3.11-alpine

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

#create a directory for the streams
RUN mkdir -p /streams
RUN mkdir -p /clipstore

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt
RUN apk add --no-cache ffmpeg

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["view.py" ]