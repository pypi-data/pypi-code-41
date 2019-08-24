# import socket

# udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# udpSocket.sendto(bytes("/cmd/json/animate?--list", "utf-8"), ("localhost", 5550))
# response, _ = udpSocket.recvfrom(2048)

# print('r: {}, x: {}'.format(response, _))

from butter.mas.api import ClientFactory

butterHttpClient = ClientFactory().getClient('localhost', protocol='udp')
result = butterHttpClient.playAnimation('welcome')

print(result)