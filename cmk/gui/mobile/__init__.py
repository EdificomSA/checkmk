#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import cmk.gui.pages
from cmk.gui.views.layout import LayoutRegistry

from .pages import page_index, page_login, page_view
from .views import LayoutMobileDataset, LayoutMobileList, LayoutMobileTable


def register(layout_registry: LayoutRegistry) -> None:
    cmk.gui.pages.register("mobile")(page_index)
    cmk.gui.pages.register("mobile_view")(page_view)
    layout_registry.register(LayoutMobileTable)
    layout_registry.register(LayoutMobileList)
    layout_registry.register(LayoutMobileDataset)


__all__ = ["page_login"]
