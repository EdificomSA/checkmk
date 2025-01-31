#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import json
from collections.abc import Collection, Iterable, Mapping, Sequence

from pydantic import BaseModel

from .agent_based_api.v1 import check_levels, register, render, Result, Service, State
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable
from .utils.graylog import deserialize_and_merge_json


class FailureMessage(BaseModel):
    type: str | None
    reason: str | None

    def to_human_readable(self) -> Iterable[str]:
        yield from (
            f"{field_name.title()}: {field_value}"
            for field_name, field_value in self.dict(exclude_none=True).items()
        )


class Failure(BaseModel):
    # The data model we have to deal with here is not a proper json model: the
    # error message of a failure can either be a json-encoded dict (so json
    # inside json) or a non-json string, which is why neither parse_obj nor
    # parse_raw can do the job.
    timestamp: str | None
    index: str | None
    message: FailureMessage | str | None

    def __init__(
        self,
        *,
        timestamp: str | None,
        index: str | None,
        message: FailureMessage | str | None,
        **data: object,
    ) -> None:
        super().__init__(timestamp=timestamp, index=index, message=message, **data)
        if isinstance(message, str):
            try:
                deserialized = json.loads(message)
            except json.JSONDecodeError:
                return
            self.message = FailureMessage.parse_obj(deserialized)

    def to_human_readable(self) -> Iterable[str]:
        for field_name, field_value in dict(self).items():
            match field_value:
                case str():
                    yield f"{field_name.title()}: {field_value}"
                case FailureMessage():
                    yield from field_value.to_human_readable()


class Section(BaseModel):
    """

    The graylog API does not specify the scheme of the endpoint providing this
    data (it only says 'anyMap'), see SUP-11170.
    """

    failures: Sequence[Failure] | None
    total: int | None
    count: int | None
    ds_param_since: float


def parse(string_table: StringTable) -> Section:
    return Section.parse_obj(deserialize_and_merge_json(string_table))


register.agent_section(
    name="graylog_failures",
    parse_function=parse,
)


def discover(section: Section) -> DiscoveryResult:
    if section.failures is None:
        return
    yield Service()


def _failure_results(failures: Collection[Failure]) -> CheckResult:
    details = [
        failure_human_readable
        for failure in sorted(failures, key=lambda f: (f.timestamp, f.index))
        if (failure_human_readable := ", ".join(failure.to_human_readable()))
    ]

    if not details:
        return

    index_count = len(set(failure.index for failure in failures if failure.index is not None))
    yield Result(
        state=State.OK,
        summary=f"Affected indices: {index_count}, see service details for further information",
    )
    yield Result(
        state=State.OK,
        notice="\n".join(details),
    )


def check(
    params: Mapping[str, tuple[int, int] | None],
    section: Section,
) -> CheckResult:
    if section.failures is None or section.total is None:
        return

    yield from check_levels(
        value=section.total,
        levels_upper=params.get("failures"),
        metric_name="failures",
        render_func=str,
        label="Total number of failures",
    )

    if section.count is None:
        return

    yield from check_levels(
        value=section.count,
        levels_upper=params.get("failures_last"),
        metric_name=None,
        render_func=str,
        label=f"Failures in last {render.timespan(section.ds_param_since)}",
    )

    if section.count == 0:
        return

    yield from _failure_results(section.failures)


register.check_plugin(
    name="graylog_failures",
    service_name="Graylog Index Failures",
    discovery_function=discover,
    check_function=check,
    check_default_parameters={},
    check_ruleset_name="graylog_failures",
)
