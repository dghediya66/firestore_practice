import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("practice-ff6c4-firebase-adminsdk-fbsvc-605ad32dd5.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


# Get all records from a collection
docs = db.collection("cities").stream()
for doc in docs:
    print(doc.id, doc.to_dict())


# Get one record by document ID
doc_ref = db.collection("cities").document("LA")
doc = doc_ref.get()
if doc.exists:
    print(doc.to_dict())
else:
    print("Document not found")


# Query records (WHERE clause)
docs = (
    db.collection("cities")
    .where("country", "==", "USA")
    # .filter("country", "==", "USA")
    .stream()
)
for doc in docs:
    print(doc.id, doc.to_dict())


# Order, limit, and pagination
docs = (
    db.collection("cities")
    # .order_by("created_at")
    .limit(10)
    .stream()
)
print(docs)


# Pagination example
first_page = db.collection("cities").order_by("created_at").limit(10).stream()
last_doc = list(first_page)[-1]

next_page = (
    db.collection("cities")
    .order_by("created_at")
    .start_after(last_doc)
    .limit(10)
    .stream()
)
# users = [doc.to_dict() for doc in db.collection("users").stream()]
