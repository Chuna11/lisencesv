# Lisencesv - Deploy Railway

## Chi can 3 file (KHONG can license_key.py nua):
- `license_server.py` - Doc lap, tu chua logic verify
- `requirements.txt` - flask + gunicorn
- `Procfile` - web: gunicorn -w 1 -b 0.0.0.0:$PORT license_server:app

## requirements.txt
```
flask>=3.0.0
gunicorn
```

## Sau deploy
- GET https://...railway.app/ -> {"ok":true,"date":"YYYYMMDD",...}
- Neu 404: kiem tra Root Directory, Procfile
