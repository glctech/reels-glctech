import os
import random
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from colorthief import ColorThief

st.set_page_config(page_title="Gerador de Post para Instagram - GLCTech", layout="centered")
st.title("🎨 Gerador de Post para Instagram - GLCTech")

# Função para calcular a cor de contraste (preto ou branco)
def cor_contraste(rgb):
    r, g, b = rgb
    luminancia = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return 'black' if luminancia > 0.6 else 'white'

# Função para renderizar o texto na imagem de fundo
def renderizar_texto_na_imagem(imagem_fundo, texto, cor_texto, texto_fonte="Arial", tamanho_fonte=20):
    img = imagem_fundo.copy()
    draw = ImageDraw.Draw(img)

    # Tentar carregar uma fonte personalizada
    try:
        fonte = ImageFont.truetype("Arial-Bold.ttf", tamanho_fonte)
    except IOError:
        fonte = ImageFont.load_default()

    # Usar textbbox() para calcular a caixa delimitadora do texto
    largura_texto, altura_texto = draw.textbbox((0, 0), texto, font=fonte)[2:4]

    # Ajustar o texto para centralizar
    posicao_texto = ((img.width - largura_texto) // 2, (img.height - altura_texto) // 2)

    # Adicionar sombra ao texto (facilita a leitura)
    draw.text((posicao_texto[0] + 2, posicao_texto[1] + 2), texto, font=fonte, fill='black')
    draw.text(posicao_texto, texto, font=fonte, fill=cor_texto)

    return img

# Função para ajustar o logotipo proporcionalmente e aumentar 50%
def ajustar_logotipo_proporcional(logo, tamanho_maximo=150, aumento=1.5):
    largura, altura = logo.size
    # Aumentar o logotipo em 50%
    fator_escala = min(tamanho_maximo / largura, tamanho_maximo / altura) * aumento
    nova_largura = int(largura * fator_escala)
    nova_altura = int(altura * fator_escala)
    return logo.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)

# Função principal do app
def main():
    # Uploads e entradas
    logo_file = st.file_uploader("Upload da logo (PNG)", type=["png"])
    bg_image_file = st.file_uploader("Upload da imagem de fundo", type=["png", "jpg", "jpeg", "gif"])
    dica_texto = st.text_area("Digite a dica de Zabbix")
    slogan_texto = st.text_input("Slogan da empresa (opcional)", "GLCTech - Monitoramento profissional com Zabbix")

    gerar = st.button("🖼️ Gerar Post")

    if gerar and logo_file and bg_image_file and dica_texto:
        st.info("Processando post...")

        # Criar pastas e salvar arquivos temporários
        os.makedirs("posts", exist_ok=True)
        logo_path = os.path.join("posts", "logo.png")
        bg_image_path = os.path.join("posts", "background.png")

        # Salvar arquivos carregados
        with open(logo_path, "wb") as f:
            f.write(logo_file.read())
        
        with open(bg_image_path, "wb") as f:
            f.write(bg_image_file.read())

        # Carregar a imagem de fundo
        try:
            bg_img = Image.open(bg_image_path)
        except IOError:
            st.error("Erro ao abrir a imagem de fundo. Por favor, tente novamente.")
            return

        # Ajustar a imagem de fundo para as dimensões do post do Instagram (1080x1080)
        bg_img = bg_img.resize((1080, 1080), Image.Resampling.LANCZOS)

        # Extrair cor dominante da imagem de fundo
        color_thief = ColorThief(bg_image_path)
        dominant_color = color_thief.get_color(quality=1)
        texto_color = cor_contraste(dominant_color)

        # Gerar texto
        try:
            texto_img = renderizar_texto_na_imagem(bg_img, dica_texto, cor_texto=texto_color)
        except Exception as e:
            st.error(f"Erro ao adicionar texto à imagem: {e}")
            return

        # Adicionar logo no canto superior esquerdo de forma proporcional
        try:
            logo = Image.open(logo_path)
            logo_resized = ajustar_logotipo_proporcional(logo, tamanho_maximo=150, aumento=1.5)
            texto_img.paste(logo_resized, (30, 30), logo_resized)
        except Exception as e:
            st.error(f"Erro ao adicionar logo à imagem: {e}")
            return

        # Salvar a imagem gerada como post
        output_image_path = os.path.join("posts", f"post_{random.randint(100,999)}.png")
        try:
            texto_img.save(output_image_path)
        except Exception as e:
            st.error(f"Erro ao salvar a imagem gerada: {e}")
            return

        st.success("Post gerado com sucesso!")
        st.image(output_image_path, caption="Post para Instagram")

        # Oferecer o download do post
        with open(output_image_path, "rb") as f:
            st.download_button("Baixar Post", f, file_name=os.path.basename(output_image_path))

    elif gerar:
        st.warning("Por favor, preencha todos os campos antes de gerar o post.")

if __name__ == "__main__":
    main()
