# app.py
import os
import random
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from colorthief import ColorThief
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, CompositeAudioClip, AudioFileClip

st.set_page_config(page_title="Gerador de Post GLCTech", layout="centered")
st.title("🖼️ Gerador de Posts para Instagram - GLCTech")

# Uploads e entradas
logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
music_file = st.file_uploader("Upload da música de fundo (MP3)", type=["mp3"])
fundo_file = st.file_uploader("Upload da imagem ou vídeo de fundo (JPG/PNG/MP4)", type=["jpg", "png", "mp4"])
dica_texto = st.text_area("Digite a dica de Zabbix")
slogan_texto = st.text_input("Slogan da empresa (opcional)", "GLCTech - Monitoramento profissional com Zabbix")

gerar = st.button("🖼️ Gerar Post")

# Função auxiliar para calcular cor de contraste
def cor_contraste(rgb):
    r, g, b = rgb
    luminancia = (0.299*r + 0.587*g + 0.114*b)/255
    return 'black' if luminancia > 0.6 else 'white'

# Função para renderizar texto em imagem
def renderizar_texto_em_imagem(texto, cor_fundo, cor_texto, largura=1080, altura=1080):
    img = Image.new('RGB', (largura, altura), color=cor_fundo)
    draw = ImageDraw.Draw(img)
    fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)

    # Centralizar texto
    bbox = draw.textbbox((0, 0), texto, font=fonte)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (largura - w) / 2
    y = (altura - h) / 2

    draw.text((x, y), texto, fill=cor_texto, font=fonte, align="center")

    caminho = os.path.join("posts", f"texto_{random.randint(100,999)}.png")
    img.save(caminho)
    return caminho

if gerar and logo_file and music_file and dica_texto:
    st.info("Processando post...")

    os.makedirs("posts", exist_ok=True)
    logo_path = os.path.join("posts", "logo.png")
    music_path = os.path.join("posts", "music.mp3")
    audio_path = os.path.join("posts", "audio.mp3")

    with open(logo_path, "wb") as f:
        f.write(logo_file.read())
    with open(music_path, "wb") as f:
        f.write(music_file.read())

    color_thief = ColorThief(logo_path)
    dominant_color = color_thief.get_color(quality=1)
    texto_color = cor_contraste(dominant_color)

    # Narração
    tts = gTTS(dica_texto, lang='pt')
    tts.save(audio_path)

    # Fundo
    if fundo_file is not None:
        fundo_path = os.path.join("posts", fundo_file.name)
        with open(fundo_path, "wb") as f:
            f.write(fundo_file.read())

        if fundo_path.lower().endswith(".mp4"):
            fundo_clip = VideoFileClip(fundo_path).subclip(0, 10).resize((1080, 1080))
        else:
            fundo_clip = ImageClip(fundo_path).set_duration(10).resize((1080, 1080))
    else:
        fundo_path = renderizar_texto_em_imagem("", cor_fundo=(150,150,150), cor_texto=texto_color)
        fundo_clip = ImageClip(fundo_path).set_duration(10)

    # Texto principal
    texto_path = renderizar_texto_em_imagem(dica_texto, cor_fundo=(0,0,0,0), cor_texto=texto_color)
    texto_clip = ImageClip(texto_path).set_duration(10).set_position('center')

    # Logo
    logo_clip = ImageClip(logo_path).set_duration(10).resize(height=150).set_position((30, 30))

    # Slogan
    slogan_path = renderizar_texto_em_imagem(slogan_texto, cor_fundo=(0,0,0,0), cor_texto=texto_color, altura=200)
    slogan_clip = ImageClip(slogan_path).set_duration(10).set_position((30, 880))

    # Áudio final
    musica = AudioFileClip(music_path).volumex(0.2)
    narracao = AudioFileClip(audio_path)
    audio_final = CompositeAudioClip([musica, narracao])

    post = CompositeVideoClip([fundo_clip, texto_clip, logo_clip, slogan_clip]).set_duration(10).set_audio(audio_final)

    output_path = os.path.join("posts", f"post_{random.randint(100,999)}.mp4")
    post.write_videofile(output_path, fps=24)

    st.success("Post gerado com sucesso!")
    st.video(output_path)

elif gerar:
    st.warning("Por favor, preencha todos os campos obrigatórios.")
