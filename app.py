import os
import random
from gtts import gTTS
from PIL import Image
import streamlit as st
from colorthief import ColorThief
from moviepy.editor import *
from moviepy.video.fx.all import fadein, fadeout

st.set_page_config(page_title="Gerador de Reels GLCTech", layout="centered")
st.title("🎬 Gerador de Reels para GLCTech")

# Uploads e entradas
logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
music_file = st.file_uploader("Upload da música de fundo (MP3)", type=["mp3"])
dica_texto = st.text_area("Digite a dica de Zabbix")
slogan_texto = st.text_input("Slogan da empresa (opcional)", "GLCTech - Monitoramento profissional com Zabbix")

gerar = st.button("🎥 Gerar Vídeo")

def cor_contraste(rgb):
    r, g, b = rgb
    luminancia = (0.299*r + 0.587*g + 0.114*b)/255
    return 'black' if luminancia > 0.6 else 'white'

if gerar and logo_file and music_file and dica_texto:
    st.info("Processando vídeo...")

    os.makedirs("reels", exist_ok=True)
    logo_path = os.path.join("reels", "logo.png")
    music_path = os.path.join("reels", "music.mp3")
    audio_path = os.path.join("reels", "audio.mp3")

    with open(logo_path, "wb") as f:
        f.write(logo_file.read())
    with open(music_path, "wb") as f:
        f.write(music_file.read())

    color_thief = ColorThief(logo_path)
    dominant_color = color_thief.get_color(quality=1)
    texto_color = cor_contraste(dominant_color)

    tts = gTTS(dica_texto, lang='pt')
    tts.save(audio_path)

    fundo = ColorClip(size=(1080, 1920), color=dominant_color, duration=10)

    texto_clip = TextClip(dica_texto, fontsize=60, color=texto_color, font='DejaVu-Sans-Bold', size=(900, None), method='label')
    texto_clip = texto_clip.set_position(('center', 'center')).set_duration(8)
    texto_clip = fadein(texto_clip, 0.5)
    texto_clip = fadeout(texto_clip, 0.5)

    slogan_clip = TextClip(slogan_texto, fontsize=40, color=texto_color, font='DejaVu-Sans-Bold', size=(1000, None), method='label')
    slogan_clip = slogan_clip.set_position(('center', 1700)).set_duration(2)
    slogan_clip = fadein(slogan_clip, 0.5)
    slogan_clip = fadeout(slogan_clip, 0.5)

    logo = ImageClip(logo_path).set_duration(10).resize(height=150).set_position((30, 30))
    logo = fadein(logo, 0.5)

    musica = AudioFileClip(music_path).volumex(0.2)
    narracao = AudioFileClip(audio_path)
    audio_final = CompositeAudioClip([musica, narracao])

    video = CompositeVideoClip([fundo, texto_clip.set_start(0), slogan_clip.set_start(8), logo])
    video = video.set_audio(audio_final).set_duration(10)

    output_path = os.path.join("reels", f"reel_{random.randint(100,999)}.mp4")
    video.write_videofile(output_path, fps=24)

    st.success("Vídeo gerado com sucesso!")
    st.video(output_path)
elif gerar:
    st.warning("Por favor, preencha todos os campos antes de gerar o vídeo.")