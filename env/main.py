from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import SessionLocal, engine
import models

# 🔹 DB tables create करो
models.Base.metadata.create_all(bind=engine)

# 🔹 FastAPI app बनाओ
app = FastAPI()

# 🔹 DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔹 Pydantic schema (for validation and response)
class UserSchema(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

# 🔹 Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI + SQLite Demo!"}

# 🔹 Get all users
@app.get("/users", response_model=List[UserSchema])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# 🔹 Create new user
@app.post("/users", response_model=UserSchema)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = models.User(id=user.id, name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 🔹 Update user
@app.put("/users/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    return db_user

# 🔹 Delete user
@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": f"User with id {user_id} deleted"}
from fastapi.responses import HTMLResponse
from fastapi import Request

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("📩 Webhook Data Received:", data)
    return {"status": "received", "data": data}
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI()

# ✅ HTML Page to Send WhatsApp-style message
@app.get("/send", response_class=HTMLResponse)
def send_page():
    return """
    <html>
    <head><title>Send Message</title></head>
    <body>
        <h2>📩 Send Message Form</h2>
        <form action="/webhook" method="post">
            <label>Name:</label><br>
            <input type="text" name="name"><br><br>
            <label>Phone:</label><br>
            <input type="text" name="phone"><br><br>
            <label>Message:</label><br>
            <textarea name="message"></textarea><br><br>
            <input type="submit" value="Send">
        </form>
    </body>
    </html>
    """

# ✅ Webhook endpoint (accepts form data or raw JSON)
@app.post("/webhook")
async def receive_message(request: Request):
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            data = await request.json()
        else:
            data = await request.form()

        name = data.get("name")
        phone = data.get("phone")
        message = data.get("message")

        print(f"📬 Message received from {name} ({phone}): {message}")
        return JSONResponse(content={"status": "success", "name": name, "phone": phone, "message": message})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
