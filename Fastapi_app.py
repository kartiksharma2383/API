from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel 
from typing import List

app = FastAPI()

class ItemCreate(BaseModel):          # BaseModel is used to define the structure of the data we expect when creating an item. 
    text: str                    
    is_done: bool = False

class Item(ItemCreate):               # Item inherits from ItemCreate, which means it has all the fields of ItemCreate (text and is_done) plus an additional field
    id: int
    
items: List[Item] = []                # This is an in-memory list that will store our items. Each item in the list is an instance of the Item class, which includes an id, text, and is_done status.
current_id = 1                        # This variable is used to assign unique IDs to each item created. It starts at 1 and increments each time a new item is added to the list.

# Home route
@app.get("/")                        
def root():
    return {"message": "FastAPI is running"}

# Create Item
@app.post("/items", response_model = Item, status_code = 201)               # This endpoint allows clients to create a new item. It expects a JSON payload that matches the ItemCreate model (text and is_done). When a new item is created, it assigns a unique ID to the item, adds it to the items list, and returns the newly created item with a 201 status code indicating that the resource was successfully created.
def create_item(item: ItemCreate):                                          # The function takes an item of type ItemCreate as input, which is automatically validated by FastAPI based on the defined model. The function then creates a new Item instance, assigns it a unique ID, and appends it to the items list before returning the new item.
    global current_id                                                       # The global keyword is used to indicate that we want to modify the current_id variable defined outside the function. This allows us to keep track of the unique IDs for each item created across multiple function calls.  
    new_item = Item(id = current_id, **item.dict())                         # The **item.dict() syntax is used to unpack the fields of the item (text and is_done) into the new Item instance. This allows us to create a new Item with the same text and is_done values as the input item, while also assigning it a unique ID.
    current_id += 1                                                         # After creating the new item, we increment the current_id variable to ensure that the next item created will receive a unique ID. This way, each item in our list will have a distinct identifier.
    item.append(new_item)                                                   # We append the newly created item to the items list, which serves as our in-memory storage for all items. This allows us to keep track of all the items that have been created and perform operations on them (like retrieval, updating, toggling, and deletion) in subsequent API endpoints.
    return new_item                                                         # The function returns the newly created item, which includes its unique ID, text, and is_done status. This response will be sent back to the client that made the POST request to create the item.

# GET all items
@app.get("/items", response_model = List[Item])                             # This endpoint allows clients to retrieve a list of all items currently stored in the items list. The response model is defined as List[Item], which means that the endpoint will return a JSON array of Item objects, each containing an id, text, and is_done status.                 
def get_items():                                                            # The function simply returns the entire items list, which contains all the items that have been created. This allows clients to see all the items that are currently stored in the application.  
    return items                                                            # The function returns the items list, which is a collection of all the Item instances that have been created and stored in memory. 

# GET item by ID
@app.get("/items/{item_id}", response_model = Item)                             # This endpoint allows clients to retrieve a specific item by its ID. The response model is defined as Item, which means that the endpoint will return a JSON object representing the item with the specified ID.
def get_item(item_id: int):                                                     # The function takes an item_id as a path parameter as an integer.
    for item in items:                                                          # The function iterates through the items list to find an item with a matching ID. If it finds an item with the specified ID, it returns that item. 
        if item.id == item_id:                                                  # If the current item in the iteration has an ID that matches the item_id provided in the path parameter, we return that item as the response to the client. The returned item will include its id, text, and is_done status as defined in the Item model.
            return item                                                         # If the function finishes iterating through the items list without finding an item with the specified ID.
    raise HTTPException(status_code = 404, detail = "Item not found")           # This line is executed if the function does not find an item with the specified ID in the items list. It raises an HTTPException with a status code of 404 (Not Found) and a detail message "Item not found".

# PUT (Update)
@app.put("/items/{item_id}", response_model = Item)                                # This endpoint allows clients to update an existing item by its ID. The response model is defined as Item, which means that the endpoint will return a JSON object representing the updated item after the update operation is performed.  
def update_item(item_id: int, updated_item: ItemCreate):                           # The function takes an item_id as a path parameter and an updated_item of type ItemCreate as the request body. The updated_item contains the new text and is_done status that the client wants to set for the item with the specified ID.
    for index, item in enumerate(items):                                           # The function iterates through the items list using enumerate, which provides both the index and the item itself. This allows us to keep track of the position of each item in the list, which is necessary for updating the item in place if we find a match.
        if item.id == item_id:                                                     # If the current item in the iteration has an ID that matches the item_id provided in the path parameter, we proceed to update that item. We create a new Item instance called updated, which combines the existing item's ID with the new text and is_done values from the updated_item. 
            updated = Item(id = item_id, **updated_item.dict())                    # The **updated_item.dict() syntax is used to unpack the fields of the updated_item (text and is_done) into the new Item instance. This allows us to create a new Item with the same text and is_done values as the updated_item, while also keeping the same ID as the original item.
            items[index] = updated                                                 # We update the item in the items list at the current index with the new updated item. This effectively replaces the old item with the new one that has the updated text and is_done status.
            return updated                                                         # The function returns the updated item. This response will be sent back to the client that made the PUT request to update the item. 
        raise HTTPException(status_code = 404, detail = "Item not found")          # If the function finishes iterating through the items list without finding an item with the specified ID, it raises an HTTPException with a status code of 404 (Not Found) and a detail message "Item not found". This indicates to the client that the item they attempted to update does not exist in the items list. 
    
# TOGGLE item (Partial Update)
@app.patch("/items/{item_id}/toggle", response_model = Item)                      # The response model is defined as Item, which means that the endpoint will return a JSON object representing the updated item after the toggle operation is performed. The endpoint is accessed via a PATCH request (updates some field inside that item) to "/items/{item_id}/toggle", where {item_id} is the ID of the item to be toggled.
def toggle_item(item_id: int):                                                    # The function takes an item_id as a path parameter, which is used to identify the specific item that the client wants to toggle. 
    for item in items:                                                            # The function iterates through the items list to find an item with a matching ID. If it finds an item with the specified ID, it toggles the is_done status of that item (i.e., if is_done is True, it becomes False, and if it is False, it becomes True) and returns the updated item. 
        if item.id == item_id:                                                    # If the current item in the iteration has an ID that matches the item_id provided in the path parameter, we proceed to toggle that item. We change the is_done status of the item to its opposite value (if it was True, it becomes False, and if it was False, it becomes True).
            item.is_done = not item.is_done                                       # After toggling the is_done status, we return the updated item. This response will be sent back to the client that made the PATCH request to toggle the item. 
            return item                                                           # If the function finishes iterating through the items list without finding an item with the specified ID, it raises an HTTPException with a status code of 404 (Not Found) and a detail message "Item not found". 
    raise HTTPException(status_code = 404, detail = "Item not found")     

# DELETE item
@app.delete("/items/{item_id}")                                                   # This endpoint allows clients to delete a specific item by its ID. The endpoint is accessed via a DELETE request to "/items/{item_id}", where {item_id} is the ID of the item to be deleted. The function does not specify a response model, which means it will return a JSON object with a message and the deleted item if the deletion is successful, or an error message if the item is not found.
def delete_item(item_id: int):                                                    # The function takes an item_id as a path parameter, which is used to identify the specific item that the client wants to delete. 
    for index, item in enumerate(items):                                          # The function iterates through the items list using enumerate, which provides both the index and the item itself. This allows us to keep track of the position of each item in the list, which is necessary for removing the item from the list if we find a match.
        if item.id == item_id:                                                    # If the current item in the iteration has an ID that matches the item_id provided in the path parameter, we proceed to delete that item. We use the pop method of the list to remove the item at the current index and store it in a variable called deleted_item. This allows us to return information about the deleted item in the response.
            deleted_item = items.pop(index)                                       # After deleting the item from the items list, we return a JSON object containing a message indicating that the item was deleted and the details of the deleted item. This response will be sent back to the client that made the DELETE request to delete the item.
            return {"message": "Item deleted", "item": deleted_item}              # If the function finishes iterating through the items list without finding an item with the specified ID, it raises an HTTPException with a status code of 404 (Not Found) and a detail message "Item not found". 
    raise HTTPException(status_code = 404, detail = "Item not found")     