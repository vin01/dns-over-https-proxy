# coding=utf-8

import socketserver
import threading
import signal
import sys
import requests
import random
import string
import ast
import logging
from dnslib import *

logging.basicConfig(
    format='%(levelname)s:%(message)s',
    level=logging.DEBUG
)


def signal_handler(sig, frame):
    logging.info('You pressed Ctrl+C!')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

SERVER_PORT = 5053
GOOGLE_RESOLVER_URL = 'https://dns.google.com/resolve'


def generate_noise():
    '''
    Random padding based on https://developers.google.com/speed/public-dns/docs/dns-over-https

    '''
    return ''.join(
        random.choice(
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits +
            '-~._')
        for _ in range(25))


def resolve_over_https(domain, query_type):
    '''
    Perform DMS queries over HTTPS
    '''
    params = {
        'edns_client_subnet': '0.0.0.0/0',
        'cd': False
    }
    params['name'] = domain
    params['type'] = query_type
    params['random_padding'] = generate_noise()

    try:
        r = requests.get(
            GOOGLE_RESOLVER_URL,
            params=params
        )
    except Exception:
        raise

    if r.ok:
        response = r.json()
        logging.debug(response)
        return response.get('Answer')


def resolve(data):
    '''
    Returns the DNS response to client requests
    '''

    request = DNSRecord.parse(data)

    logging.debug(request)

    reply = DNSRecord(
        DNSHeader(
            id=request.header.id,
            qr=1,
            aa=1,
            ra=1
        ),
        q=request.q
    )

    domain = request.q.qname
    query_type = request.q.qtype

    logging.debug('Domain: %s' % domain)
    logging.debug('Query type: %s' % query_type)

    raw_resp = resolve_over_https(str(domain), int(query_type))

    if raw_resp:

        for response in raw_resp:
            logging.debug('Response: %s' % response)

            if response.get('type'):
                record_type = getattr(
                    sys.modules[__name__],
                    QTYPE.get(response.get('type'))
                )
                response_type = response.get('type')
                dns_args = response.get('data')

                '''
                Handle CAA, DNSKEY records as exceptions
                If passed as it is to dnslib, these will
                cause exceptions and shall be passed 
                after being parsed as separate fields.
                '''

                if response_type in (257, 48):
                    tmp_args = dns_args.split(' ')
                    dns_args = []
                    for arg in tmp_args:
                        try:
                            dns_args.append(ast.literal_eval(arg))
                        except:
                            dns_args.append(arg)
                    rdata = record_type(*dns_args)
                else:
                    rdata = record_type(dns_args)

                reply.add_answer(RR(rname=domain, rtype=response.get(
                    'type'), rclass=1, ttl=response['TTL'], rdata=rdata))

    return reply.pack()


class BaseRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):

        try:
            data = self.get_data()
            self.send_data(resolve(data))
        except Exception:
            # Possible data format mismatch
            raise


class TCPRequestHandler(BaseRequestHandler):

    def get_data(self):
        data = self.request.recv(8092).strip()
        sz = struct.unpack('>H', data[:2])[0]
        return data[2:]

    def send_data(self, data):
        sz = struct.pack('>H', len(data))
        return self.request.sendall(sz + data)


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


def run():

    server_threads = []

    socketserver.ThreadingUDPServer.allow_reuse_address = True
    server_threads.append(socketserver.ThreadingUDPServer(
        ('', SERVER_PORT), UDPRequestHandler))
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    server_threads.append(socketserver.ThreadingTCPServer(
        ('', SERVER_PORT), TCPRequestHandler))

    for server_thread in server_threads:
        thread = threading.Thread(target=server_thread.serve_forever)
        thread.daemon = True
        thread.start()

    logging.info('Listening on %s for connections.' % SERVER_PORT)
    signal.pause()


if __name__ == '__main__':
    run()
