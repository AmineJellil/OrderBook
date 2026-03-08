FROM python:3.6.8

COPY /app /app
WORKDIR /app
RUN python3 -m pip install -r requirements.txt
EXPOSE 443
EXPOSE 80
ENV PYTHONPATH "${PYTHONPATH}:app"
ENTRYPOINT "./wrapper.sh"

