import os
import requests
import textwrap
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')
NOMBRE_LOGO = "logo_jjmex.png" # El archivo que subiste

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
    if not TOKEN or not CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('motivacion.jpg', image_bytes)}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        requests.post(url, files=files, data=data)
    except Exception as e: print(f"Error TG: {e}")

tema_actual = "Inspiración"

def obtener_imagen_inteligente(frase_es):
    global tema_actual
    print(f"Analizando frase: '{frase_es}'")
    frase_low = frase_es.lower()
    
    busqueda = random.choice(TEMAS["default"])
    tema_actual = "Motivación"
    
    for palabra_clave, busquedas_posibles in TEMAS.items():
        if palabra_clave in frase_low and palabra_clave != "default":
            busqueda = random.choice(busquedas_posibles)
            tema_actual = palabra_clave.capitalize()
            break
            
    print(f"Tema: {tema_actual} | Buscando en Pexels: '{busqueda}'")

    try:
        headers = {'Authorization': PEXELS_KEY}
        params = {'query': busqueda, 'orientation': 'portrait', 'per_page': 5} 
        response = requests.get(URL_PEXELS_SEARCH, headers=headers, params=params, timeout=15)
        data = response.json()
        
        if 'photos' in data and len(data['photos']) > 0:
            foto = random.choice(data['photos'])
            return Image.open(BytesIO(requests.get(foto['src']['large2x']).content))
        else:
            raise Exception("Sin resultados en Pexels")
            
    except Exception as e:
        print(f"⚠️ Usando respaldo ({e})")
        return Image.open(BytesIO(requests.get(URL_BACKUP).content))

def crear_poster():
    # 1. Obtener Frase
    try:
        data = requests.get(URL_FRASE).json()[0]
        frase_en = data['q']
        autor = data['a']
        frase_es = GoogleTranslator(source='auto', target='es').translate(frase_en)
    except:
        frase_es = "La disciplina tarde o temprano vencerá a la inteligencia."
        autor = "Yokoi Kenji"

    # 2. Obtener Imagen de Fondo
    img = obtener_imagen_inteligente(frase_es)
    img = img.resize((1080, 1920)) 
    img = img.filter(ImageFilter.GaussianBlur(3))
    W, H = img.size

    # 3. Dibujar Texto
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

    # --- AQUÍ ESTÁ EL CAMBIO ---
    # 4. Pegar el Logo
    try:
        logo = Image.open(NOMBRE_LOGO).convert("RGBA")
        # Redimensionar logo (un 15% del ancho de la imagen)
        ancho_logo = int(W * 0.15)
        alto_logo = int((ancho_logo / logo.width) * logo.height)
        logo = logo.resize((ancho_logo, alto_logo), Image.LANCZOS)
        
        # Calcular posición: Esquina inferior derecha con margen
        margen = 50
        pos_x = W - ancho_logo - margen
        pos_y = H - alto_logo - margen
        
        # Pegar el logo sobre la imagen principal (usando su canal alfa como máscara)
        img.paste(logo, (pos_x, pos_y), logo)
        print("Logo pegado con éxito.")
    except Exception as e:
        print(f"No se pudo pegar el logo: {e}")
        # Si falla (ej. no subiste la imagen), escribe el texto de respaldo
        draw.text((W/2 - 60, H - 150), "JJMex Motivation", font=font_autor, fill="white")

    # 5. Enviar
    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    
    caption_final = f"🚀 <b>{frase_es}</b>\n\n#MenteYExito365 #{tema_actual}"
    enviar_foto(bio, caption_final)

if __name__ == "__main__":
    crear_poster()
