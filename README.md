# Triton Third-Party Packages - ROCm Edition

This repository builds and manages third-party dependencies for Triton Inference Server with AMD ROCm GPU support.

## 1. What Does This Repo Do?

This repository:
- Downloads, builds, and installs third-party libraries required by Triton Inference Server
- Provides ROCm/HIP support for GPU-related libraries (specifically `cnmem`)
- Uses CMake's `ExternalProject_Add` to manage dependencies with consistent build configurations
- Installs all libraries to a common prefix (`TRITON_THIRD_PARTY_INSTALL_PREFIX`) for easy consumption by other Triton components

## 2. What Third-Party Repos Are Built?

| Library | Version/Tag | Purpose |
|---------|-------------|---------|
| curl | curl-7_86_0 | HTTP client library |
| grpc | v1.54.3 | RPC framework |
| nlohmann-json | v3.11.3 | JSON library |
| absl (abseil-cpp) | (from grpc) | Google's C++ common libraries |
| protobuf | (from grpc) | Protocol buffers serialization |
| re2 | (from grpc) | Regular expression library |
| googletest | (from grpc) | Testing framework |
| c-ares | (from grpc) | Async DNS resolver |
| libevent | release-2.1.12-stable | Event notification library |
| libevhtp | (local) | HTTP server library |
| prometheus-cpp | v1.0.1 | Metrics library |
| crc32c | b9d6e825 | CRC32C implementation |
| google-cloud-cpp | v2.28.0 | GCS storage client |
| azure-iot-sdk-c | LTS_03_2024_Ref02 | Azure IoT SDK |
| azure-sdk | azure-storage-blobs_12.13.0 | Azure storage client |
| cnmem | (local) | CUDA/HIP memory manager |
| aws-sdk-cpp | 1.11.60 | AWS S3 client |
| opentelemetry-cpp | v1.13.0 | Distributed tracing |

## 3. Which Libraries Are Cloned vs Local?

### Cloned from Git (downloaded during build):
- `curl` - https://github.com/curl/curl.git
- `grpc-repo` - https://github.com/grpc/grpc.git (includes absl, protobuf, re2, googletest, c-ares as submodules)
- `nlohmann-json` - https://github.com/nlohmann/json.git
- `libevent` - https://github.com/libevent/libevent.git
- `prometheus-cpp` - https://github.com/jupp0r/prometheus-cpp.git
- `crc32c` - https://github.com/google/crc32c.git
- `google-cloud-cpp` - https://github.com/googleapis/google-cloud-cpp.git
- `azure-iot-sdk-c` - https://github.com/Azure/azure-iot-sdk-c.git
- `azure-sdk` - https://github.com/Azure/azure-sdk-for-cpp.git
- `aws-sdk-cpp` - https://github.com/aws/aws-sdk-cpp.git
- `opentelemetry-cpp` - https://github.com/open-telemetry/opentelemetry-cpp.git

### Local (bundled in this repo):
- `libevhtp/libevhtp/` - HTTP server library (requires patches)
- `cnmem/cnmem/` - CUDA/HIP memory manager (requires hipification for ROCm)

## 4. How Is Hipification Done?

Hipification (converting CUDA code to HIP for AMD GPUs) is performed for **cnmem only**:

### Process:
1. **hipify-perl** (from ROCm) performs initial CUDA→HIP translation
2. **amd_hipify.py** applies additional Triton-specific replacements
3. Hipified sources are written to `build/cnmem/amdgpu/`
4. HIP runtime headers and libraries are provided via `hip::host` CMake target

### Key Files:
- `cnmem/cnmem/amd_hipify.py` - Python script for hipification, hipify-perl is called here with post-processing fixes
- `cnmem/cnmem/CMakeLists.txt` - Contains hipification logic in `if(TRITON_ENABLE_ROCM)` block

## 5. Where Are Libraries After Build?

### Build Directory Structure:
```
tis-third-party/build/
├── curl/                    # curl build directory
├── grpc/                    # grpc build directory
├── cnmem/
│   ├── amdgpu/              # Hipified source files
│   │   ├── src/cnmem.cpp
│   │   └── include/cnmem.h
│   └── src/cnmem-build/     # Actual build output
│       └── libcnmem.a
├── ...                      # Other library build dirs
│
└── install/                 # Installation prefix
    ├── cnmem/
    │   ├── include/cnmem.h
    │   └── lib/libcnmem.a
    ├── grpc/
    │   ├── include/
    │   └── lib/
    ├── protobuf/
    │   ├── include/
    │   └── lib/
    └── ...
```

### How the Server Repo  Uses These Libraries:

1. **FetchContent downloads this repo:**
   ```cmake
   FetchContent_Declare(repo-third-party
     GIT_REPOSITORY https://github.com/ROCm/tis-third-party.git
     GIT_TAG ${TRITON_THIRD_PARTY_REPO_TAG}
   )
   FetchContent_MakeAvailable(repo-third-party)
   ```

2. **Server depends on third-party targets:**
   ```cmake
   set(TRITON_DEPENDS triton-core protobuf googletest grpc libevent libevhtp ...)
   ```

3. **CMake finds installed libraries via paths:**
   ```cmake
   -DgRPC_DIR:PATH=${TRITON_THIRD_PARTY_INSTALL_PREFIX}/grpc/lib/cmake/grpc
   -DProtobuf_DIR:PATH=${TRITON_THIRD_PARTY_INSTALL_PREFIX}/protobuf/lib/cmake/protobuf
   -Dlibevhtp_DIR:PATH=${TRITON_THIRD_PARTY_INSTALL_PREFIX}/libevhtp/lib/cmake/libevhtp
   ```

### Building Standalone:
```bash
mkdir build && cd build
cmake -DTRITON_THIRD_PARTY_INSTALL_PREFIX=$(pwd)/install \
      -DTRITON_ENABLE_ROCM=ON \
      -DTRITON_BUILD_ROCM_HOME=/opt/rocm \
      ..
make cnmem VERBOSE=1 -j$(nproc)      # Build cnmem only
make libevent libevhtp VERBOSE=1 -j$(nproc)    # Build HTTP dependencies
```

---

## Original triton-inference-server/third_party Documentation

> **Note**: The following documentation is from NVIDIA's upstream Triton Inference Server and primarily covers NVIDIA GPU (CUDA) usage. For ROCm/AMD GPU support, refer to the ROCm-specific documentation above.

---

This repo contains software that Triton must patch or otherwise modify
before using.
