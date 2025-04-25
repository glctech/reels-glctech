# app.py
import os
import random
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from colorthief import ColorThief
import tempfile

st.set_page_config(page_title="Gerador de Posts GLCTech", layout="centered")
st.title("🖼️ Gerador de Posts para Instagram - GLCTech")

# Uploads e entradas
logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
background_file = st.file_uploader("Imagem de fundo (JPG, PNG, GIF)", type=["jpg", "jpeg", "png", "gif"])
dica_texto = st.text_area("Digite a dica de Zabbix")
slogan_texto = st.text_input("Slogan da empresa (opcional)", "GLCTech - Monitoramento profissional com Zabbix")

gerar = st.button("🖼️ Gerar Post")

# Função auxiliar para cor de contraste
def cor_contraste(rgb):
    r, g, b = rgb
    luminancia = (0.299*r + 0.587*g + 0.114*b)/255
    return 'black' if luminancia > 0.6 else 'white'

# Função para criar imagem com texto sobre a imagem de fundo
def criar_post(fundo_path, logo_path, dica, slogan, output_path):
    imagem_fundo = Image.open(fundo_path).convert("RGB")
    imagem_fundo = imagem_fundo.resize((1080, 1080))  # tamanho padrão Instagram

    draw = ImageDraw.Draw(imagem_fundo)

    color_thief = ColorThief(fundo_path)
    cor_dominante = color_thief.get_color(quality=1)
    cor_texto = cor_contraste(cor_dominante)

    try:
        fonte_dica = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
        fonte_slogan = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except:
        fonte_dica = ImageFont.load_default()
        fonte_slogan = ImageFont.load_default()

    # Caixa de texto centralizada
    margem = 60
    caixa_largura = 960
    x_texto = (imagem_fundo.width - caixa_largura) // 2
    y_texto = 300

    draw.text((x_texto, y_texto), dica, font=fonte_dica, fill=cor_texto)
    draw.text((x_texto, 900), slogan, font=fonte_slogan, fill=cor_texto)

    # Adiciona logo
    logo_img = Image.open(logo_path).convert("RGBA")
    logo_img = logo_img.resize((180, 180))
    imagem_fundo.paste(logo_img, (30, 30), logo_img)

    imagem_fundo.save(output_path)

if gerar and logo_file and background_file and dica_texto:
    st.info("Gerando post...")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_logo:
        tmp_logo.write(logo_file.read())
        logo_path = tmp_logo.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_fundo:
        tmp_fundo.write(background_file.read())
        fundo_path = tmp_fundo.name

    output_path = os.path.join("post_final.png")

    criar_post(fundo_path, logo_path, dica_texto, slogan_texto, output_path)

    st.success("Post gerado com sucesso!")
    st.image(output_path, use_column_width=True)

elif gerar:
    st.warning("Por favor, preencha todos os campos antes de gerar o post.")
