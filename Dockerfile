FROM ubuntu:latest
RUN apt update
Run apt install python3 -y
Run apt install sentinelsat -y
Run apt install pip -y
WORKDIR /home/lt-339/PycharmProjects/tudip/Practicals/
COPY requirement.txt ./

COPY Sentinel_Data.sqlite .

RUN pip install -r requirement.txt
COPY Sentinel.geojson ./

COPY fetDataUsProdId.py ./
CMD ["python3","./fetDataUsProdId.py"]