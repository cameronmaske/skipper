import contextlib
from click.exceptions import ClickException


class ServiceException(Exception):
    pass


class NoSuchService(ServiceException):
    pass


class RepoException(Exception):
    pass


class RepoNoPermission(RepoException):
    pass


class RepoNotFound(RepoException):
    pass


class cli_exceptions(object):
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc, value, traceback):
        raise ClickException(traceback)

@contextlib.contextmanager
def cli_exceptions():
    """
    For use in cli functions. Helps to dry up exception
    handling.

    with cli_exceptions:
        run(...)

    """
    try:
        yield
    except (RepoException, ServiceException) as e:
        raise ClickException(e.message)
