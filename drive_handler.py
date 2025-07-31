# drive_handler.py
import io
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def descargar_excel_drive(nombre_archivo, creds_path='AIzaSyAs-J76TVWwyur66m7UHhBnMElfGIDq01U'):
    """Descarga un archivo de Excel desde Drive y lo devuelve como DataFrame."""
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    # Autenticación
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    
    # Buscar archivo por nombre
    results = service.files().list(q=f"name='{nombre_archivo}'", fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if not items:
        raise FileNotFoundError(f"Archivo '{nombre_archivo}' no encontrado en Drive.")
    
    file_id = items[0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    # Descargar
    done = False
    while not done:
        _, done = downloader.next_chunk()
    
    fh.seek(0)
    return pd.read_excel(fh)
