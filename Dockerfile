FROM matthewfeickert/docker-python3-ubuntu:latest

COPY . .

RUN sudo apt install -y --no-install-recommends ffmpeg

RUN pip install --upgrade --user pip
RUN pip install --user -r requirements.txt
RUN pip install --user pytest

ENTRYPOINT /bin/bash
