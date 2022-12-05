FROM golang:1.18.3

COPY . /

WORKDIR /

RUN \
tar xvf /go-ipfs_v0.12.2_linux-amd64.tar.gz && \
cp /go-ipfs/ipfs /usr/local/bin && \
ipfs init

EXPOSE 5001

CMD ["ipfs", "daemon"]
