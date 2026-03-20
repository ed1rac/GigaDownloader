import customtkinter as ctk
from tkinter import filedialog
import yt_dlp
import os
import threading
import re

# Configuração Padrão do Tema e Cores do CustomTkinter
ctk.set_appearance_mode("System")  # Segue o modo claro/escuro do Sistema Operacional
ctk.set_default_color_theme("blue")  # Temas disponíveis: blue, dark-blue, green

class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("Giga Downloader de Vídeos")
        self.geometry("600x480")
        self.resizable(False, False)

        # Caminho Padrão de Download
        if os.name == 'nt':
            self.download_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        else:
            self.download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

        # === Título Central ===
        self.title_label = ctk.CTkLabel(self, text="🎬 Giga Downloader", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.pack(pady=(30, 15))

        # === Campo de Entrada (URL) ===
        self.url_entry = ctk.CTkEntry(self, width=450, height=40, font=ctk.CTkFont(size=14), placeholder_text="Cole o link do vídeo aqui (YouTube, TikTok, Twitter X...)")
        self.url_entry.pack(pady=10)

        # === Frame de Seleção de Pasta ===
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=10)

        self.path_label = ctk.CTkLabel(self.path_frame, text=f"Salvar em: {self.download_path}", font=ctk.CTkFont(size=12))
        self.path_label.pack(side="left", padx=(0, 10))

        self.change_path_btn = ctk.CTkButton(self.path_frame, text="Mudar Pasta", width=100, font=ctk.CTkFont(size=12, weight="bold"), command=self.change_directory)
        self.change_path_btn.pack(side="left")

        # === Botão de Download ===
        self.download_btn = ctk.CTkButton(self, text="📥 Baixar Vídeo", width=250, height=45, font=ctk.CTkFont(size=16, weight="bold"), command=self.start_download)
        self.download_btn.pack(pady=20)

        # === Barra de Progresso ===
        self.progress_bar = ctk.CTkProgressBar(self, width=450)
        self.progress_bar.set(0) # Inicialmente ZERADA
        self.progress_bar.pack(pady=5)
        
        # === Label de Status ===
        self.status_label = ctk.CTkLabel(self, text="Aguardando link...", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.pack(pady=5)

        # === Rodapé / Créditos ===
        self.footer_label = ctk.CTkLabel(self, text="Ed (ED1@rac)", font=ctk.CTkFont(size=10), text_color="gray")
        self.footer_label.pack(side="bottom", pady=10)

    def change_directory(self):
        """Abre janela para o usuário escolher nova pasta de Downloads"""
        # Abre o selecionador de diretório em cima do atual
        folder_selected = filedialog.askdirectory(initialdir=self.download_path, title="Escolha onde salvar o vídeo")
        if folder_selected:
            self.download_path = folder_selected
            self.path_label.configure(text=f"Salvar em: {self.download_path}")

    def progress_hook(self, d):
        """Captura o progresso gerado pelo yt-dlp e joga para a interface gráfica"""
        if d['status'] == 'downloading':
            try:
                # Extraindo o percentual em número da string bruta retornada pelo yt-dlp que vêm com lixo do console
                percent_str = d.get('_percent_str', '0.0%').strip()
                percent_clean = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
                percent = float(percent_clean.replace('%', ''))
                
                # Atualizando a barra verde do CustomTkinter
                self.progress_bar.set(percent / 100)
                
                # Velocidade do download
                speed = d.get('_speed_str', 'N/A')
                speed = re.sub(r'\x1b\[[0-9;]*m', '', speed)
                
                # Atualiza a mensagem da tela (Ex: Baixando: 15.0% (Velocidade: 2MiB/s))
                # Aqui utilizamos configure para não precisar repintar a tela (thread safe no CTk na maioria das vezes)
                self.status_label.configure(text=f"Baixando: {percent_clean} (Velocidade: {speed})", text_color=("black", "white"))
            except Exception:
                self.status_label.configure(text="Baixando...", text_color=("black", "white"))

        elif d['status'] == 'finished':
            self.progress_bar.set(1)
            self.status_label.configure(text="Download Concluído! Aguarde o processamento do arquivo...", text_color="#2b8a3e")  # verde

    def download_thread(self, link):
        """Função que roda em 2º plano (Thread) para não travar a GUI"""
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'no_warnings': True
        }

        try:
            self.status_label.configure(text="Buscando informações do vídeo...", text_color=("black", "white"))
            # Inicia o download (enviando métricas para o progress_hook)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
                
            self.status_label.configure(text="✅ Vídeo baixado com sucesso!", text_color="#2b8a3e")  # verde
        except yt_dlp.utils.DownloadError:
            self.status_label.configure(text="❌ Erro: URL inválida ou vídeo indisponível.", text_color="#c92a2a") # vermelho
        except Exception as e:
            self.status_label.configure(text="❌ Ocorreu um erro no download.", text_color="#c92a2a")
            print(f"Erro detalhado: {e}")
        finally:
            # Ao fim de tudo (seja erro ou sucesso), reativa os inputs para poder baixar outro vídeo
            self.download_btn.configure(state="normal")
            self.url_entry.configure(state="normal")
            self.change_path_btn.configure(state="normal")

    def start_download(self):
        """Acionado ao clicar no Botão. Faz validação básica e inicia a Thread."""
        link = self.url_entry.get().strip()
        if not link:
            self.status_label.configure(text="⚠️ Por favor, insira um link válido.", text_color="#e67700") # laranja
            return

        # Desabilita botões para usuário não clicar 10 vezes
        self.download_btn.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.change_path_btn.configure(state="disabled")
        
        self.progress_bar.set(0)
        self.status_label.configure(text="Iniciando...", text_color=("black", "white"))

        # Joga o processo pesado para uma Thread (assim a janela continua respondendo a cliques)
        thread = threading.Thread(target=self.download_thread, args=(link,))
        thread.start()

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
