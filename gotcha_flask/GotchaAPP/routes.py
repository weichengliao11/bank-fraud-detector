import pandas as pd
import numpy as np
from flask import render_template, request
from GotchaAPP import db, clf, app
from GotchaAPP import Fraud
from google.cloud import bigtable
import google.cloud.bigtable.row_filters as row_filters


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        data = pd.read_csv(request.files['fileupload'], index_col=[0])
        X = data.drop(columns=['fraud_ind']).iloc[:100]
        X_test = data.drop(columns=['fraud_ind', 'cano', 'conam']).iloc[:100]
        X_predict = clf.predict(X_test)
        fraud_index = np.where(X_predict == 1)[0].tolist()

        count = 0
        for index, case in X.iterrows():
            if(count in fraud_index):
                new_case = Fraud(
                    cano=case['cano'], amount=case['conam'], fraud_label=True)
            else:
                new_case = Fraud(
                    cano=case['cano'], amount=case['conam'], fraud_label=False)
            try:
                db.session.add(new_case)
                db.session.commit()
            except:
                return 'There was an issue adding your task'
            count += 1

        fraud_case = Fraud.query.order_by(Fraud.time).all()

        db.session.query(Fraud).delete()
        db.session.commit()
        return render_template('result.html', cases=fraud_case)


@app.route('/stats', methods=["POST"])
def show_stats():

    def print_row(row):
        print("Reading data for {}:".format(row.row_key.decode("utf-8")))
        for cf, cols in sorted(row.cells.items()):
            print("Column Family {}".format(cf))
            for col, cells in sorted(cols.items()):
                for cell in cells:
                    labels = (
                        " [{}]".format(",".join(cell.labels)) if len(
                            cell.labels) else ""
                    )
                    print(
                        "\t{}: {} @{}{}".format(
                            col.decode("utf-8"),
                            cell.value.decode("utf-8"),
                            cell.timestamp,
                            labels,
                        )
                    )
        print("")

    client = bigtable.Client(project="ds-final-gotcha", admin=True)
    instance = client.instance("ds-final-instance")
    table = instance.table("ds-final-table")

    contp_selected = request.form.get('contp')
    csmcu_selected = request.form.get('csmcu')
    mchno_selected = request.form.get('mchno')

    rows = table.read_rows(
        filter_=row_filters.RowKeyRegexFilter(
            ".*#.*#{}#.*".format(csmcu_selected).encode("utf-8"))
    )

    cases = []
    for row in rows:
        print
        row_to_add = {}
        row_to_add["time"] = row.cell_value(
            "attributes", b"Time").decode('utf-8')[:10]
        row_to_add["Amount"] = row.cell_value(
            "attributes", b"Amount").decode('utf-8')
        row_to_add["Coin"] = row.cell_value(
            "attributes", b"Coin").decode('utf-8')
        row_to_add["Country"] = row.cell_value(
            "attributes", b"Country").decode('utf-8')
        row_to_add["Fraud"] = row.cell_value(
            "attributes", b"Fraud").decode('utf-8')
        row_to_add["acqic"] = row.cell_value(
            "attributes", b"acqic").decode('utf-8')
        row_to_add["bacno"] = row.cell_value(
            "attributes", b"bacno").decode('utf-8')
        row_to_add["cano"] = row.cell_value(
            "attributes", b"cano").decode('utf-8')
        cases.append(row_to_add)
    return render_template('result.html', cases=cases)
