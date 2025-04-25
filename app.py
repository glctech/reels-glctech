import os
import random
import textwrap
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from colorthief import ColorThief

st.set_page_config(page_title="Gerador de Reels GLCTech", layout="centered")
st.title("🎬 Gerador de Reels para GLCTech")

# Entradas
logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
music_file = st.file_uploader("Upload da música de fundo (MP3)", type=["mp3"])
dica_texto = st.text_area("Digite a dica de Zabbix")
slogan_texto = st.text_input("Slogan da empresa (opcional)", "GLCTech - Monitoramento profissional com Zabbix")
gerar = st.button("🎥 Gerar Vídeo")

def cor_contraste(rgb):
    r, g, b = rgb
    luminancia = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return 'black' if luminancia > 0.6 else 'white'

def quebra_texto(texto, max_caracteres=40):
    return "\n".join(textwrap.wrap(texto, width=max_caracteres))

def gerar_texto_clip(texto, tamanho_fonte, cor, dimensao, duracao=8):
    largura, altura = dimensao
    img = Image.new('RGBA', dimensao, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    try:
        fonte = ImageFont.truetype("arial.ttf", tamanho_fonte)
    except:
        fonte = ImageFont.load_default()

    linhas = texto.split('\n')
    altura_texto = sum([draw.textbbox((0, 0), linha, font=fonte)[3] for linha in linhas])
    y_texto = (altura - altura_texto) // 2

    for linha in linhas:
        largura_linha = draw.textbbox((0, 0), linha, font=fonte)[2]
        x_texto = (largura - largura_linha) // 2
        draw.text((x_texto, y_texto), linha, font=fonte, fill=cor)
        y_texto += draw.textbbox((0, 0), linha, font=fonte)[3]

    caminho = "reels/temp_texto.png"
    img.save(caminho)
    return ImageClip(caminho).set_duration(duracao)

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

    # Narração
    tts = gTTS(dica_texto, lang='pt')
    tts.save(audio_path)

    fundo_top = ColorClip(size=(1080, 960), color=dominant_color, duration=10)
    fundo_bottom = ColorClip(size=(1080, 960), color=tuple(min(255, c + 30) for c in dominant_color), duration=10)
    fundo = concatenate_videoclips([fundo_top, fundo_bottom], method="compose")

    # Geração do texto da dica e slogan como imagem com PIL
    texto_quebrado = quebra_texto(dica_texto)
    texto_clip = gerar_texto_clip(texto_quebrado, 60, texto_color, (1000, 1000), duracao=8).set_position("center").fadein(0.5).fadeout(0.5)
    slogan_clip = gerar_texto_clip(slogan_texto, 40, texto_color, (1000, 200), duracao=2).set_position(("center", 1700)).fadein(0.5).fadeout(0.5)

    logo = ImageClip(logo_path).set_duration(10).resize(height=150).set_position((30, 30)).fadein(0.5)

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
