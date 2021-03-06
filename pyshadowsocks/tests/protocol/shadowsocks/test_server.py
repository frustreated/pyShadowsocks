#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import asyncio
import unittest
from argparse import Namespace
from socket import socketpair

import constants
import encrypt
from packet.stream_packer import StreamPacker
from protocol.shadowsocks.encoder import ShadowsocksEncryptionWrapperEncoder
from protocol.shadowsocks.header import ShadowsocksPacketHeader
from protocol.shadowsocks.proxy_server import ShadowsocksProxyServerProtocol


class ShadowsocksServerTest(unittest.TestCase):
    def test_data_relay(self):
        # Create a pair of connected sockets
        lsock, rsock = socketpair()
        loop = asyncio.get_event_loop()

        _args = {constants.ARG_CIPHER_METHOD: encrypt.AES_256_CFB, constants.ARG_PASSWORD: '123456'}
        config = Namespace(**_args)

        # Register the socket to wait for data
        connect_coro = loop.create_connection(lambda: ShadowsocksProxyServerProtocol(loop, config), sock=lsock)
        transport, protocol = loop.run_until_complete(connect_coro)

        cipher_method = encrypt.AES_256_CFB
        password = '123456'

        encoder = encoder = ShadowsocksEncryptionWrapperEncoder(
            encrypt_method=cipher_method,
            password=password,
            encript_mode=True)

        decoder = ShadowsocksEncryptionWrapperEncoder(
            encrypt_method=cipher_method,
            password=password,
            encript_mode=False)

        packer = StreamPacker()

        protocol.loop = loop
        header = ShadowsocksPacketHeader(addr='example.com', port=80, addr_type=constants.SOCKS5_ADDRTYPE_HOST)
        http_request_content = b'GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: curl/7.43.0\r\nAccept: */*\r\n\r\n'

        # Simulate the reception of data from the network
        encoded_data = packer.pack(header=header, data=http_request_content)
        encoded_data = encoder.encode(encoded_data)
        loop.call_soon(rsock.send, encoded_data)

        def reader():
            data = rsock.recv(100)
            if not data or len(data) == 0:
                return

            data = decoder.decode(data)
            _, http_response_content = packer.unpack(data, header=None)
            self.assertEqual(http_response_content[:4], b'HTTP')
            # We are done: unregister the file descriptor
            loop.remove_reader(rsock)
            lsock.close()
            rsock.close()
            # Stop the event loop
            loop.stop()

        # Register the file descriptor for read event
        loop.add_reader(rsock, reader)
        # Run the event loop
        loop.run_forever()
        # We are done, close sockets and the event loop
