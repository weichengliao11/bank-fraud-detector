FROM golang:1.18.3 AS interval

COPY . /

WORKDIR /model_server

RUN \
go mod tidy && \
cp -r ./getmodel /usr/local/go/src/ && \
cd ./getmodel_server && \
go build

FROM golang:1.18.3

COPY --from=interval /model_server/getmodel_server/getmodel_server /

EXPOSE 50052

CMD ["/getmodel_server"]
