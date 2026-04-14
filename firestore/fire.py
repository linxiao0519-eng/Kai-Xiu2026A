import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "陳楷修",
  "mail": "Linxiao0519@gmail.com",
  "lab": 6767
}

#doc_ref = db.collection("靜宜資管2026a").document("CKX1")
#doc_ref.set(doc)

#collection_ref = db.collection("靜宜資管2026a")
#collection_ref.add(doc)

docs = [
{
  "name": "陳武林",
  "mail": "wlchen@pu.edu.tw",
  "lab": 665
},
{
  "name": "王耀德",
  "mail": "ytwang@pu.edu.tw",
  "lab": 686
},

{
  "name": "康贊清",
  "mail": "tckang@pu.edu.tw",
  "lab": 783
}

]

collection_ref = db.collection("靜宜資管2026a")
for doc in docs:
  collection_ref.add(doc)
