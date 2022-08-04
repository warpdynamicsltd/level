FROM python:3.6.0-alpine
WORKDIR /
RUN mkdir level
COPY level /level
WORKDIR /level
RUN ./install.sh
RUN python3 --version
CMD ["level", "test"]
