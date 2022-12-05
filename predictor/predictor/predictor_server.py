from concurrent import futures
import logging

from bigtable import BigtableThread

import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

import queue
import os
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)
BUF_SIZE = 300000
q = queue.Queue(BUF_SIZE)
date = ""

# class Predictor(credit_predict_pb2_grpc.PredictorServicer):
#     def __init__(self) -> None:
#         super().__init__()
#         self.date = ""

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/getData',  methods=["POST", "GET"])
def getData():
    if request.method == "POST":
        data = request.files['inputFile']
        y = Predict(data)
        return render_template("home.html")

        
def Predict(data):

    model = GetModel()

    data = pd.read_csv(data, index_col=[0])
    X_test, _ = Preprocessing(pd.DataFrame(data))
    result = model.predict(X_test)

    data['fraud_ind'] = result

    for id, row in data.iterrows():
        q.put(row.tolist())

    return result

def GetModel():
    global date
    if date != str(datetime.date(datetime.now())):
        date = str(datetime.date(datetime.now()))
        pwd = os.getcwd()
        popen = subprocess.Popen(["./getmodel_client"], stdout=subprocess.PIPE)
        popen.wait()

    return joblib.load('./model.sav')

def Preprocessing(df: pd.DataFrame):

    df.drop(columns=['acqic', 'bacno', 'txkey', 'time'], inplace=True)

    cate_feat = ['ecfg', 'flbmk', 'flg_3dsmk', 'insfg', 'ovrlt']
    for column in df.columns:
        if column in cate_feat:
            df[column] = df[column].replace(['N','Y',''],[0,1,2])
        else:
            df[column].apply(lambda x: float(x))
    
    scaler = StandardScaler()
    scaler.fit(df[['conam']])
    df[['conam_after_std']] = scaler.transform(df[['conam']])

    X_test = df.drop(columns=['fraud_ind', 'cano', 'conam'])
    y_test = df['fraud_ind']

    return X_test, y_test

# def serve():
#     MAX_MESSAGE_LENGTH = 256*1024*1024
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=5), options=[
#         ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
#         ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
#     ])
#     credit_predict_pb2_grpc.add_PredictorServicer_to_server(Predictor(), server)
#     server.add_insecure_port('localhost:50051')

#     print("server started.")

#     server.start()
#     server.wait_for_termination()

if __name__ == '__main__':
    c = BigtableThread(name='consumer', queue=q)
    c.start()
    app.run(debug=True, host="0.0.0.0", port=8000)
    logging.basicConfig()