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
