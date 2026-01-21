from fastapi import FastAPI, HTTPException, Query
from google.cloud import firestore
import schemas


app = FastAPI(title="Firestore CRUD operations")

firestore_db = firestore.Client(project="practice-ff6c4")
COLLECTION_NAME = "cities"


@app.post("/add-city")
def add_record(data: schemas.CityCreate):
    doc_ref = firestore_db.collection(COLLECTION_NAME).document()
    doc_ref.set(data.dict())
    return {
        "message": "New Record added successfully",
        "document_id": doc_ref.id
    }


@app.post("/add-city-with-id/{city_id}")
def add_record_with_id(city_id: str, data: schemas.CityCreate):
    firestore_db.collection(COLLECTION_NAME).document(city_id).set(data.dict())
    return {
        "message": "Record created/overwritten",
        "document_id": city_id
    }


@app.put("/cities/{city_id}/update-field")
def update_city_field(city_id: str, data: schemas.UpdateField):
    city_ref = firestore_db.collection(COLLECTION_NAME).document(city_id)

    if not city_ref.get().exists:
        raise HTTPException(status_code=404, detail="City not found")

    city_ref.update({data.field: data.value})
    return {"message": "Field updated successfully"}


# @app.put("/cities/{city_id}/timestamp")
# def update_timestamp(city_id: str):
#     city_ref = firestore_db.collection(COLLECTION_NAME).document(city_id)

#     if not city_ref.get().exists:
#         raise HTTPException(status_code=404, detail="City not found")

#     city_ref.update({"timestamp": firestore.SERVER_TIMESTAMP})
#     return {"message": "Timestamp updated"}


@app.put("/cities/{city_id}/regions/add")
def add_regions(city_id: str, data: schemas.RegionUpdate):
    city_ref = firestore_db.collection(COLLECTION_NAME).document(city_id)

    city_ref.update({
        "regions": firestore.ArrayUnion(data.regions)
    })

    return {"message": "Regions added"}


@app.put("/cities/{city_id}/regions/remove")
def remove_regions(city_id: str, data: schemas.RegionUpdate):
    city_ref = firestore_db.collection(COLLECTION_NAME).document(city_id)

    city_ref.update({
        "regions": firestore.ArrayRemove(data.regions)
    })

    return {"message": "Regions removed"}


@app.put("/cities/{city_id}/increment")
def increment_population(city_id: str, data: schemas.IncrementValue):
    city_ref = firestore_db.collection(COLLECTION_NAME).document(city_id)

    city_ref.update({
        "population": firestore.Increment(data.value)
    })

    return {"message": "Population incremented"}


@app.put("/cities/{city_id}/transaction/increment")
def transaction_increment(city_id: str):
    transaction = firestore_db.transaction()
    city_ref = firestore_db.collection(COLLECTION_NAME).document(city_id)

    @firestore.transactional
    def update_in_transaction(transaction, city_ref):
        snapshot = city_ref.get(transaction=transaction)

        if not snapshot.exists:
            raise HTTPException(status_code=404, detail="City not found")

        population = snapshot.get("population")
        if population >= 1_000_000:
            return False

        transaction.update(city_ref, {"population": population + 1})
        return True

    result = update_in_transaction(transaction, city_ref)

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Population too large to update"
        )

    return {"message": "Population updated via transaction"}


@app.get("/get-all-cities")
def get_all_cities():
    docs = firestore_db.collection(COLLECTION_NAME).stream()

    result = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)

    return result


@app.get("/get-city-by-id/{city_id}")
def get_city_by_id(city_id: str):
    doc = firestore_db.collection(COLLECTION_NAME).document(city_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="City not found")

    data = doc.to_dict()
    data["id"] = doc.id
    return data


@app.get("/search-cities-by-country")
def search_cities(country: str = Query(..., example="USA")):
    docs = (
        firestore_db.collection(COLLECTION_NAME)
        .where("country", "==", country)
        .stream()
    )

    result = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)

    return result


@app.get("/cities/limited")
def get_limited_cities(limit: int = Query(10, ge=1, le=100)):
    docs = (
        firestore_db.collection(COLLECTION_NAME)
        .limit(limit)
        .stream()
    )

    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]


@app.get("/cities/paginated")
def get_paginated_cities(
    limit: int = Query(10, ge=1, le=50),
    start_after_id: str | None = None
):
    query = firestore_db.collection(COLLECTION_NAME).order_by("name")

    if start_after_id:
        last_doc = (
            firestore_db.collection(COLLECTION_NAME)
            .document(start_after_id)
            .get()
        )
        if not last_doc.exists:
            raise HTTPException(status_code=404, detail="Invalid start_after_id")
        query = query.start_after(last_doc)

    docs = query.limit(limit).stream()

    result = []
    last_id = None

    for doc in docs:
        result.append({**doc.to_dict(), "id": doc.id})
        last_id = doc.id

    return {
        "data": result,
        "next_start_after_id": last_id
    }


@app.delete("/delete-cities/{city_id}")
def delete_city(city_id: str):
    doc_ref = firestore_db.collection("cities").document(city_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="City not found")

    doc_ref.delete()
    return {"message": f"City '{city_id}' deleted successfully"}


@app.patch("/cities/{city_id}/delete-field")
def delete_city_field(city_id: str, data: schemas.DeleteField):
    city_ref = firestore_db.collection("cities").document(city_id)

    if not city_ref.get().exists:
        raise HTTPException(status_code=404, detail="City not found")

    city_ref.update({
        data.field_name: firestore.DELETE_FIELD
    })

    return {
        "message": f"Field '{data.field_name}' deleted from city '{city_id}'"
    }


@app.delete("/delete-collections/{collection_name}")
def delete_collection(
    collection_name: str,
    batch_size: int = Query(50, ge=1, le=500)
):
    coll_ref = firestore_db.collection(collection_name)
    deleted_count = 0

    while True:
        docs = list(coll_ref.list_documents(page_size=batch_size))
        if not docs:
            break

        for doc in docs:
            print(f"Deleting doc {doc.id}")
            doc.delete()
            deleted_count += 1

    return {
        "message": f"Collection '{collection_name}' deleted",
        "deleted_documents": deleted_count
    }


# @app.delete("/collections/{collection_name}/force")
# def delete_collection_force(
#     collection_name: str,
#     confirm: bool = Query(False)
# ):
#     if not confirm:
#         raise HTTPException(
#             status_code=400,
#             detail="Set confirm=true to delete entire collection"
#         )

#     coll_ref = firestore_db.collection(collection_name)
#     deleted = 0

#     while True:
#         docs = list(coll_ref.list_documents(page_size=100))
#         if not docs:
#             break

#         for doc in docs:
#             doc.delete()
#             deleted += 1

#     return {"deleted_documents": deleted}

