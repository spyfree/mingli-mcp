# Apify Actor image for the Mingli MCP server (Standby mode HTTP server)
FROM apify/actor-python:3.13

COPY . ./

RUN pip install --no-cache-dir . apify

ENV TRANSPORT_TYPE=http

CMD ["python3", "apify_main.py"]
