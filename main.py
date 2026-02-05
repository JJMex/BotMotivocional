import os
import requests
import textwrap
import random
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')
NOMBRE_LOGO = "logo_jjmex.png"

# APIs
URL_FRASE = "https://zenquotes.io/api/random"
URL_PEXELS_SEARCH = "https://api.pexels.com/v1/search"
URL_BACKUP = "https://picsum.photos/1080/1920"

# --- CEREBRO DE TEMAS ---
TEMAS = {
    "dinero": ["luxury lifestyle", "business success", "expensive car", "private jet", "money stack"],
    "éxito": ["mountain top view", "luxury office", "man in suit", "skyscraper"],
    "riqueza": ["gold bars", "luxury watch", "mansion", "finance"],
    "negocio": ["business meeting", "entrepreneur", "stock market", "ceo"],
    "ejercicio": ["gym workout", "fitness motivation", "runner", "weightlifting", "boxing"],
    "fuerza": ["lion face", "bodybuilder", "crossfit"],
    "salud": ["healthy food", "yoga nature", "meditation"],
    "disciplina": ["alarm clock morning", "training hard"],
    "mente": ["chess board", "library", "brain"],
    "paz": ["sunset ocean", "forest path", "calm lake"],
    "amor": ["couple goals", "holding hands sunset"],
    "default": ["epic landscape", "majestic mountains", "sunrise clouds"]
}

def enviar_foto(image_bytes, caption):
    if not TOKEN or not CHAT_ID: return False # Si no hay llaves, falla
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('motivacion.jpg', image_bytes)}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        response = requests.post(url, files=files, data=data, timeout=20) # Timeout aumentado
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error Telegram: {response.text}")
            return False
    except Exception as e: 
        print(f"Excepción Telegram: {e}")
        return False

tema_actual = "Inspiración"

def obtener_imagen_inteligente(frase_es):
    global tema_actual
    frase_low = frase_es.lower()
    
    busqueda = random.choice(TEMAS["default"])
    tema_actual = "Motivación"
    
    for palabra_clave, busquedas_posibles in TEMAS.items():
        if palabra_clave in frase_low and palabra_clave != "default":
            busqueda = random.choice(busquedas_posibles)
            tema_actual = palabra_clave.capitalize()
            break
            
    print(f"Tema: {tema_actual} | Buscando: '{busqueda}'")

    try:
        headers = {'Authorization': PEXELS_KEY}
        params = {'query': busqueda, 'orientation': 'portrait', 'per_page': 5} 
        response = requests.get(URL_PEXELS_SEARCH, headers=headers, params=params, timeout=15)
        data = response.json()
        
        if 'photos' in data and len(data['photos']) > 0:
            foto = random.choice(data['photos'])
            return Image.open(BytesIO(requests.get(foto['src']['large2x'], timeout=15).content))
        else:
            raise Exception("Sin resultados Pexels")
    except Exception as e:
        print(f"⚠️ Usando respaldo ({e})")
        return Image.open(BytesIO(requests.get(URL_BACKUP, timeout=15).content))

def crear_poster():
    # 1. Obtener Frase
    try:
        data = requests.get(URL_FRASE, timeout=10).json()[0]
        frase_en = data['q']
        autor = data['a']
        frase_es = GoogleTranslator(source='auto', target='es').translate(frase_en)
    except:
        frase_es = "La perseverancia es fallar 19 veces y tener éxito la vigésima."
        autor = "Julie Andrews"

    # 2. Imagen y Diseño
    img = obtener_imagen_inteligente(frase_es)
    img = img.resize((1080, 1920)) 
    img = img.filter(ImageFilter.GaussianBlur(3))
    W, H = img.size

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 85)
        font_autor = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
    except:
        font = ImageFont.load_default()
        font_autor = ImageFont.load_default()

    lineas = textwrap.wrap(frase_es, width=18)
    
    altura_bloque = 0
    espacio_linea = 20
    for linea in lineas:
        bbox = draw.textbbox((0, 0), linea, font=font)
        altura_bloque += (bbox[3] - bbox[1]) + espacio_linea

    y_text = (H - altura_bloque) / 2

    for linea in lineas:
        bbox = draw.textbbox((0, 0), linea, font=font)
        w_line = bbox[2] - bbox[0]
        h_line = bbox[3] - bbox[1]
        
        x = (W - w_line) / 2
        draw.text((x+5, y_text+5), linea, font=font, fill="black")
        draw.text((x, y_text), linea, font=font, fill="white")
        y_text += h_line + espacio_linea

    y_text += 50
    bbox_a = draw.textbbox((0, 0), f"- {autor}", font=font_autor)
    w_a = bbox_a[2] - bbox_a[0]
    x_a = (W - w_a) / 2
    draw.text((x_a+3, y_text+3), f"- {autor}", font=font_autor, fill="black")
    draw.text((x_a, y_text), f"- {autor}", font=font_autor, fill="#dddddd")

    # Pegar Logo
    try:
        logo = Image.open(NOMBRE_LOGO).convert("RGBA")
        ancho_logo = int(W * 0.15)
        alto_logo = int((ancho_logo / logo.width) * logo.height)
        logo = logo.resize((ancho_logo, alto_logo), Image.LANCZOS)
        img.paste(logo, (W - ancho_logo - 50, H - alto_logo - 50), logo)
    except:
        draw.text((W/2 - 60, H - 150), "JJMex Motivation", font=font_autor, fill="white")

    # Preparar envío
    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    caption_final = f"🚀 <b>{frase_es}</b>\n\n#MenteYExito365 #{tema_actual}"
    
    # --- SISTEMA DE REINTENTOS (La parte robusta) ---
    max_intentos = 3
    for i in range(max_intentos):
        print(f"📤 Intento de envío {i+1}/{max_intentos}...")
        exito = enviar_foto(bio, caption_final)
        if exito:
            print("✅ ¡Enviado correctamente!")
            break
        else:
            print(f"⚠️ Falló el envío. Reintentando en 30 segundos...")
            bio.seek(0) # Rebobinar la imagen para volver a leerla
            time.sleep(30) # Esperar antes de reintentar
    else:
        print("❌ Se acabaron los intentos. No se pudo enviar hoy.")

if __name__ == "__main__":
    # Bucle general por si falla la generación de imagen
    try:
        crear_poster()
    except Exception as e:
        print(f"Error crítico en el script: {e}")
        # Aquí podrías mandar un mensaje de error simple a Telegram si quisieras
