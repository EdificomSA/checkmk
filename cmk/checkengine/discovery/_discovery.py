#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol

from cmk.utils.hostaddress import HostName

from cmk.checkengine.checking import CheckPluginName
from cmk.checkengine.parameters import Parameters
from cmk.checkengine.sectionparser import ParsedSectionName

from ._autochecks import AutocheckEntry

__all__ = ["DiscoveryPlugin"]


class PService(Protocol):
    def as_autocheck_entry(self, name: CheckPluginName) -> AutocheckEntry:
        ...


@dataclass(frozen=True)
class DiscoveryPlugin:
    sections: Sequence[ParsedSectionName]
    # There is a single user of the `service_name` attribute.  Is it
    # *really* needed?  Does it *really* belong to the check plugin?
    # This doesn't feel right.
    service_name: str
    function: Callable[..., Iterable[PService]]
    parameters: Callable[[HostName], Sequence[Parameters] | Parameters | None]
