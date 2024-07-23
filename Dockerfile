FROM python:3.10-buster

WORKDIR /app

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

ENV PATH=/opt/conda/bin:$PATH

RUN conda install -c conda-forge conda-lock

# Install and activate pyrorisks environment

COPY pyrorisks.conda-lock.yml pyrorisks.conda-lock.yml

RUN conda-lock install --name pyrorisks pyrorisks.conda-lock.yml && conda clean -a

ENV CONDA_DEFAULT_ENV=pyrorisks
ENV PATH /opt/conda/envs/${CONDA_DEFAULT_ENV}/bin:$PATH
RUN echo "conda activate ${CONDA_DEFAULT_ENV}" >> ~/.bashrc

# Install poetry
RUN pip install poetry==1.8.1

# Set environment variables for poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/opt/conda/envs/${CONDA_DEFAULT_ENV} \
    PATH="/opt/conda/envs/${CONDA_DEFAULT_ENV}/bin:$PATH" \
    PYTHONPATH="/opt/conda/envs/${CONDA_DEFAULT_ENV}/lib/python3.10/site-packages:${PYTHONPATH}"

COPY app ./app
COPY pyrorisks ./pyrorisks
COPY pyproject.toml poetry.lock README.md ./

# Install pyrorisks package in pyrorisks conda environment
RUN poetry install

CMD ["bash"]
