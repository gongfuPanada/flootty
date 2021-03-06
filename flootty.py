#!/usr/bin/env python

# Heavily influenced by the work of Joshua D. Bartlett
# see: http://sqizit.bartletts.id.au/2011/02/14/pseudo-terminals-in-python/
# original copyright
# Copyright (c) 2011 Joshua D. Bartlett
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import atexit
import fcntl
import json
import optparse
import array
import os
import pty
import select
import socket
import ssl
import sys
import tempfile
import termios
import tty
import signal
import time
import re
from collections import defaultdict

try:
    from urllib.parse import urlparse
    assert urlparse
except ImportError:
    from urlparse import urlparse


CA_CERT = '''-----BEGIN CERTIFICATE-----
MIIHyTCCBbGgAwIBAgIBATANBgkqhkiG9w0BAQUFADB9MQswCQYDVQQGEwJJTDEW
MBQGA1UEChMNU3RhcnRDb20gTHRkLjErMCkGA1UECxMiU2VjdXJlIERpZ2l0YWwg
Q2VydGlmaWNhdGUgU2lnbmluZzEpMCcGA1UEAxMgU3RhcnRDb20gQ2VydGlmaWNh
dGlvbiBBdXRob3JpdHkwHhcNMDYwOTE3MTk0NjM2WhcNMzYwOTE3MTk0NjM2WjB9
MQswCQYDVQQGEwJJTDEWMBQGA1UEChMNU3RhcnRDb20gTHRkLjErMCkGA1UECxMi
U2VjdXJlIERpZ2l0YWwgQ2VydGlmaWNhdGUgU2lnbmluZzEpMCcGA1UEAxMgU3Rh
cnRDb20gQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwggIiMA0GCSqGSIb3DQEBAQUA
A4ICDwAwggIKAoICAQDBiNsJvGxGfHiflXu1M5DycmLWwTYgIiRezul38kMKogZk
pMyONvg45iPwbm2xPN1yo4UcodM9tDMr0y+v/uqwQVlntsQGfQqedIXWeUyAN3rf
OQVSWff0G0ZDpNKFhdLDcfN1YjS6LIp/Ho/u7TTQEceWzVI9ujPW3U3eCztKS5/C
Ji/6tRYccjV3yjxd5srhJosaNnZcAdt0FCX+7bWgiA/deMotHweXMAEtcnn6RtYT
Kqi5pquDSR3l8u/d5AGOGAqPY1MWhWKpDhk6zLVmpsJrdAfkK+F2PrRt2PZE4XNi
HzvEvqBTViVsUQn3qqvKv3b9bZvzndu/PWa8DFaqr5hIlTpL36dYUNk4dalb6kMM
Av+Z6+hsTXBbKWWc3apdzK8BMewM69KN6Oqce+Zu9ydmDBpI125C4z/eIT574Q1w
+2OqqGwaVLRcJXrJosmLFqa7LH4XXgVNWG4SHQHuEhANxjJ/GP/89PrNbpHoNkm+
Gkhpi8KWTRoSsmkXwQqQ1vp5Iki/untp+HDH+no32NgN0nZPV/+Qt+OR0t3vwmC3
Zzrd/qqc8NSLf3Iizsafl7b4r4qgEKjZ+xjGtrVcUjyJthkqcwEKDwOzEmDyei+B
26Nu/yYwl/WL3YlXtq09s68rxbd2AvCl1iuahhQqcvbjM4xdCUsT37uMdBNSSwID
AQABo4ICUjCCAk4wDAYDVR0TBAUwAwEB/zALBgNVHQ8EBAMCAa4wHQYDVR0OBBYE
FE4L7xqkQFulF2mHMMo0aEPQQa7yMGQGA1UdHwRdMFswLKAqoCiGJmh0dHA6Ly9j
ZXJ0LnN0YXJ0Y29tLm9yZy9zZnNjYS1jcmwuY3JsMCugKaAnhiVodHRwOi8vY3Js
LnN0YXJ0Y29tLm9yZy9zZnNjYS1jcmwuY3JsMIIBXQYDVR0gBIIBVDCCAVAwggFM
BgsrBgEEAYG1NwEBATCCATswLwYIKwYBBQUHAgEWI2h0dHA6Ly9jZXJ0LnN0YXJ0
Y29tLm9yZy9wb2xpY3kucGRmMDUGCCsGAQUFBwIBFilodHRwOi8vY2VydC5zdGFy
dGNvbS5vcmcvaW50ZXJtZWRpYXRlLnBkZjCB0AYIKwYBBQUHAgIwgcMwJxYgU3Rh
cnQgQ29tbWVyY2lhbCAoU3RhcnRDb20pIEx0ZC4wAwIBARqBl0xpbWl0ZWQgTGlh
YmlsaXR5LCByZWFkIHRoZSBzZWN0aW9uICpMZWdhbCBMaW1pdGF0aW9ucyogb2Yg
dGhlIFN0YXJ0Q29tIENlcnRpZmljYXRpb24gQXV0aG9yaXR5IFBvbGljeSBhdmFp
bGFibGUgYXQgaHR0cDovL2NlcnQuc3RhcnRjb20ub3JnL3BvbGljeS5wZGYwEQYJ
YIZIAYb4QgEBBAQDAgAHMDgGCWCGSAGG+EIBDQQrFilTdGFydENvbSBGcmVlIFNT
TCBDZXJ0aWZpY2F0aW9uIEF1dGhvcml0eTANBgkqhkiG9w0BAQUFAAOCAgEAFmyZ
9GYMNPXQhV59CuzaEE44HF7fpiUFS5Eyweg78T3dRAlbB0mKKctmArexmvclmAk8
jhvh3TaHK0u7aNM5Zj2gJsfyOZEdUauCe37Vzlrk4gNXcGmXCPleWKYK34wGmkUW
FjgKXlf2Ysd6AgXmvB618p70qSmD+LIU424oh0TDkBreOKk8rENNZEXO3SipXPJz
ewT4F+irsfMuXGRuczE6Eri8sxHkfY+BUZo7jYn0TZNmezwD7dOaHZrzZVD1oNB1
ny+v8OqCQ5j4aZyJecRDjkZy42Q2Eq/3JR44iZB3fsNrarnDy0RLrHiQi+fHLB5L
EUTINFInzQpdn4XBidUaePKVEFMy3YCEZnXZtWgo+2EuvoSoOMCZEoalHmdkrQYu
L6lwhceWD3yJZfWOQ1QOq92lgDmUYMA0yZZwLKMS9R9Ie70cfmu3nZD0Ijuu+Pwq
yvqCUqDvr0tVk+vBtfAii6w0TiYiBKGHLHVKt+V9E9e4DGTANtLJL4YSjCMJwRuC
O3NJo2pXh5Tl1njFmUNj403gdy3hZZlyaQQaRwnmDwFWJPsfvw55qVguucQJAX6V
um0ABj6y6koQOdjQK/W/7HW/lwLFCRsI3FU34oH7N4RDYiDK51ZLZer+bMEkkySh
NOsF/5oirpt9P/FlUQqmMGqz9IgcgA38corog14=
-----END CERTIFICATE-----'''

PROTO_VERSION = '0.02'
CLIENT = 'flootty'
INITIAL_RECONNECT_DELAY = 1000
FD_READ_BYTES = 4096
TIMEOUTS = defaultdict(list)
SELECT_TIMEOUT = 0.2
# in secs
NET_TIMEOUT = 10


def set_timeout(func, timeout=None, *args, **kwargs):
    if timeout is None:
        timeout = 0
    then = time.time() + (timeout / 1000.0)
    TIMEOUTS[then].append(lambda: func(*args, **kwargs))


def call_timeouts():
    now = time.time()
    to_remove = []
    for t, timeouts in TIMEOUTS.items():
        if now >= t:
            for timeout in timeouts:
                timeout()
            to_remove.append(t)
    for k in to_remove:
        del TIMEOUTS[k]


def read_floorc():
    settings = {}
    p = os.path.expanduser('~/.floorc')
    try:
        fd = open(p, 'rb')
    except IOError as e:
        if e.errno == 2:
            return settings
        raise
    data = fd.read().decode('utf-8')
    fd.close()
    for line in data.split('\n'):
        position = line.find(' ')
        if position < 0:
            continue
        settings[line[:position]] = line[position + 1:]
    return settings


def write(fd, b):
    while len(b):
        try:
            # TODO: fix this for python3
            n = os.write(fd, b)
            b = b[n:]
        except (IOError, OSError):
            pass


def read(fd):
    buf = ''
    while True:
        try:
            d = os.read(fd, FD_READ_BYTES)
            if not d or d == '':
                break
            buf += d
        except (IOError, OSError):
            break
    return buf


def out(*args):
    buf = "%s\r\n" % " ".join(args)
    write(pty.STDOUT_FILENO, buf)


def err(*args):
    buf = "%s\r\n" % " ".join(args)
    write(pty.STDERR_FILENO, buf)


def die(*args):
    err(*args)
    sys.exit(1)


def parse_url(room_url):
    secure = True
    owner = None
    room_name = None
    parsed_url = urlparse(room_url)
    port = parsed_url.port
    if not port:
        port = 3448
    if parsed_url.scheme == 'http':
        if not port:
            port = 3148
        secure = False
    result = re.match('^/r/([-\w]+)/([-\w]+)/?$', parsed_url.path)
    if result:
        (owner, room_name) = result.groups()
    else:
        raise ValueError('%s is not a valid Floobits URL' % room_url)
    return {
        'host': parsed_url.hostname,
        'owner': owner,
        'port': port,
        'room': room_name,
        'secure': secure,
    }


def main():
    settings = read_floorc()
    usage = "usage: %prog  --workspace=WORKSPACE --owner=OWNER [options] term_name.\n\n\tSee https://github.com/Floobits/flootty"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-u", "--username",
                      dest="username",
                      default=settings.get('username'),
                      help="Your Floobits username")

    parser.add_option("-s", "--secret",
                      dest="secret",
                      default=settings.get('secret'),
                      help="Your Floobits secret (api key)")

    parser.add_option("--host",
                      dest="host",
                      default="floobits.com",
                      help="The host to connect to")

    parser.add_option("-p", "--port",
                      dest="port",
                      default=3448,
                      help="The port to connect to")

    parser.add_option("-c", "--create",
                      dest="create",
                      default=False,
                      action="store_true",
                      help="The terminal name to create")

    parser.add_option("-w", "--workspace",
                      dest="room",
                      help="The workspace name")

    parser.add_option("-o", "--owner",
                      dest="owner",
                      help="The workspace owner")

    parser.add_option("-l", "--list",
                      dest="list",
                      default=False,
                      action="store_true",
                      help="List all ptys in the workspace")

    parser.add_option("--no-ssl",
                      dest="use_ssl",
                      default=True,
                      action="store_false",
                      help="Do not use this option unless you know what you are doing!")

    parser.add_option("--url",
                      dest="room_url",
                      default=None,
                      help="The URL of the workspace to connect to. This is a convenience for copy-pasting from the browser.")

    options, args = parser.parse_args()

    default_term_name = ""
    if options.create:
        default_term_name = "_"

    term_name = args and args[0] or default_term_name

    if options.room and options.owner and options.room_url:
        parser.error("You can either specify --workspace and --owner, or --url, but not both.")

    if not options.room or not options.owner:
        floo = {}
        if options.room_url:
            floo = parse_url(options.room_url)
        else:
            for floo_path in walk_up(os.path.realpath('.')):
                try:
                    floo = json.loads(open(os.path.join(floo_path, '.floo'), 'rb').read().decode('utf-8'))
                    floo = parse_url(floo['url'])
                except Exception:
                    pass
        options.room = floo.get('room')
        options.owner = floo.get('owner')
        if not options.port:
            options.port = floo.get('port')
        if not options.host:
            options.host = floo.get('host')

    if options.list:
        if len(term_name) != 0:
            die("I don't understand why you gave me a positional argument.")

    for opt in ['room', 'owner', 'username', 'secret']:
        if not getattr(options, opt):
            parser.error('%s not given' % opt)

    f = Flootty(options, term_name)
    atexit.register(f.cleanup)
    f.connect_to_internet()


def walk_up(path):
    step_up = lambda x: os.path.realpath(os.path.join(x, '..'))
    parent = step_up(path)
    while parent != path:
        yield path
        path = parent
        parent = step_up(path)
    yield path


class FD(object):
    def __init__(self, fileno, reader=None, writer=None, errer=None, name=None):
        self.fileno = fileno
        self.reader = reader
        self.writer = writer
        self.errer = errer
        self.name = name

    def __getitem__(self, key):
        return getattr(self, key, None)

    def __str__(self):
        return str(self.name)


class Flootty(object):
    '''Mostly OK at sharing a shell'''

    def __init__(self, options, term_name):
        self.master_fd = None
        self.original_wincher = None
        self.fds = {}
        self.readers = set()
        self.writers = set()
        self.errers = set()
        self.empty_selects = 0

        self.buf_out = []
        self.buf_in = ''

        self.host = options.host
        self.port = int(options.port)
        self.room = options.room
        self.owner = options.owner
        self.options = options
        self.term_name = term_name

        self.authed = False
        self.term_id = None
        self.orig_stdin_atts = None
        self.orig_stdout_atts = None

    def add_fd(self, fileno, **kwargs):
        try:
            fileno = fileno.fileno()
        except:
            fileno = fileno
        fd = FD(fileno, **kwargs)

        self.fds[fileno] = fd
        if fd.reader:
            self.readers.add(fileno)
        if fd.writer:
            self.writers.add(fileno)
        if fd.errer:
            self.errers.add(fileno)

    def transport(self, name, data):
        data['name'] = name
        self.buf_out.append(data)

    def select(self):
        '''
        '''
        attrs = ('errer', 'reader', 'writer')

        while True:
            call_timeouts()

            if len(self.buf_out) == 0:
                self.writers.remove(self.sock.fileno())
            try:
                # NOTE: you will never have to write anything without reading first from a different one
                _in, _out, _except = select.select(self.readers, self.writers, self.errers, SELECT_TIMEOUT)
            except (IOError, OSError) as e:
                continue
            except (select.error, socket.error, Exception) as e:
                # Interrupted system call.
                if e[0] == 4:
                    continue
                err('Error in select(): %s' % str(e))
                return self.reconnect()
            finally:
                self.writers.add(self.sock.fileno())

            for position, fds in enumerate([_except, _in, _out]):
                attr = attrs[position]
                for fd in fds:
                    handler = self.fds[fd][attr]
                    if handler:
                        handler(fd)
                    else:
                        raise Exception('no handler for fd: %s %s' % (fd, attr))

    def cloud_read(self, fd):
        buf = ''
        while True:
            try:
                d = self.sock.recv(FD_READ_BYTES)
                if not d:
                    break
                buf += d
            except (socket.error, TypeError):
                break
        if buf:
            self.empty_selects = 0
            self.handle(buf)
        else:
            self.empty_selects += 1
            if (int(self.empty_selects * SELECT_TIMEOUT)) > NET_TIMEOUT:
                err('No data from sock.recv() {0} times.'.format(self.empty_selects))
                return self.reconnect()

    def cloud_write(self, fd):
        while True:
            try:
                item = self.buf_out.pop(0)
                self.sock.sendall((json.dumps(item) + '\n').encode('utf-8'))
            except IndexError:
                break

    def cloud_err(self, err):
        out('reconnecting because of %s' % err)
        self.reconnect()

    def handle(self, req):
        self.buf_in += req
        while True:
            before, sep, after = self.buf_in.partition('\n')
            if not sep:
                break
            try:
                data = json.loads(before, encoding='utf-8')
            except Exception as e:
                out('Unable to parse json: %s' % str(e))
                raise e
            self.handle_event(data)
            self.buf_in = after

    def handle_event(self, data):
        name = data.get('name')
        if not name:
            return out('no name in data?!?')
        func = getattr(self, "on_%s" % (name), None)
        if not func:
            #out('unknown name %s data: %s' % (name, data))
            return
        func(data)

    def on_room_info(self, ri):
        self.authed = True
        self.ri = ri
        if self.options.create:
            buf = self._get_pty_size()
            return self.transport('create_term', {'term_name': self.term_name, 'size': [buf[1], buf[0]]})
        elif self.options.list:
            out('Terminals in %s::%s' % (self.owner, self.room))
            for term_id, term in ri['terms'].items():
                owner = str(term['owner'])
                out('terminal %s created by %s' % (term['term_name'], ri['users'][owner]))
            return die()
        elif not self.term_name:
            if len(ri['terms']) == 0:
                out('There is no active terminal in this workspace. Do you want to share your terminal? (y/n)')
                choice = raw_input().lower()
                self.term_name = "_"
                if choice == 'y':
                    self.options.create = True
                    buf = self._get_pty_size()
                    return self.transport('create_term', {'term_name': self.term_name, 'size': [buf[1], buf[0]]})
                else:
                    die('If you ever change your mind, you can share your terminal using the --create [super_awesome_name] flag.')
            elif len(ri['terms']) == 1:
                term_id, term = ri['terms'].items()[0]
                self.term_id = int(term_id)
                self.term_name = term['term_name']
            else:
                out('More than one active term exists in this workspace.')
                for term_id, term in ri['terms'].items():
                    owner = str(term['owner'])
                    out('terminal %s created by %s' % (term['term_name'], ri['users'][owner]))
                    die('Please pick a workspace like so: flootty [super_awesome_name]')
        else:
            for term_id, term in ri['terms'].items():
                if term['term_name'] == self.term_name:
                    self.term_id = int(term_id)
                    break

        if self.term_id is None:
            die('No terminal with name %s' % self.term_name)
        return self.join_term()

    def on_disconnect(self, data):
        die('You were disconnected because: %s.' % data.get('reason', '').lower())

    def on_error(self, data):
        if self.term_id is None:
            die(data.get('msg'))
        else:
            out('Error from server: %s' % data.get('msg'))

    def on_create_term(self, data):
        if data.get('term_name') != self.term_name:
            return
        self.term_id = data.get('id')
        self.create_term()

    def on_delete_term(self, data):
        if data.get('id') != self.term_id:
            return
        die('User %s killed the terminal. Exiting.' % (data.get('username')))

    def on_update_term(self, data):
        if data.get('id') != self.term_id:
            return
        self._set_pty_size()

    def on_term_stdin(self, data):
        if data.get('id') != self.term_id:
            return
        if not self.options.create:
            return
        self.handle_stdio(data['data'])

    def on_term_stdout(self, data):
        if data.get('id') != self.term_id:
            return
        self.handle_stdio(data['data'])

    def reconnect(self):
        die('not reconnecting.')

    def send_auth(self):
        self.buf_out = []
        self.transport('auth', {
            'username': self.options.username,
            'secret': self.options.secret,
            'room': self.room,
            'room_owner': self.owner,
            'client': CLIENT,
            'platform': sys.platform,
            'version': PROTO_VERSION
        })

    def connect_to_internet(self):
        self.empty_selects = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.options.use_ssl:
            self.cert_fd = tempfile.NamedTemporaryFile()
            self.cert_fd.write(CA_CERT.encode('utf-8'))
            self.cert_fd.flush()
            self.sock = ssl.wrap_socket(self.sock, ca_certs=self.cert_fd.name, cert_reqs=ssl.CERT_REQUIRED)
        elif self.port == 3448:
            self.port = 3148
        out('Connecting to %s:%s.' % (self.host, self.port))
        try:
            self.sock.connect((self.host, self.port))
            if self.options.use_ssl:
                self.sock.do_handshake()
        except socket.error as e:
            out('Error connecting: %s.' % e)
            self.reconnect()
        self.sock.setblocking(0)
        out('Connected!')
        self.send_auth()
        self.add_fd(self.sock, reader=self.cloud_read, writer=self.cloud_write, errer=self.cloud_err, name='net')
        self.reconnect_delay = INITIAL_RECONNECT_DELAY
        self.select()

    def room_url(self):
        proto = {True: "https", False: "http"}
        proto_str = proto[self.options.use_ssl]
        port_str = ''
        if self.options.use_ssl:
            if self.port != 3448:
                port_str = ':%s' % self.port
        else:
            if self.port != 3148:
                port_str = ':%s' % self.port
        return '%s://%s%s/r/%s/%s/' % (proto_str, self.host, port_str, self.owner, self.room)

    def join_term(self):
        out('Successfully joined %s' % (self.room_url()))
        self.orig_stdout_atts = tty.tcgetattr(sys.stdout)
        stdout = sys.stdout.fileno()
        tty.setraw(stdout)
        fl = fcntl.fcntl(stdout, fcntl.F_GETFL)
        fcntl.fcntl(stdout, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self.orig_stdin_atts = tty.tcgetattr(sys.stdin)
        stdin = sys.stdin.fileno()
        tty.setraw(stdin)
        fl = fcntl.fcntl(stdin, fcntl.F_GETFL)
        fcntl.fcntl(stdin, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        def ship_stdin(fd):
            data = read(fd)
            if data:
                self.transport("term_stdin", {'data': data, 'id': self.term_id})

        if 'term_stdin' in self.ri['perms']:
            out('You have permission to write to this terminal. Remember: With great power comes great responsibility.')
            self.add_fd(stdin, reader=ship_stdin, name='join_term_stdin')
        else:
            out('You do not have permission to write to this terminal.')

        def stdout_write(buf):
            write(stdout, buf.encode('utf-8'))

        self.handle_stdio = stdout_write
        self._set_pty_size(self.ri['terms'][str(self.term_id)]['size'])

    def create_term(self):
        '''
        Create a spawned process.
        Based on the code for pty.spawn().
        '''
        out('Successfully joined %s' % (self.room_url()))

        assert self.master_fd is None
        shell = os.environ['SHELL']

        self.child_pid, self.master_fd = pty.fork()
        if self.child_pid == pty.CHILD:
            os.execlp(shell, shell, '--login')

        self.orig_stdin_atts = tty.tcgetattr(sys.stdin)
        tty.setraw(pty.STDIN_FILENO)
        self.original_wincher = signal.signal(signal.SIGWINCH, self._signal_winch)
        self._set_pty_size()

        def slave_death(fd):
            die('Exiting flootty because child exited.')

        self.extra_data = ''

        def stdout_write(fd):
            '''
            Called when there is data to be sent from the child process back to the user.
            '''
            data = self.extra_data + os.read(fd, FD_READ_BYTES)
            self.extra_data = ""
            if data:
                while True:
                    try:
                        data.decode('utf-8')
                    except UnicodeDecodeError:
                        self.extra_data = data[-1] + self.extra_data
                        data = data[:-1]
                    else:
                        break
                    if len(self.extra_data) > 100:
                        die('not a valid utf-8 string: %s' % self.extra_data)
                if data:
                    self.transport("term_stdout", {'data': data, 'id': self.term_id})
                    write(pty.STDOUT_FILENO, data)

        self.add_fd(self.master_fd, reader=stdout_write, errer=slave_death, name='create_term_stdout_write')

        def stdin_write(fd):
            data = os.read(fd, FD_READ_BYTES)
            if data:
                write(self.master_fd, data)
                self.transport("term_stdin", {'data': data, 'id': self.term_id})

        self.add_fd(pty.STDIN_FILENO, reader=stdin_write, name='create_term_stdin_write')

        def net_stdin_write(buf):
            write(self.master_fd, buf)

        self.handle_stdio = net_stdin_write
        color_start = '\\[\\e[32m\\]'
        color_reset = '\\[\\033[0m\\]'

        # TODO: other shells probably use weird color escapes
        if 'zsh' in shell:
            color_start = "%{%F{green}%}"
            color_reset = ""

        set_prompt_command = 'PS1="%s%s::%s::%s%s $PS1"\n' % (color_start, self.owner, self.room, self.term_name, color_reset)
        net_stdin_write(set_prompt_command)

    def _signal_winch(self, signum, frame):
        '''
        Signal handler for SIGWINCH - window size has changed.
        '''
        self._set_pty_size()

    def _get_pty_size(self):
        buf = array.array('h', [0, 0, 0, 0])
        fcntl.ioctl(pty.STDOUT_FILENO, termios.TIOCGWINSZ, buf, True)
        return buf

    def _set_pty_size(self, size=None):
        '''
        Sets the window size of the child pty based on the window size of our own controlling terminal.
        '''
        # Get the terminal size of the real terminal, set it on the pseudoterminal.
        buf = self._get_pty_size()
        if size:
            buf[0] = size[1]
            buf[1] = size[0]

        if self.options.create:
            assert self.master_fd is not None
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, buf)
            if self.term_id:
                self.transport('update_term', {'id': self.term_id, 'size': [buf[1], buf[0]]})
        else:
            # XXXX: this resizes the window :/
            #os.write(pty.STDOUT_FILENO, "\x1b[8;{rows};{cols}t".format(rows=buf[0], cols=buf[1]))
            fcntl.ioctl(pty.STDOUT_FILENO, termios.TIOCSWINSZ, buf)

    def cleanup(self):
        if self.orig_stdout_atts:
            self.orig_stdout_atts[3] = self.orig_stdout_atts[3] | termios.ECHO
            tty.tcsetattr(sys.stdout, tty.TCSAFLUSH, self.orig_stdout_atts)
        if self.orig_stdin_atts:
            self.orig_stdin_atts[3] = self.orig_stdin_atts[3] | termios.ECHO
            tty.tcsetattr(sys.stdin, tty.TCSAFLUSH, self.orig_stdin_atts)
        if self.original_wincher:
            signal.signal(signal.SIGWINCH, self.original_wincher)
        try:
            self.cert_fd.close()
        except Exception:
            pass
        print('ciao.')
        sys.exit()

if __name__ == '__main__':
    main()
