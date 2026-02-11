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

# Rutas de Fuentes (Instaladas vía YAML)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

URL_API_FRASE = "https://zenquotes.io/api/random"
URL_PEXELS = "https://api.pexels.com/v1/search"
URL_BACKUP = "https://picsum.photos/1080/1920"

TEMAS = {
    "riqueza": ["luxury lifestyle", "expensive watch", "private jet", "lamborghini", "yacht"],
    "negocios": ["business man suit", "skyscraper view", "luxury office", "entrepreneur"],
    "poder": ["lion face dark", "chess king", "wolf dark", "throne"],
    "gym": ["bodybuilder", "heavy weights", "boxing training", "fitness model"],
    "disciplina": ["alarm clock 5am", "samurai", "spartan warrior", "running rain"],
    "default": ["stormy ocean", "mountain peak", "dark city night", "galaxy stars"]
}

FRASES_MANUALES = [
    "El dinero no duerme, y tú tampoco deberías.", "Tu cuenta bancaria es el reflejo de tus hábitos.",
    "Mientras ellos duermen, tú construyes tu imperio.", "La pobreza es una enfermedad mental. Cúrate.",
    "Sé un monstruo en los negocios y un caballero en la vida.", "Si no trabajas por tus sueños, alguien te contratará para que trabajes por los suyos.",
    "Gana dinero mientras duermes o trabajarás hasta que mueras.", "No persigas el dinero, persigue la visión y el dinero te seguirá.",
    "El éxito ama la preparación y odia la excusa.", "Naciste para liderar, no para seguir.",
    "Hazlo en silencio y deja que tu éxito haga el ruido.", "Obsesión es la palabra que los vagos usan para describir la dedicación.",
    "Prefiero llorar en un Ferrari que en un autobús.", "El salario es la droga que te dan para olvidar tus sueños.",
    "Invierte en ti, es la única inversión que no quiebra.", "Los perdedores miran la pared, los ganadores la escalan.",
    "No te pagan por la hora, te pagan por el valor que aportas a la hora.", "El riesgo es el precio que pagas por la oportunidad.",
    "Deja de comprar cosas que no necesitas para impresionar a gente que no te importa.", "El dinero es libertad amplificada.",
    "Si te juntas con 5 millonarios, tú serás el sexto.", "Las excusas no pagan facturas.",
    "Trabaja hasta que tus ídolos se conviertan en tus rivales.", "El lunes es el día favorito de los que aman lo que construyen.",
    "No busques comodidad, busca apalancamiento.", "La riqueza se oculta a los que no tienen disciplina.",
    "Vende el problema que resuelves, no el producto.", "Sé tan bueno que no puedan ignorarte.",
    "El mercado no tiene sentimientos, tiene tendencias.", "Ahorrar es de pobres, invertir es de ricos.",
    "Tu red de contactos es tu patrimonio neto.", "No hables de planes, muestra resultados.",
    "La suerte es lo que sucede cuando la preparación se encuentra con la oportunidad.", "El dolor es temporal, la gloria es eterna.",
    "No te detengas cuando estés cansado, detente cuando hayas terminado.", "El cuerpo logra lo que la mente cree.",
    "La disciplina es hacer lo que odias como si lo amaras.", "Tu única competencia es quien eras ayer.",
    "Si fuera fácil, todo el mundo lo haría.", "No bajes la meta, aumenta el esfuerzo.",
    "Suda en el entrenamiento para no sangrar en la batalla.", "El gimnasio es mi terapia, el hierro mi psicólogo.",
    "Construye un cuerpo que no necesite presentación.", "La motivación te inicia, el hábito te mantiene.",
    "Un día o día uno. Tú decides.", "El dolor de hoy es la fuerza de mañana.",
    "Cómete el mundo o el mundo te comerá a ti.", "Entrena como una bestia para lucir como un rey.",
    "Las sentadillas no mienten.", "El sudor es la grasa llorando.",
    "No hay atajos para lugares que valgan la pena.", "El descanso es parte del entreno, la pereza no.",
    "Domina tu mente y dominarás tu cuerpo.", "La fuerza no viene de ganar, viene de no rendirse.",
    "Si no te desafía, no te cambia.", "Menos charla, más peso.",
    "Tu cuerpo es el único lugar que tienes para vivir.", "La debilidad es una elección.",
    "No cuentes las repeticiones, haz que las repeticiones cuenten.", "Levántate. Entrena. Repite.",
    "El sacrificio de hoy es el cuerpo del verano.", "Entrena hasta que tus ídolos te pidan consejos.",
    "Soy el arquitecto de mi propio físico.", "Un león no se preocupa por la opinión de las ovejas.",
    "El precio de la grandeza es la responsabilidad.", "No busques culpables, busca soluciones.",
    "Lo que no te mata, te hace más fuerte.", "Sé el dueño de tu destino, el capitán de tu alma.",
    "La calma es la cuna del poder.", "Nunca digas todo lo que sabes.",
    "El poder real no se grita, se siente.", "Mantén la cabeza fría y el corazón ardiente.",
    "La lealtad es un regalo caro, no lo esperes de gente barata.", "Un rey no necesita gritar para ser escuchado.",
    "La venganza es perder el tiempo, el éxito es la mejor revancha.", "No temas a la soledad, los leones caminan solos.",
    "El respeto se gana, no se pide.", "Controla tus emociones o ellas te controlarán a ti.",
    "El silencio es la mejor respuesta para un necio.", "Sé peligroso pero mantente controlado.",
    "La confianza en sí mismo es el primer secreto del éxito.", "Mira a los ojos cuando hables.",
    "Cumple tu palabra o no la des.", "Sé implacable con tus objetivos y flexible con tus métodos.",
    "La historia la escriben los vencedores.", "Si quieres paz, prepárate para la guerra.",
    "El carácter es lo que haces cuando nadie te mira.", "No expliques tu filosofía, encárnala.",
    "Vive como si fueras a morir mañana, aprende como si fueras a vivir siempre.", "La paciencia es amarga, pero su fruto es dulce.",
    "No eres lo que logras, eres lo que superas.", "El miedo es una reacción, el coraje es una decisión.",
    "Sé el cambio que quieres ver en el mundo, pero empieza por tu cuenta bancaria.", "La mediocridad es el peor enemigo.",
    "Nunca te rindas, los milagros ocurren todos los días.", "Tu tiempo es limitado, no lo despercidies viviendo la vida de otro.",
    "Atrévete a ser diferente.", "El fracaso es solo la oportunidad de comenzar de nuevo con más inteligencia."
]

def enviar_telegram(image_bytes, caption):
    if not TOKEN or not CHAT_ID: return False
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': "📡 <i>Sincronizando banco de datos de mentalidad y generando activo visual...</i>", 'parse_mode': 'HTML'}, timeout=10)
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('motivacion.jpg', image_bytes)}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        r = requests.post(url, files=files, data=data, timeout=30)
        return r.status_code == 200
    except Exception as e:
        print(f"Error envío: {e}")
        return False

def obtener_imagen_contextual(frase):
    frase_low = frase.lower()
    busqueda = "luxury"
    tema_slug = "ESTRATÉGICO"

    palabras_clave = {
        "dinero": "riqueza", "riqueza": "riqueza", "millonario": "riqueza", "lujo": "riqueza",
        "negocio": "negocios", "éxito": "negocios", "imperio": "negocios",
        "gym": "gym", "entrena": "gym", "cuerpo": "gym", "hierro": "gym",
        "león": "poder", "rey": "poder", "lobo": "poder", "poder": "poder",
        "disciplina": "disciplina", "hábito": "disciplina", "noche": "disciplina"
    }

    for palabra, categoria in palabras_clave.items():
        if palabra in frase_low:
            busqueda = random.choice(TEMAS[categoria])
            tema_slug = categoria.upper()
            break
            
    try:
        if not PEXELS_KEY: raise Exception("No API Key")
        headers = {'Authorization': PEXELS_KEY}
        params = {'query': busqueda, 'orientation': 'portrait', 'per_page': 5}
        r = requests.get(URL_PEXELS, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        foto = random.choice(data['photos'])
        img_data = requests.get(foto['src']['large2x'], timeout=15).content
        return Image.open(BytesIO(img_data)), tema_slug
    except Exception as e:
        print(f"Pexels falló ({e}). Usando Backup.")
        img_data = requests.get(URL_BACKUP, timeout=15).content
        return Image.open(BytesIO(img_data)), "MOTIVACIONAL"

def aplicar_gradiente(img):
    """Crea un gradiente vertical: más oscuro al centro para el texto."""
    width, height = img.size
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for y in range(height):
        # Curva de opacidad: 80 en bordes, hasta 190 en el centro (y=960)
        distancia_centro = abs(y - height/2) / (height/2)
        opacidad = int(200 - (distancia_centro * 120))
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, opacidad))
    
    return Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

def crear_poster():
    # 1. Error Handling en Frase
    try:
        if random.random() < 0.6:
            frase, autor = random.choice(FRASES_MANUALES), "JJMex"
        else:
            r = requests.get(URL_API_FRASE, timeout=10).json()[0]
            frase = GoogleTranslator(source='auto', target='es').translate(r['q'])
            autor = r['a']
    except Exception as e:
        print(f"Error Frase: {e}")
        frase, autor = random.choice(FRASES_MANUALES), "JJMex"

    # 2. Imagen y Gradiente Avanzado
    img, tema_tag = obtener_imagen_contextual(frase)
    img = img.resize((1080, 1920))
    img = aplicar_gradiente(img)
    
    draw = ImageDraw.Draw(img)
    
    # 3. Variedad de Tipografías (Selección por Tema) 
    # Poder/Gym -> Bold Sans | Riqueza/Negocios -> Serif Elegante 
    try:
        if tema_tag in ["RIQUEZA", "NEGOCIOS"]:
            fnt_path, fnt_size = FONT_SERIF, 85
        elif tema_tag in ["PODER", "GYM"]:
            fnt_path, fnt_size = FONT_BOLD, 80
        else:
            fnt_path, fnt_size = FONT_REGULAR, 75
            
        fnt = ImageFont.truetype(fnt_path, fnt_size)
        fnt_autor = ImageFont.truetype(FONT_REGULAR, 45)
    except:
        fnt = ImageFont.load_default()
        fnt_autor = ImageFont.load_default()

    # 4. Dibujar Texto
    lineas = textwrap.wrap(frase, width=18)
    y_text = (1920 - (len(lineas) * (fnt_size + 20))) / 2
    for l in lineas:
        w = draw.textbbox((0, 0), l, font=fnt)[2]
        draw.text(((1080-w)/2, y_text), l, font=fnt, fill="white")
        y_text += fnt_size + 20

    # Autor
    texto_autor = f"- {autor}"
    w_a = draw.textbbox((0, 0), texto_autor, font=fnt_autor)[2]
    draw.text(((1080 - w_a) / 2, y_text + 40), texto_autor, font=fnt_autor, fill="#dddddd")

    # 5. Logo JJMex
    try:
        logo = Image.open(NOMBRE_LOGO).convert("RGBA")
        logo.thumbnail((280, 280)) 
        img.paste(logo, (750, 1620), logo) 
    except: pass

    # 6. Envío Robusto
    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    
    caption = f"🐺 <b>{frase}</b>\n\n- {autor}\n\n#Poder #JJMex #{tema_tag}"
    
    if not enviar_telegram(bio, caption):
        print("Fallo crítico en envío.")

if __name__ == "__main__":
    crear_poster()
