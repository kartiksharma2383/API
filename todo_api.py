# This code defines a complete CRUD (Create, Read, Update, Delete) API for managing todo items using FastAPI.
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field     # BaseModel from pydantic: Used to define request/response data models with type validation, Field: Used to add validation rules (e.g. length) and metadata (like description).
from typing import Optional, List         # Optional: Used to indicate that a field is optional, List: Used to specify a list of items of a certain type.
from enum import IntEnum                  # IntEnum: Used to create enumerated constants with integer values.

api = FastAPI(title = "Todo API")

class Priority(IntEnum):                  # Define priority levels as integers using IntEnum to ensure each level has a specific integer value.
    low = 3
    medium = 2
    high = 1

class TodoBase(BaseModel):                                                                                  # min_length, max_length: validation rules for string fields.
    todo_name: str = Field(..., min_length = 3, max_length = 512, description = "Name of the todo item")    # Field(...): Required field or todo_name.
    todo_description: str = Field(..., description = "Description of the todo item")                        # Field(...): Required field or todo_description.
    priority: Priority = Field(default = Priority.low, description = "Priority of the todo item")           # Field(...): Field with a default value of Priority.low.

class TodoCreate(TodoBase):                                                      # Used specifically when a new todo is being created.
    pass

class TodoUpdate(BaseModel):                                                     # Used for updating an existing todo.
    todo_name: Optional[str] = Field(None, min_length = 3, max_length = 512)     # Optional field for todo_name.
    todo_description: Optional[str] = None                                       # Optional field for todo_description.
    priority: Optional[Priority] = None                                          # Optional field for priority.

class Todo(TodoBase):                                                            # Represents a complete todo item with an ID.
    todo_id: int

@api.get("/")                                                                    # Defines a GET route at /.
def home():                                                                      # Defines the home endpoint of the API.
    return {"message": "Your FastAPI Todo API is running"}

all_todos: List[Todo] = [
    Todo(todo_id = 1, todo_name = "Exercise", todo_description = "Gym", priority = Priority.medium),
    Todo(todo_id = 2, todo_name = "Read", todo_description = "Library", priority = Priority.low),
    Todo(todo_id = 3, todo_name = "Shop", todo_description = "Mall", priority = Priority.high),
    Todo(todo_id = 4, todo_name = "Study", todo_description = "College", priority = Priority.medium),
    Todo(todo_id = 5, todo_name = "Meditate", todo_description = "Session", priority = Priority.low)
]

@api.get("/todos/{todo_id}", response_model = Todo)     # Defines a GET route at /todos/{todo_id} that response or returns a single Todo object.
def get_todo(todo_id: int):                             # Defines the get_todo endpoint that accepts a todo_id path parameter.
    for todo in all_todos:                              # Check if the todo_id is valid (within the range of the all_todos list).
        if todo.todo_id == todo_id:                     # If current todo's ID is equal to the requested todo_id, then return that todo as API response.
            return todo                                                   
    raise HTTPException(status_code = 404, detail = "Todo not found")      # If not equal to any todo's ID, raise a 404 HTTPException.

@api.get("/todos", response_model = List[Todo])                            # Defines a GET route at /todos that response or returns a list of Todo objects.
def get_todos(first_n: Optional[int] = None):                              # Defines the get_todos endpoint that accepts an optional query parameter first_n.
    if first_n is not None:                                                # If first_n is provided, return a slice of the all_todos list from index 0 to first_n.
        return all_todos[:first_n]                                       
    return all_todos                                                       # If first_n is not provided, return the entire all_todos list.

@api.post("/todos", response_model = Todo)                                 # Defines a POST route at /todos that response or returns a single Todo object.
def create_todo(todo: TodoCreate):                                         # Defines the create_todo endpoint that accepts a TodoCreate object in the request body.
    new_todo_id = max([t.todo_id for t in all_todos], default = 0) + 1     # Generate a new todo_id by finding the maximum existing ID and adding 1.
    new_todo = Todo(
        todo_id = new_todo_id,
        todo_name = todo.todo_name,
        todo_description = todo.todo_description,
        priority = todo.priority
    )
    all_todos.append(new_todo)                                             # Add the new todo to the all_todos list.
    return new_todo

@api.put("/todos/{todo_id}", response_model = Todo)                        # Defines a PUT route at /todos/{todo_id} that response or returns a single Todo object.
def update_todo(todo_id: int, updated_todo: TodoUpdate):                   # Defines the update_todo endpoint that accepts a todo_id path parameter and a TodoUpdate object in the request body.
    for todo in all_todos:                                                 # Loop through all todos to find the one with the matching todo_id.
        if todo.todo_id == todo_id:                                        # If found, update the fields of the todo with the values from updated_todo if they are provided.
            if updated_todo.todo_name is not None:                         
                todo.todo_name = updated_todo.todo_name                    
            if updated_todo.todo_description is not None:                  
                todo.todo_description = updated_todo.todo_description      
            if updated_todo.priority is not None:                          
                todo.priority = updated_todo.priority
            return todo
    raise HTTPException(status_code = 404, detail = "Todo not found")      # If no matching todo_id is found, raise a 404 HTTPException.

@api.delete("/todos/{todo_id}", response_model = dict)                     # Defines a DELETE route at /todos/{todo_id} that response or returns a dictionary.
def delete_todo(todo_id: int):                                             # Defines the delete_todo endpoint that accepts a todo_id path parameter.
    for index, todo in enumerate(all_todos):                               # Loop through all todos with their index to find the one with the matching todo_id. 
        if todo.todo_id == todo_id:                                        # If found, remove the todo from the all_todos list and return the deleted todo in a dictionary.
            deleted_todo = all_todos.pop(index)                            
            return {"deleted": deleted_todo}                               
    raise HTTPException(status_code = 404, detail = "Todo not found")      # If no matching todo_id is found, raise a 404 HTTPException.     
