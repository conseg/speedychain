FROM python:2.7-alpine

LABEL maintainer="CONSEG – Grupo de Confiabilidade e Segurança de Sistemas <conseg@pucrs.br>"
LABEL version="1.0"

COPY conf/pip.conf /etc/
RUN pip install --upgrade pip && \
    pip install Pyro4 dill

EXPOSE 9090

 # name-server = ec2-50-16-193-245.compute-1.amazonaws.com = 172.31.42.239
# sudo su
# ps -aux | grep pyro
# pyro4-ns -n 0.0.0.0 -p 9090 &
# pyro4-nsc -n 0.0.0.0 -p 9090 list
ENTRYPOINT [ "pyro4-ns", "-n", "0.0.0.0", "-p", "9090" ]
