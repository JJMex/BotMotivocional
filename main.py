import os
import requests
import textwrap
import random
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from io import BytesIO
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')
NOMBRE_LOGO = "logo_jjmex.png"
HISTORIAL_FILE = "historial.txt"

# Rutas de Fuentes (Asegúrate que coincidan con tu diario.yml)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

URL_API_FRASE = "https://zenquotes.io/api/random"
URL_PEXELS = "https://api.pexels.com/v1/search"
URL_BACKUP = "https://picsum.photos/1080/1920"

# --- PALETA ATMOSFÉRICA ---
COLORES_TEMA = {
    "RIQUEZA": (50, 40, 15),    # Oro/Ámbar
    "NEGOCIOS": (30, 35, 50),   # Azul ejecutivo
    "PODER": (50, 10, 10),      # Carmesí profundo
    "GYM": (40, 40, 40),        # Acero/Gris
    "DISCIPLINA": (10, 30, 50), # Azul marino
    "MOTIVACIONAL": (20, 20, 20) # Negro neutro
}

TEMAS = {
    "riqueza": ["luxury", "gold", "yacht", "rolex"],
    "negocios": ["suit", "skyscrapers", "trading", "office"],
    "poder": ["lion", "wolf", "king", "eagle"],
    "gym": ["bodybuilding", "gym", "weights", "workout"],
    "disciplina": ["samurai", "spartan", "discipline", "running"],
    "default": ["dark nature", "stormy sky", "night city"]
}

# --- ARSENAL COMPLETO (100 FRASES) ---
FRASES_MANUALES = [
    "La disciplina te llevará donde la motivación no alcanza.", "Tu mente es tu activo más valioso; invierte en ella cada día.",
    "Los imperios no se construyen en horario de oficina.", "El dolor de la disciplina pesa gramos; el del arrepentimiento, toneladas.",
    "Sé un león en un mundo de ovejas que solo saben quejarse.", "Tu cuenta bancaria es el tablero de puntuación de tus decisiones.",
    "No te detengas cuando estés cansado, detente cuando hayas terminado.", "La riqueza no se trata de tener dinero, se trata de tener opciones.",
    "Trabaja en silencio, que el rugido de tu motor hable por ti.", "El éxito es la mejor venganza contra los que dudaron.",
    "Si no naces con el privilegio, construye el legado.", "La comodidad es la droga que mata los grandes sueños.",
    "No busques suerte, busca frecuencia y ejecución impecable.", "El mercado solo paga por resultados, no por buenas intenciones.",
    "Tu red de contactos define tu patrimonio neto.", "Gana dinero mientras duermes o trabajarás hasta el último aliento.",
    "La obsesión vence al talento cuando el talento no se obsesiona.", "Sé tan bueno que sea imposible que te ignoren.",
    "No cuentes tus planes, muestra tus activos.", "El miedo es un indicador de que vas por el camino correcto.",
    "La autodisciplina es la forma más alta de amor propio.", "Tu cuerpo es el templo que sostiene tu imperio; entrénalo.",
    "No bajes el precio de tus sueños, aumenta tu valor en el mercado.", "Un ganador es un perdedor que lo intentó una vez más.",
    "La verdadera libertad es no tener que pedir permiso a nadie.", "Si te juntas con 5 millonarios, tú serás el sexto de la lista.",
    "El sudor del gimnasio previene las lágrimas del hospital.", "Los perdedores miran la pared; los ganadores escalan la montaña.",
    "El dinero es libertad amplificada; úsalo con inteligencia.", "Naciste para liderar, no para seguir el rebaño.",
    "Hazlo con miedo, hazlo cansado, pero hazlo.", "Tu pasado es solo una lección, no una sentencia de por vida.",
    "La paciencia es amarga, pero el fruto del éxito es dulce.", "No esperes la oportunidad, crea el entorno para que aparezca.",
    "El respeto se gana con hechos, no con palabras vacías.", "Tu única competencia real es la persona que viste en el espejo ayer.",
    "Construye una vida de la que no necesites vacaciones.", "El riesgo es el precio de la entrada a la grandeza.",
    "Sé implacable con tus metas y flexible con tus métodos.", "El lunes es el día de caza para los que aman el proceso.",
    "No busques aprobación, busca apalancamiento.", "La lealtad es un regalo caro que no se encuentra en gente barata.",
    "Tu mentalidad es el motor; tu disciplina es el combustible.", "Si fuera fácil, todos tendrían el Ferrari.",
    "La excelencia es un hábito, no un evento aislado.", "El dolor es temporal, pero la gloria de haberlo logrado es eterna.",
    "No te compares con nadie, cada imperio tiene su propio tiempo.", "La disciplina es hacer lo que odias como si lo amaras.",
    "Prefiero morir en el intento que vivir en la mediocridad.", "El dinero no cambia a la gente, solo muestra quiénes son realmente.",
    "Si quieres paz, prepárate para la guerra en los negocios.", "La mayor inversión es la que haces en tu propio cerebro.",
    "No persigas el dinero, persigue la visión e impacto.", "Sé la oveja negra que cambia la historia de su familia.",
    "El fracaso es solo el fertilizante para tu próximo éxito.", "Tu red es tu patrimonio; elige bien con quién te sientas.",
    "Obsesión es lo que los mediocres llaman dedicación.", "Si no estás creciendo, estás muriendo lentamente.",
    "El gimnasio forja el carácter que los negocios necesitan.", "No cuentes las repeticiones, haz que cada repetición cuente.",
    "La suerte favorece a la mente preparada y disciplinada.", "Vive un par de años como nadie quiere, para vivir el resto como nadie puede.",
    "La confianza no es 'les gustaré', es 'estaré bien si no les gusto'.", "Los líderes leen mientras los demás duermen.",
    "El carácter se forja en la oscuridad y se celebra bajo la luz.", "No busques el camino fácil, busca el que valga la pena.",
    "Tu salario es la droga que te dan para olvidar tus sueños.", "La gratitud te da paz, pero la ambición te da el mundo.",
    "Nunca tomes consejos de alguien que no tenga los resultados que quieres.", "El éxito es 1% inspiración y 99% ejecución.",
    "No bajes el volumen de tu ambición para que otros estén cómodos.", "Cada 'no' te acerca más al 'sí' que cambiará tu vida.",
    "La verdadera riqueza es tiempo libre y salud física.", "Si no puedes controlar tus emociones, no controlas tu dinero.",
    "Sé un caballero en el trato y un monstruo en la ejecución.", "El mundo no te debe nada; sal y gánatelo tú mismo.",
    "Tu potencial es infinito, tus miedos son solo mentiras.", "La consistencia vence al talento cada día.",
    "No busques comodidad, busca desafíos que te obliguen a crecer.", "El dinero fluye hacia donde hay orden y valor.",
    "Tu vida cambia el día que decides que no aceptarás menos.", "La pobreza es un estado mental; la escasez es solo una etapa.",
    "Sé el arquitecto de tu propio destino y capitán de tu alma.", "No dejes que mentes pequeñas limiten tus sueños.",
    "El éxito requiere sacrificio, pero el fracaso es más caro.", "Entrena hasta que tus ídolos sean tus competidores.",
    "La lealtad a tus metas debe ser inquebrantable.", "No expliques tu filosofía, simplemente encárnala.",
    "El tiempo es el único recurso que no recuperas; úsalo bien.", "Sé peligroso pero mantente bajo control absoluto.",
    "La marca JJMex es sinónimo de disciplina y poder.", "El éxito es la suma de pequeños esfuerzos diarios.",
    "No hables de tus planes, deja que tus activos hablen.", "La cima está vacía porque pocos pagan el precio.",
    "Ahorrar es sobrevivir, invertir es conquistar.", "Si te rindes hoy, el sacrificio de ayer no sirvió.",
    "El dolor del entreno es nada comparado con la debilidad.", "Sé implacable. Sé legendario. Sé JJMex.",
    "Tu visión debe ser tan clara que tus miedos sean irrelevantes.", "El imperio comienza en tu mente antes que en la realidad."
]

# --- UTILIDADES DE DISEÑO ---

def seleccionar_frase_unica():
    usadas = []
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r") as f:
            usadas = f.read().splitlines()
    
    disponibles = [f for f in FRASES_MANUALES if f not in usadas]
    if not disponibles:
        disponibles = FRASES_MANUALES
        open(HISTORIAL_FILE, "w").close() # Reset
    
    frase = random.choice(disponibles)
    with open(HISTORIAL_FILE, "a") as f:
        f.write(frase + "\n")
    return frase

def aplicar_estetica_jjmex(img, tema_slug):
    width, height = img.size
    color = COLORES_TEMA.get(tema_slug, (20,20,20))
    
    # 1. Gradiente Atmosférico
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(height):
        dist = abs(y - height/2) / (height/2)
        opacidad = int(215 - (dist * 135))
        draw.line([(0, y), (width, y)], fill=(color[0], color[1], color[2], opacidad))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # 2. Grano Fílmico
    arr = np.array(img).astype(float)
    ruido = np.random.randn(*arr.shape) * 255 * 0.06
    img = Image.fromarray(np.clip(arr + ruido, 0, 255).astype(np.uint8))
    
    # 3. Marco de Galería
    draw_b = ImageDraw.Draw(img)
    draw_b.rectangle([25, 25, width-25, height-25], outline=(255, 255, 255, 40), width=2)
    return img

def tintar_logo(logo, color_tema):
    logo = logo.convert("RGBA")
    r, g, b, a = logo.split()
    # Tintado sutil al 30% del color del tema
    r = ImageChops.multiply(r, Image.new('L', r.size, int(color_tema[0]*0.5 + 127)))
    g = ImageChops.multiply(g, Image.new('L', g.size, int(color_tema[1]*0.5 + 127)))
    b = ImageChops.multiply(b, Image.new('L', b.size, int(color_tema[2]*0.5 + 127)))
    return Image.merge("RGBA", (r, g, b, a))

def dibujar_texto_pro(draw, frase, autor, tema_slug):
    # Lógica de Fuente Dinámica (Smart Size)
    base_size = 85
    if len(frase) > 60: base_size = 72
    elif len(frase) < 30: base_size = 100

    fnt_path = FONT_SERIF if tema_slug in ["RIQUEZA", "NEGOCIOS"] else FONT_BOLD
    fnt = ImageFont.truetype(fnt_path, base_size)
    fnt_a = ImageFont.truetype(FONT_REGULAR, 48)

    lineas = textwrap.wrap(frase, width=18 if base_size > 80 else 22)
    y_text = (1920 - (len(lineas) * (base_size + 20))) / 2
    
    for l in lineas:
        w = draw.textbbox((0,0), l, font=fnt)[2]
        # Sombra de profundidad
        for o in [(3,3), (5,5)]:
            draw.text(((1080-w)/2 + o[0], y_text + o[1]), l, font=fnt, fill=(0,0,0,150))
        draw.text(((1080-w)/2, y_text), l, font=fnt, fill="white")
        y_text += base_size + 20

    # Autor
    t_a = f"- {autor}"
    w_a = draw.textbbox((0,0), t_a, font=fnt_a)[2]
    draw.text(((1080-w_a)/2, y_text + 60), t_a, font=fnt_a, fill="#cccccc")

# --- MOTOR PRINCIPAL ---

def crear_poster():
    # 1. Frase Única
    try:
        if random.random() < 0.7: frase, autor = seleccionar_frase_unica(), "JJMex"
        else:
            r = requests.get(URL_API_FRASE, timeout=10).json()[0]
            frase = GoogleTranslator(source='auto', target='es').translate(r['q'])
            autor = r['a']
    except: frase, autor = random.choice(FRASES_MANUALES), "JJMex"

    # 2. Imagen Contextual
    tema_tag = "MOTIVACIONAL"
    busqueda = "dark luxury"
    for k, v in {"dinero":"RIQUEZA", "éxito":"NEGOCIOS", "gym":"GYM", "poder":"PODER", "león":"PODER", "disciplina":"DISCIPLINA"}.items():
        if k in frase.lower():
            tema_tag = v
            busqueda = random.choice(TEMAS.get(v.lower(), ["luxury"]))
            break

    try:
        headers = {'Authorization': PEXELS_KEY}
        r = requests.get(URL_PEXELS, headers=headers, params={'query': busqueda, 'orientation': 'portrait'}, timeout=15).json()
        img = Image.open(BytesIO(requests.get(random.choice(r['photos'])['src']['large2x']).content))
    except: img = Image.open(BytesIO(requests.get(URL_BACKUP).content))

    # 3. Arte
    img = img.resize((1080, 1920))
    img = aplicar_estetica_jjmex(img, tema_tag)
    draw = ImageDraw.Draw(img)
    dibujar_texto_pro(draw, frase, autor, tema_tag)

    # 4. Logo Tintado
    try:
        logo = Image.open(NOMBRE_LOGO)
        logo = tintar_logo(logo, COLORES_TEMA.get(tema_tag, (255,255,255)))
        logo.thumbnail((300, 300))
        img.paste(logo, (740, 1610), logo)
    except: pass

    # 5. Envío
    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={'chat_id': CHAT_ID, 'text': "📡 <i>Sincronizando banco de datos de mentalidad y generando activo visual...</i>", 'parse_mode': 'HTML'})
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                  files={'photo': ('p.jpg', bio)}, 
                  data={'chat_id': CHAT_ID, 'caption': f"🐺 <b>{frase}</b>\n\n- {autor}\n\n#JJMex #{tema_tag}", 'parse_mode': 'HTML'})

if __name__ == "__main__":
    crear_poster()
