from fastapi import FastAPI, HTTPException     # HTTPException: Used to return HTTP errors (like 404 Not Found).
from pydantic import BaseModel                 # BaseModel from pydantic: Used to define request/response data models with type validation.

app = FastAPI()

class Item(BaseModel):
    text: str = None
    is_done: bool = False

items = []

@app.get("/")                     # Defines a GET route at /.
def root():                       # Defines the root endpoint of the API. If someone accesses the root URL, it will return {"Hello": "World"}.
    return {"Hello": "World"}

@app.post("/items")               # Defines a POST route at /items.
def create_item(item: Item):      # Defines the create_item endpoint that accepts an Item object in the request body.
    items.append(item)            # Add the received item to the items list.
    return items

@app.get("/items", response_model = list[Item])     # Defines a GET route at /items that response or returns a list of Item objects.
def list_items(limit: int = 10):                    # Defines the list_items endpoint that accepts an optional query parameter limit (default is 10).
    return items[0:limit]                           # Returns a slice of the items list from index 0 to limit.

@app.get("/items/{item_id}", response_model = Item)   # Defines a GET route at /items/{item_id} that response or returns a single Item object.
def create_item(item_id: int) -> Item:                # Defines the create_item endpoint that accepts an item_id path parameter.
    if item_id < len(items):                          # Check if the item_id is valid (within the range of the items list).
        return items[item_id]
    else:
        raise HTTPException(status_code = 404, detail = "Item not found")     # If the item_id is invalid, raise a 404 HTTPException with the message "Item not found".
    