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


class RawOutputDisplay(object):
    def __init__(self, computation):
        self._computation = computation

    def stream(self):
        try:
            for message in self._computation.stream():
                pass
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
    utils.message('{\n')
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
        RawOutputDisplay(c).stream()
    except Exception as e:
        print('Exception: {}'.format(e))

    utils.message('{}\n}\n')
