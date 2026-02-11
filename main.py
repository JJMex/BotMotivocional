import os
import requests
import textwrap
import random
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')
NOMBRE_LOGO = "logo_jjmex.png"

# Fuentes del sistema (Instaladas vía diario.yml)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

URL_API_FRASE = "https://zenquotes.io/api/random"
URL_PEXELS = "https://api.pexels.com/v1/search"
URL_BACKUP = "https://picsum.photos/1080/1920"

# --- PALETA Y TEMAS ---
COLORES_TEMA = {
    "RIQUEZA": (45, 35, 10), "NEGOCIOS": (25, 25, 35), "PODER": (40, 5, 5),
    "GYM": (30, 30, 30), "DISCIPLINA": (5, 25, 45), "MOTIVACIONAL": (15, 15, 15)
}

TEMAS = {
    "riqueza": ["luxury", "gold", "yacht", "mansion"],
    "negocios": ["office", "wall street", "suit", "success"],
    "poder": ["lion", "wolf", "king", "throne"],
    "gym": ["bodybuilding", "workout", "fitness", "weights"],
    "disciplina": ["samurai", "spartan", "discipline", "running"],
    "default": ["dark mountains", "city night", "ocean storm"]
}

# --- ARSENAL DE 100+ FRASES ELITE ---
FRASES_MANUALES = [
    "La disciplina te llevará donde la motivación no alcanza.",
    "Tu mente es tu activo más valioso; invierte en ella cada día.",
    "Los imperios no se construyen en horario de oficina.",
    "El dolor de la disciplina pesa gramos; el del arrepentimiento, toneladas.",
    "Sé un león en un mundo de ovejas que solo saben quejarse.",
    "Tu cuenta bancaria es el tablero de puntuación de tus decisiones.",
    "No te detengas cuando estés cansado, detente cuando hayas terminado.",
    "La riqueza no se trata de tener dinero, se trata de tener opciones.",
    "Trabaja en silencio, que el rugido de tu motor hable por ti.",
    "El éxito es la mejor venganza contra los que dudaron.",
    "Si no naces con el privilegio, construye el legado.",
    "La comodidad es la droga que mata los grandes sueños.",
    "No busques suerte, busca frecuencia y ejecución impecable.",
    "El mercado solo paga por resultados, no por buenas intenciones.",
    "Tu red de contactos define tu patrimonio neto.",
    "Gana dinero mientras duermes o trabajarás hasta el último aliento.",
    "La obsesión vence al talento cuando el talento no se obsesiona.",
    "Sé tan bueno que sea imposible que te ignoren.",
    "No cuentes tus planes, muestra tus activos.",
    "El miedo es un indicador de que vas por el camino correcto.",
    "La autodisciplina es la forma más alta de amor propio.",
    "Tu cuerpo es el templo que sostiene tu imperio; entrénalo.",
    "No bajes el precio de tus sueños, aumenta tu valor en el mercado.",
    "Un ganador es un perdedor que lo intentó una vez más.",
    "La verdadera libertad es no tener que pedir permiso a nadie.",
    "Si te juntas con 5 millonarios, tú serás el sexto de la lista.",
    "El sudor del gimnasio previene las lágrimas del hospital.",
    "Los perdedores miran la pared; los ganadores escalan la montaña.",
    "El dinero es libertad amplificada; úsalo con inteligencia.",
    "Naciste para liderar, no para seguir el rebaño.",
    "Hazlo con miedo, hazlo cansado, pero hazlo.",
    "Tu pasado es solo una lección, no una sentencia de por vida.",
    "La paciencia es amarga, pero el fruto del éxito es dulce.",
    "No esperes la oportunidad, crea el entorno para que aparezca.",
    "El respeto se gana con hechos, no con palabras vacías.",
    "Tu única competencia real es la persona que viste en el espejo ayer.",
    "Construye una vida de la que no necesites vacaciones.",
    "El riesgo es el precio de la entrada a la grandeza.",
    "Sé implacable con tus metas y flexible con tus métodos.",
    "El lunes es el día de caza para los que aman el proceso.",
    "No busques aprobación, busca apalancamiento.",
    "La lealtad es un regalo caro que no se encuentra en gente barata.",
    "Tu mentalidad es el motor; tu disciplina es el combustible.",
    "Si fuera fácil, todos tendrían el Ferrari.",
    "La excelencia es un hábito, no un evento aislado.",
    "El dolor es temporal, pero la gloria de haberlo logrado es eterna.",
    "No te compares con nadie, cada imperio tiene su propio tiempo.",
    "La disciplina es hacer lo que odias como si lo amaras.",
    "Prefiero morir en el intento que vivir en la mediocridad.",
    "El dinero no cambia a la gente, solo muestra quiénes son realmente.",
    "Si quieres paz, prepárate para la guerra en los negocios.",
    "La mayor inversión es la que haces en tu propio cerebro.",
    "No persigas el dinero, persigue la visión y el impacto.",
    "Sé la oveja negra que cambia la historia de su familia.",
    "El fracaso es solo el fertilizante para tu próximo éxito.",
    "Tu red es tu patrimonio; elige bien con quién te sientas a la mesa.",
    "Obsesión es lo que los mediocres llaman dedicación.",
    "Si no estás creciendo, estás muriendo lentamente.",
    "El gimnasio forja el carácter que los negocios necesitan.",
    "No cuentes las repeticiones, haz que cada repetición cuente.",
    "La suerte favorece a la mente preparada y disciplinada.",
    "Vive un par de años como nadie quiere, para vivir el resto como nadie puede.",
    "La confianza no es 'les gustaré', es 'estaré bien si no les gusto'.",
    "Los líderes leen mientras los demás duermen o ven televisión.",
    "El carácter se forja en la oscuridad y se celebra bajo la luz.",
    "No busques el camino fácil, busca el camino que valga la pena.",
    "Tu salario es la droga que te dan para olvidar tus sueños.",
    "La gratitud te da paz, pero la ambición te da el mundo.",
    "Nunca tomes consejos de alguien que no tenga los resultados que tú quieres.",
    "El éxito es 1% inspiración y 99% ejecución implacable.",
    "No bajes el volumen de tu ambición para que los demás estén cómodos.",
    "Cada 'no' te acerca más al 'sí' que cambiará tu vida.",
    "La verdadera riqueza es tiempo libre y salud física.",
    "Si no puedes controlar tus emociones, no puedes controlar tu dinero.",
    "Sé un caballero en el trato y un monstruo en la ejecución.",
    "El mundo no te debe nada; sal y gánatelo tú mismo.",
    "Tu potencial es infinito, tus miedos son solo mentiras.",
    "La consistencia vence al talento cada día de la semana.",
    "No busques comodidad, busca desafíos que te obliguen a crecer.",
    "El dinero fluye hacia donde hay orden y valor.",
    "Tu vida cambia el día que decides que no aceptarás menos de lo que mereces.",
    "La pobreza es un estado mental; la escasez es solo una etapa.",
    "Sé el arquitecto de tu propio destino y el capitán de tu alma.",
    "No dejes que mentes pequeñas te digan que tus sueños son muy grandes.",
    "El éxito requiere sacrificio, pero el fracaso es mucho más caro.",
    "Entrena hasta que tus ídolos se conviertan en tus competidores.",
    "La lealtad a tus metas debe ser inquebrantable.",
    "No expliques tu filosofía, simplemente encárnala.",
    "El tiempo es el único recurso que no puedes recuperar; úsalo bien.",
    "Sé peligroso pero mantente bajo control absoluto.",
    "La marca JJMex es sinónimo de disciplina y poder.",
    "El éxito es la suma de pequeños esfuerzos repetidos cada día.",
    "No hables de tus planes, deja que tus activos hablen por ti.",
    "La cima está vacía porque muy pocos están dispuestos a pagar el precio.",
    "Ahorrar es sobrevivir, invertir es conquistar.",
    "Si te rindes hoy, el sacrificio de ayer no sirvió de nada.",
    "El dolor del entrenamiento es insignificante comparado con el de la debilidad.",
    "Sé implacable. Sé legendario. Sé JJMex.",
    "Tu visión debe ser tan clara que tus miedos se vuelvan irrelevantes.",
    "El imperio comienza en tu mente antes de manifestarse en la realidad."
]

# --- UTILIDADES VISUALES AVANZADAS ---

def añadir_grano(img, intensidad=0.06):
    """Añade ruido fílmico para unificar los elementos visuales."""
    img_array = np.array(img).astype(float)
    ruido = np.random.randn(*img_array.shape) * 255 * intensidad
    img_ruido = np.clip(img_array + ruido, 0, 255).astype(np.uint8)
    return Image.fromarray(img_ruido)

def dibujar_texto_con_profundidad(draw, position, texto, fuente, color_relleno="white"):
    """Dibuja texto con sombra proyectada para efecto 3D."""
    x, y = position
    for offset in [(2,2), (4,4)]:
        draw.text((x+offset[0], y+offset[1]), texto, font=fuente, fill=(0,0,0,120))
    draw.text((x, y), texto, font=fuente, fill=color_relleno)

# --- MOTORES DE GENERACIÓN ---

def obtener_imagen_segura(frase):
    """Blindaje de errores: Si Pexels falla, activa respaldo."""
    frase_low = frase.lower()
    tema_slug = "MOTIVACIONAL"
    busqueda = "dark luxury"

    keywords = {
        "dinero": "RIQUEZA", "riqueza": "RIQUEZA", "millonario": "RIQUEZA",
        "negocio": "NEGOCIOS", "éxito": "NEGOCIOS", "imperio": "NEGOCIOS",
        "gym": "GYM", "entrena": "GYM", "cuerpo": "GYM", "hierro": "GYM",
        "león": "PODER", "rey": "PODER", "lobo": "PODER", "poder": "PODER",
        "disciplina": "DISCIPLINA", "hábito": "DISCIPLINA", "noche": "DISCIPLINA"
    }

    for k, v in keywords.items():
        if k in frase_low:
            tema_slug = v
            busqueda = random.choice(TEMAS.get(v.lower(), ["luxury"]))
            break

    try:
        headers = {'Authorization': PEXELS_KEY}
        r = requests.get(URL_PEXELS, headers=headers, params={'query': busqueda, 'orientation': 'portrait'}, timeout=15)
        r.raise_for_status()
        data = r.json()
        foto = random.choice(data['photos'])
        img_data = requests.get(foto['src']['large2x']).content
        return Image.open(BytesIO(img_data)), tema_slug
    except Exception as e:
        print(f"⚠️ Pexels offline: {e}. Usando Backup.")
        img_data = requests.get(URL_BACKUP).content
        return Image.open(BytesIO(img_data)), "MOTIVACIONAL"

def crear_poster():
    # 1. Selección de Contenido (60% Manual / 40% API)
    try:
        if random.random() < 0.6:
            frase, autor = random.choice(FRASES_MANUALES), "JJMex"
        else:
            r = requests.get(URL_API_FRASE, timeout=10).json()[0]
            frase = GoogleTranslator(source='auto', target='es').translate(r['q'])
            autor = r['a']
    except: frase, autor = random.choice(FRASES_MANUALES), "JJMex"

    # 2. Procesamiento de Imagen Pro
    img, tema_tag = obtener_imagen_segura(frase)
    img = img.resize((1080, 1920))
    
    # Aplicar Gradiente de Color Atmosférico
    color_base = COLORES_TEMA.get(tema_tag, (0,0,0))
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(1920):
        dist = abs(y - 960) / 960
        opacidad = int(215 - (dist * 135))
        draw_ov.line([(0, y), (1080, y)], fill=(color_base[0], color_base[1], color_base[2], opacidad))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    img = añadir_grano(img) # Textura cinematográfica
    
    # Marco de Galería Minimalista
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 25, 1055, 1895], outline=(255, 255, 255, 45), width=2)

    # 3. Tipografía Dinámica por Tema
    try:
        fnt_path = FONT_SERIF if tema_tag in ["RIQUEZA", "NEGOCIOS"] else FONT_BOLD
        fnt = ImageFont.truetype(fnt_path, 82)
        fnt_autor = ImageFont.truetype(FONT_REGULAR, 48)
    except:
        fnt = ImageFont.load_default()
        fnt_autor = ImageFont.load_default()

    # 4. Dibujar Texto con Profundidad
    lineas = textwrap.wrap(frase, width=18)
    y_text = (1920 - (len(lineas) * 110)) / 2
    for l in lineas:
        w = draw.textbbox((0, 0), l, font=fnt)[2]
        dibujar_texto_con_profundidad(draw, ((1080-w)/2, y_text), l, fnt)
        y_text += 110

    # Dibujar Autor
    texto_a = f"- {autor}"
    w_a = draw.textbbox((0, 0), texto_a, font=fnt_autor)[2]
    dibujar_texto_con_profundidad(draw, ((1080-w_a)/2, y_text + 60), texto_a, fnt_autor, color_relleno="#e0e0e0")

    # 5. Logo JJMex Visible
    try:
        logo = Image.open(NOMBRE_LOGO).convert("RGBA")
        logo.thumbnail((300, 300)) 
        img.paste(logo, (740, 1610), logo) 
    except: pass

    # 6. Envío a Telegram con Aviso de Sistema
    bio = BytesIO()
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={'chat_id': CHAT_ID, 'text': "📡 <i>Sincronizando banco de datos de mentalidad y generando activo visual...</i>", 'parse_mode': 'HTML'}, timeout=10)
    
    caption_txt = f"🐺 <b>{frase}</b>\n\n- {autor}\n\n#Poder #JJMex #{tema_tag}"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                  files={'photo': ('poster.jpg', bio)}, 
                  data={'chat_id': CHAT_ID, 'caption': caption_txt, 'parse_mode': 'HTML'})

if __name__ == "__main__":
    crear_poster()
