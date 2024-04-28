import block_pb2_grpc
import block_pb2
import transaction_pb2_grpc
import transaction_pb2
import time
import grpc

def run():
  channel = grpc.insecure_channel('localhost:50051')
  stub_block = block_pb2_grpc.BlockServiceStub(channel)
  stub_transaction = transaction_pb2_grpc.TransactionServiceStub(channel)
  
  hash = block_pb2.FindBlockByHashRequest(hash="sint pariatur officia ut")
  response = stub_block.FindBlockByHash(hash)

  print(response)

if __name__ == "__main__":
    run()