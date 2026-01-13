# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
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

import argparse
import os
import subprocess


def hipify(hipify_perl_path, src_file_path, dst_file_path):
    dir_name = os.path.dirname(dst_file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    # Run hipify-perl first, capture output
    s = subprocess.run([hipify_perl_path, "-roc", src_file_path], stdout=subprocess.PIPE, text=True, check=False).stdout

    # Additional exact-match replacements.
    s = s.replace("kCudaExecutionProvider", "kRocmExecutionProvider")
    s = s.replace("CUDAStreamType", "HIPStreamType")
    s = s.replace("kCudaStreamDefault", "kHipStreamDefault")
    s = s.replace("kCudaStreamCopyIn", "kHipStreamCopyIn")
    s = s.replace("kCudaStreamCopyOut", "kHipStreamCopyOut")
    s = s.replace("kTotalCudaStreams", "kTotalHipStreams")
    s = s.replace("CublasHandle", "RocblasHandle")
    s = s.replace("cublas_handle", "rocblas_handle")
    s = s.replace("hipblasHandle_t", "rocblas_handle")
    s = s.replace("hipblasDatatype_t", "rocblas_datatype")
    s = s.replace("HIPBLAS_STATUS_SUCCESS", "rocblas_status_success")
    s = s.replace("hipblasStatus_t", "rocblas_status")
    s = s.replace("hipblasCreate", "rocblas_create_handle")
    s = s.replace("hipblasDestroy", "rocblas_destroy_handle")
    s = s.replace("hipblasSetStream", "rocblas_set_stream")
    s = s.replace("HIPBLAS_OP_T", "rocblas_operation_transpose")
    s = s.replace("HIPBLAS_OP_N", "rocblas_operation_none")
    s = s.replace("rocblas_half", "__half")
    s = s.replace("RegisterCudaContribKernels", "RegisterRocmContribKernels")
    s = s.replace("cudaEvent", "hipEvent")
    s = s.replace("CreateCudaAllocator", "CreateRocmAllocator")
    s = s.replace("CudaDeviceCount", "RocmDeviceCount")
    s = s.replace("CudaErrString", "RocmErrString")
    s = s.replace("CudaAsyncBuffer", "RocmAsyncBuffer")
    s = s.replace("CudaKernel", "RocmKernel")
    s = s.replace("CudaStream", "RocmStream")
    s = s.replace("ToCudaType", "ToHipType")
    s = s.replace("CudaT", "HipT")
    s = s.replace("CUDA_LONG", "HIP_LONG")
    s = s.replace("CUDA_RETURN_IF_ERROR", "HIP_RETURN_IF_ERROR")
    s = s.replace("CUDA_KERNEL_ASSERT", "HIP_KERNEL_ASSERT")
    s = s.replace("CUDA_CALL", "HIP_CALL")
    s = s.replace("SliceCuda", "SliceRocm")
    s = s.replace("thrust::cuda", "thrust::hip")
    s = s.replace("CudaCall", "RocmCall")
    s = s.replace("cuda", "rocm")
    s = s.replace("void CUDART_CB", "static void")
    s = s.replace("#ifdef TRITON_ENABLE_GPU", "#ifdef TRITON_ENABLE_ROCM")
    s = s.replace("#ifndef TRITON_ENABLE_GPU", "#ifndef TRITON_ENABLE_ROCM")
    s = s.replace("#elif defined(TRITON_ENABLE_GPU)", "#elif defined(TRITON_ENABLE_ROCM)")
    s = s.replace("CUDA", "ROCM")
    s = s.replace("GPU_WARP_SIZE = 32", "GPU_WARP_SIZE = 64")
    s = s.replace("std::exp", "expf")
    s = s.replace("std::log", "logf")
    s = s.replace("WaitCudaNotificationOnDevice", "WaitRocmNotificationOnDevice")
    s = s.replace("hipHostAlloc", "hipHostMalloc")
    s = s.replace("CUBLAS", "ROCBLAS")
    s = s.replace("Cublas", "Rocblas")
    s = s.replace("cublas", "rocblas")
    s = s.replace("ROCMRT_INF_F", "std::numeric_limits<float>::infinity()")
    s = s.replace("HIPBLAS_R_16F", "rocblas_datatype_f16_r")
    s = s.replace("HIPBLAS_R_32F", "rocblas_datatype_f32_r")
    s = s.replace("ROCBLAS_GEMM_DEFAULT_TENSOR_OP", "rocblas_gemm_algo_standard")
    s = s.replace("ROCBLAS_TENSOR_OP_MATH", "0")
    s = s.replace("CURAND", "HIPRAND")
    s = s.replace("Curand", "Hiprand")
    s = s.replace("curand", "hiprand")
    s = s.replace("#include <nccl.h>", "#include <rccl/rccl.h>")
    s = s.replace("CUDNN", "MIOPEN")
    s = s.replace("Cudnn", "Miopen")
    s = s.replace("cudnn", "miopen")
    s = s.replace("#include <hipDNN.h>", "#include <miopen/miopen.h>")
    s = s.replace("hipdnn", "miopen")
    s = s.replace("HIPDNN_STATUS_SUCCESS", "miopenStatusSuccess")
    s = s.replace("HIPDNN", "MIOPEN")
    s = s.replace("CUSPARSE", "HIPSPARSE")
    s = s.replace("CUFFT", "HIPFFT")

    # Undo over-hipification
    s = s.replace("id, ROCM", "id, CUDA")
    s = s.replace("rocm_utils.h", "cuda_utils.h")
    s = s.replace("rocm_memory_manager.h", "cuda_memory_manager.h")
    s = s.replace("model_config_rocm.h", "model_config_cuda.h")
    s = s.replace("ROCM error executing", "HIP error executing")
    s = s.replace("ROCM_PINNED", "CUDA_PINNED")
    s = s.replace("rocm_err", "hip_err")
    s = s.replace("ROCM_VERSION", "CUDA_VERSION")
    s = s.replace("__ROCM_ARCH__", "__CUDA_ARCH__")
    s = s.replace("logfic_error", "std::logic_error")
    s = s.replace('#include "device_atomic_functions.h"', "")
    s = s.replace("#include <hiprand_kernel.h>", "#include <hiprand/hiprand_kernel.h>")
    s = s.replace("#include <rocblas.h>", "#include <rocblas/rocblas.h>")
    s = s.replace("#include <hipblas.h>", "#include <hipblas/hipblas.h>")
    s = s.replace("#include <hipfft.h>", "#include <hipfft/hipfft.h>")

    with open(dst_file_path, "w") as f:
        f.write(s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hipify_perl", required=True)
    parser.add_argument("--output", "-o", help="output file")
    parser.add_argument("src", help="src")
    args = parser.parse_args()
    print("hipifying " + str(args.src))
    hipify(args.hipify_perl, args.src, args.output)
