from concurrent.futures.process import _chain_from_iterable_of_lists
import os
import sys
import datetime
import queue

# dataset = sys.argv[1]

from google.cloud import bigtable
from google.cloud.bigtable import column_family
from google.cloud.bigtable import row_filters

import threading

PROJECT_ID = "ds-final-gotcha"
INSTANCE_ID = "ds-final-instance"
TABLE_ID = "ds-final-table"

class BigtableThread(threading.Thread):
    def __init__(self, queue: queue.Queue, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(BigtableThread,self).__init__()
        self.target = target
        self.name = name
        self.q = queue
        return

    def run(self):

        print("Connecting the {} project...".format(PROJECT_ID))
        client = client = bigtable.Client(project=PROJECT_ID, admin=True)
        print("Connected {} project!".format(PROJECT_ID))
        print("Connecting the {} instance...".format(INSTANCE_ID))
        instance = client.instance(INSTANCE_ID)
        print("Connected {} instance!".format(INSTANCE_ID))
        print("Creating the {} table...".format(TABLE_ID))
        table = instance.table(TABLE_ID)
        print("Created {} table!".format(TABLE_ID))

        print("Creating column family cf1 with Max Version GC rule...")
        # Create a column family with GC policy : most recent N versions
        # Define the GC policy to retain only the most recent 2 versions
        max_versions_rule = column_family.MaxVersionsGCRule(1)
        column_family_id = "attributes"
        column_families = {column_family_id: max_versions_rule}
        if not table.exists():
            table.create(column_families=column_families)
        else:
            print("Table {} already exists.".format(TABLE_ID))

        while True:
            # column = "value".encode()
            if not self.q.empty():
                row = self.q.get()

                for i in range(len(row)):
                    row[i] = str(row[i])

                row[-1] = row[-1].replace(" ", "|")
                value = row[4] + "#" + row[6] + "#" + row[7] \
                    + "#" + row[8] + "#" + row[9] + "#" + row[10] \
                    + "#" + row[11] + "#" + row[12] + "#" +row[13] \
                    + "#" + row[14] + "#" + row[15] + "#" + row[16] \
                    + "#" + row[18] + "#" + row[19]

                row_key = (row[-1] + "#" + row[4] + "#" + row[5] + "#" + row[14] + "#" + row[-3]).encode()
                gen = table.direct_row(row_key)
                gen.set_cell(column_family_id, "acqic",
                    row[0], timestamp=datetime.datetime.utcnow())
                gen.set_cell(column_family_id, "bacno",
                    row[1], timestamp=datetime.datetime.utcnow())
                gen.set_cell(column_family_id, "cano",
                    row[2], timestamp=datetime.datetime.utcnow())
                gen.set_cell(column_family_id, "Amount",
                    row[3], timestamp=datetime.datetime.utcnow())
                gen.set_cell(column_family_id, "Country",
                    row[-5], timestamp=datetime.datetime.utcnow())
                gen.set_cell(column_family_id, "Coin",
                    row[5], timestamp=datetime.datetime.utcnow())
                gen.set_cell(column_family_id, "Fraud",
                    row[-2], timestamp=datetime.datetime.utcnow())
                gen.set_cell(column_family_id, "Time",
                    row[-1], timestamp=datetime.datetime.utcnow())
                gen.set_cell(column_family_id, "other-data",
                    value, timestamp=datetime.datetime.utcnow())

                table.mutate_rows([gen])

#  cano,conam,contp,csmcu,ecfg,etymd,
#  flbmk,flg_3dsmk,hcefg,insfg,iterm,
#  mcc,mchno,ovrlt,scity,stocn,stscd,
#  fraud_ind,conam_after_std

# acqic,bacno,cano,conam,contp,csmcu,
# ecfg,etymd,flbmk,flg_3dsmk,hcefg,
# insfg,iterm,mcc,mchno,ovrlt,scity,
# stocn,stscd,txkey,fraud_ind,time

# CMD = "cbt createtable final-table"
    
# print(CMD)
# os.system(CMD)

# CMD = "cbt createfamily final-table attribute"
    
# print(CMD)
# os.system(CMD)

# with open(dataset) as f:
#     for line in f.read().splitlines()[1:]:
#         [serial, id, bank, bankAccount, cardNum, tradeAmount, type, currency, \
#         transacAnno, transacType, fallBacMark, flg_3dsmk, paymentType, insfg, \
#         iterm, mcc, mchno, ovrlt, scity, stocn, stscd, txkey, \
#         fraud_ind, time] = line.split(",")

#         time = time.replace(" ", "#")

#         CMD = "cbt set final-table " + time + "#" + bank + "#" + bankAccount + "#" + cardNum \
#             + " attribute:value=" + tradeAmount + "#" + type + "#" + currency + "#" + transacAnno + "#" + transacType \
#             + "#" + fallBacMark + "#" + flg_3dsmk + "#" + paymentType + "#" + insfg + "#" + iterm + "#" + mcc \
#             + "#" + mchno + "#" + ovrlt + "#" + scity + "#" + stocn + "#" + stscd + "#" + txkey + "#" + fraud_ind
#         print(CMD)
#         os.system(CMD)


# if __name__ == "__main__":
#     inputDataToBigTable(dataset)
