#!/usr/bin/env python
# -*- coding: utf-8 -*-

# made by vaxquis

from __future__ import print_function

import json
import tslib
import six

from ansicolor import green, red, white
from signalfx import signalflow

from . import utils


class EventsOutputDisplay(object):
    _DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z (%z)'

    def __init__(self, computation, tz, start):
        self._computation = computation
        self._tz = tz
        self._last_hour = start
        self._last_day = -1

    def _render_date(self, date):
        return (date.astimezone(self._tz)
                .strftime(EventsOutputDisplay._DATE_FORMAT))

    def _render_event(self, event):
        """Render the latest events emitted by the computation.
        """
        def maybe_json(v):
            return json.loads(v) if isinstance(v, six.string_types) else v

        ets = self._computation.get_metadata(event.tsid)
        contexts = json.loads(ets.get('sf_detectInputContexts', '{}'))

        values = maybe_json(event.properties.get('inputs', '{}'))
        values = ' | '.join([
            u'{name} ({key}): {value}'.format(
                name=white(contexts[k].get('identifier', k)),
                key=','.join([u'{0}:{1}'.format(dim_name, dim_value)
                              for dim_name, dim_value
                              in v.get('key', {}).items()]),
                value=v['value'])
            for k, v in values.items()])

        date = tslib.date_from_utc_ts(event.timestamp_ms)
        is_now = event.properties['is']

        print(u'\n {mark} {date} [{incident}]: {values}'
              .format(mark=green('*') if is_now == 'ok' else red('!'),
                      date=white(self._render_date(date), bold=True),
                      incident=event.properties['incidentId'],
                      values=values))

    def stream(self):
        try:
            for message in self._computation.stream():
                if isinstance(message, signalflow.messages.JobStartMessage):
                    utils.message('job started; waiting for data... ')
                elif isinstance(message, signalflow.messages.JobProgressMessage):
                    utils.message('{0}% '.format(message.progress))
                    if message.progress == 100:
                        utils.message('\n')
                elif isinstance(message, signalflow.messages.EventMessage):
                    self._render_event(message)
                elif isinstance(message, signalflow.messages.DataMessage):
                    if not message.data.items():
                        msg = red('X')
                    else:
                        ts = message.logical_timestamp_ms
                        if ts > self._last_hour + 60 * 60 * 1000:
                            self._last_hour = ts
                            msg = white('-')
                        else:
                            msg = '.'
                        if ts > self._last_day + 24 * 60 * 60 * 1000:
                            self._last_day = ts
                            date = tslib.date_from_utc_ts(ts)
                            print(u'\n {date}'.format(date=white(self._render_date(date), bold=True)))
                    utils.message(msg)
        except KeyboardInterrupt:
            pass
        finally:
            self._computation.close()
            print('')

def stream(flow, tz, program, start, stop, resolution, max_delay):
    """Execute a streaming SignalFlow computation and display the events.

    :param flow: An open SignalFlow client connection.
    :param tz: A pytz timezone for date and time representations.
    :param program: The program to execute.
    :param start: The absolute start timestamp, in milliseconds since Epoch.
    :param stop: An optional stop timestamp, in milliseconds since Epoch, or
        None for infinite streaming.
    :param resolution: The desired compute resolution, in milliseconds.
    :param max_delay: The desired maximum data wait, in milliseconds, or None
        for automatic.
    """
    utils.message('Job request sent. Awaiting response... ')
    try:
        c = flow.execute(program, start=start, stop=stop,
                         resolution=resolution, max_delay=max_delay,
                         persistent=False)
    except signalflow.errors.SignalFlowException as e:
        if not e.message:
            print('failed ({0})!'.format(e.code))
        else:
            print('failed!')
            print('\033[31;1m{0}\033[;0m'.format(e.message))
        return

    try:
        EventsOutputDisplay(c, tz, start).stream()
    except Exception as e:
        print('Exception: {}'.format(e))
