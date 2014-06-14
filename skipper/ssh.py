import contextlib
from sshtunnel import SSHTunnelForwarder


@contextlib.contextmanager
def docker_tunnel(instance):
    server = SSHTunnelForwarder(**instance.tunnel_params)
    server.start()
    try:
        yield server.local_bind_port
    finally:
        server.stop()
