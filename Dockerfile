# syntax=docker/dockerfile:1

FROM python:3.11-alpine3.19
LABEL maintainer="rbravoh99@gmail.com"

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

#Copy requirement files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.txt /tmp/requirements.dev.txt

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Switch to the non-privileged user to run the application.
USER django-user

ENV PATH="/py/bin:$PATH"

# Copy the source code into the container.
COPY ./app /app
WORKDIR /app

# Expose the port that the application listens on.
EXPOSE 8000
