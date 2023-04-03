FROM andres77872/ubuntu_minimal_search:23.04-17322

#RUN apt-get update \
#    && apt-get install -y ca-certificates tzdata \
#    && rm -rf /var/lib/apt/lists/*

EXPOSE 6333
EXPOSE 6334
EXPOSE 5000

ENV TZ=Etc/UTC \
    RUN_MODE=production


WORKDIR /api

COPY qdrant /api/qdrant
COPY src /api/src
COPY requirements.txt /api

RUN pip install -r requirements.txt

CMD python3.10 -m uvicorn src.main:app --host 0.0.0.0 --port 5000

#CMD ["./qdrant"]








