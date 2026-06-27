###########
# BUILDER #
###########
#
# Base stage for both building production artifacts and running tests
#

#
# Pull official base image
#
FROM python:3.13-alpine AS builder

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

#
# Install psycopg dependencies we will need to build the wheels and run tests
#
RUN apk --no-progress update \
    && apk --no-progress add postgresql-dev gcc python3-dev git

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
# Install nodejs/npm, then install our node packages
#
RUN --mount=type=cache,dst=/var/cache \
    apk --no-progress add nodejs npm && npm ci

#
# Build our webpack, which will drop build artifacts into the static subdirectory
#
RUN --mount=type=cache,dst=/var/cache \
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
FROM python:3.13-alpine AS production

#
# Create the directory for the app user
#
RUN mkdir -p /var/www/job-application-tracker

#
# Create the app user
#
RUN addgroup -S app && adduser -S app -G app

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
RUN apk --no-progress add --no-cache tzdata \
    && cp /usr/share/zoneinfo/America/New_York /etc/localtime \
    && echo "America/New_York" > /etc/timezone
ENV TZ=America/New_York

#
# Install SSL certificates authorities
#
RUN apk --no-progress add --no-cache ca-certificates

#
# Install OS dependencies
#
RUN apk --no-progress update && apk --no-progress add libpq

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
