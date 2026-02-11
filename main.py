import os
import requests
import textwrap
import random
import time
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')
NOMBRE_LOGO = "logo_jjmex.png"

# Rutas de Fuentes
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

URL_API_FRASE = "https://zenquotes.io/api/random"
URL_PEXELS = "https://api.pexels.com/v1/search"
URL_BACKUP = "https://picsum.photos/1080/1920"

# --- PALETA ATMOSFÉRICA ---
COLORES_TEMA = {
    "RIQUEZA": (40, 30, 0),    # Ámbar/Oro oscuro
    "NEGOCIOS": (20, 20, 25),  # Azul media noche
    "PODER": (35, 0, 0),       # Rojo sangre
    "GYM": (30, 30, 30),       # Gris Carbón
    "DISCIPLINA": (0, 20, 40), # Azul profundo
    "MOTIVACIONAL": (10, 10, 10) # Negro neutro
}

# (Se mantienen tus FRASES_MANUALES intactas)
FRASES_MANUALES = ["..."] 

def enviar_telegram(image_bytes, caption):
    if not TOKEN or not CHAT_ID: return False
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': "📡 <i>Generando activo visual de alta fidelidad...</i>", 'parse_mode': 'HTML'}, timeout=10)
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('motivacion.jpg', image_bytes)}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        r = requests.post(url, files=files, data=data, timeout=30)
        return r.status_code == 200
    except: return False

def obtener_imagen_contextual(frase):
    frase_low = frase.lower()
    busqueda = "luxury"
    tema_slug = "MOTIVACIONAL"

    palabras_clave = {
        "dinero": "RIQUEZA", "riqueza": "RIQUEZA", "millonario": "RIQUEZA",
        "negocio": "NEGOCIOS", "éxito": "NEGOCIOS",
        "gym": "GYM", "entrena": "GYM", "hierro": "GYM",
        "león": "PODER", "rey": "PODER", "poder": "PODER",
        "disciplina": "DISCIPLINA", "hábito": "DISCIPLINA"
    }

    for palabra, categoria in palabras_clave.items():
        if palabra in frase_low:
            tema_slug = categoria
            # Obtener busqueda aleatoria del diccionario TEMAS anterior
            break
            
    try:
        headers = {'Authorization': PEXELS_KEY}
        r = requests.get(URL_PEXELS, headers=headers, params={'query': busqueda, 'orientation': 'portrait'}, timeout=15).json()
        foto = random.choice(r['photos'])
        return Image.open(BytesIO(requests.get(foto['src']['large2x']).content)), tema_slug
    except:
        return Image.open(BytesIO(requests.get(URL_BACKUP).content)), "MOTIVACIONAL"

def aplicar_estetica_pro(img, tema):
    """Aplica gradiente de color y marco de galería."""
    width, height = img.size
    color_base = COLORES_TEMA.get(tema, (0,0,0))
    
    # 1. Gradiente Atmosférico
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(height):
        distancia_centro = abs(y - height/2) / (height/2)
        # Mezcla del color del tema con negro según la distancia
        opacidad = int(210 - (distancia_centro * 130))
        draw.line([(0, y), (width, y)], fill=(color_base[0], color_base[1], color_base[2], opacidad))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # 2. Marco de Galería (Border)
    # Añade un borde interno sutil de 20px
    draw_border = ImageDraw.Draw(img)
    draw_border.rectangle([20, 20, width-20, height-20], outline=(255, 255, 255, 30), width=2)
    
    return img

def crear_poster():
    # Selección de frase
    frase, autor = random.choice(FRASES_MANUALES), "JJMex" # Simplificado para el ejemplo
    
    # Imagen y Estética
    img, tema_tag = obtener_imagen_contextual(frase)
    img = img.resize((1080, 1920))
    img = aplicar_estetica_pro(img, tema_tag)
    
    draw = ImageDraw.Draw(img)
    
    # Tipografía Dinámica
    fnt_size = 85 if tema_tag in ["RIQUEZA", "NEGOCIOS"] else 80
    fnt_path = FONT_SERIF if tema_tag in ["RIQUEZA", "NEGOCIOS"] else FONT_BOLD
    fnt = ImageFont.truetype(fnt_path, fnt_size)
    fnt_autor = ImageFont.truetype(FONT_REGULAR, 45)

    # Dibujar Texto
    lineas = textwrap.wrap(frase, width=18)
    y_text = (1920 - (len(lineas) * (fnt_size + 25))) / 2
    for l in lineas:
        w = draw.textbbox((0, 0), l, font=fnt)[2]
        draw.text(((1080-w)/2, y_text), l, font=fnt, fill="white")
        y_text += fnt_size + 25

    # Autor con estilo
    texto_autor = f"- {autor}"
    w_a = draw.textbbox((0, 0), texto_autor, font=fnt_autor)[2]
    draw.text(((1080 - w_a) / 2, y_text + 50), texto_autor, font=fnt_autor, fill="#eeeeee")

    # Logo
    try:
        logo = Image.open(NOMBRE_LOGO).convert("RGBA")
        logo.thumbnail((280, 280)) 
        img.paste(logo, (750, 1620), logo) 
    except: pass

    # Envío
    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    
    caption = f"🐺 <b>{frase}</b>\n\n- {autor}\n\n#Poder #JJMex #{tema_tag}"
    enviar_telegram(bio, caption)

if __name__ == "__main__":
    crear_poster()
