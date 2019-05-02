FROM python:3

LABEL maintainer="CONSEG – Grupo de Confiabilidade e Segurança de Sistemas <conseg@pucrs.br>"
LABEL version="1.0"

WORKDIR /src

COPY ./src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

CMD [ "python", "./app/r2ac.py" ]