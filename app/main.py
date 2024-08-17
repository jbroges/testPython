import io
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Response, HTTPException
import requests
from models import User
import fitz
import random
import json

app = FastAPI()
app.title = "Test de Pymupdf"

# Endpoint de la API
@app.get("/random_user")
async def get_random_user():
    # URL de la API
    url = "https://jsonplaceholder.typicode.com/users"
    ramdon_id_user = random.randint(1, 10)

    try:
        # Hacer la solicitud a la API
        response = requests.get(url)
        response.raise_for_status()  # Verificar si la respuesta es exitosa

        data = response.json()
        # Buscar el usuario con id=4 utilizando list comprehension
        user = [item for item in data if item['id'] == ramdon_id_user]

        # Validar la existencia del usuario (opcional)
        if not user:
            raise HTTPException(status_code=404, detail="User with id=4 not found")

        # Crear el modelo de usuario
        user_model = User(**user[0]).model_dump()  # Desempaquetar el diccionario de usuario

        return user_model

    except requests.RequestException as e:
        # Manejar errores de conexión u otros errores al hacer la solicitud
        error_message = f"Error making request: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)

    except HTTPException as he:
        # Manejar errores HTTP generados por FastAPI
        raise he


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    data = await  get_random_user()
    # Crear el directorio temporal si no existe
    os.makedirs("temp", exist_ok=True)

    # Guardar el archivo temporalmente
    with open(f"temp/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Abrir el PDF con PyMuPDF
    pdf_document = fitz.open(f"temp/{file.filename}")
    with open('settings.json', 'r', encoding='utf-8') as f:
        data_settings = json.load(f)
    # Map data to PDF fields (replace with your specific mapping)
    print(data_settings["form1"])
    field_map = data_settings["form1"]['field_map']

    sub_keys = data_settings["form1"]['sub_keys']

    page = pdf_document[0]

    for name, value in data.items():
        if name in field_map:
            field_name = field_map[name]
            field = page.search_for(field_name)
            positions = data_settings["form1"]['positions']
            if field:
                x, y = field[0][:2]  # Obteniendo las coordenadas x e y del campo
                page.insert_text((x+positions[name][0], y+positions[name][1]), value, fontsize=12, fill=(0, 0, 1))
        if name in sub_keys:
            for sub_name, sub_value in value.items():
                if sub_name in field_map:
                    field_name = field_map[sub_name]
                    field = page.search_for(field_name)
                    if field:
                        x, y = field[0][:2]  # Obteniendo las coordenadas x e y del campo
                        page.insert_text((x, y+30), sub_value, fontsize=12, fill=(0, 0, 1))
        
    output = io.BytesIO()
    pdf_document.save(output)
    output.seek(0)

    # Crear la respuesta de descarga
    response = Response(content=output.read())
    response.headers["Content-Disposition"] = "attachment; filename=nuevo_documento.pdf"
    response.headers["Content-Type"] = "application/pdf"

    return response