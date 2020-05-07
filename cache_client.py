import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
from node_ring import NodeRing
from LRUCache import LRUCache
from bloomfilter import BloomFilter
BUFFER_SIZE = 1024
lru_get = None
lru_put = None
lru_delete = None
bloomfilter = BloomFilter(1000,0.001)

class UDPClient():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

    def send(self, request):
        print('Connecting to server at {}:{}'.format(self.host, self.port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(request, (self.host, self.port))
            response, ip = s.recvfrom(BUFFER_SIZE)
            return response
        except socket.error:
            print("Error! {}".format(socket.error))
            exit()


def lru_cache(size=2):
    def inner(func):
        def wrapper(*args, **kwargs):
            if func.__name__  == 'get':
                global lru_get
                if lru_get is None:
                    lru_get = LRUCache(size)
                if args[0] in lru_get.dictCache:
                    return lru_get[args[0]]
                else:
                    out = func(*args, **kwargs)
                    lru_get[args[0]] = out
                    return out
                pass
            elif func.__name__ == 'put':
                global lru_put
                if lru_put is None:
                    lru_put = LRUCache(size)
                hashCode = serialize_PUT(args[0])[1]
                if hashCode in lru_put.dictCache:
                    return lru_put[hashCode]
                else:
                    out = func(*args, **kwargs)
                    lru_put[hashCode] = out
                    return out
            elif func.__name__ == 'delete':
                global lru_delete
                if lru_delete is None:
                    lru_delete = LRUCache(size)
                if args[0] in lru_delete.dictCache:
                    return lru_delete[args[0]]
                else:
                    out = func(*args, **kwargs)
                    lru_delete[args[0]] = out
                    return out
            else:
                pass
            return func(*args, **kwargs)
        return wrapper

    return inner

@lru_cache(5)
def get(id, clientRing):
    data, key = serialize_GET(id)
    if bloomfilter.is_member(key):
        return clientRing.get_node(key).send(data)
    else:
        return None


@lru_cache(5)
def put(object, clientRing):
    data, key = serialize_PUT(object)
    bloomfilter.add(key)
    return clientRing.get_node(key).send(data)


@lru_cache(5)
def delete(id, clientRing):
    data, key = serialize_DELETE(id)
    if bloomfilter.is_member(key):
        return clientRing.get_node(key).send(data)
    else:
        return None


def process(udp_clients):
    client_ring = NodeRing(udp_clients)
    hash_codes = set()
    # PUT all users.
    for u in USERS:
        response = put(u,client_ring)
        print(response)
        hash_codes.add(str(response.decode()))

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    # GET all users.
    for i in range(0,3):
        for hc in hash_codes:
            print(hc)
            response = get(hc,client_ring)
            print(response)

    for hc in hash_codes:
        out = delete(hc,client_ring)
        print(out)

    for hc in hash_codes:
        print(hc)
        response = get(hc, client_ring)
        print(response)


if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ]
    process(clients)
