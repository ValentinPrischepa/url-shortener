import base64
import datetime
import hashlib

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from google.cloud import firestore

app = FastAPI()
db = firestore.Client()


def hash_url(url: str, length: int = 8) -> str:
    sha = hashlib.sha256(url.encode()).digest()
    code = base64.urlsafe_b64encode(sha).decode()[:length]
    return code


@app.post("/shorten")
def shorten(url: str):
    code = hash_url(url)
    ref = db.collection("urls").document(code)
    if not ref.get().exists:
        ref.set({
            "url": url,
            "created_at": datetime.datetime.utcnow().isoformat()
        })
    return {"short_url": f"https://your-service.run.app/{code}"}


@app.get("/{code}")
def redirect(code: str):
    doc = db.collection("urls").document(code).get()
    if doc.exists:
        long_url = doc.to_dict()["url"]
        return RedirectResponse(long_url)
    else:
        raise HTTPException(status_code=404, detail="Not found")
