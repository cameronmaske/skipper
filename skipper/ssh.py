from logger import log

import contextlib
import SocketServer
import select
import threading
import paramiko


@contextlib.contextmanager
def ssh_tunnel(params):
    server = SSHTunnelForwarder(**params)
    server.start()
    try:
        yield server.local_bind_port
    finally:
        server.stop()


# Taken from pahaz's sshtunnel.
# https://github.com/pahaz/sshtunnel/blob/master/LICENSE
class SSHTunnelError(Exception):
    pass


class BaseHandler(SocketServer.BaseRequestHandler):
    remote_address = None
    ssh_transport = None
    logger = None

    def handle(self):
        assert isinstance(self.remote_address, tuple)

        try:
            chan = self.ssh_transport.open_channel(
                'direct-tcpip',
                self.remote_address,
                self.request.getpeername())
        except Exception as e:
            m = 'Incoming request failed: {0}'.format(repr(e))
            self.logger.error(m)
            raise SSHTunnelError(m)

        if chan is None:
            m = 'Incoming request was rejected'
            self.logger.error(m)
            raise SSHTunnelError(m)

        self.logger.debug('Connected! Tunnel open.')
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)
        chan.close()
        self.request.close()
        self.logger.debug('Tunnel closed.')


class ThreadingForwardServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    daemon_threads = False
    allow_reuse_address = True

    @property
    def bind_port(self):
        return self.socket.getsockname()[1]

    @property
    def bind_host(self):
        return self.socket.getsockname()[0]


def make_ssh_forward_server(_remote_address, _local_bind_address, _ssh_transport):
    """
    Makes an SSH forward proxy Server class.
    """

    class SubHander(BaseHandler):
        remote_address = _remote_address
        ssh_transport = _ssh_transport
        logger = log

    server = ThreadingForwardServer(_local_bind_address, SubHander)
    return server


class SSHTunnelForwarder(threading.Thread):
    """
    Class for forward remote server port throw SSH tunnel to local port.

     - start()
     - stop()
     - local_bind_port
     - local_bind_host

    Example:
    >>> server = SSHTunnelForwarder(
        ssh_address=('pahaz.urfuclub.ru', 22),
        ssh_username="pahaz",
        ssh_password="secret",
        remote_bind_address=('127.0.0.1', 5555))
    >>> server.start()
    >>> print(server.local_bind_port)
    >>> server.stop()
    """

    def __init__(self,
                 ssh_address=None,
                 ssh_host_key=None,
                 ssh_username=None,
                 ssh_password=None,
                 ssh_private_key=None,
                 remote_bind_address=None,
                 local_bind_address=None,
                 threaded=True):
        """
        Remote and local address take the form: (host, port)
        """
        assert isinstance(remote_bind_address, tuple)

        if local_bind_address is None:
            # Use random local port
            local_bind_address = ('', 0)

        self._local_bind_address = local_bind_address
        self._remote_bind_address = remote_bind_address
        self._ssh_private_key = ssh_private_key
        self._ssh_password = ssh_password
        self._ssh_username = ssh_username
        self._ssh_host_key = ssh_host_key

        self._transport = paramiko.Transport(ssh_address)
        self._server = make_ssh_forward_server(
            self._remote_bind_address,
            self._local_bind_address,
            self._transport,
        )
        self._is_started = False
        super(SSHTunnelForwarder, self).__init__()

    def start(self):
        self._transport.connect(
            hostkey=self._ssh_host_key,
            username=self._ssh_username,
            password=self._ssh_password,
            pkey=self._ssh_private_key)
        super(SSHTunnelForwarder, self).start()
        self._is_started = True

    def run(self):
        self._server.serve_forever()

    def stop(self):
        if not self._is_started:
            m = "Server don't started! Please .start() first!"
            raise SSHTunnelError(m)
        self._server.shutdown()
        self._transport.close()

    @property
    def local_bind_port(self):
        if not self._is_started:
            m = "Server don't started! Please .start() first!"
            raise SSHTunnelError(m)
        return self._server.bind_port

    @property
    def local_bind_host(self):
        if not self._is_started:
            m = "Server don't started! Please .start() first!"
            raise SSHTunnelError(m)
        return self._server.bind_host

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
