FROM --platform=$BUILDPLATFORM python:3.12
ARG TARGETARCH
ARG BUILDPLATFORM
ARG TARGETPLATFORM
ARG TARGETOS

WORKDIR /mt-query-ms

COPY . /mt-query-ms

RUN pip install --upgrade pip

RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python", "app.py"]
