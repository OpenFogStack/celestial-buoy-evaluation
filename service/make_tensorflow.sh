#!/bin/sh

docker run -rm -it -v $(pwd)/files:/files alpine:latest /bin/sh -c "apk add --update --no-cache \
    curl \
    git \
    python3 \
    py3-pip \
    python3-dev \
    py3-numpy \
    make \
    cmake \
    gcc \
    g++ \
    swig \
    libjpeg-turbo-dev \
    zlib-dev \
    bash \
    linux-headers \
    py3-numpy-dev \
    && python3 -m pip install --upgrade \
    pip \
    numpy \
    pybind11 \
    wheel \
    setuptools\
    && git clone clone https://github.com/tensorflow/tensorflow.git \
    && cd /tensorflow \
    && git checkout v2.8.0 \
    && bash tensorflow/lite/tools/pip_package/build_pip_package_with_cmake.sh \
    && /bin/sh"
