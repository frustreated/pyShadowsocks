#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
#

import asyncio

import constants
from pac.http_server import FakeHTTPGetProtocol
from protocol.shadowsocks.server import ShadowsocksServerRelayProtocol
from protocol.shadowsocks.socks5_server import ShadowsocksSOCKS5ServerProtocol
from util.config import parse_args_new


def main():
    ns = parse_args_new()

    if ns.server_mode == constants.ARG_LOCAL_SERVER:
        if ns.protocol_mode == constants.ARG_PROTOCOL_SHADOWSOCKS:
            loop = asyncio.get_event_loop()
            # Each client connection will create a new protocol instance
            coro = loop.create_server(
                lambda: ShadowsocksSOCKS5ServerProtocol(loop, config=ns),
                '0.0.0.0',
                ns.listen_port)
            server = loop.run_until_complete(coro)

            coro = loop.create_server(FakeHTTPGetProtocol, '127.0.0.1', 8080)
            server = loop.run_until_complete(coro)

            loop.run_forever()
    elif ns.server_mode == constants.ARG_REMOTE_SERVER:
        if ns.protocol_mode == constants.ARG_PROTOCOL_SHADOWSOCKS:
            loop = asyncio.get_event_loop()
            # Each client connection will create a new protocol instance
            coro = loop.create_server(lambda: ShadowsocksServerRelayProtocol(loop, config=ns), '0.0.0.0',
                                      ns.listen_port)
            server = loop.run_until_complete(coro)
            loop.run_forever()


if __name__ == '__main__':
    main()