# Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""LLDB pretty printer for cuda::std::span."""

from __future__ import annotations

import re

import lldb

# LLDB's display type name elides a template argument that equals its default
# value, so a dynamic-extent span shows as "cuda::std::span<T>" with no visible
# extent at all, while a static-extent one shows the real "cuda::std::span<T,
# N>". Recognition therefore cannot require a trailing extent; only the
# static-extent branch (below) needs to parse one back out.
_SPAN_PATTERN = re.compile(r"^cuda::std::span<.+>$")
_STATIC_EXTENT_PATTERN = re.compile(r",\s*(\d+)>$")
InternalDict = dict[str, object]


def is_cuda_span(value_type: lldb.SBType, _internal_dict: InternalDict) -> bool:
    type_name = (
        value_type.GetCanonicalType().GetUnqualifiedType().GetDisplayTypeName() or ""
    )
    return _SPAN_PATTERN.fullmatch(type_name) is not None


def _display_type_name(value: lldb.SBValue) -> str:
    return (
        value.GetType().GetCanonicalType().GetUnqualifiedType().GetDisplayTypeName()
        or ""
    )


def _span_size(value: lldb.SBValue) -> int | None:
    # A dynamic-extent span (and only a dynamic-extent one) carries its own
    # runtime size; a static-extent span's size lives solely in its type.
    size_member = value.GetChildMemberWithName("__size_")
    if size_member.IsValid():
        return size_member.GetValueAsUnsigned(0)

    match = _STATIC_EXTENT_PATTERN.search(_display_type_name(value))
    if match is None:
        return None
    return int(match.group(1))


def span_summary(value: lldb.SBValue, _internal_dict: InternalDict) -> str | None:
    value = value.GetNonSyntheticValue()
    if _SPAN_PATTERN.fullmatch(_display_type_name(value)) is None:
        return None
    size = _span_size(value)
    if size is None:
        return None
    return f"of length {size}"


class SpanSyntheticProvider:
    """Expose cuda::std::span elements as LLDB synthetic children."""

    def __init__(self, value: lldb.SBValue, _internal_dict: InternalDict) -> None:
        self.value = value.GetNonSyntheticValue()
        self.update()

    def update(self) -> bool:
        self.data = self.value.GetChildMemberWithName("__data_")
        self.size = 0
        if not self.data.IsValid():
            return False

        size = _span_size(self.value)
        if size is None:
            return False

        self.size = size
        self.element_type = self.data.GetType().GetPointeeType()
        self.element_size = self.element_type.GetByteSize()
        return True

    def num_children(self) -> int:
        return self.size

    def has_children(self) -> bool:
        return self.size != 0

    def get_type_name(self) -> str:
        # STL element access can preserve an alloc_traits::value_type typedef.
        # Report the canonical display name so LLDB shows cuda::std::span instead.
        return _display_type_name(self.value)

    def get_child_index(self, name: str) -> int:
        if name.startswith("[") and name.endswith("]"):
            try:
                return int(name[1:-1])
            except ValueError:
                pass
        return -1

    def get_child_at_index(self, index: int) -> lldb.SBValue | None:
        if index < 0 or index >= self.size:
            return None
        offset = index * self.element_size
        return self.data.CreateChildAtOffset(f"[{index}]", offset, self.element_type)


def register(debugger: lldb.SBDebugger, category: str, module: str) -> None:
    """Register the cuda::std::span formatter in an LLDB category."""
    debugger.HandleCommand(
        f"type summary add --category {category} --expand --python-function {module}.span_summary "
        f"--recognizer-function {module}.is_cuda_span"
    )
    debugger.HandleCommand(
        f"type synthetic add --category {category} --python-class {module}.SpanSyntheticProvider "
        f"--recognizer-function {module}.is_cuda_span"
    )
