# 🐺 JJMex: Bot de Motivación y Poder

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Elite-gold?style=for-the-badge)
![Framework](https://img.shields.io/badge/Engine-Pillow%20%7C%20Numpy-red?style=for-the-badge)

Este bot es el motor de mentalidad del ecosistema **JJMex**. Genera y publica automáticamente piezas de arte visual con frases de alto impacto sobre riqueza, poder, disciplina y fitness, enviándolas directamente a Telegram con un acabado cinematográfico profesional.

---

## 🧠 Inteligencia Visual y Diseño

A diferencia de un bot de frases convencional, este sistema utiliza un motor de procesamiento de imagen avanzado:

* **🎬 Acabado Cinematográfico:** Aplica un efecto de *Film Grain* (grano fílmico) y gradientes atmosféricos dinámicos para una estética de fotografía profesional.
* **🎨 Color Grading Temático:** El bot detecta el sentimiento de la frase (Riqueza, Poder, Gym) y ajusta los tonos de la imagen y el tinte del logo automáticamente.
* **🔡 Tipografía Dinámica:** Cambia entre fuentes *Serif* elegantes para negocios y *Sans Bold* impactantes para temas de fuerza.
* **👁️ Legibilidad Blindada:** Implementa sombras proyectadas (*Drop Shadows*) y capas de transparencia inteligente para que el texto sea siempre el protagonista.

---

## ⚡ Características Técnicas

* **🚫 Sistema Anti-Repetición:** Utiliza un archivo `historial.txt` para asegurar que ninguna de las +100 frases se repita hasta agotar el arsenal completo.
* **🖼️ Búsqueda Contextual:** Conexión con la API de **Pexels** para encontrar fondos que coincidan con las palabras clave de la frase.
* **🛡️ Resiliencia Total:** Doble motor de contenido. Si las APIs externas fallan, el bot activa automáticamente el banco de frases manuales y el motor de imágenes de respaldo.
* **☁️ 100% Serverless:** Ejecutado mediante **GitHub Actions** sin costos de mantenimiento.

---

## 🚀 Instalación y Configuración

1.  **Repositorio:** Realiza un Fork o crea un nuevo repositorio con los archivos `main.py` y `logo_jjmex.png`.
2.  **Historial:** Asegúrate de incluir un archivo llamado `historial.txt` (puede estar vacío al inicio).
3.  **Secretos de GitHub:** Configura las siguientes variables en `Settings > Secrets and variables > Actions`:
    * `TELEGRAM_TOKEN`: Token de tu bot de @BotFather.
    * `TELEGRAM_CHAT_ID`: ID de tu canal o chat personal.
    * `PEXELS_API_KEY`: Tu llave de la API de Pexels.
4.  **Permisos:** Ve a `Settings > Actions > General` y en **Workflow permissions** selecciona *Read and write permissions* para que el bot pueda actualizar el historial.

---

## 📸 Formato de Salida

> 📡 _Sincronizando banco de datos de mentalidad y generando activo visual..._
> 
> **[Imagen con diseño de élite generado por JJMex]**
> 
> 🐺 **La disciplina te llevará donde la motivación no alcanza.**
> 
> - JJMex
> 
> #Poder #JJMex #DISCIPLINA

---

<p align="center">
  <i>"Automatizando la ciudad y la mente para recuperar nuestro tiempo."</i><br>
  <b>Infraestructura de Sistemas JJMex.</b>
</p>
