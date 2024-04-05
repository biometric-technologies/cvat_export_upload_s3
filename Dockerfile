# Start with Ubuntu base image
FROM ubuntu:latest

# Update Ubuntu Software repository
RUN apt-get update

# Install Python 3, WireGuard, and iproute2
RUN apt-get install -y python3 python3-pip software-properties-common
RUN apt-get update
RUN apt-get install -y wireguard iproute2 openresolv

VOLUME /etc/wireguard/
VOLUME /app/conf

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY *.py /app/
COPY export.sh /app/

RUN chmod +x export.sh

CMD ["/app/export.sh"]