import os
import random
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from colorthief import ColorThief
from moviepy.editor import (
    ColorClip, CompositeVideoClip, ImageClip,
    AudioFileClip, CompositeAudioClip
)

st.set_page_config(page_title="Gerador de Reels GLCTech", layout="centered")
st.title("🎬 Gerador de Reels para GLCTech")

logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
music_file = st.file_uploader("Upload da música de fundo (MP3)", type=["mp3"])
dica_texto = st.text_area("Digite a dica de Zabbix")
slogan_texto = st.text_input("Slogan da empresa (opcional)", "GLCTech - Monitoramento profissional com Zabbix")

gerar = st.button("🎥 Gerar Vídeo")

def cor_contraste(rgb):
    r, g, b = rgb
    luminancia = (0.299*r + 0.587*g + 0.114*b)/255
    return 'black' if luminancia > 0.6 else 'white'

def gerar_texto_clip(texto, tamanho, cor_texto, largura=1080, altura=300, duracao=4):
    img = Image.new("RGB", (largura, altura), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", tamanho)
    except:
        fonte = ImageFont.load_default()
    text_w, text_h = draw.textsize(texto, font=fonte)
    pos = ((largura - text_w) // 2, (altura - text_h) // 2)
    draw.text(pos, texto, fill=cor_texto, font=fonte)
    path_tmp = f"reels/texto_{random.randint(1000,9999)}.png"
    img.save(path_tmp)
    return ImageClip(path_tmp).set_duration(duracao)

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

    texto_clip = gerar_texto_clip(dica_texto, 60, texto_color, duracao=5)
    texto_clip = texto_clip.set_position(("center", "center"))

    slogan_clip = gerar_texto_clip(slogan_texto, 40, texto_color, duracao=3)
    slogan_clip = slogan_clip.set_position(("center", 1600)).set_start(7)

    logo = ImageClip(logo_path).set_duration(10).resize(height=150).set_position((30, 30))

    musica = AudioFileClip(music_path).volumex(0.2)
    narracao = AudioFileClip(audio_path)
    audio_final = CompositeAudioClip([musica, narracao])

    video = CompositeVideoClip([fundo, texto_clip, slogan_clip, logo])
    video = video.set_audio(audio_final).set_duration(10)

    output_path = os.path.join("reels", f"reel_{random.randint(100,999)}.mp4")
    video.write_videofile(output_path, fps=24)

    st.success("Vídeo gerado com sucesso!")
    st.video(output_path)

elif gerar:
    st.warning("Por favor, preencha todos os campos antes de gerar o vídeo.")