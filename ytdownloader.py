import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import os
import sys
import threading
import re
import shutil
import urllib.request
import json
import tempfile
import subprocess
import webbrowser

# Configuração Padrão do Tema e Cores do CustomTkinter
ctk.set_appearance_mode("System")  # Segue o modo claro/escuro do Sistema Operacional
ctk.set_default_color_theme("blue")  # Temas disponíveis: blue, dark-blue, green

CURRENT_VERSION = "v1.0.8"
GITHUB_REPO = "ed1rac/GigaDownloader"

def parse_version(v_str):
    """Converte string de versão (ex: 'v1.0.8') em objeto comparável"""
    try:
        from packaging import version
        return version.parse(v_str.lstrip('v'))
    except Exception:
        nums = [int(n) for n in re.findall(r'\d+', v_str)]
        return tuple(nums)

class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title(f"Giga Downloader de Vídeos - {CURRENT_VERSION}")
        self.geometry("600x500")
        self.resizable(False, False)

        # Caminho Padrão de Download
        if os.name == 'nt':
            self.download_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        else:
            self.download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

        # === Título Central ===
        self.title_label = ctk.CTkLabel(self, text="🎬 Giga Downloader", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.pack(pady=(25, 12))

        # === Campo de Entrada (URL) ===
        self.url_entry = ctk.CTkEntry(self, width=450, height=40, font=ctk.CTkFont(size=14), placeholder_text="Cole o link do vídeo aqui (YouTube, TikTok, Twitter X...)")
        self.url_entry.pack(pady=10)

        # === Frame de Seleção de Pasta ===
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=8)

        self.path_label = ctk.CTkLabel(self.path_frame, text=f"Salvar em: {self.download_path}", font=ctk.CTkFont(size=12))
        self.path_label.pack(side="left", padx=(0, 10))

        self.change_path_btn = ctk.CTkButton(self.path_frame, text="Mudar Pasta", width=100, font=ctk.CTkFont(size=12, weight="bold"), command=self.change_directory)
        self.change_path_btn.pack(side="left")

        # === Botão de Download ===
        self.download_btn = ctk.CTkButton(self, text="📥 Baixar Vídeo", width=250, height=45, font=ctk.CTkFont(size=16, weight="bold"), command=self.start_download)
        self.download_btn.pack(pady=18)

        # === Barra de Progresso ===
        self.progress_bar = ctk.CTkProgressBar(self, width=450)
        self.progress_bar.set(0) # Inicialmente ZERADA
        self.progress_bar.pack(pady=5)
        
        # === Label de Status ===
        self.status_label = ctk.CTkLabel(self, text="Aguardando link...", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.pack(pady=5)

        # === Rodapé com Versão e Botão de Atualização ===
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", padx=25, pady=(5, 12))

        self.footer_label = ctk.CTkLabel(
            self.footer_frame, 
            text=f"Ed (ED1@rac) • {CURRENT_VERSION}", 
            font=ctk.CTkFont(size=11), 
            text_color="gray"
        )
        self.footer_label.pack(side="left")

        self.update_btn = ctk.CTkButton(
            self.footer_frame,
            text="🔄 Buscar Atualização",
            width=150,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            border_width=1,
            hover_color=("gray85", "gray25"),
            text_color=("gray20", "gray80"),
            command=self.start_check_update
        )
        self.update_btn.pack(side="right")

    def change_directory(self):
        """Abre janela para o usuário escolher nova pasta de Downloads"""
        folder_selected = filedialog.askdirectory(initialdir=self.download_path, title="Escolha onde salvar o vídeo")
        if folder_selected:
            self.download_path = folder_selected
            self.path_label.configure(text=f"Salvar em: {self.download_path}")

    def progress_hook(self, d):
        """Captura o progresso gerado pelo yt-dlp e joga para a interface gráfica"""
        if d['status'] == 'downloading':
            try:
                percent_str = d.get('_percent_str', '0.0%').strip()
                percent_clean = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
                percent = float(percent_clean.replace('%', ''))
                
                self.progress_bar.set(percent / 100)
                
                speed = d.get('_speed_str', 'N/A')
                speed = re.sub(r'\x1b\[[0-9;]*m', '', speed)

                vcodec = d.get('info_dict', {}).get('vcodec')
                tipo = "vídeo" if (vcodec and vcodec != 'none') else "áudio"
                
                self.status_label.configure(text=f"Baixando {tipo}: {percent_clean} (Velocidade: {speed})", text_color=("black", "white"))
            except Exception:
                self.status_label.configure(text="Baixando...", text_color=("black", "white"))

        elif d['status'] == 'finished':
            self.progress_bar.set(1)
            self.status_label.configure(text="Download concluído! Processando arquivo...", text_color="#2b8a3e")  # verde

    def postprocessor_hook(self, d):
        """Notifica quando o FFmpeg está processando ou mesclando as faixas"""
        if d.get('status') == 'started':
            self.status_label.configure(text="Mesclando vídeo e áudio...", text_color=("black", "white"))

    def download_thread(self, link):
        """Função que roda em 2º plano (Thread) para não travar a GUI"""
        ffmpeg_bin = shutil.which('ffmpeg')
        if not ffmpeg_bin:
            for candidate in [r'C:\ffmpeg\bin\ffmpeg.exe', r'C:\ffmpeg\bin']:
                if os.path.exists(candidate):
                    ffmpeg_bin = candidate
                    break

        ydl_opts = {
            'format': 'bestvideo*+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'progress_hooks': [self.progress_hook],
            'postprocessor_hooks': [self.postprocessor_hook],
            'quiet': True,
            'no_warnings': True
        }

        if ffmpeg_bin:
            ydl_opts['ffmpeg_location'] = ffmpeg_bin

        try:
            self.status_label.configure(text="Buscando informações do vídeo...", text_color=("black", "white"))
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
                
            self.status_label.configure(text="✅ Vídeo baixado com sucesso!", text_color="#2b8a3e")  # verde
        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e)
            print(f"Erro detalhado (DownloadError): {err_msg}")
            if "Requested format is not available" in err_msg:
                self.status_label.configure(text="❌ Erro: Formato indisponível para este vídeo.", text_color="#c92a2a")
            elif "Sign in" in err_msg or "confirm you're not a bot" in err_msg:
                self.status_label.configure(text="❌ Erro: Bloqueio do YouTube (anti-bot).", text_color="#c92a2a")
            elif "Private video" in err_msg:
                self.status_label.configure(text="❌ Erro: Vídeo privado.", text_color="#c92a2a")
            else:
                self.status_label.configure(text="❌ Erro: URL inválida ou vídeo indisponível.", text_color="#c92a2a")
        except Exception as e:
            self.status_label.configure(text="❌ Ocorreu um erro no download.", text_color="#c92a2a")
            print(f"Erro detalhado: {e}")
        finally:
            self.download_btn.configure(state="normal")
            self.url_entry.configure(state="normal")
            self.change_path_btn.configure(state="normal")

    def start_download(self):
        """Acionado ao clicar no Botão. Faz validação básica e inicia a Thread."""
        link = self.url_entry.get().strip()
        if not link:
            self.status_label.configure(text="⚠️ Por favor, insira um link válido.", text_color="#e67700") # laranja
            return

        self.download_btn.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.change_path_btn.configure(state="disabled")
        
        self.progress_bar.set(0)
        self.status_label.configure(text="Iniciando...", text_color=("black", "white"))

        thread = threading.Thread(target=self.download_thread, args=(link,))
        thread.start()

    def start_check_update(self):
        """Inicia verificação de nova versão em thread para não travar a UI"""
        if self.download_btn.cget('state') == 'disabled' and 'Baixando' in self.status_label.cget('text'):
            messagebox.showwarning("Aviso", "Por favor, aguarde o download atual terminar antes de verificar atualizações.")
            return

        self.update_btn.configure(state="disabled", text="Verificando...")
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    def check_for_updates(self):
        """Consulta a API do GitHub Releases para checar novas versões disponíveis"""
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'GigaDownloader-App'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            
            latest_tag = data.get('tag_name', '').strip()
            if not latest_tag:
                messagebox.showwarning("Aviso", "Não foi possível identificar a versão mais recente.")
                return

            cur_v = parse_version(CURRENT_VERSION)
            lat_v = parse_version(latest_tag)

            if lat_v <= cur_v:
                messagebox.showinfo("Atualizações", f"Você já está usando a versão mais recente ({CURRENT_VERSION})!")
                return

            # Nova versão encontrada!
            assets = data.get('assets', [])
            release_url = data.get('html_url', f"https://github.com/{GITHUB_REPO}/releases/latest")
            
            target_asset = None
            if sys.platform == 'win32':
                for a in assets:
                    if a['name'].endswith('.exe'):
                        target_asset = a
                        break
            elif sys.platform.startswith('linux'):
                for a in assets:
                    if 'Linux' in a['name']:
                        target_asset = a
                        break
            elif sys.platform == 'darwin':
                for a in assets:
                    if 'macOS' in a['name'] or 'Mac' in a['name']:
                        target_asset = a
                        break

            msg = (
                f"🎉 Nova versão disponível: {latest_tag}!\n"
                f"(Sua versão atual: {CURRENT_VERSION})\n\n"
                "Deseja atualizar automaticamente agora?"
            )
            if not messagebox.askyesno("Nova Atualização", msg):
                return

            # Se estiver executando como executável compilado (.exe / binary)
            if getattr(sys, 'frozen', False):
                if not target_asset:
                    messagebox.showwarning(
                        "Atualização Manual Necessária",
                        f"O instalador para seu sistema ainda está sendo gerado ou não foi encontrado.\n\nAbrindo a página da release..."
                    )
                    webbrowser.open(release_url)
                    return

                self.perform_executable_update(target_asset['browser_download_url'], latest_tag)
            else:
                # Executando a partir do código-fonte Python (.py)
                self.perform_source_update(latest_tag, release_url)

        except Exception as e:
            print(f"Erro ao checar atualizações: {e}")
            messagebox.showerror("Erro de Verificação", f"Não foi possível verificar atualizações:\n{e}")
        finally:
            self.update_btn.configure(state="normal", text="🔄 Buscar Atualização")

    def perform_executable_update(self, download_url, latest_tag):
        """Baixa a nova versão do executável e substitui o arquivo atual com reinicialização"""
        self.download_btn.configure(state="disabled")
        self.status_label.configure(text=f"Baixando atualização {latest_tag}...", text_color=("black", "white"))
        self.progress_bar.set(0)

        try:
            temp_dir = tempfile.gettempdir()
            ext = ".exe" if sys.platform == 'win32' else ""
            temp_file = os.path.join(temp_dir, f"GigaDownloader_update_{latest_tag}{ext}")

            req = urllib.request.Request(download_url, headers={'User-Agent': 'GigaDownloader-App'})
            with urllib.request.urlopen(req, timeout=60) as resp, open(temp_file, 'wb') as out_f:
                total_size = int(resp.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 64 * 1024
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    out_f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = downloaded / total_size
                        self.progress_bar.set(pct)
                        mb_down = downloaded / (1024 * 1024)
                        mb_tot = total_size / (1024 * 1024)
                        self.status_label.configure(text=f"Baixando atualização: {int(pct*100)}% ({mb_down:.1f}MB/{mb_tot:.1f}MB)")

            self.status_label.configure(text="Aplicando atualização e reiniciando...", text_color="#2b8a3e")
            current_exe = os.path.abspath(sys.executable)

            if sys.platform == 'win32':
                old_exe = current_exe + ".old"
                if os.path.exists(old_exe):
                    try:
                        os.remove(old_exe)
                    except Exception:
                        pass
                os.rename(current_exe, old_exe)
                shutil.move(temp_file, current_exe)

                # Reinicia a aplicação na nova versão
                subprocess.Popen([current_exe])
                # Agenda limpeza silenciosa do arquivo .old
                cleanup_cmd = f'ping 127.0.0.1 -n 3 > NUL & del /f /q "{old_exe}"'
                subprocess.Popen(cleanup_cmd, shell=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                os._exit(0)
            else:
                os.chmod(temp_file, 0o755)
                shutil.move(temp_file, current_exe)
                subprocess.Popen([current_exe])
                os._exit(0)

        except Exception as e:
            print(f"Erro ao aplicar atualização: {e}")
            messagebox.showerror("Erro de Atualização", f"Falha ao baixar/aplicar a atualização:\n{e}")
            self.status_label.configure(text="Falha na atualização.", text_color="#c92a2a")
        finally:
            self.download_btn.configure(state="normal")

    def perform_source_update(self, latest_tag, release_url):
        """Quando rodando em ambiente Python, atualiza o yt-dlp via pip e abre a release"""
        self.status_label.configure(text="Atualizando yt-dlp via pip...", text_color=("black", "white"))
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], check=False)
            webbrowser.open(release_url)
            messagebox.showinfo(
                "Ambiente Atualizado",
                f"O pacote 'yt-dlp' foi atualizado no seu ambiente local!\n\n"
                f"A página da versão {latest_tag} foi aberta no navegador para você baixar o novo executável ou realizar 'git pull'."
            )
            self.status_label.configure(text="Aguardando link...", text_color="gray")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar dependências:\n{e}")
            self.status_label.configure(text="Aguardando link...", text_color="gray")

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
