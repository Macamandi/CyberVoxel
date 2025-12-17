# 🧊 CyberVoxel

**CyberVoxel** é um editor de voxel 16x16x16 desenvolvido em Python (Ursina Engine), projetado especificamente para **Cyberdecks** e telas pequenas (3.5").

Diferente de editores tradicionais, o CyberVoxel segue uma filosofia **"Keyboard Driven"** (100% controlado via teclado), eliminando a necessidade de mouse e permitindo um fluxo de trabalho extremamente rápido e ergonômico em dispositivos portáteis.

![Screenshot do CyberVoxel](caminho/para/sua/screenshot.png)

## ✨ Funcionalidades

* **Cyberdeck Ready:** Interface minimalista otimizada para telas de baixa resolução (480x320).
* **Keyboard Workflow:** Controle total de eixos, pintura e câmera sem tocar no mouse.
* **Smart Export (.OBJ):** Exportador nativo com algoritmo de **Face Culling**. Remove faces internas invisíveis, gerando modelos leves prontos para **Godot**, **Blender** ou **Unity**.
* **Modos de Visualização:** Alterne entre `Ghost Mode` (transparente para edição) e `Solid Mode` (visualização final).
* **Blueprints:** Suporte para carregar imagens de referência (`.png`) nos eixos X, Y e Z.
* **Ferramentas:** Conta-gotas (Pipette), Seletor de Cores DB32 e Save/Load (JSON).

## 🛠️ Instalação

Necessário Python 3.x instalado.

```bash
pip install ursina
python CyberVoxel.py
