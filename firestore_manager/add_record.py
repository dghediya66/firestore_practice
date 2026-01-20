import datetime
# from client import db
from google.cloud import firestore

db = firestore.Client(project="practice-ff6c4")

collection_name = "cities"
data = {"name": "Los Angeles", "state": "CA", "country": "USA"}

# Use the set() method
""" 
If the document does not exist, it will be created. 
If the document does exist, its contents will be overwritten with the newly provided data, 
unless specify that the data should be merged into the existing document
"""
db.collection(collection_name).document("LA").set(data)


# To merged into the existing document
city = db.collection(collection_name).document("BJ")
city.set({"capital": True}, merge=True)


# Firestore support many types of data types
data = {
    "stringExample": "Hello, World!",
    "booleanExample": True,
    "numberExample": 3.14159265,
    "dateExample": datetime.datetime.now(tz=datetime.timezone.utc),
    "arrayExample": [5, True, "hello"],
    "nullExample": None,
    "objectExample": {"a": 5, "b": True},
}

db.collection("data").document("one").set(data)


""" 
Using Map or Dictionary objects to represent your documents is often inconvenient, 
so Firestore supports writing documents with custom classes. 
Firestore converts the objects to supported data types.
"""
class City:
    def __init__(self, name, state, country, capital=False, population=0, regions=[]):
        self.name=name
        self.state = state
        self.country = country
        self.capital = capital
        self.population = population
        self.regions = regions

    @staticmethod
    def from_dict(source):
        return City(
            name=source.get("name"),
            state=source.get("state"),
            country=source.get("country"),
            capital=source.get("capital", False),
            population=source.get("population", 0),
            regions=source.get("regions", []),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "state": self.state,
            "country": self.country,
            "capital": self.capital,
            "population": self.population,
            "regions": self.regions,
        }

    def __repr__(self):
        return f"City(\
                name={self.name}, \
                country={self.country}, \
                population={self.population}, \
                capital={self.capital}, \
                regions={self.regions}\
            )"
    
city = City(name="Ahmedabad", state="Gujarat", country="India")
db.collection(collection_name).document("Ah").set(city.to_dict())


# add() method
""" 
If there isn't a meaningful ID for the document, Firestore can auto-generate an ID for you. 
can call the following language-specific add() methods
"""
city = {"name": "Tokyo", "country": "Japan"}
update_time, city_ref = db.collection(collection_name).add(city)
print("update_time, city_ref ---", update_time, city_ref.id) # 2026-01-19 11:58:52.797664+00:00 zSgozHXBgI4k24HTUQ3M


# to create a document reference with an auto-generated ID, then use the reference later
new_city_ref = db.collection(collection_name).document()
# later, 
new_city_ref.set(
    {
        ...
    }
)
