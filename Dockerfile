FROM python:3

LABEL maintainer="CONSEG – Grupo de Confiabilidade e Segurança de Sistemas <conseg@pucrs.br>" \
      codeAuthor="CONSEG – Grupo de Confiabilidade e Segurança de Sistemas <conseg@pucrs.br>"

WORKDIR /src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./your-daemon-or-script.py" ]