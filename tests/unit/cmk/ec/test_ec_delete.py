#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""EC delete methods with one or more event IDs"""
from tests.testlib import CMKEventConsole

from tests.unit.cmk.ec.helpers import FakeStatusSocket

from cmk.utils.type_defs import HostName

from cmk.ec.main import Event, EventStatus, StatusServer


def test_delete_event(event_status: EventStatus, status_server: StatusServer) -> None:
    """Delete 1 event"""
    event: Event = {
        "host": "ABC1",
        "text": "not important",
        "core_host": HostName("ABC"),
    }
    event_status.new_event(CMKEventConsole.new_event(event))

    assert len(event_status.events()) == 1

    s = FakeStatusSocket(b"COMMAND DELETE;1;testuser")
    status_server.handle_client(s, True, "127.0.0.1")

    assert len(event_status.events()) == 0


def test_delete_multiple_events(event_status: EventStatus, status_server: StatusServer) -> None:
    """Delete event list"""
    events: list[Event] = [
        {
            "host": "ABC1",
            "text": "event1 text",
            "core_host": HostName("ABC"),
        },
        {
            "host": "ABC2",
            "text": "event2 text",
            "core_host": HostName("ABC"),
        },
    ]
    for event in events:
        event_status.new_event(CMKEventConsole.new_event(event))

    assert len(event_status.events()) == 2

    s = FakeStatusSocket(b"COMMAND DELETE;1,2;testuser")
    status_server.handle_client(s, True, "127.0.0.1")

    assert len(event_status.events()) == 0


def test_delete_partially_existing_multiple_events(
    event_status: EventStatus, status_server: StatusServer
) -> None:
    """Event list with a missing ID still deletes the existing ID"""
    events: list[Event] = [
        {
            "host": "ABC1",
            "text": "event1 text",
            "core_host": HostName("ABC"),
        },
        {
            "host": "ABC2",
            "text": "event2 text",
            "core_host": HostName("ABC"),
        },
    ]
    for event in events:
        event_status.new_event(CMKEventConsole.new_event(event))

    assert len(event_status.events()) == 2

    s = FakeStatusSocket(b"COMMAND DELETE;2;testuser")
    status_server.handle_client(s, True, "127.0.0.1")

    assert len(event_status.events()) == 1

    s = FakeStatusSocket(b"COMMAND DELETE;1,2;testuser")
    status_server.handle_client(s, True, "127.0.0.1")

    assert len(event_status.events()) == 0


def test_delete_events_of_host(event_status: EventStatus, status_server: StatusServer) -> None:
    """Delete all events of host"""
    events: list[Event] = [
        {
            "host": "ABC1",
            "text": "event1 text",
            "core_host": HostName("ABC"),
        },
        {
            "host": "ABC1",
            "text": "event2 text",
            "core_host": HostName("ABC"),
        },
    ]
    for event in events:
        event_status.new_event(CMKEventConsole.new_event(event))

    assert len(event_status.events()) == 2

    s = FakeStatusSocket(b"COMMAND DELETE_EVENTS_OF_HOST;ABC1;testuser")
    status_server.handle_client(s, True, "127.0.0.1")

    assert len(event_status.events()) == 0
