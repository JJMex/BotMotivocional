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
    "riqueza": ["luxury lifestyle", "stacks of money", "gold bars", "expensive watch", "private jet", "lamborghini", "ferrari", "yacht"],
    "negocios": ["business man suit", "stock market wall street", "skyscraper view", "luxury office", "signing contract", "entrepreneur"],
    "poder": ["lion face dark", "chess king", "wolf dark", "throne", "military discipline", "eagle flying"],
    "gym": ["bodybuilder", "heavy weights", "boxing training", "sprinter running", "crossfit", "sweat gym", "fitness model"],
    "disciplina": ["alarm clock 5am", "working late night office", "samurai", "spartan warrior", "running rain"],
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
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={'chat_id': CHAT_ID, 'text': "📡 <i>Sincronizando banco de datos de mentalidad y generando activo visual...</i>", 'parse_mode': 'HTML'})
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('motivacion.jpg', image_bytes)}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        r = requests.post(url, files=files, data=data, timeout=30)
        return r.status_code == 200
    except: return False

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
        headers = {'Authorization': PEXELS_KEY}
        params = {'query': busqueda, 'orientation': 'portrait', 'per_page': 5}
        r = requests.get(URL_PEXELS, headers=headers, params=params, timeout=20).json()
        foto = random.choice(r['photos'])
        return Image.open(BytesIO(requests.get(foto['src']['large2x']).content)), tema_slug
    except:
        return Image.open(BytesIO(requests.get(URL_BACKUP).content)), "MOTIVACIONAL"

def crear_poster():
    if random.random() < 0.6:
        frase, autor = random.choice(FRASES_MANUALES), "JJMex"
    else:
        try:
            data = requests.get(URL_API_FRASE).json()[0]
            frase = GoogleTranslator(source='auto', target='es').translate(data['q'])
            autor = data['a']
        except: frase, autor = random.choice(FRASES_MANUALES), "JJMex"

    img, tema_tag = obtener_imagen_contextual(frase)
    img = img.resize((1080, 1920))
    
    # Transparencia negra (Legibilidad texto)
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 160)) 
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    draw = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 75)
        # Fuente para el autor (Un poco más pequeña)
        fnt_autor = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
    except:
        fnt = ImageFont.load_default()
        fnt_autor = ImageFont.load_default()

    # Centrado de frase principal
    lineas = textwrap.wrap(frase, width=20)
    y_text = (1920 - (len(lineas) * 100)) / 2
    for l in lineas:
        bbox = draw.textbbox((0, 0), l, font=fnt)
        w = bbox[2] - bbox[0]
        draw.text(((1080-w)/2, y_text), l, font=fnt, fill="white")
        y_text += 100

    # --- DIBUJAR AUTOR EN IMAGEN ---
    texto_autor = f"- {autor}"
    bbox_a = draw.textbbox((0, 0), texto_autor, font=fnt_autor)
    w_a = bbox_a[2] - bbox_a[0]
    draw.text(((1080 - w_a) / 2, y_text + 40), texto_autor, font=fnt_autor, fill="#cccccc")

    # Logo
    try:
        logo = Image.open(NOMBRE_LOGO).convert("RGBA")
        logo.thumbnail((280, 280)) 
        img.paste(logo, (750, 1600), logo) 
    except: pass

    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    
    caption = f"🐺 <b>{frase}</b>\n\n- {autor}\n\n#Poder #JJMex #{tema_tag}"
    enviar_telegram(bio, caption)

if __name__ == "__main__":
    crear_poster()
