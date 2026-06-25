# Instalacao do Python2 via Pyenv
## Dependências de compilação do Pyenv

```bash
sudo apt update
sudo apt install -y build-essential checkinstall libncursesw5-dev libssl-dev \
libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev libreadline-dev
```
## Instalacao do Pyenv
``` bash
curl https://pyenv.run | bash
```
## Variaveis de ambiente
``` bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
``` 
## Instalacao e definição do python2
``` bash
pyenv install 2.7.18
pyenv local 2.7.18
``` 


