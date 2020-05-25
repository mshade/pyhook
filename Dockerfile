FROM python:3.8-alpine as builder
LABEL maintainer="mshade@mshade.org"
ENV PYTHONUNBUFFERED=1
COPY app/requirements.txt /app/
RUN pip install -U --no-cache pip && \
  pip install --no-cache -r /app/requirements.txt
USER 1000
WORKDIR /app


FROM builder as test
USER 0
RUN pip install mock pytest
USER 1000
COPY --chown=1000:1000 . /src
WORKDIR /src
RUN python -m pytest -v


FROM builder as final
COPY app/ /app/
EXPOSE 8080
CMD gunicorn -w 1 -b 0.0.0.0:8080 --access-logfile - app:app
