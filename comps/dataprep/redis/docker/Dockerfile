
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

FROM python:3.11-slim

ENV LANG C.UTF-8

RUN apt-get update -y && apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    libgl1-mesa-glx \
    libjemalloc-dev \
    vim

RUN useradd -m -s /bin/bash user && \
    mkdir -p /home/user && \
    chown -R user /home/user/

USER user

COPY comps /home/user/comps

RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r /home/user/comps/dataprep/redis/requirements.txt && \
    pip uninstall -y nvidia-cublas-cu12 nvidia-cuda-cupti-cu12 \
                    nvidia-cuda-nvrtc-cu12 nvidia-cuda-runtime-cu12 \
                    nvidia-cudnn-cu12 nvidia-cufft-cu12 nvidia-curand-cu12 \
                    nvidia-cusolver-cu12 nvidia-cusparse-cu12 \
                    nvidia-nccl-cu12 nvidia-nvjitlink-cu12 nvidia-nvtx-cu12 

ENV PYTHONPATH=$PYTHONPATH:/home/user

USER root

RUN mkdir -p /home/user/comps/dataprep/redis/uploaded_files && chown -R user /home/user/comps/dataprep/redis/uploaded_files

USER user

WORKDIR /home/user/comps/dataprep/redis

ENTRYPOINT ["python", "prepare_doc_redis.py"]

