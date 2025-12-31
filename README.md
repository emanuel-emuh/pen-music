🎵 Pen Music - Baixador Automático para Pendrive
Pen Music é uma aplicação desktop desenvolvida em Python para simplificar o processo de baixar músicas e playlists do YouTube diretamente para um Pendrive, com organização automática de pastas e normalização de áudio profissional.

🚀 Funcionalidades
Download de Áudio e Vídeo: Suporte a links do YouTube (Vídeos únicos ou Playlists completas).

Organização Automática: O usuário seleciona o gênero (ex: Funk, Sertanejo) e o software cria a pasta automaticamente no pendrive.

Detector de Unidades: Identifica drives conectados (D:, E:, F:...) e valida a existência antes do download.

Engenharia de Áudio: Utiliza FFmpeg para converter para MP3 (192kbps) e aplicar filtro de normalização (Loudnorm), garantindo volume estável.

Interface Visual (GUI): Desenvolvida com CustomTkinter para um visual moderno (Dark Mode), com barra de progresso real e preview da capa do vídeo (thumbnail).

Thread-Safe: O download roda em uma thread separada para não travar a interface durante o processamento.

🛠️ Tecnologias Utilizadas
O projeto foi construído utilizando as seguintes bibliotecas e ferramentas:

Python 3.12: Linguagem base.

CustomTkinter: Para construção da Interface Gráfica (GUI) moderna.

yt-dlp: Motor robusto para extração de vídeo e áudio do YouTube.

FFmpeg & FFprobe: Ferramentas externas essenciais para conversão de codecs e normalização de áudio.

Pillow (PIL): Manipulação de imagem para exibir o preview (thumbnail) do vídeo.

Threading: Para gerenciamento de processos em segundo plano.

PyInstaller: Para compilação do código em um executável (.exe) standalone.

⚙️ Como Funciona (Arquitetura)
Aqui está a explicação técnica do fluxo de dados da aplicação:

1. Inicialização e Segurança (__init__)
Ao iniciar, a classe AppDownloader executa uma verificação de integridade (verificar_ferramentas). Ela checa se os binários ffmpeg.exe e ffprobe.exe estão presentes no diretório raiz. Se não estiverem, o app bloqueia a inicialização para prevenir erros de runtime.

2. Captura de Preview
Quando o usuário cola o link, o sistema utiliza a biblioteca urllib combinada com o yt-dlp (em modo simulação) para extrair a URL da imagem de capa (thumbnail) sem baixar o vídeo inteiro. A imagem é processada via Pillow e exibida na GUI.

3. O Processo de Download (yt-dlp Hook)
O download não é bloqueante. Utilizamos a biblioteca threading para rodar o processo em paralelo.

Hook de Progresso: Uma função callback (hook_progresso) intercepta os dados do yt-dlp em tempo real, calculando a porcentagem de bytes baixados e atualizando a barra de progresso visual (CTkProgressBar).

4. Processamento de Áudio (FFmpeg)
Após o download, o arquivo passa por um pós-processamento rigoroso definido nos argumentos do FFmpeg:

Python

'postprocessor_args': {'ffmpeg': ['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11']}
Isso aplica o filtro Loudness Normalization, padronizando o áudio para -16 LUFS (padrão de rádio/TV), evitando que uma música fique mais baixa que a outra.

5. Gerenciamento de Arquivos (shutil)
Ao finalizar a conversão, o script utiliza a biblioteca os e shutil para:

Verificar se a pasta do gênero existe no Pendrive (ex: D:/Sertanejo).

Criar a pasta caso não exista.

Mover o arquivo MP3 da pasta temporária para o destino final.

📦 Como rodar o projeto localmente
Pré-requisitos
Python 3.x instalado.

FFmpeg instalado e configurado (ou os executáveis na pasta do projeto).

Passo a Passo
Clone o repositório:

Bash

git clone https://github.com/SEU-USUARIO/pen-music.git
Instale as dependências:

Bash

pip install customtkinter yt-dlp pillow
Configure o FFmpeg: Baixe o ffmpeg.exe e ffprobe.exe e coloque-os na raiz do projeto (junto com o main.py).

Execute a aplicação:

Bash

python main.py
🔨 Como criar o Executável (.exe)
Para distribuir a aplicação para quem não tem Python instalado, utilizamos o PyInstaller. O comando abaixo garante que as bibliotecas gráficas e de imagem sejam empacotadas corretamente:

Bash

pyinstaller --noconsole --onefile --collect-all customtkinter --collect-all PIL --icon="icone.ico" --name="Pen Music" main.py
Nota: É necessário ter o arquivo .ico na pasta.

📝 Licença
Este projeto é de uso livre para fins educacionais.

Desenvolvido por [Seu Nome]