#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Final

from cmk.gui.plugins.metrics.utils import ExplicitGraphRecipe
from cmk.gui.utils.graph_specification import ExplicitGraphSpecification

from .graph_recipe_builder import graph_recipe_builder_registry


class ExplicitGraphRecipeBuilder:
    def __init__(self) -> None:
        self.graph_type: Final = "explicit"

    def __call__(self, spec: ExplicitGraphSpecification) -> list[ExplicitGraphRecipe]:
        return [
            {
                "title": spec.title,
                "unit": spec.unit,
                "consolidation_function": spec.consolidation_function,
                "explicit_vertical_range": spec.explicit_vertical_range,
                "omit_zero_metrics": spec.omit_zero_metrics,
                "horizontal_rules": spec.horizontal_rules,
                "context": spec.context,
                "add_context_to_title": spec.add_context_to_title,
                "metrics": spec.metrics,
                "specification": (
                    "explicit",
                    spec.to_legacy_format(),
                ),
            }
        ]


graph_recipe_builder_registry.register(ExplicitGraphRecipeBuilder())
