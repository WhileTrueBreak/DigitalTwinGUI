from connections.opcua import Opcua
import asyncio

print('.')
opcua = Opcua('oct.tpc://172.32.1.236:4840/server/')
print('.')
v = asyncio.run(opcua.getValue('d_Joi1'))
print('.')
print(v)