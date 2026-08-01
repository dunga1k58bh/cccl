// Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
//
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

#include <cuda/std/span>

#include <vector>

template <class T>
[[gnu::noinline]] void keep_for_debugger(const T& value)
{
  asm volatile("" : : "g"(&value) : "memory");
}

using span_alias = cuda::std::span<int, 4>;

[[gnu::noinline]] void inspect_normal_dynamic(const cuda::std::span<int>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_normal_static(const cuda::std::span<int, 4>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_empty_dynamic(const cuda::std::span<int>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_empty_static(const cuda::std::span<int, 0>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_single(const cuda::std::span<int>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_alias(const span_alias& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_const(const cuda::std::span<int>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_const_element(const cuda::std::span<const int>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_pointer_element(const cuda::std::span<int*>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_nested(const cuda::std::span<cuda::std::span<int>, 2>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_vector(const std::vector<cuda::std::span<int>>& values)
{
  keep_for_debugger(values[0]);
  keep_for_debugger(values[1]);
}

[[gnu::noinline]] void inspect_before_update(const cuda::std::span<int>& values)
{
  keep_for_debugger(values);
}

[[gnu::noinline]] void inspect_after_update(const cuda::std::span<int>& values)
{
  keep_for_debugger(values);
}

int main()
{
  int normal_data[4] = {-7, 0, 42, 13};
  const cuda::std::span<int> normal_dynamic(normal_data);
  const cuda::std::span<int, 4> normal_static(normal_data);

  const cuda::std::span<int> empty_dynamic;
  const cuda::std::span<int, 0> empty_static;

  int single_data[1] = {99};
  const cuda::std::span<int> single(single_data);

  int alias_data[4] = {-31, 17, 8, -64};
  const span_alias alias(alias_data);

  const cuda::std::span<int> const_span(normal_data);
  const cuda::std::span<const int> const_element(normal_data);

  int* pointer_data[3] = {&normal_data[0], &normal_data[1], &normal_data[2]};
  const cuda::std::span<int*> pointer_element(pointer_data);

  int nested_normal_data[2]            = {13, -5};
  cuda::std::span<int> nested_inner[2] = {
    cuda::std::span<int>(nested_normal_data),
    cuda::std::span<int>(),
  };
  const cuda::std::span<cuda::std::span<int>, 2> nested(nested_inner);

  int vector_data0[3] = {-2, 4, 6};
  int vector_data1[3] = {11, -9, 27};
  const std::vector<cuda::std::span<int>> span_vector{
    cuda::std::span<int>(vector_data0),
    cuda::std::span<int>(vector_data1),
  };

  int update_before_data[3] = {6, -91, 52};
  int update_after_data[5]  = {3, 85, -12, 1, 2};
  cuda::std::span<int> updated_values(update_before_data);

  inspect_normal_dynamic(normal_dynamic);
  inspect_normal_static(normal_static);
  inspect_empty_dynamic(empty_dynamic);
  inspect_empty_static(empty_static);
  inspect_single(single);
  inspect_alias(alias);
  inspect_const(const_span);
  inspect_const_element(const_element);
  inspect_pointer_element(pointer_element);
  inspect_nested(nested);
  inspect_vector(span_vector);
  inspect_before_update(updated_values);
  updated_values = cuda::std::span<int>(update_after_data);
  inspect_after_update(updated_values);
}
