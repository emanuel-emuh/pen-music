import customtkinter as ctk
import yt_dlp
import os
import shutil
import threading
from tkinter import messagebox
import string
import subprocess
import sys
from PIL import Image # Biblioteca de imagem
import urllib.request # Para baixar a imagem da web
import io # Para tratar a imagem na memória

# --- CONFIGURAÇÕES VISUAIS ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

GENEROS = [
    "Musicas-Baixadas-Recentes",
    "Forró-Piseiro",
    "Funk",
    "Hip Hop",
    "Louvores - Hinos",
    "MPB",
    "Música Gringa",
    "Pagode",
    "Reggae",
    "Rock",
    "Sad",
    "Seresta",
    "Sertanejo",
    "TikTok",
    "Trap-Rap"
]

OPCOES_DRIVE = [f"{letra}" for letra in string.ascii_uppercase if letra >= 'D']

# --- LOGGER ---
class MyLogger:
    def __init__(self, app_instance):
        self.app = app_instance
    def debug(self, msg):
        if not msg.startswith('[debug] '): 
            self.app.log(msg)
    def info(self, msg):
        pass 
    def warning(self, msg):
        self.app.log(f"⚠️ {msg}")
    def error(self, msg):
        self.app.log(f"❌ {msg}")

class AppDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. 🛡️ VERIFICAÇÃO DE INICIALIZAÇÃO (ANTI-ERRO)
        if not self.verificar_ferramentas():
            # Se falhar, o código para aqui e fecha
            self.destroy()
            return

        self.title("Pen Music 7.0")
        self.geometry("500x750") # Aumentei altura para caber a foto
        self.resizable(False, False)

        # Cabeçalho
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=(20, 5))
        
        self.label_titulo = ctk.CTkLabel(self.frame_top, text="Pen Music", font=("Arial", 24, "bold"), text_color="#3B8ED0")
        self.label_titulo.pack(side="left", padx=10)

        # 4. 🔄 BOTÃO ATUALIZAR (UPDATE CORE)
        self.btn_update = ctk.CTkButton(self.frame_top, text="🔄 Atualizar Core", width=80, height=20, fg_color="#333", command=self.atualizar_core)
        self.btn_update.pack(side="right")
        
        self.label_subtitulo = ctk.CTkLabel(self, text="Baixador Profissional com Preview", font=("Arial", 12))
        self.label_subtitulo.pack(pady=(0, 10))

        # Input e Botão Colar
        self.frame_input = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_input.pack(pady=5)

        self.entry_link = ctk.CTkEntry(self.frame_input, placeholder_text="Cole o link aqui...", width=350, height=35)
        self.entry_link.pack(side="left", padx=(0, 10))

        self.btn_colar = ctk.CTkButton(self.frame_input, text="📋 Colar", width=60, height=35, fg_color="#444", hover_color="#666", command=self.colar_link)
        self.btn_colar.pack(side="left")

        # 3. 🖼️ ÁREA DE PREVIEW (FOTO DO VÍDEO)
        self.label_preview = ctk.CTkLabel(self, text="[Capa do Vídeo]", width=300, height=160, fg_color="#222", corner_radius=10)
        self.label_preview.pack(pady=10)

        # Seleções
        self.frame_selecao = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_selecao.pack(pady=5)

        # Gênero
        self.label_genero = ctk.CTkLabel(self.frame_selecao, text="Gênero:", font=("Arial", 12, "bold"))
        self.label_genero.grid(row=0, column=0, padx=5, sticky="w")
        self.combobox_genero = ctk.CTkComboBox(self.frame_selecao, values=GENEROS, width=200)
        self.combobox_genero.set("Musicas-Baixadas-Recentes")
        self.combobox_genero.grid(row=1, column=0, padx=5)

        # Pendrive
        self.label_drive = ctk.CTkLabel(self.frame_selecao, text="Pendrive:", font=("Arial", 12, "bold"))
        self.label_drive.grid(row=0, column=1, padx=5, sticky="w")
        self.combobox_drive = ctk.CTkComboBox(self.frame_selecao, values=OPCOES_DRIVE, width=80)
        self.combobox_drive.set("D") 
        self.combobox_drive.grid(row=1, column=1, padx=5)

        # Botão Baixar
        self.btn_baixar = ctk.CTkButton(
            self, 
            text="BAIXAR E SALVAR", 
            command=self.iniciar_download, 
            height=45, 
            width=200,
            font=("Arial", 15, "bold"), 
            fg_color="green", 
            hover_color="darkgreen"
        )
        self.btn_baixar.pack(pady=15)

        # Barra de Progresso
        self.label_status = ctk.CTkLabel(self, text="Aguardando link...", text_color="gray")
        self.label_status.pack(pady=(5, 0))

        self.barra_progresso = ctk.CTkProgressBar(self, width=400, height=15, progress_color="green")
        self.barra_progresso.set(0)
        self.barra_progresso.pack(pady=(5, 10))

        # Log
        self.textbox_log = ctk.CTkTextbox(self, height=100, width=460)
        self.textbox_log.pack(pady=5)
        self.textbox_log.insert("0.0", "--- Sistema Iniciado ---\n")

    # --- FUNÇÃO 1: VERIFICAÇÃO DE INICIALIZAÇÃO ---
    def verificar_ferramentas(self):
        """Verifica se o FFmpeg existe antes de abrir o app"""
        # Verifica se estamos rodando como .exe ou script .py
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS # Pasta temporária do executável
            # Mas o ffmpeg geralmente fica na pasta ONDE o exe está
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        ffmpeg_path = os.path.join(base_path, "ffmpeg.exe")
        ffprobe_path = os.path.join(base_path, "ffprobe.exe")

        if not os.path.exists(ffmpeg_path) or not os.path.exists(ffprobe_path):
            messagebox.showerror(
                "ERRO CRÍTICO - ARQUIVOS FALTANDO",
                "🚫 O programa não pode iniciar!\n\n"
                "Os arquivos 'ffmpeg.exe' e 'ffprobe.exe' não foram encontrados.\n"
                "Por favor, coloque-os na mesma pasta deste aplicativo."
            )
            return False # Impede o app de abrir
        return True

    def log(self, mensagem):
        self.textbox_log.insert("end", mensagem + "\n")
        self.textbox_log.see("end")

    def colar_link(self):
        try:
            texto = self.clipboard_get()
            self.entry_link.delete(0, 'end')
            self.entry_link.insert(0, texto)
            # Assim que colar, tenta carregar a imagem
            threading.Thread(target=self.carregar_preview, args=(texto,)).start()
        except:
            self.log("⚠️ Nada para colar.")

    # --- FUNÇÃO 3: PREVIEW DA IMAGEM ---
    def carregar_preview(self, url):
        self.label_preview.configure(text="Carregando imagem...")
        try:
            # Pega info básica sem baixar o vídeo (rápido)
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                thumbnail_url = info.get('thumbnail')
                titulo = info.get('title', 'Vídeo')

            # Baixa a imagem da internet
            if thumbnail_url:
                with urllib.request.urlopen(thumbnail_url) as u:
                    raw_data = u.read()
                
                # Converte para imagem compatível com a janela
                image = Image.open(io.BytesIO(raw_data))
                # Redimensiona para caber na label (proporcional)
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(280, 158))
                
                self.label_preview.configure(image=ctk_image, text="") # Mostra imagem, apaga texto
                self.label_status.configure(text=f"Detectado: {titulo[:30]}...", text_color="white")
        except Exception as e:
            self.label_preview.configure(text="Sem Imagem", image=None)
            self.log(f"⚠️ Não foi possível carregar prévia: {e}")

    # --- FUNÇÃO 4: ATUALIZAR CORE ---
    def atualizar_core(self):
        """Roda o pip install para atualizar o yt-dlp"""
        self.log("🔄 Verificando atualizações...")
        
        def run_update():
            try:
                # Se for executável congelado, avisar que não dá pra atualizar via pip
                if getattr(sys, 'frozen', False):
                    messagebox.showinfo("Atualização", "Para atualizar esta versão executável,\né necessário baixar um novo arquivo com o criador.")
                    return

                subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
                self.log("✅ Sistema atualizado com sucesso!")
                messagebox.showinfo("Sucesso", "Bibliotecas atualizadas!\nReinicie o programa.")
            except Exception as e:
                self.log(f"❌ Erro ao atualizar: {e}")

        threading.Thread(target=run_update).start()

    def hook_progresso(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                baixado = d.get('downloaded_bytes')
                if total:
                    porcentagem = baixado / total
                    self.barra_progresso.set(porcentagem)
                    porcentagem_texto = int(porcentagem * 100)
                    self.label_status.configure(text=f"Baixando: {porcentagem_texto}%", text_color="#3B8ED0")
            except: pass
        elif d['status'] == 'finished':
            self.barra_progresso.set(1)
            self.label_status.configure(text="Processando Áudio...", text_color="orange")

    def iniciar_download(self):
        letra_escolhida = self.combobox_drive.get()
        if not os.path.exists(f"{letra_escolhida}:/"):
            messagebox.showerror("Erro", f"Pendrive {letra_escolhida}: não encontrado!")
            return
        threading.Thread(target=self.executar_download, args=(letra_escolhida,)).start()

    def executar_download(self, letra_drive):
        link = self.entry_link.get()
        genero_escolhido = self.combobox_genero.get()
        
        if not link:
            messagebox.showwarning("Aviso", "Cole um link primeiro!")
            return

        self.btn_baixar.configure(state="disabled", text="TRABALHANDO...")
        self.barra_progresso.set(0)
        
        pasta_temp = "downloads"
        caminho_pendrive = f"{letra_drive}:/{genero_escolhido}"

        if os.path.exists(pasta_temp):
            for arq in os.listdir(pasta_temp):
                try: os.remove(os.path.join(pasta_temp, arq))
                except: pass
        else:
             os.makedirs(pasta_temp)

        if not os.path.exists(caminho_pendrive):
            try: os.makedirs(caminho_pendrive)
            except: pass

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': False,
            'logger': MyLogger(self),
            'progress_hooks': [self.hook_progresso], 
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
            'postprocessor_args': {'ffmpeg': ['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11']},
            'outtmpl': f'{pasta_temp}/%(title)s.%(ext)s', 
            'quiet': False,
            'no_warnings': True,
        }

        try:
            self.log(f"🚀 Iniciando...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except Exception as e:
            self.log(f"❌ Erro: {e}")
            self.resetar_botoes()
            return

        import time
        time.sleep(2) 

        movidos = 0
        try:
            arquivos = os.listdir(pasta_temp)
            for arquivo in arquivos:
                if arquivo.endswith(".mp3"):
                    origem = os.path.join(pasta_temp, arquivo)
                    destino = os.path.join(caminho_pendrive, arquivo)
                    
                    if os.path.exists(destino):
                        try: os.remove(destino)
                        except: pass
                    
                    shutil.move(origem, destino)
                    movidos += 1
                    self.log(f"💾 Salvo: {arquivo}")
            
            if movidos > 0:
                self.label_status.configure(text="Concluído com Sucesso!", text_color="green")
                self.barra_progresso.set(1)
                messagebox.showinfo("Sucesso", f"{movidos} músicas salvas no Pendrive {letra_drive}:")
                self.entry_link.delete(0, 'end')
                self.label_preview.configure(image=None, text="[Capa do Vídeo]") # Limpa a foto
            else:
                self.log("⚠️ Nenhum arquivo MP3 gerado.")
                
        except Exception as e:
            self.log(f"❌ Erro ao mover: {e}")

        self.resetar_botoes()

    def resetar_botoes(self):
        self.btn_baixar.configure(state="normal", text="BAIXAR E SALVAR")
        if self.label_status.cget("text") != "Concluído com Sucesso!":
            self.label_status.configure(text="Pronto", text_color="white")
            self.barra_progresso.set(0)

if __name__ == "__main__":
    app = AppDownloader()
    app.mainloop()