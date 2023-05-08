FROM debian:bullseye-slim
MAINTAINER Luca DArcangelo <luca.darcangelo@bluewin.ch>

RUN apt-get update && apt-get install -y python3.9 sudo postgresql git pip libcap-dev libcups2-dev libpq-dev python3-dev libcgroup-dev openjdk-17-jdk openjdk-17-jre zip vim

RUN pip install markupsafe==2.0.1
RUN echo "postgres ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN useradd -ms /bin/bash admin && \
    echo "admin ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /code
WORKDIR /code

EXPOSE 8888 8889 8890
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD ["grader"]
