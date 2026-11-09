# 🎬 Giga Downloader

Um aplicativo rápido, leve e multiplataforma com interface gráfica para baixar vídeos e áudios de milhares de sites (YouTube, Instagram, TikTok, Twitter/X, Reddit, Twitch, Vimeo, etc.).

## 🚀 Como usar
1. Abra o aplicativo.
2. Cole a URL do vídeo desejado.
3. Escolha a pasta de destino (o padrão é a pasta `Downloads` do sistema).
4. Clique em **Baixar Vídeo**.

## 💻 Para Desenvolvedores

### Requisitos
- Python 3.10+
- Instalar as dependências:
```bash
pip install -r requirements.txt
```

### Como compilar manualmente
Para gerar o executável na sua máquina, utilize o [PyInstaller](https://pyinstaller.org/):
```bash
pyinstaller --noconsole --onefile --name "GigaDownloader" ytdownloader.py
```
O executável será gerado na pasta `dist/`.

## 🤖 CI/CD Automático
Este projeto utiliza o GitHub Actions para compilar automaticamente os executáveis de **Windows**, **Linux**, e **macOS** a cada nova versão lançada no repositório.

---
Desenvolvido por *Ed (ED1@rac)*

---

## ☕ Apoie o Projeto (Me Pague um Café / Buy Me a Coffee)

Este projeto é desenvolvido com dedicação e carinho. Se este projeto foi útil para os seus estudos, trabalho ou produtividade diária e você quiser apoiar o desenvolvimento contínuo:

- ☕ **Buy Me a Coffee (Internacional / Cartão / QR Code)**:
  - 👉 **[https://buymeacoffee.com/edkallenn](https://buymeacoffee.com/edkallenn)**
  - [![](https://img.shields.io/badge/☕_Buy_Me_a_Coffee-Apoiar_Projeto-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/edkallenn)
  - Escaneie o QR Code abaixo com a câmera do celular para abrir diretamente:

<div align="center">
  <a href="https://buymeacoffee.com/edkallenn" target="_blank">
    <img src="./bmc_qr.png" alt="Buy Me a Coffee QR Code — Edkallenn (@ed1rac)" width="220" />
  </a>
</div>

- 🇧🇷 **PIX (Brasil — Qualquer valor, taxa zero)**:
  - **Chave PIX (E-mail)**: `edkevan@gmail.com`
  - **Titular**: Edkallenn

Muito obrigado pelo apoio! 🚀

---
