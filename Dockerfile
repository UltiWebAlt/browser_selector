# syntax=docker/dockerfile:1
#
# Test image for the local-clone installation. The project is copied to a
# predictable path, and `install.sh` installs into the user's ~/.local/bin.
FROM debian:bookworm-slim

ARG APP_UID=1000
ARG APP_GID=1000

ENV DEBIAN_FRONTEND=noninteractive \
    HOME=/home/browser-selector \
    XDG_CONFIG_HOME=/home/browser-selector/.config \
    XDG_DATA_HOME=/home/browser-selector/.local/share \
    QT_QPA_PLATFORM=wayland

# Firefox supplies a real /usr/share/applications/firefox-esr.desktop entry
# for the selector.  The default configuration calls it firefox.desktop, so
# the install step below also creates an alias.  The remaining libraries are
# Qt's Wayland/OpenGL runtime dependencies; no compositor is started here.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        firefox-esr \
        libegl1 \
        libgl1 \
        libglib2.0-0 \
        libxkbcommon0 \
        libxkbcommon-x11-0 \
        libxcb-cursor0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-xinerama0 \
        libxcb-xkb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxi6 \
        libxrandr2 \
        libxtst6 \
        python3 \
        python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid "$APP_GID" browser-selector \
    && useradd --uid "$APP_UID" --gid "$APP_GID" --create-home browser-selector \
    && mkdir -p /workspace /run/user/1000 \
    && chown browser-selector:browser-selector /workspace /run/user/1000 \
    && ln -s firefox-esr.desktop /usr/share/applications/firefox.desktop

WORKDIR /workspace/browser-selector
COPY --chown=browser-selector:browser-selector . .

USER browser-selector

# Run the project's normal installer during the image build.  It writes the
# venv and desktop integration below $HOME, which makes their locations easy
# to inspect in a running container.
RUN ./install.sh

# A bind mount can replace the baked-in source while keeping its path stable:
#   -v "$(pwd):/workspace/browser-selector"
VOLUME ["/workspace/browser-selector"]

# With the Wayland socket and /dev/dri supplied by `docker run`, start the
# installed GUI immediately.  Use `--entrypoint bash` to inspect or rerun
# the installer interactively.
CMD ["/home/browser-selector/.local/bin/browser-selector/.venv/bin/browser-selector"]
