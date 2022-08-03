FROM alpine
RUN apk add --no-cache bash
RUN apk add --no-cache python3 py3-pip
WORKDIR /
RUN mkdir level
COPY level /level
WORKDIR /level
RUN ./install.sh
CMD ["level", "test"]
