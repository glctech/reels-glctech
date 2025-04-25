# app.py
import os
import random
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from gtts import gTTS
from colorthief import ColorThief

st.set_page_config(page_title="Gerador de Post GLCTech", layout="centered")
st.title("🖼️ Gerador de Post para Instagram - GLCTech")

# Uploads e entradas
logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
dica_texto = st.text_area("Digite a dica de Zabbix")
slogan_texto = st.text_input("Slogan da empresa (opcional)", "GLCTech - Monitoramento profissional com Zabbix")
gerar = st.button("📸 Gerar Post")

# Função auxiliar para calcular cor de contraste
def cor_contraste(rgb):
    r, g, b = rgb
    luminancia = (0.299*r + 0.587*g + 0.114*b)/255
    return 'black' if luminancia > 0.6 else 'white'

# Função para gerar imagem do post
def gerar_post(logo_path, dica, slogan, cor_fundo, cor_texto, output_path):
    largura, altura = 1080, 1080
    imagem = Image.new('RGB', (largura, altura), cor_fundo)
    draw = ImageDraw.Draw(imagem)

    try:
        fonte_dica = ImageFont.truetype("DejaVuSans-Bold.ttf", size=60)
        fonte_slogan = ImageFont.truetype("DejaVuSans-Bold.ttf", size=40)
    except:
        fonte_dica = ImageFont.load_default()
        fonte_slogan = ImageFont.load_default()

    # Centralizar texto da dica
    linhas = dica.split('\n')
    y_text = 300
    for linha in linhas:
        w, h = draw.textbbox((0, 0), linha, font=fonte_dica)[2:]
        draw.text(((largura - w) / 2, y_text), linha, font=fonte_dica, fill=cor_texto)
        y_text += h + 10

    # Slogan na parte inferior
    w_s, h_s = draw.textbbox((0, 0), slogan, font=fonte_slogan)[2:]
    draw.text(((largura - w_s) / 2, altura - 120), slogan, font=fonte_slogan, fill=cor_texto)

    # Inserir logo
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((200, 200))
    imagem.paste(logo, (30, 30), logo)

    imagem.save(output_path)

if gerar and logo_file and dica_texto:
    st.info("Gerando imagem...")

    os.makedirs("posts", exist_ok=True)
    logo_path = os.path.join("posts", "logo.png")
    with open(logo_path, "wb") as f:
        f.write(logo_file.read())

    color_thief = ColorThief(logo_path)
    dominant_color = color_thief.get_color(quality=1)
    texto_color = cor_contraste(dominant_color)

    output_path = os.path.join("posts", f"post_{random.randint(100,999)}.png")
    gerar_post(logo_path, dica_texto, slogan_texto, dominant_color, texto_color, output_path)

    st.success("Post criado com sucesso!")
    st.image(output_path, caption="Prévia do Post", use_column_width=True)
    with open(output_path, "rb") as f:
        st.download_button("📥 Baixar imagem", f, file_name=os.path.basename(output_path))

elif gerar:
    st.warning("Por favor, preencha todos os campos obrigatórios para gerar o post.")
