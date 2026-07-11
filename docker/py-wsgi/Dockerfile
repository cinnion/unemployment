###########
# BUILDER #
###########
#
# Base stage for both building production artifacts and running tests
#

#
# Pull official base image
#
FROM python:3.13-slim-trixie AS builder

#
# Set the user
#
USER root

#
# Set work directory
#
WORKDIR /usr/src/app

#
# Install uv
#
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

#
# Set environment variables
#
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#
# Tell uv to install as non-editable and skip progress
#
ENV UV_NO_EDITABLE 1
ENV UV_SKIP_PROGRESS 1
ENV UV_CACHE_DIR "/var/cache/uv"

#
# Make APT really quiet
#
RUN cat << EOD > /etc/apt/apt.conf.d/99no-progress-no-cache
APT::Color "0";
APT::Keep-Downloaded-Packages "false";
Dpkg::Progress-Fancy "0";
Dpkg::Use-Pty "0";
EOD

#
# Install psycopg dependencies we will need to build the wheels and run tests
#
RUN apt-get update \
    && apt-get -y install gcc python3-dev git

#
# Copy our source in, as we need .git, packages.json, package-lock.json and
# webpack.config.js at a minimum for our builders, and test will want everything.
#
COPY . .

#
# Install our core dependencies
#
RUN --mount=type=cache,dst=/var/cache \
    uv sync --frozen --no-dev

############
# BUILDER2 #
############
#
# Base stage for both building production artifacts and running tests
#
FROM builder AS builder2

#
# Environment to point the NPM cache to our cache directory
#
ENV npm_config_cache="/var/cache/npm"

#
# Add our .venv to our path
#
ENV PATH=/usr/src/app/.venv/bin:${PATH}

#
# Install nodejs/npm, then install our node packages
#
RUN --mount=type=cache,dst=/var/cache \
    apt-get -y install nodejs npm && npm ci

#
# Build our webpack, which will drop build artifacts into the static subdirectory
#
RUN --mount=type=cache,dst=/var/cache \
    ./manage.py collectstatic_js_reverse && \
    npm run build

##########
# TESTER #
##########
#
# Test runner, for running pylint and the unit tests for coverage.
#
FROM builder AS tester

#
# Set work directory
#
WORKDIR /usr/src/app

#
# Tell uv to install as non-editable and skip progress
#
ENV UV_NO_EDITABLE 1
ENV UV_SKIP_PROGRESS 1
ENV UV_CACHE_DIR "/var/cache/uv"

#
# Add our .venv to our path
#
ENV PATH=/usr/src/app/.venv/bin:${PATH}

#
# Install our dev dependencies
#
RUN --mount=type=cache,dst=/var/cache \
    uv sync --frozen

##############
# Production #
##############

#
# pull official base image
#
FROM python:3.13-slim-trixie AS production

#
# Create the directory for the app user
#
RUN mkdir -p /var/www/job-application-tracker

#
# Create the app user
#
RUN adduser --system --group app

#
# Make APT really quiet
#
RUN cat << EOD > /etc/apt/apt.conf.d/99no-progress-no-cache
APT::Color "0";
APT::Keep-Downloaded-Packages "false";
Dpkg::Progress-Fancy "0";
Dpkg::Use-Pty "0";
EOD

#
# Create the appropriate directories
#
ENV HOME=/var/www/job-application-tracker
ENV APP_HOME=/var/www/job-application-tracker/web
RUN mkdir $APP_HOME

#
# Add our .venv to our path
#
ENV PATH=${APP_HOME}/.venv/bin:${PATH}

#
# Set work directory
#
WORKDIR $APP_HOME

#
# Install tzdata and set the timezone
#
RUN apt-get -y install tzdata \
    && cp /usr/share/zoneinfo/America/New_York /etc/localtime \
    && echo "America/New_York" > /etc/timezone
ENV TZ=America/New_York

#
# Install SSL certificates authorities
#
RUN apt-get -y install ca-certificates

#
# Install OS dependencies
#
RUN apt-get update && apt-get -y install libpq5

#
# Copy over build artifacts from builder2 and install our wheels
#
COPY --from=builder2 /usr/src/app/.venv .venv
COPY --from=builder2 /usr/src/app/static static

#
# Copy in the entrypoint script
#
COPY ./docker/py-wsgi/entrypoint.sh .
RUN chown root:root $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

#
# Copy in the project and clean up files like .git and docker, which are only
# needed for builds.
#
COPY . .
RUN rm -rf .git docker package.json package-lock.json pypackage.toml uv.lock webpack.config.js

#
# Chown all the files to the app user
#
RUN chown -R root:root $APP_HOME

#
# Run entrypoint.sh when we start up.
#
ENTRYPOINT [ "./entrypoint.sh" ]
