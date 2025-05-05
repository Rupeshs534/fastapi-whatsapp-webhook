from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

@app.get("/send", response_class=HTMLResponse)
def send_page():
    return """
    <html><body>
    <h2>Send Message Form</h2>
    <form action="/webhook" method="post">
        Name: <input name="name"><br>
        Phone: <input name="phone"><br>
        Message: <textarea name="message"></textarea><br>
        <input type="submit" value="Send">
    </form></body></html>
    """

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.form()
    print("📩 Message received:", dict(data))
    return JSONResponse(content={"status": "received", "data": dict(data)})
