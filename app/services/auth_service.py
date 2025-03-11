from app.database.connection import users_collection
from app.core.security import verify_password, create_access_token, get_password_hash
from bson.objectid import ObjectId

async def get_user_by_username(username: str) -> dict:
    user = await users_collection.find_one({"username": username})
    return user

async def authenticate_user(username: str, password: str) -> dict:
    user = await get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

async def register_data(username: str, email: str, password: str, conf_pass: str) -> dict:
    # Ensure the password and confirmation match
    if password != conf_pass:
        return {"error": "Passwords do not match"}
    
    # Check if a user with the same username already exists
    existing_user = await get_user_by_username(username)
    if existing_user:
        return {"error": "Username already exists"}
    
    # Hash the password for secure storage
    hashed_password = get_password_hash(password)
    
    # Prepare the new user document
    new_user = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password
    }
    
    # Insert the new user into the database
    result = await users_collection.insert_one(new_user)
    
    if result.inserted_id:
        # Optionally add the new user's ID to the returned dict
        new_user["id"] = str(result.inserted_id)
        return new_user
    
    return {"error": "Registration failed"}
