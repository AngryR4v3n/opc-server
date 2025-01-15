FROM python:3.10.15-bullseye
WORKDIR /opt/requirements.txt
COPY requirements.txt .
COPY opc_ua_unified_namespace.py .
ARG FILENAME
ARG FREQUENCY
COPY ${FILENAME} .
RUN pip install -r requirements.txt
ENV OPC_STRUCTURE=${FILENAME}
ENV TAG_FREQUENCY=${FREQUENCY}
ENTRYPOINT ["python", "opc_ua_unified_namespace.py"]