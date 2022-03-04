FROM alpine:latest

RUN apk add --update --no-cache \
    curl \
    git \
    python3 \
    py3-pip \
    python3-dev \
    make \
    cmake \
    gcc \
    g++ \
    swig \
    libjpeg-turbo-dev \
    zlib-dev \
    bash \
    linux-headers

RUN python3 -m pip install --upgrade pip numpy pybind11 wheel setuptools

RUN git clone https://github.com/tensorflow/tensorflow.git \
    && cd tensorflow \
    && git checkout v2.8.0

# 38 cd tensorflow/
# 44 bash tensorflow/lite/tools/pip_package/build_pip_package_with_cmake.sh