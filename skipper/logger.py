import logging
import json
import sys

console = logging.StreamHandler()

log = logging.getLogger('skipper')
log.setLevel(logging.INFO)
log.addHandler(console)
log.propagate = False


class EventError(Exception):
    pass


def capture_events(stream):
    """
    Prints out the output from various Docker client commands.
    A stripped down version of Fig's `stream_output`
    """
    events = []
    previous = None
    for line in stream:
        try:
            line = json.loads(line)
            if line.get('stream'):
                log.info(line['stream'].replace('\n', ''))
                events.append(line['stream'])
            elif 'progressDetail' in line:
                if previous != line['status']:
                    log.info(line['status'])
                    previous = line['status']
            elif line.get('status'):
                log.info(line['status'])
            elif line.get('errorDetail'):
                raise EventError(line.get('errorDetail').get('message'))
        except ValueError as e:
            log.debug(e)
    return events
