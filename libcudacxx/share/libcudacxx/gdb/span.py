# Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""GDB pretty printer for cuda::std::span."""

from __future__ import annotations

from collections.abc import Iterator
from types import ModuleType

import memory_resource

import gdb
import gdb.printing

# static_cast<size_t>(-1), the value of cuda::std::dynamic_extent.
_DYNAMIC_EXTENT = (1 << 64) - 1


def _template_name(value_type: gdb.Type) -> str:
    return str(value_type).split("<", 1)[0]


def _is_cuda_span(value_type: gdb.Type) -> bool:
    value_type = value_type.strip_typedefs().unqualified()
    template_name = _template_name(value_type)
    return (
        template_name.startswith("cuda::std::")
        and template_name.rsplit("::", 1)[-1] == "span"
    )


class SpanPrinter:
    """Expose cuda::std::span metadata and elements to GDB."""

    def __init__(self, value: gdb.Value) -> None:
        self.value = value
        self.type = value.type.strip_typedefs().unqualified()
        self.type_name = memory_resource.public_type_name(self.type)
        self.data = value["__data_"]

        extent = int(self.type.template_argument(1))
        if extent == _DYNAMIC_EXTENT:
            self.size = int(value["__size_"])
        else:
            self.size = extent

    def children(self) -> Iterator[tuple[str, gdb.Value]]:
        for index in range(self.size):
            yield f"[{index}]", (self.data + index).dereference()

    def to_string(self) -> str:
        return f"{self.type_name} of length {self.size}"


class SpanPrinterLookup(gdb.printing.PrettyPrinter):
    """Select the cuda::std::span printer by its public class name."""

    def __init__(self) -> None:
        super().__init__("cuda::std::span")

    def __call__(self, value: gdb.Value) -> SpanPrinter | None:
        if _is_cuda_span(value.type):
            return SpanPrinter(value)
        return None


def register(objfile: ModuleType) -> None:
    """Register the cuda::std::span printer with GDB."""
    gdb.printing.register_pretty_printer(objfile, SpanPrinterLookup(), replace=True)
