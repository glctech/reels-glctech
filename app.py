# app.py
import os
import random
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from colorthief import ColorThief

st.set_page_config(page_title="Gerador de Posts GLCTech", layout="centered")
st.title("🖼️ Gerador de Posts para Instagram - GLCTech")

# Uploads e entradas
logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
music_file = st.file_uploader("Upload da música de fundo (MP3)", type=["mp3"])
background_file = st.file_uploader("Upload da imagem de fundo (JPG, PNG, GIF)", type=["jpg", "jpeg", "png", "gif"])
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
    img = Image.new('RGB', (largura, altura), cor_fundo)
    draw = ImageDraw.Draw(img)
    try:
        fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
    except:
        fonte = ImageFont.load_default()
    texto_linhas = texto.split("\n")
    altura_total = sum(fonte.getbbox(linha)[3] for linha in texto_linhas) + len(texto_linhas)*10
    y_texto = (altura - altura_total) // 2
    for linha in texto_linhas:
        largura_texto = fonte.getlength(linha)
        x_texto = (largura - largura_texto) // 2
        draw.text((x_texto, y_texto), linha, fill=cor_texto, font=fonte)
        y_texto += fonte.getbbox(linha)[3] + 10
    caminho = os.path.join("posts", f"post_{random.randint(100,999)}.png")
    img.save(caminho)
    return caminho

if gerar and logo_file and dica_texto and background_file:
    st.info("Gerando post...")

    os.makedirs("posts", exist_ok=True)
    logo_path = os.path.join("posts", "logo.png")
    bg_path = os.path.join("posts", background_file.name)
    
    with open(logo_path, "wb") as f:
        f.write(logo_file.read())
    with open(bg_path, "wb") as f:
        f.write(background_file.read())

    # Extrair cor dominante
    color_thief = ColorThief(logo_path)
    dominant_color = color_thief.get_color(quality=1)
    texto_color = cor_contraste(dominant_color)

    # Criar imagem base
    imagem_fundo = Image.open(bg_path).convert("RGB").resize((1080, 1080))
    draw = ImageDraw.Draw(imagem_fundo)

    # Fonte segura
    try:
        fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
    except:
        fonte = ImageFont.load_default()

    # Texto principal
    texto_linhas = dica_texto.split("\n")
    altura_total = sum(fonte.getbbox(linha)[3] for linha in texto_linhas) + len(texto_linhas)*10
    y_texto = (1080 - altura_total) // 2
    for linha in texto_linhas:
        largura_texto = fonte.getlength(linha)
        x_texto = (1080 - largura_texto) // 2
        draw.text((x_texto, y_texto), linha, fill=texto_color, font=fonte)
        y_texto += fonte.getbbox(linha)[3] + 10

    # Logo
    logo = Image.open(logo_path).convert("RGBA").resize((150, 150))
    imagem_fundo.paste(logo, (30, 30), logo)

    # Slogan
    largura_slogan = fonte.getlength(slogan_texto)
    x_slogan = (1080 - largura_slogan) // 2
    draw.text((x_slogan, 1020), slogan_texto, fill=texto_color, font=fonte)

    post_path = os.path.join("posts", f"post_final_{random.randint(100,999)}.png")
    imagem_fundo.save(post_path)

    st.success("Post gerado com sucesso!")
    st.image(post_path)

elif gerar:
    st.warning("Por favor, preencha todos os campos obrigatórios.")
