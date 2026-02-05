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
URL_API_FRASE = "https://zenquotes.io/api/random"
URL_PEXELS = "https://api.pexels.com/v1/search"
URL_BACKUP = "https://picsum.photos/1080/1920"

# --- DICCIONARIO DE PODER (SOLO TEMAS FUERTES) ---
TEMAS = {
    "riqueza": ["luxury lifestyle", "stacks of money", "gold bars", "expensive watch", "private jet", "lamborghini", "ferrari"],
    "negocios": ["business man suit", "stock market wall street", "skyscraper view", "luxury office", "signing contract"],
    "poder": ["lion face dark", "chess king", "wolf dark", "throne", "military discipline"],
    "gym": ["bodybuilder", "heavy weights", "boxing training", "sprinter running", "crossfit", "sweat gym"],
    "disciplina": ["alarm clock 5am", "working late night office", "samurai", "spartan warrior"],
    
    # El default también debe ser poderoso, nada de flores
    "default": ["stormy ocean", "mountain peak", "eagle flying", "dark city night"]
}

# --- LISTA DE FRASES BLINDADA (ESTILO LOBO DE WALL STREET/GYM) ---
# Estas frases garantizan el tono que buscas.
FRASES_MANUALES = [
    "No te detengas cuando estés cansado, detente cuando hayas terminado.",
    "El dinero no duerme, y tú tampoco deberías.",
    "Tu cuenta bancaria es el reflejo de tus hábitos.",
    "Mientras ellos duermen, tú construyes tu imperio.",
    "El dolor es temporal, la gloria es eterna.",
    "No busques culpables, busca soluciones.",
    "La pobreza es una enfermedad mental. Cúrate.",
    "Sé un monstruo en los negocios y un caballero en la vida.",
    "Si no trabajas por tus sueños, alguien te contratará para que trabajes por los suyos.",
    "La disciplina es hacer lo que odias como si lo amaras.",
    "Tu única competencia es quien eras ayer.",
    "El éxito ama la preparación y odia la excusa.",
    "Naciste para liderar, no para seguir.",
    "Hazlo en silencio y deja que tu éxito haga el ruido.",
    "Si fuera fácil, todo el mundo lo haría.",
    "No bajes la meta, aumenta el esfuerzo.",
    "El precio de la grandeza es la responsabilidad.",
    "Un león no se preocupa por la opinión de las ovejas.",
    "Obsesión es la palabra que los vagos usan para describir la dedicación.",
    "Gana dinero mientras duermes o trabajarás hasta que mueras."
]

def enviar_foto(image_bytes, caption):
    if not TOKEN or not CHAT_ID: return False
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('motivacion.jpg', image_bytes)}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        requests.post(url, files=files, data=data, timeout=20)
        return True
    except Exception as e: 
        print(f"Error TG: {e}")
        return False

# Variable para guardar qué tema se usó
tema_actual = "Éxito"

def obtener_imagen_fitness_lujo(frase):
    global tema_actual
    frase_low = frase.lower()
    
    # 1. Detectar palabras clave en la frase
    palabras_clave = {
        "dinero": "riqueza", "banco": "riqueza", "millonario": "riqueza", "pobreza": "riqueza",
        "negocio": "negocios", "trabajo": "negocios", "imperio": "negocios",
        "gym": "gym", "fuerza": "gym", "dolor": "gym", "cuerpo": "gym", "entrenar": "gym",
        "lider": "poder", "león": "poder", "lobo": "poder", "rey": "poder",
        "tiempo": "disciplina", "disciplina": "disciplina", "noche": "disciplina"
    }

    tema_encontrado = "default"
    for palabra, categoria in palabras_clave.items():
        if palabra in frase_low:
            tema_encontrado = categoria
            break
    
    # Si no encuentra palabra clave, elegimos uno AL AZAR de los temas fuertes (no default aburrido)
    if tema_encontrado == "default":
        tema_encontrado = random.choice(list(TEMAS.keys()))

    tema_actual = tema_encontrado.upper()
    busqueda = random.choice(TEMAS[tema_encontrado])
    print(f"Tema: {tema_actual} | Buscando: '{busqueda}'")

    try:
        headers = {'Authorization': PEXELS_KEY}
        params = {'query': busqueda, 'orientation': 'portrait', 'per_page': 8} 
        response = requests.get(URL_PEXELS, headers=headers, params=params, timeout=15)
        data = response.json()
        if 'photos' in data and len(data['photos']) > 0:
            foto = random.choice(data['photos'])
            return Image.open(BytesIO(requests.get(foto['src']['large2x'], timeout=15).content))
        else:
            raise Exception("Sin resultados")
    except:
        return Image.open(BytesIO(requests.get(URL_BACKUP).content))

def obtener_frase():
    # 70% de probabilidad de usar nuestras frases MANUALES (Garantía de calidad)
    # 30% de probabilidad de usar API (Variedad)
    if random.random() < 0.7:
        print("Usando frase manual de PODER")
        return random.choice(FRASES_MANUALES), "Mente & Éxito"
    
    try:
        print("Buscando frase en API...")
        data = requests.get(URL_API_FRASE, timeout=5).json()[0]
        frase_en = data['q']
        autor = data['a']
        # Traducir
        frase_es = GoogleTranslator(source='auto', target='es').translate(frase_en)
        return frase_es, autor
    except:
        return random.choice(FRASES_MANUALES), "JJMex"

def crear_poster():
    # 1. Obtener contenido
    frase_es, autor = obtener_frase()

    # 2. Obtener Imagen (Lujo/Gym)
    img = obtener_imagen_fitness_lujo(frase_es)
    img = img.resize((1080, 1920)) 
    # Oscurecer imagen un poco para que el texto blanco resalte más (Toque Dark Mode)
    # Creamos una capa negra semitransparente
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 60)) # 60 es la opacidad
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    
    W, H = img.size
    draw = ImageDraw.Draw(img)
    
    # Fuentes
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_autor = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
    except:
        font = ImageFont.load_default()
        font_autor = ImageFont.load_default()

    # Formato de texto
    lineas = textwrap.wrap(frase_es, width=18)
    altura_bloque = sum([draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1] + 20 for l in lineas])
    y_text = (H - altura_bloque) / 2

    for linea in lineas:
        bbox = draw.textbbox((0, 0), linea, font=font)
        w_line = bbox[2] - bbox[0]
        h_line = bbox[3] - bbox[1]
        x = (W - w_line) / 2
        
        # Sombra sólida para agresividad
        draw.text((x+4, y_text+4), linea, font=font, fill="black")
        draw.text((x, y_text), linea, font=font, fill="white")
        y_text += h_line + 20

    # Autor
    y_text += 40
    bbox_a = draw.textbbox((0, 0), f"- {autor}", font=font_autor)
    x_a = (W - (bbox_a[2] - bbox_a[0])) / 2
    draw.text((x_a, y_text), f"- {autor}", font=font_autor, fill="#cccccc")

    # Pegar Logo
    try:
        logo = Image.open(NOMBRE_LOGO).convert("RGBA")
        ancho_logo = int(W * 0.18) # Un poco más grande para imponer marca
        alto_logo = int((ancho_logo / logo.width) * logo.height)
        logo = logo.resize((ancho_logo, alto_logo), Image.LANCZOS)
        img.paste(logo, (W - ancho_logo - 60, H - alto_logo - 60), logo)
    except:
        pass

    # Enviar con Reintentos
    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    
    caption = f"🐺 <b>{frase_es}</b>\n\n#Riqueza #Poder #JJMex"
    
    for i in range(3):
        if enviar_foto(bio, caption): break
        time.sleep(10)
        bio.seek(0)

if __name__ == "__main__":
    crear_poster()
