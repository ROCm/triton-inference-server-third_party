# Copyright 2015-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Modifications Copyright (c) 2024 Advanced Micro Devices, Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# CMakeLists to build the cnmem library.
cmake_minimum_required(VERSION 3.31.8)
project(cnmem)

# Rules to build the cnmem library.
if(${TRITON_ENABLE_ROCM})
  find_package(hip REQUIRED)
  find_package(HIP)
  enable_language(HIP)
  find_package(Python3 COMPONENTS Interpreter REQUIRED)

  if (NOT TRITON_HIPIFY_PERL)
    find_path(HIPIFY_PERL_PATH
      NAMES hipify-perl
      HINTS
      ${TRITON_BUILD_ROCM_HOME}/bin
      ${TRITON_BUILD_ROCM_HOME}/hip/bin)
    if (HIPIFY_PERL_PATH-NOTFOUND)
      MESSAGE(FATAL_ERROR "hipify-perl not found")
    endif()
    set(TRITON_HIPIFY_PERL ${HIPIFY_PERL_PATH}/hipify-perl)
  endif() #TRITON_HIPIFY_PERL

  set(HIPIFY_TOOL ${PROJECT_SOURCE_DIR}/amd_hipify.py)
  
  # AMDGPU_BUILD_DIR is passed from parent CMakeLists.txt for consistent structure
  if(NOT AMDGPU_BUILD_DIR)
    set(AMDGPU_BUILD_DIR ${CMAKE_CURRENT_BINARY_DIR}/amdgpu)
  endif()

  # Source files to hipify
  set(CNMEM_CUDA_SRCS
    ${PROJECT_SOURCE_DIR}/src/cnmem.cpp
  )
  set(CNMEM_CUDA_HDRS
    ${PROJECT_SOURCE_DIR}/include/cnmem.h
  )

  # Hipify each source file to amdgpu directory
  set(CNMEM_HIP_SRCS)
  set(CNMEM_HIP_HDRS)

  foreach(src_file ${CNMEM_CUDA_SRCS})
    file(RELATIVE_PATH rel_path "${PROJECT_SOURCE_DIR}" "${src_file}")
    string(REPLACE "cuda" "rocm" rel_path_hip "${rel_path}")
    set(out_file "${AMDGPU_BUILD_DIR}/${rel_path_hip}")

    add_custom_command(
      OUTPUT ${out_file}
      COMMAND Python3::Interpreter ${HIPIFY_TOOL}
        --hipify_perl ${TRITON_HIPIFY_PERL}
        ${src_file} -o ${out_file}
      DEPENDS ${HIPIFY_TOOL} ${src_file}
      COMMENT "Hipify: ${rel_path} -> ${out_file}"
    )
    list(APPEND CNMEM_HIP_SRCS ${out_file})
  endforeach()

  foreach(hdr_file ${CNMEM_CUDA_HDRS})
    file(RELATIVE_PATH rel_path "${PROJECT_SOURCE_DIR}" "${hdr_file}")
    string(REPLACE "cuda" "rocm" rel_path_hip "${rel_path}")
    set(out_file "${AMDGPU_BUILD_DIR}/${rel_path_hip}")

    add_custom_command(
      OUTPUT ${out_file}
      COMMAND Python3::Interpreter ${HIPIFY_TOOL}
        --hipify_perl ${TRITON_HIPIFY_PERL}
        ${hdr_file} -o ${out_file}
      DEPENDS ${HIPIFY_TOOL} ${hdr_file}
      COMMENT "Hipify: ${rel_path} -> ${out_file}"
    )
    list(APPEND CNMEM_HIP_HDRS ${out_file})
  endforeach()

  # Mark generated files
  set_source_files_properties(${CNMEM_HIP_SRCS} PROPERTIES GENERATED TRUE)
  set_source_files_properties(${CNMEM_HIP_HDRS} PROPERTIES GENERATED TRUE)

  # Use hipified sources for build
  include_directories(${AMDGPU_BUILD_DIR}/include)
  add_definitions(-DCNMEM_DLLEXPORT)
  add_library(cnmem STATIC ${CNMEM_HIP_SRCS} ${CNMEM_HIP_HDRS})
  set_target_properties(cnmem PROPERTIES VERSION 1.0.0 SOVERSION 1)

  target_compile_options(
    cnmem
    PRIVATE
      -Wno-unused-result
  )

  target_link_libraries(
    cnmem
    PUBLIC
      hip::host
  )

  # Install hipified headers
  install(FILES ${AMDGPU_BUILD_DIR}/include/cnmem.h DESTINATION include)
else()
  # We need CUDA to build that library.
  find_package(CUDAToolkit QUIET REQUIRED)
  message(STATUS "CUDAToolkit_VERSION: ${CUDAToolkit_VERSION}")
  include_directories(${CUDAToolkit_INCLUDE_DIRS})

  include_directories(include)
  add_definitions(-DCNMEM_DLLEXPORT)
  add_library(cnmem STATIC src/cnmem.cpp)
  set_target_properties(cnmem PROPERTIES VERSION 1.0.0 SOVERSION 1)
  target_link_libraries(cnmem LINK_PUBLIC ${CUDAToolkit_LIBRARY_DIR})

  # Install original headers
  install(FILES include/cnmem.h DESTINATION include)
endif() # TRITON_ENABLE_ROCM

install(TARGETS cnmem RUNTIME DESTINATION bin ARCHIVE DESTINATION lib LIBRARY DESTINATION lib)

# Add the tests.
if(WITH_TESTS)

  # Get Google tests.
  find_package(GTest QUIET REQUIRED)
  include_directories(${GTEST_INCLUDE_DIRS})

  # Build the executable.
  add_executable(cnmem_tests tests/cnmem_tests.cpp)
  if(MSVC)
    if(MSVC_VERSION GREATER 1700) # Visual Studio 11 or more.
      add_definitions(-DUSE_CPP_11)
    endif(MSVC_VERSION GREATER 1700)
  endif(MSVC)
  if(CMAKE_COMPILER_IS_GNUCC)
    add_definitions(-std=c++11 -DUSE_CPP_11)
  endif(CMAKE_COMPILER_IS_GNUCC)
  target_link_libraries(cnmem_tests LINK_PUBLIC cnmem ${CUDAToolkit_LIBRARY_DIR} ${GTEST_LIBRARIES} -lpthread)
  install(TARGETS cnmem_tests RUNTIME DESTINATION bin)

  # Tests that launch kernels to force reading and writing to memory
  cuda_add_executable(cnmem_kernel_tests tests/cnmem_kernel_test.cu)
  target_link_libraries(cnmem_kernel_tests cnmem ${CUDAToolkit_LIBRARY_DIR} ${GTEST_LIBRARIES} -lpthread)
  install(TARGETS cnmem_kernel_tests RUNTIME DESTINATION bin)

  # On Windows, we copy the Google test DLL to the bin folder.
  if(MSVC)
    get_filename_component(gtest_dll_path ${GTEST_LIBRARIES} DIRECTORY)
    install(FILES ${gtest_dll_path}/gtest.dll DESTINATION bin)
  endif(MSVC)

endif(WITH_TESTS)
