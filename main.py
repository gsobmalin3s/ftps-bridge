import os
import ssl
import ftplib
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# Config desde variables de entorno
FTPS_HOST     = os.environ.get("FTPS_HOST", "")
FTPS_PORT     = int(os.environ.get("FTPS_PORT", "21"))
FTPS_USER     = os.environ.get("FTPS_USER", "")
FTPS_PASS     = os.environ.get("FTPS_PASS", "")
FTPS_DIR      = os.environ.get("FTPS_DIR", "/")
API_KEY       = os.environ.get("API_KEY", "demo-key-123")

@app.get("/")
def health():
    return {"status": "ok", "service": "ftps-bridge"}

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    x_api_key: str = Header(default=None)
):
    # Validar API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Contexto TLS (acepta certificados autofirmados)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        ftp = ftplib.FTP_TLS(context=ctx)
        ftp.connect(FTPS_HOST, FTPS_PORT, timeout=15)
        ftp.login(FTPS_USER, FTPS_PASS)
        ftp.prot_p()  # cifrado en transferencia de datos

        if FTPS_DIR != "/":
            ftp.cwd(FTPS_DIR)

        file_data = await file.read()
        import io
        ftp.storbinary(f"STOR {file.filename}", io.BytesIO(file_data))
        ftp.quit()

        return JSONResponse({"status": "ok", "file": file.filename})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
