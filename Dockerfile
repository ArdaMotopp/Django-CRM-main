FROM ubuntu:20.04

# invalidate cache
ARG APP_NAME=backendapp

# test arg
RUN test -n "$APP_NAME"

# install system packages
RUN apt-get update -y
RUN apt-get install -y \
  python3-pip \
  python3-venv \
  build-essential \
  libpq-dev \
  libmariadbclient-dev \
  libjpeg62-dev \
  zlib1g-dev \
  libwebp-dev \
  curl  \
  vim \
  net-tools && \
  rm -rf /var/lib/apt/lists/*

# setup user
RUN useradd -ms /bin/bash ubuntu
USER ubuntu

# install app
RUN mkdir -p /home/ubuntu/"$APP_NAME"/"$APP_NAME"
WORKDIR /home/ubuntu/"$APP_NAME"/"$APP_NAME"
# Create venv
RUN python3 -m venv ../venv
ENV PATH="/home/ubuntu/$APP_NAME/venv/bin:${PATH}"

# Copy only requirements first (better cache)
COPY --chown=ubuntu:ubuntu requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Now copy the rest of the source
COPY --chown=ubuntu:ubuntu . .

# If this is a web app, expose a port (adjust as needed)
EXPOSE 8000
