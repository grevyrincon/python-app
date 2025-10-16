from fastapi import FastAPI, HTTPException
from pymongo.errors import PyMongoError
from db import names_collection, client  

app = FastAPI()

@app.get("/")
def root():
    return {"msg": "API is running"}

@app.get("/health")
def healthcheck():
    try:
        client.admin.command("ping")
        return {"status": "ok", "database": "connected"}
    except PyMongoError as e:
        raise HTTPException(status_code=503, detail=f"Database not reachable: {str(e)}")

# CRUD 
@app.post("/names/{name}")
def create_name(name: str):
    if names_collection.find_one({"name": name}):
        raise HTTPException(status_code=400, detail="Name already exists")
    names_collection.insert_one({"name": name})
    return {"msg": f"Name {name} created"}

@app.get("/names")
def read_names():
    all_names = list(names_collection.find({}, {"_id": 0, "name": 1}))
    return {"names": [n["name"] for n in all_names]}
