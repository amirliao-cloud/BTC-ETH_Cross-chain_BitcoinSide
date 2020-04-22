import socket
from Network.NetworkEnvelope import NetworkEnvelope
from Network.Messages import VersionMessage, VerAckMessage, PingMessage, PongMessage
from unittest import TestCase


class SimpleNode:
    def __init__(self, host, port=None, testnet=False, logging=False):
        if port is None:
            if testnet:
                port = 18333
            else:
                port = 8333
        self.testnet = testnet
        self.logging = logging
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with self.socket as s:
            s.connect((host, port))
            self.stream = s.makefile('rb', None)

    def send(self, message):
        '''Send a message to the connected node'''
        envelope = NetworkEnvelope(message.command, message.serialize(), testnet=self.testnet)
        if self.logging:
            print('sending: {}'.format(envelope))
        self.socket.sendall(envelope.serialize())

    def read(self):
        '''Read a message from the socket'''
        envelope = NetworkEnvelope.parse(self.stream, testnet=self.testnet)
        if self.logging:
            print('receiving: {}'.format(envelope))
        return envelope

    def wait_for(self, *message_classes):
        '''Wait for one of the messages in the list'''
        command = None
        command_to_class = {m.command: m for m in message_classes}
        while command not in command_to_class.keys():
            envelope = self.read()
            command = envelope.command
            if command == VersionMessage.command:
                self.send(VerAckMessage())
            elif command == PingMessage.command:
                self.send(PongMessage(envelope.payload))
        return command_to_class[command].parse(envelope.stream())

    def handshake(self):
        '''Do a handshake with the other node.
        Handshake is sending a version message and getting a verack back.'''
        # create a version message
        version = VersionMessage()
        # send the command
        self.send(version)
        # wait for a verack message
        self.wait_for(VerAckMessage)


class SimpleNodeTest(TestCase):
    def test_handshake(self):
        node = SimpleNode('testnet.programmingbitcoin.com', testnet=True)
        node.handshake()

if __name__ == '__main__':
    pass
    # HOST= 'testnet.programmingbitcoin.com'
    # PORT = 18333
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    #     stream = s.makefile('rb', None)
    #     version = VersionMessage()
    #     envelope = NetworkEnvelope(version.command, version.serialize())
    #     s.sendall(envelope.serialize())
    #     while True:
    #         new_message = NetworkEnvelope.parse(stream)
    #         print(new_message)