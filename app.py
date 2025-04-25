import os
import random
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from colorthief import ColorThief
from io import BytesIO

st.set_page_config(page_title="Gerador de Post para Instagram - GLCTech", layout="centered")
st.title("🎨 Gerador de Post para Instagram - GLCTech")

# Uploads e entradas
logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
bg_image_file = st.file_uploader("Upload da imagem de fundo", type=["png", "jpg", "jpeg", "gif"])
music_file = st.file_uploader("Upload da música de fundo (MP3)", type=["mp3"])
dica_texto = st.text_area("Digite a dica de Zabbix")
slogan_texto = st.text_input("Slogan da empresa (opcional)", "GLCTech - Monitoramento profissional com Zabbix")

gerar = st.button("🖼️ Gerar Post")

# Função auxiliar para calcular cor de contraste
def cor_contraste(rgb):
    r, g, b = rgb
    luminancia = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return 'black' if luminancia > 0.6 else 'white'

# Função para adicionar o texto na imagem de fundo
def renderizar_texto_na_imagem(imagem_fundo, texto, cor_texto, cor_fundo, texto_fonte="Arial", tamanho_fonte=60):
    img = imagem_fundo.copy()
    draw = ImageDraw.Draw(img)

    # Escolher uma fonte
    try:
        fonte = ImageFont.truetype("Arial-Bold.ttf", tamanho_fonte)
    except IOError:
        fonte = ImageFont.load_default()
    
    largura_texto, altura_texto = draw.textsize(texto, font=fonte)
    
    # Ajustar o texto para centralizar
    posicao_texto = ((img.width - largura_texto) // 2, (img.height - altura_texto) // 2)
    
    # Adicionar sombra ao texto
    draw.text((posicao_texto[0] + 2, posicao_texto[1] + 2), texto, font=fonte, fill='black')
    draw.text(posicao_texto, texto, font=fonte, fill=cor_texto)

    return img

if gerar and logo_file and bg_image_file and dica_texto:
    st.info("Processando post...")

    # Criar pastas e salvar arquivos temporários
    os.makedirs("posts", exist_ok=True)
    logo_path = os.path.join("posts", "logo.png")
    bg_image_path = os.path.join("posts", "background.png")
    audio_path = os.path.join("posts", "audio.mp3")

    # Salvar arquivos carregados
    with open(logo_path, "wb") as f:
        f.write(logo_file.read())
    
    with open(bg_image_path, "wb") as f:
        f.write(bg_image_file.read())

    # Carregar a imagem de fundo
    bg_img = Image.open(bg_image_path)

    # Ajustar a imagem de fundo para as dimensões do post do Instagram (1080x1080)
    bg_img = bg_img.resize((1080, 1080), Image.ANTIALIAS)
    
    # Extrair cor dominante da imagem de fundo
    color_thief = ColorThief(bg_image_path)
    dominant_color = color_thief.get_color(quality=1)
    texto_color = cor_contraste(dominant_color)

    # Gerar texto
    texto_img = renderizar_texto_na_imagem(bg_img, dica_texto, cor_texto=texto_color, cor_fundo=dominant_color)

    # Adicionar logo no canto superior esquerdo
    logo = Image.open(logo_path)
    logo_resized = logo.resize((150, 150))
    texto_img.paste(logo_resized, (30, 30), logo_resized)

    # Salvar a imagem gerada como post
    output_image_path = os.path.join("posts", f"post_{random.randint(100,999)}.png")
    texto_img.save(output_image_path)

    st.success("Post gerado com sucesso!")
    st.image(output_image_path, caption="Post para Instagram")

    # Oferecer o download do post
    with open(output_image_path, "rb") as f:
        st.download_button("Baixar Post", f, file_name=os.path.basename(output_image_path))

elif gerar:
    st.warning("Por favor, preencha todos os campos antes de gerar o post.")
