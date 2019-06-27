FROM python:2.7-alpine

LABEL maintainer="CONSEG – Grupo de Confiabilidade e Segurança de Sistemas <conseg@pucrs.br>"
LABEL version="1.0"

COPY conf/pip.conf /etc/
RUN pip install --upgrade pip && \
    pip install Pyro4 dill

EXPOSE 9090

ENTRYPOINT [ "pyro4-ns", "-n", "172.28.0.2", "-p", "9090" ]
