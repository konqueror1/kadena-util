import requests
import socket
from clint.textui import colored, puts
from clint.textui import progress
from geolite2 import geolite2
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_peer_list(old_list_with_heights):
    sort_order = {(h, p): i for i, (h, p, ht)
                  in enumerate(sorted(old_list_with_heights, key=lambda t: -t[-1] if t[-1] is not None else 0))}
    def sort_func(t):
        if t in sort_order:
            return sort_order[t]
        else:
            return len(sort_order)

    items = requests.get('https://us-e2.chainweb.com/chainweb/0.0/mainnet01/cut/peer').json()['items']
    items = [(host['address']['hostname'], host['address']['port'])
             for host in items]
    items.sort(key=sort_func)
    return items

def get_peer_height(host, port):
    height = None
    try:
        height = requests.get(
            'https://%s:%s/chainweb/0.0/mainnet01/cut/' % (host, port),
            verify=False, timeout=3).json()['height'] // 10
    except KeyboardInterrupt as e:
        raise e
    except:
        return None
    return height

def host2ip(host):
    try:
        ip = socket.gethostbyname(host)
    except:
        ip = '127.0.0.1'
    return ip

def main():
    last_host_list = []

    while True:
        new_host_list = []

        all_peers = get_peer_list(last_host_list)
        with progress.Bar(label="Fetching data", expected_size=len(all_peers)) as bar:
            for i, (host, port) in enumerate(get_peer_list(last_host_list)):
                height = get_peer_height(host, port)
                new_host_list.append((host, port, height))
                bar.show(i)

        new_host_list = sorted(new_host_list, key=lambda t: -t[-1] if t[-1] is not None else 0)

        last_host_list = new_host_list

        for (host, port, height) in new_host_list:

            reader = geolite2.reader()
            match = reader.get(host2ip(host))
            if match is not None:
              if 'country' in match:
                country = match['country']['iso_code']
              elif 'continent' in match:
                country = match['continent']['code']
            else:
                country = "??"

            print("%3s %30s %6s %7s" %(country, host, port, height if height is not None else "??????"))

if __name__ == "__main__":
    main()
