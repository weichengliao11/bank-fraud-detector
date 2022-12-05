FROM golang:1.18.3 AS interval

COPY ./getmodel_client /getmodel_client

WORKDIR /getmodel_client

RUN \
go mod tidy && \
cp -r ./getmodel /usr/local/go/src/ && \
cd ./getmodel_client && \
go build

FROM golang:1.18.3

COPY ./predictor /predictor
COPY --from=interval /getmodel_client/getmodel_client/getmodel_client /predictor

RUN \
apt-get update && \
apt-get install sudo -y && \
apt-get install curl -y && \
apt-get install python3 -y && \
apt-get install python3-pip -y && \
pip3 install google-cloud google-cloud-bigtable && \
pip3 install sklearn && \
pip3 install pandas && \
pip3 install flask

RUN \
apt-get install apt-transport-https ca-certificates gnupg -y && \
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
sudo apt-get update -y && sudo apt-get install google-cloud-cli -y

ENV GOOGLE_APPLICATION_CREDENTIALS=/predictor/tester.json

WORKDIR /predictor

EXPOSE 8000

CMD ["python3", "predictor_server.py"]