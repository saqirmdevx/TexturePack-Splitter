# TextureSplitter

Divide spritesheets no estilo TexturePacker (PNG + JSON) em imagens de frame
individuais, organizadas em pastas por animação. Inclui tanto um script de
linha de comando quanto uma interface gráfica (GUI) para desktop.

*English: [README.md](README.md)*

## Recursos

- **GUI** (`app.py`): selecione o JSON por uma janela de arquivos — o PNG é
  detectado automaticamente ao lado dele através do campo `meta.image` do
  JSON — escolha um tamanho de sprite (16, 32, 48, 64, 96, 128, 256, 512 ou
  personalizado), pré-visualize cada sprite, inspecione seus metadados do
  JSON (`frame`, `anchor`, `spriteSourceSize`, `sourceSize`, `rotated`,
  `trimmed`) e exporte direto para a pasta que você escolher.
  - `64 x 64` por padrão; o desenho nunca é redimensionado, apenas centralizado
    em um canvas transparente.
  - A saída espelha o bloco `animations` do JSON em pastas por animação; sem
    `animations`, a saída é plana.
  - Disponível em Português, English, Español, 中文 e Slovenčina.
  - No Windows, tenta criar um atalho `TextureSplitter.lnk` na área de
    trabalho.
- **CLI** (`split_spritesheet.py`): processa em lote todos os spritesheets
  encontrados em `input/`, com uma flag opcional `-fs` para preencher os
  frames em um canvas de tamanho fixo.

## 1. Instale o Python

Você precisa do Python 3.8 ou mais recente.

- **macOS**: o Python 3 geralmente já vem instalado. Verifique com:
  ```bash
  python3 --version
  ```
  Se estiver faltando ou for muito antigo, instale via [Homebrew](https://brew.sh):
  ```bash
  brew install python
  ```
- **Windows**: baixe o instalador em [python.org/downloads](https://www.python.org/downloads/)
  e execute-o (marque "Add python.exe to PATH" durante a instalação).
- **Linux**: instale via seu gerenciador de pacotes, por exemplo:
  ```bash
  sudo apt install python3 python3-venv python3-tk
  ```
  (`python3-tk` é necessário para a GUI; o script de linha de comando não
  precisa dele.)

## 2. Instale as dependências

Na pasta do projeto, crie um ambiente virtual e instale as dependências
(atualmente apenas o [Pillow](https://python-pillow.org/), a biblioteca de
imagens):

```bash
python3 -m venv .venv
```

Ative-o:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

A GUI também precisa do `tkinter`, que já vem com o instalador padrão do
Python no Windows/macOS. No Linux, instale-o separadamente (veja acima), já
que ele não é distribuído via pip.

## 3. Execute

### GUI

Com o ambiente virtual ativado, execute:

```bash
python app.py
```

No Windows você também pode dar duplo clique em `run_TextureSplitter.bat`.

Selecione o arquivo JSON (o PNG correspondente é carregado automaticamente a
partir de `meta.image`), escolha um tamanho de sprite, escolha uma pasta de
saída e clique em **CORTAR IMAGENS**. Use o botão de idioma no canto superior
direito para trocar o idioma da interface.

### CLI

Com o ambiente virtual ativado, execute a partir da pasta do projeto:

```bash
python split_spritesheet.py
```

As pastas de entrada e saída são fixas — sempre `input/` e `output/` ao lado
do script, sem precisar de flags de caminho. No macOS/Linux você também pode
usar `./run.sh`, e no Windows `run.bat` (ambos esperam que a pasta `.venv` já
exista).

### Opções

| Flag | Descrição | Padrão |
|---|---|---|
| `-fs N`, `--frame-size N` | Preenche cada frame em um canvas transparente e centralizado de `N x N` (sem redimensionar) | desligado |

Exemplo:

```bash
# Preenche cada frame para 64x64 (adiciona espaço transparente, não redimensiona a arte)
python split_spritesheet.py -fs 64
```

### Estrutura de entrada

O script varre recursivamente `input/` procurando arquivos `.json`. O campo
`meta.image` de cada JSON indica o PNG que está ao lado dele na mesma pasta,
então você pode dividir vários spritesheets em uma única execução aninhando-os
em subpastas:

```
input/
  creatures/
    0/
      spritesheet.json   # meta.image: "spritesheet.png"
      spritesheet.png
    1/
      spritesheet.json
      spritesheet.png
```

### Estrutura de saída

A saída de cada spritesheet espelha sua localização de pasta dentro de
`input/`, e depois se divide em animações dentro dessa pasta:

- Se o JSON define um bloco `"animations"`, os frames são agrupados em uma
  pasta por animação, nomeados de acordo com o nome de arquivo original de
  cada frame:
  ```
  output/creatures/0/Attack/0.png
  output/creatures/0/Attack/1.png
  output/creatures/0/Walk/0.png
  output/creatures/1/Attack/0.png
  ...
  ```
- Se não houver bloco `"animations"`, todos os frames daquele spritesheet são
  escritos de forma plana na pasta de destino (os separadores de caminho no
  nome do frame são substituídos por `_` para manter os nomes de arquivo
  únicos).

### Limpando a saída antiga

Se `output/` já tiver conteúdo, o script pergunta antes de tocar nele:

```
Output directory 'output' is not empty. Clear it before continuing? [y/N]:
```

- `y` — apaga tudo em `output/` primeiro e depois grava os resultados novos.
- `n` (ou apenas pressionar Enter) — mantém os arquivos existentes intactos; a
  execução ainda grava/sobrescreve os frames dos spritesheets encontrados,
  mas arquivos antigos de execuções anteriores não são removidos.

## Gerando um executável independente

Você pode empacotar a GUI e a CLI em binários independentes (sem precisar de
Python instalado para executá-los) usando o
[PyInstaller](https://pyinstaller.org/). O binário de cada plataforma precisa
ser gerado nessa mesma plataforma — não há compilação cruzada.

- **macOS**: `./build_mac.sh`
- **Windows**: dê duplo clique em `build_windows.bat` (ou execute em um terminal)

Ambos os scripts criam/reaproveitam um `.venv`, instalam `requirements.txt` e
`requirements-build.txt` (apenas o `pyinstaller`) e então geram o build a
partir de `TextureSplitter.spec` (GUI) e `TextureSplitterCLI.spec` (CLI). O
resultado fica em `dist/`:

- `dist/TextureSplitter.app` (macOS) / `dist/TextureSplitter.exe` (Windows) — a GUI
- `dist/TextureSplitterCLI` (macOS) / `dist/TextureSplitterCLI.exe` (Windows) — a CLI

Observação: o PyInstaller empacota o bytecode Python dentro do executável, mas
não o protege — ferramentas como `pyinstxtractor` conseguem extraí-lo de
volta. Ele esconde o código-fonte `.py` de um usuário casual, não de alguém
disposto a fazer engenharia reversa.

## Notas de qualidade

- Os frames são recortados pixel a pixel da imagem de origem — nenhuma
  reamostragem ou artefato de recompressão é introduzido.
- A opção de preenchimento `-fs` cola o frame em um canvas totalmente
  transparente sem mesclagem, então pixels de borda anti-aliased/semi-
  transparentes são copiados exatamente como estão.
- Os PNGs de saída carregam o perfil de cor ICC do spritesheet original,
  quando presente, ou usam como alternativa o perfil sRGB padrão incluído
  (`srgb.icc`), garantindo que os frames exportados sejam corretamente
  marcados com o perfil de cor, em vez de ficarem como RGB sem marcação.
