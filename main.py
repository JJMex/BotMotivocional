import os
import requests
import textwrap
import random
import time
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')
NOMBRE_LOGO = "logo_jjmex.png"

URL_API_FRASE = "https://zenquotes.io/api/random"
URL_PEXELS = "https://api.pexels.com/v1/search"
URL_BACKUP = "https://picsum.photos/1080/1920"

TEMAS = {
    "riqueza": ["luxury lifestyle", "stacks of money", "expensive watch", "lamborghini"],
    "negocios": ["business man suit", "luxury office", "entrepreneur"],
    "poder": ["lion face dark", "chess king", "wolf dark", "eagle flying"],
    "gym": ["bodybuilder", "heavy weights", "boxing training", "fitness model"],
    "disciplina": ["alarm clock 5am", "working late night office", "samurai"],
    "default": ["stormy ocean", "mountain peak", "dark city night"]
}

# (Tu lista FRASES_MANUALES se mantiene igual, omitida por brevedad)
FRASES_MANUALES = ["El dinero no duerme, y tú tampoco deberías.", "Tu cuenta bancaria es el reflejo de tus hábitos."] 

def enviar_telegram(image_bytes, caption):
    if not TOKEN or not CHAT_ID: return False
    # Primero enviamos el mensaje de "Despertar" para consistencia
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={'chat_id': CHAT_ID, 'text': "📡 <i>Sincronizando banco de datos de mentalidad y generando activo visual...</i>", 'parse_mode': 'HTML'})
    time.sleep(2)
    
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('motivacion.jpg', image_bytes)}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        r = requests.post(url, files=files, data=data, timeout=30)
        return r.status_code == 200
    except: return False

def obtener_imagen(frase):
    frase_low = frase.lower()
    busqueda = "luxury" # Default
    
    # Lógica de detección de tema mejorada
    for categoria, terminos in TEMAS.items():
        if any(t in frase_low for t in terminos):
            busqueda = random.choice(TEMAS[categoria])
            break
            
    try:
        headers = {'Authorization': PEXELS_KEY}
        params = {'query': busqueda, 'orientation': 'portrait', 'per_page': 5}
        r = requests.get(URL_PEXELS, headers=headers, params=params, timeout=20).json()
        foto = random.choice(r['photos'])
        return Image.open(BytesIO(requests.get(foto['src']['large2x']).content)), busqueda.upper()
    except:
        return Image.open(BytesIO(requests.get(URL_BACKUP).content)), "ESTRATÉGICO"

def crear_poster():
    # 1. Frase y Autor
    if random.random() < 0.7:
        frase, autor = random.choice(FRASES_MANUALES), "JJMex"
    else:
        try:
            data = requests.get(URL_API_FRASE).json()[0]
            frase = GoogleTranslator(source='auto', target='es').translate(data['q'])
            autor = data['a']
        except: frase, autor = random.choice(FRASES_MANUALES), "JJMex"

    # 2. Imagen y Estética
    img, tema = obtener_imagen(frase)
    img = img.resize((1080, 1920))
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 110)) # Oscurecer para legibilidad
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # 3. Dibujar Texto
    draw = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 75)
    except: fnt = ImageFont.load_default()

    lineas = textwrap.wrap(frase, width=20)
    y_text = 800 # Centrado aprox
    for l in lineas:
        w, h = draw.textbbox((0, 0), l, font=fnt)[2:]
        draw.text(((1080-w)/2, y_text), l, font=fnt, fill="white")
        y_text += h + 20

    # 4. Logo JJMex (Opcional si el archivo existe)
    try:
        logo = Image.open(NOMBRE_LOGO).convert("RGBA")
        logo.thumbnail((200, 200))
        img.paste(logo, (820, 1750), logo)
    except: pass

    # 5. Envío
    bio = BytesIO()
    img.save(bio, 'JPEG', quality=90)
    bio.seek(0)
    
    caption = f"🐺 <b>{frase}</b>\n──────────────────\n<i>- {autor}</i>\n\n#Poder #JJMex #{tema}"
    enviar_telegram(bio, caption)

if __name__ == "__main__":
    crear_poster()
