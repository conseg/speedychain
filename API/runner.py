
"""
import io
import time

import Pyro4
import Pyro4.naming
import subprocess
from .src.controller import Gateway
from threading import Thread
import Pyro4.naming

import sys

from .src.controller import Gateway


def runGateway(nameServerIP, nameServerPort, gatewayName):
    Gateway.main(nameServerIP, nameServerPort, gatewayName)

def runPyro4(nameServerIP, nameServerPort):
    Pyro4.naming.startNSloop(nameServerIP, nameServerPort)

def runPyro(nameServerIP, nameServerPort):
    pyro = Thread(target=runPyro4, args=(nameServerIP, nameServerPort)).start()
"""
import sys
import argparse

from pycallgraph import PyCallGraph, Config, GlobbingFilter
from pycallgraph.output import GraphvizOutput
import os

from src.controller import Gateway

parser = argparse.ArgumentParser(description='Run the Gateway')

parser.add_argument('-n', '--nameServerIP', type=str, metavar='', help='Server IP address')
parser.add_argument('-p', '--nameServerPort', type=str, metavar='', help='Server port')
parser.add_argument('-G', '--gatewayName', type=str, metavar='', help='The name of the gateway')
parser.add_argument('-C', '--gatewayContext', type=str, metavar='', help='The context of the gateway')
parser.add_argument('-S', '--poolSize', type=str, metavar='', help='Amount of Tx from each Pool')
args = parser.parse_args()

# 1. Configuracao estrita dos filtros do PyCallGraph
config = Config()

# Rastreia apenas as suas subpastas dentro de API/src/
config.trace_filter = GlobbingFilter(
    include=['*'], # Deixa tudo passar...
    exclude=[      # ...e vai podando o mato alto
        'pycallgraph.*', 'serpent.*', 'selectors34.*', 'Pyro4.*', 
        'encodings.*', 'sys.*', 'os.*', 'posix.*', 'socket.*', 'threading.*'
    ]
)

# 2. Configuracao do arquivo de saida PNG
# Ele sera salvo na mesma pasta de onde voce disparar o terminal
output = GraphvizOutput()
output.output_file = os.path.abspath('fluxo_execucao_gateway.png')

print("================================================================")
print(" INICIANDO GATEWAY COM MAPEAMENTO DINAMICO ATIVADO")
print(" Execute seus testes. Para gerar o grafico, pare este terminal com CTRL+C.")
print("================================================================")

# 3. Execucao protegida
try:
    with PyCallGraph(output=output, config=config):
        Gateway.main(args.nameServerIP, int(args.nameServerPort), args.gatewayName, args.gatewayContext,int(args.poolSize))
except KeyboardInterrupt:
    print("\n[INFO] Sinal de parada recebido. Renderizando grafico...")
    print("[SUCESSO] Grafico salvo em: {}".format(output.output_file))

