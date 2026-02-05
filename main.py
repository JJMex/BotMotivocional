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

# --- DICCIONARIO DE PODER ---
TEMAS = {
    "riqueza": ["luxury lifestyle", "stacks of money", "gold bars", "expensive watch", "private jet", "lamborghini", "ferrari", "yacht"],
    "negocios": ["business man suit", "stock market wall street", "skyscraper view", "luxury office", "signing contract", "entrepreneur"],
    "poder": ["lion face dark", "chess king", "wolf dark", "throne", "military discipline", "eagle flying"],
    "gym": ["bodybuilder", "heavy weights", "boxing training", "sprinter running", "crossfit", "sweat gym", "fitness model"],
    "disciplina": ["alarm clock 5am", "working late night office", "samurai", "spartan warrior", "running rain"],
    "default": ["stormy ocean", "mountain peak", "dark city night", "galaxy stars"]
}

# --- ARSENAL DE 100 FRASES (RIQUEZA, PODER, GYM) ---
FRASES_MANUALES = [
    # --- RIQUEZA Y NEGOCIOS ---
    "El dinero no duerme, y tú tampoco deberías.",
    "Tu cuenta bancaria es el reflejo de tus hábitos.",
    "Mientras ellos duermen, tú construyes tu imperio.",
    "La pobreza es una enfermedad mental. Cúrate.",
    "Sé un monstruo en los negocios y un caballero en la vida.",
    "Si no trabajas por tus sueños, alguien te contratará para que trabajes por los suyos.",
    "Gana dinero mientras duermes o trabajarás hasta que mueras.",
    "No persigas el dinero, persigue la visión y el dinero te seguirá.",
    "El éxito ama la preparación y odia la excusa.",
    "Naciste para liderar, no para seguir.",
    "Hazlo en silencio y deja que tu éxito haga el ruido.",
    "Obsesión es la palabra que los vagos usan para describir la dedicación.",
    "Prefiero llorar en un Ferrari que en un autobús.",
    "El salario es la droga que te dan para olvidar tus sueños.",
    "Invierte en ti, es la única inversión que no quiebra.",
    "Los perdedores miran la pared, los ganadores la escalan.",
    "No te pagan por la hora, te pagan por el valor que aportas a la hora.",
    "El riesgo es el precio que pagas por la oportunidad.",
    "Deja de comprar cosas que no necesitas para impresionar a gente que no te importa.",
    "El dinero es libertad amplificada.",
    "Si te juntas con 5 millonarios, tú serás el sexto.",
    "Las excusas no pagan facturas.",
    "Trabaja hasta que tus ídolos se conviertan en tus rivales.",
    "El lunes es el día favorito de los que aman lo que construyen.",
    "No busques comodidad, busca apalancamiento.",
    "La riqueza se oculta a los que no tienen disciplina.",
    "Vende el problema que resuelves, no el producto.",
    "Sé tan bueno que no puedan ignorarte.",
    "El mercado no tiene sentimientos, tiene tendencias.",
    "Ahorrar es de pobres, invertir es de ricos.",
    "Tu red de contactos es tu patrimonio neto.",
    "No hables de planes, muestra resultados.",
    "La suerte es lo que sucede cuando la preparación se encuentra con la oportunidad.",

    # --- GYM, DOLOR Y DISCIPLINA ---
    "El dolor es temporal, la gloria es eterna.",
    "No te detengas cuando estés cansado, detente cuando hayas terminado.",
    "El cuerpo logra lo que la mente cree.",
    "La disciplina es hacer lo que odias como si lo amaras.",
    "Tu única competencia es quien eras ayer.",
    "Si fuera fácil, todo el mundo lo haría.",
    "No bajes la meta, aumenta el esfuerzo.",
    "Suda en el entrenamiento para no sangrar en la batalla.",
    "El gimnasio es mi terapia, el hierro mi psicólogo.",
    "Construye un cuerpo que no necesite presentación.",
    "La motivación te inicia, el hábito te mantiene.",
    "Un día o día uno. Tú decides.",
    "El dolor de hoy es la fuerza de mañana.",
    "Cómete el mundo o el mundo te comerá a ti.",
    "Entrena como una bestia para lucir como un rey.",
    "Las sentadillas no mienten.",
    "El sudor es la grasa llorando.",
    "No hay atajos para lugares que valgan la pena.",
    "El descanso es parte del entreno, la pereza no.",
    "Domina tu mente y dominarás tu cuerpo.",
    "La fuerza no viene de ganar, viene de no rendirse.",
    "Si no te desafía, no te cambia.",
    "Menos charla, más peso.",
    "Tu cuerpo es el único lugar que tienes para vivir.",
    "La debilidad es una elección.",
    "No cuentes las repeticiones, haz que las repeticiones cuenten.",
    "Levántate. Entrena. Repite.",
    "El sacrificio de hoy es el cuerpo del verano.",
    "Entrena hasta que tus ídolos te pidan consejos.",
    "Soy el arquitecto de mi propio físico.",
    
    # --- PODER, MENTALIDAD Y ESTOICISMO ---
    "Un león no se preocupa por la opinión de las ovejas.",
    "El precio de la grandeza es la responsabilidad.",
    "No busques culpables, busca soluciones.",
    "Lo que no te mata, te hace más fuerte.",
    "Sé el dueño de tu destino, el capitán de tu alma.",
    "La calma es la cuna del poder.",
    "Nunca digas todo lo que sabes.",
    "El poder real no se grita, se siente.",
    "Mantén la cabeza fría y el corazón ardiente.",
    "La lealtad es un regalo caro, no lo esperes de gente barata.",
    "Un rey no necesita gritar para ser escuchado.",
    "La venganza es perder el tiempo, el éxito es la mejor revancha.",
    "No temas a la soledad, los leones caminan solos.",
    "El respeto se gana, no se pide.",
    "Controla tus emociones o ellas te controlarán a ti.",
    "El silencio es la mejor respuesta para un necio.",
    "Sé peligroso pero mantente controlado.",
    "La confianza en sí mismo es el primer secreto del éxito.",
    "Mira a los ojos cuando hables.",
    "Cumple tu palabra o no la des.",
    "Sé implacable con tus objetivos y flexible con tus métodos.",
    "La historia la escriben los vencedores.",
    "Si quieres paz, prepárate para la guerra.",
    "El carácter es lo que haces cuando nadie te mira.",
    "No expliques tu filosofía, encárnala.",
    "Vive como si fueras a morir mañana, aprende como si fueras a vivir siempre.",
    "La paciencia es amarga, pero su fruto es dulce.",
    "No eres lo que logras, eres lo que superas.",
    "El miedo es una reacción, el coraje es una decisión.",
    "Sé el cambio que quieres ver en el mundo, pero empieza por tu cuenta bancaria.",
    "La mediocridad es el peor enemigo.",
    "Nunca te rindas, los milagros ocurren todos los días.",
    "Tu tiempo es limitado, no lo desperdicies viviendo la vida de otro.",
    "Atrévete a ser diferente.",
    "El fracaso es solo la oportunidad de comenzar de nuevo con más inteligencia."
]

def enviar_foto(image_bytes, caption):
    if not TOKEN or not CHAT_ID: return False
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('motivacion.jpg', image_bytes)}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        requests.post(url, files=files, data=data, timeout=30)
        return True
    except Exception as e: 
        print(f"Error TG: {e}")
        return False

# Variable global para guardar qué tema se usó
tema_actual = "Éxito"

def obtener_imagen_fitness_lujo(frase):
    global tema_actual
    frase_low = frase.lower()
    
    # Detector de palabras clave mejorado
    palabras_clave = {
        "dinero": "riqueza", "banco": "riqueza", "millonario": "riqueza", "pobreza": "riqueza", "lujo": "riqueza", "ferrari": "riqueza", "invertir": "riqueza", "facturas": "riqueza",
        "negocio": "negocios", "trabajo": "negocios", "imperio": "negocios", "éxito": "negocios", "mercado": "negocios", "vender": "negocios",
        "gym": "gym", "fuerza": "gym", "dolor": "gym", "cuerpo": "gym", "entrenar": "gym", "suda": "gym", "pesas": "gym", "físico": "gym",
        "lider": "poder", "león": "poder", "lobo": "poder", "rey": "poder", "guerra": "poder", "venganza": "poder", "carácter": "poder",
        "tiempo": "disciplina", "disciplina": "disciplina", "noche": "disciplina", "hábito": "disciplina", "reloj": "disciplina"
    }

    tema_encontrado = "default"
    for palabra, categoria in palabras_clave.items():
        if palabra in frase_low:
            tema_encontrado = categoria
            break
    
    if tema_encontrado == "default":
        tema_encontrado = random.choice(list(TEMAS.keys()))

    tema_actual = tema_encontrado.upper()
    busqueda = random.choice(TEMAS[tema_encontrado])
    print(f"Tema: {tema_actual} | Buscando: '{busqueda}'")

    try:
        headers = {'Authorization': PEXELS_KEY}
        # Pedimos más resultados (8) para tener variedad
        params = {'query': busqueda, 'orientation': 'portrait', 'per_page': 8} 
        response = requests.get(URL_PEXELS, headers=headers, params=params, timeout=20)
        data = response.json()
        if 'photos' in data and len(data['photos']) > 0:
            foto = random.choice(data['photos'])
            return Image.open(BytesIO(requests.get(foto['src']['large2x'], timeout=20).content))
        else:
            raise Exception("Sin resultados Pexels")
    except:
        return Image.open(BytesIO(requests.get(URL_BACKUP).content))

def obtener_frase():
    # --- LÓGICA 60/40 ---
    # Si el número aleatorio (0.0 a 1.0) es menor a 0.6, usamos la lista manual (60%)
    if random.random() < 0.6:
        print("⚡ Usando frase MANUAL de Poder")
        # --- AQUÍ ESTÁ EL CAMBIO SOLICITADO ---
        return random.choice(FRASES_MANUALES), "JJMex"
    
    # El otro 40% usamos la API externa
    try:
        print("🌐 Buscando frase en API...")
        data = requests.get(URL_API_FRASE, timeout=10).json()[0]
        frase_en = data['q']
        autor = data['a']
        frase_es = GoogleTranslator(source='auto', target='es').translate(frase_en)
        return frase_es, autor
    except:
        # Si falla la API, volvemos a la lista manual como respaldo
        return random.choice(FRASES_MANUALES), "JJMex"

def crear_poster():
    # 1. Obtener contenido
    frase_es, autor = obtener_frase()

    # 2. Obtener Imagen
    img = obtener_imagen_fitness_lujo(frase_es)
    img = img.resize((1080, 1920)) 
    
    # 3. Efecto Dark Mode (Capa negra al 60% de opacidad)
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 60))
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    
    W, H = img.size
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_autor = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
    except:
        font = ImageFont.load_default()
        font_autor = ImageFont.load_default()

    lineas = textwrap.wrap(frase_es, width=18)
    altura_bloque = sum([draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1] + 20 for l in lineas])
    y_text = (H - altura_bloque) / 2

    for linea in lineas:
        bbox = draw.textbbox((0, 0), linea, font=font)
        w_line = bbox[2] - bbox[0]
        h_line = bbox[3] - bbox[1]
        x = (W - w_line) / 2
        
        # Sombra negra fuerte para máxima legibilidad
        draw.text((x+4, y_text+4), linea, font=font, fill="black")
        draw.text((x, y_text), linea, font=font, fill="white")
        y_text += h_line + 20

    y_text += 40
    bbox_a = draw.textbbox((0, 0), f"- {autor}", font=font_autor)
    x_a = (W - (bbox_a[2] - bbox_a[0])) / 2
    draw.text((x_a, y_text), f"- {autor}", font=font_autor, fill="#cccccc")

    # 4. Pegar Logo (si existe)
    try:
        logo = Image.open(NOMBRE_LOGO).convert("RGBA")
        ancho_logo = int(W * 0.18)
        alto_logo = int((ancho_logo / logo.width) * logo.height)
        logo = logo.resize((ancho_logo, alto_logo), Image.LANCZOS)
        img.paste(logo, (W - ancho_logo - 60, H - alto_logo - 60), logo)
    except:
        pass

    # 5. Enviar (Con 3 Reintentos)
    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    
    # Hashtags dinámicos
    caption = f"🐺 <b>{frase_es}</b>\n\n#Riqueza #Poder #JJMex #{tema_actual}"
    
    for i in range(3):
        print(f"Intento {i+1}...")
        if enviar_foto(bio, caption): 
            print("✅ Enviado.")
            break
        time.sleep(10)
        bio.seek(0)

if __name__ == "__main__":
    crear_poster()
