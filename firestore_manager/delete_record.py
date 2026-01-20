from google.cloud import firestore

db = firestore.Client(project="practice-ff6c4")


# Use the delete() method
db.collection("cities").document("DC").delete()


# To delete specific fields from a document, Use the firestore.DELETE_FIELD method
city_ref = db.collection("cities").document("BJ")
city_ref.update({"capital": firestore.DELETE_FIELD})


"""
To delete an entire collection or subcollection in Firestore, 
retrieve (read) all the documents within the collection or subcollection and delete them.
- If you have larger collections, you may want to delete the documents in smaller batches to avoid out-of-memory errors
"""
def delete_collection(coll_ref, batch_size):
    if batch_size == 0:
        return

    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)
    


