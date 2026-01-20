from google.cloud import firestore


db = firestore.Client(project="practice-ff6c4")

# city = db.collection("cities").document("DC")
# # Use the update() method
# city.update({"capital": True})


# # To set a field in document to a server timestamp which tracks when the server receives the update.
# city_ref = db.collection("cities").document("LA")
# city_ref.update({"timestamp": firestore.SERVER_TIMESTAMP})


# # Update fields in nested objects
# frank_ref = db.collection("users").document("frank")
# frank_ref.set(
#     {
#         "name": "Frank",
#         "favorites": {"food": "Pizza", "color": "Blue", "subject": "Recess"},
#         "age": 12,
#     }
# )
# # Update age and favorite color
# frank_ref.update({"age": 13, "favorites.color": "Red"})


# city_ref = db.collection("cities").document("LA")
# # Atomically add a new region to the 'regions' array field.
# city_ref.update({"regions": firestore.ArrayUnion(["greater_virginia"])})
# # Atomically remove a region from the 'regions' array field.
# city_ref.update({"regions": firestore.ArrayRemove(["east_coast"])})


# # Increment a numeric value
# washington_ref = db.collection("cities").document("LA")
# washington_ref.update({"population": firestore.Increment(50)})



""" Updating data with transactions """
transaction = db.transaction()

city = db.collection("cities").document("LB")

@firestore.transactional
def update_in_transaction(transaction, city):
    snapshot = city.get(transaction=transaction)
    try:
        new_population = snapshot.get("population") + 1
    except:
        return False

    # Passing information out of transactions
    if new_population < 1000000:
        transaction.update(city, {"population": new_population})
        return True
    return False

result = update_in_transaction(transaction, city)
if result:
    print("Population updated")
else:
    print("Sorry! Population is too big.")


"""
Batched writes---
- If you do not need to read any documents in your operation set, 
- can execute multiple write operations as a single batch that contains any combination of set(), update(), or delete() operations. 
"""
batch = db.batch()

# Set the data for NYC
nyc_ref = db.collection("cities").document("NYC")
batch.set(nyc_ref, {"name": "New York City"})

# Update the population for SF
sf_ref = db.collection("cities").document("LA")
batch.update(sf_ref, {"population": 1000000})

# Delete DEN
den_ref = db.collection("cities").document("DEN")
batch.delete(den_ref)

# Commit the batch
batch.commit()

