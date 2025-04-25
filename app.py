# app.py
import os
import random
from gtts import gTTS
from moviepy.editor import *
from PIL import Image
import streamlit as st
from colorthief import ColorThief

st.set_page_config(page_title="Gerador de Posts GLCTech", layout="centered")
st.title("📸 Gerador de Posts para GLCTech")

# Uploads e entradas
logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
music_file = st.file_uploader("Upload da música de fundo (MP3)", type=["mp3"])
fundo_file = st.file_uploader("Upload da imagem ou vídeo de fundo (JPG, PNG, GIF, MP4)", type=["jpg", "jpeg", "png", "gif", "mp4"])
dica_texto = st.text_area("Digite a dica de Zabbix")
slogan_texto = st.text_input("Slogan da empresa (opcional)", "GLCTech - Monitoramento profissional com Zabbix")

gerar = st.button("📸 Gerar Post")

# Função auxiliar para calcular cor de contraste
def cor_contraste(rgb):
    r, g, b = rgb
    luminancia = (0.299*r + 0.587*g + 0.114*b)/255
    return 'black' if luminancia > 0.6 else 'white'

if gerar and logo_file and music_file and fundo_file and dica_texto:
    st.info("Processando post...")

    # Criar pastas e salvar arquivos temporários
    os.makedirs("posts", exist_ok=True)
    logo_path = os.path.join("posts", "logo.png")
    music_path = os.path.join("posts", "music.mp3")
    audio_path = os.path.join("posts", "audio.mp3")
    fundo_path = os.path.join("posts", fundo_file.name)

    with open(logo_path, "wb") as f:
        f.write(logo_file.read())
    with open(music_path, "wb") as f:
        f.write(music_file.read())
    with open(fundo_path, "wb") as f:
        f.write(fundo_file.read())

    # Extrair cor dominante da logo
    color_thief = ColorThief(logo_path)
    dominant_color = color_thief.get_color(quality=1)
    texto_color = cor_contraste(dominant_color)

    # Gerar narração
    tts = gTTS(dica_texto, lang='pt')
    tts.save(audio_path)

    # Definir fundo
    if fundo_path.endswith(".mp4"):
        fundo = VideoFileClip(fundo_path).subclip(0, 10).resize((1080, 1080))
    else:
        fundo = ImageClip(fundo_path).set_duration(10).resize((1080, 1080))

    # Texto da dica
    texto_clip = TextClip(dica_texto, fontsize=60, color=texto_color, size=(1000, None), method='caption', font='Arial-Bold')
    texto_clip = texto_clip.set_position(('center', 'center')).set_duration(8)
    texto_clip = texto_clip.margin(top=20, bottom=20, opacity=0).with_border(color="black", thickness=2)
    texto_clip = texto_clip.fadein(0.5).fadeout(0.5)

    # Slogan
    slogan_clip = TextClip(slogan_texto, fontsize=40, color=texto_color, size=(1000, None), method='caption', font='Arial-Bold')
    slogan_clip = slogan_clip.set_position(('center', 960)).set_duration(2)
    slogan_clip = slogan_clip.margin(top=10, bottom=10, opacity=0).with_border(color="black", thickness=2)
    slogan_clip = slogan_clip.fadein(0.5).fadeout(0.5)

    # Logo
    logo = ImageClip(logo_path).set_duration(10).resize(height=150).set_position((30, 30)).fadein(0.5)

    # Música e narração
    musica = AudioFileClip(music_path).volumex(0.2)
    narracao = AudioFileClip(audio_path)
    audio_final = CompositeAudioClip([musica, narracao])

    # Montar post
    post = CompositeVideoClip([fundo, texto_clip.set_start(0), slogan_clip.set_start(8), logo])
    post = post.set_audio(audio_final).set_duration(10)

    output_path = os.path.join("posts", f"post_{random.randint(100,999)}.mp4")
    post.write_videofile(output_path, fps=24)

    st.success("Post gerado com sucesso!")
    st.video(output_path)

elif gerar:
    st.warning("Por favor, preencha todos os campos antes de gerar o post.")
