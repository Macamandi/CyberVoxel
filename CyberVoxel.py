from ursina import *
import json
import os

# --- Configuração da Janela ---
app = Ursina(size=(480, 320), title='CyberVoxel Terminal', vsync=True)
mouse.visible = False
window.color = color.hex('#222222') 
window.fps_counter.enabled = False 
window.exit_button.enabled = False

# --- Configurações Globais ---
TAMANHO = 16
CENTRO = (TAMANHO - 1) / 2 
voxels_data = {} 
referencias_visuais = [] 
ARQUIVO_PADRAO = "modelo.json"
NOME_EXPORT = "exportado" 

# --- PALETA DB32 ---
DB32_RAW = [
    (0,0,0), (34,32,52), (69,40,60), (102,57,49), (143,86,59), (223,113,38), (217,160,102), (238,195,154),
    (251,242,54), (153,229,80), (106,190,48), (55,148,110), (75,105,47), (82,75,36), (50,60,57), (63,63,116),
    (48,96,130), (91,110,225), (99,155,255), (95,205,228), (203,219,252), (255,255,255), (155,173,183), (132,126,135),
    (105,106,106), (89,86,82), (118,66,138), (172,50,50), (217,87,99), (215,123,186), (143,151,74), (138,111,48)
]
PALETA = [color.rgba(r/255, g/255, b/255, 1) for r,g,b in DB32_RAW]

# Estado do Editor
estado = {
    'eixo': 'z', 'camada': 0, 'cor_idx': 22, 'cursor': [0, 0],
    'modo_ghost': True, 'seletor_aberto': False, 'seletor_cursor': [0, 0],
    'ajuda_aberta': False
}

# --- Câmera e Layout ---
camera.orthographic = True
camera.fov = 10
camera.position = (0, 0)

# --- SISTEMA DE ARQUIVOS ---
def salvar_modelo():
    dados_para_salvar = []
    for pos, cor in voxels_data.items():
        item = { "x": int(pos[0]), "y": int(pos[1]), "z": int(pos[2]), "rgba": tuple(cor) }
        dados_para_salvar.append(item)
    try:
        with open(ARQUIVO_PADRAO, "w") as f: json.dump(dados_para_salvar, f)
        mostrar_mensagem(f"SALVO: {len(dados_para_salvar)} VOXELS", color.lime)
    except: mostrar_mensagem("ERRO AO SALVAR", color.red)

def carregar_modelo():
    global voxels_data
    if not os.path.exists(ARQUIVO_PADRAO): mostrar_mensagem("ARQUIVO NAO EXISTE", color.red); return
    try:
        with open(ARQUIVO_PADRAO, "r") as f: dados = json.load(f)
        voxels_data.clear()
        for item in dados:
            voxels_data[(item["x"], item["y"], item["z"])] = color.rgba(*item["rgba"])
        atualizar_grade_2d(); atualizar_preview(); mostrar_mensagem("MODELO CARREGADO", color.cyan)
    except: mostrar_mensagem("ARQUIVO CORROMPIDO", color.red)

def exportar_obj_otimizado():
    try:
        cores_usadas = set()
        for cor in voxels_data.values(): cores_usadas.add(tuple(cor))
        with open(f"{NOME_EXPORT}.mtl", "w") as mtl:
            mtl.write("# CyberVoxel Optimized MTL\n")
            for c in cores_usadas:
                r, g, b, a = c
                mat_name = f"Mat_{int(r*255)}_{int(g*255)}_{int(b*255)}"
                mtl.write(f"newmtl {mat_name}\nKd {r:.4f} {g:.4f} {b:.4f}\nd 1.0\nillum 2\n\n")
        with open(f"{NOME_EXPORT}.obj", "w") as f:
            f.write(f"# CyberVoxel Export (Face Culling)\nmtllib {NOME_EXPORT}.mtl\n")
            vert_idx = 1
            faces_check = [((0, 0, -1), [(-0.5,-0.5,-0.5), (-0.5,0.5,-0.5), (0.5,0.5,-0.5), (0.5,-0.5,-0.5)]),
                           ((0, 0, 1),  [(0.5,-0.5,0.5), (0.5,0.5,0.5), (-0.5,0.5,0.5), (-0.5,-0.5,0.5)]),
                           ((0, -1, 0), [(-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,-0.5,0.5), (-0.5,-0.5,0.5)]),
                           ((0, 1, 0),  [(-0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5)]),
                           ((-1, 0, 0), [(-0.5,-0.5,0.5), (-0.5,0.5,0.5), (-0.5,0.5,-0.5), (-0.5,-0.5,-0.5)]),
                           ((1, 0, 0),  [(0.5,-0.5,-0.5), (0.5,0.5,-0.5), (0.5,0.5,0.5), (0.5,-0.5,0.5)])]
            for pos, cor in voxels_data.items():
                x, y, z = pos; r, g, b, a = tuple(cor)
                mat_name = f"Mat_{int(r*255)}_{int(g*255)}_{int(b*255)}"
                f.write(f"usemtl {mat_name}\n"); cx, cy, cz = x - CENTRO, y - CENTRO, z - CENTRO
                for offset, face_verts in faces_check:
                    dx, dy, dz = offset; vizinho = (x + dx, y + dy, z + dz)
                    if vizinho not in voxels_data:
                        for vx, vy, vz in face_verts: f.write(f"v {cx + vx} {cy + vy} {cz + vz}\n")
                        f.write(f"f {vert_idx} {vert_idx+1} {vert_idx+2} {vert_idx+3}\n"); vert_idx += 4
        mostrar_mensagem("EXPORTADO: OTIMIZADO", color.yellow)
    except Exception as e: print(e); mostrar_mensagem("ERRO EXPORTACAO", color.red)

def carregar_referencias():
    for ref in referencias_visuais: destroy(ref)
    referencias_visuais.clear()
    if os.path.exists("refz.png"): referencias_visuais.append(Entity(parent=preview_pivot, model='quad', texture='refz.png', scale=TAMANHO, double_sided=True, color=color.white, alpha=0.4))
    if os.path.exists("refx.png"): referencias_visuais.append(Entity(parent=preview_pivot, model='quad', texture='refx.png', scale=TAMANHO, rotation_y=90, double_sided=True, color=color.white, alpha=0.4))
    if os.path.exists("refy.png"): referencias_visuais.append(Entity(parent=preview_pivot, model='quad', texture='refy.png', scale=TAMANHO, rotation_x=90, double_sided=True, color=color.white, alpha=0.4))
    if len(referencias_visuais) > 0: mostrar_mensagem("REFS CARREGADAS", color.cyan)
    else: mostrar_mensagem("NENHUMA IMG REF", color.orange)

# --- 1. A GRADE 2D ---
grade_bg = Entity(model='quad', scale=(8.2, 8.2), color=color.hex('#111111'), position=(-3.5, 0), z=1)
pixels_grade = []
for y in range(TAMANHO):
    linha = []
    for x in range(TAMANHO):
        p = Entity(parent=grade_bg, model='quad', scale=1/TAMANHO - 0.005,
                   x=(x/TAMANHO)-0.5+(0.5/TAMANHO), y=(y/TAMANHO)-0.5+(0.5/TAMANHO), color=color.black, z=-0.1)
        linha.append(p)
    pixels_grade.append(linha)
cursor_visual = Entity(parent=grade_bg, model='quad', scale=1/TAMANHO, color=color.white, alpha=0.5, z=-0.2)

# --- 2. O PREVIEW 3D ---
preview_pivot = Entity(position=(4.5, 0), scale=0.35, rotation=(0, 0, 0)) 
voxels_preview = []
limite_area = Entity(parent=preview_pivot, model='wireframe_cube', scale=TAMANHO, color=color.gray)
cursor_3d = Entity(parent=preview_pivot, model='wireframe_cube', color=color.lime, scale=1.1)

# FUNCAO NOVA: Alinha a camera automaticamente ao mudar de eixo
def snap_rotacao_camera():
    if estado['eixo'] == 'z':
        preview_pivot.animate_rotation((0, 0, 0), duration=0.2)
    elif estado['eixo'] == 'y':
        preview_pivot.animate_rotation((90, 0, 0), duration=0.2)
    elif estado['eixo'] == 'x':
        preview_pivot.animate_rotation((0, -90, 0), duration=0.2)

def atualizar_posicao_cursor_3d():
    cx, cy = estado['cursor']; pz = estado['camada']
    # MAPA CORRIGIDO: X agora mapeia para (Z, Y) para alinhar com a visão lateral
    px, py, pz = (cx, cy, pz) if estado['eixo'] == 'z' else ((cx, pz, cy) if estado['eixo'] == 'y' else (pz, cy, cx))
    cursor_3d.position = (px - CENTRO, py - CENTRO, pz - CENTRO)

def atualizar_preview():
    for v in voxels_preview: destroy(v)
    voxels_preview.clear()
    for pos, cor in voxels_data.items():
        alpha_val, scale_val = 1.0, 1.0
        if estado['modo_ghost']:
            eh_foco = False
            if estado['eixo'] == 'z' and pos[2] == estado['camada']: eh_foco = True
            elif estado['eixo'] == 'y' and pos[1] == estado['camada']: eh_foco = True
            elif estado['eixo'] == 'x' and pos[0] == estado['camada']: eh_foco = True
            if not eh_foco: alpha_val = 0.1; scale_val = 0.8
        
        v = Entity(model='cube', color=cor, position=(pos[0]-CENTRO, pos[1]-CENTRO, pos[2]-CENTRO),
                   parent=preview_pivot, scale=scale_val, unlit=True)
        if alpha_val < 1: v.alpha = alpha_val; v.double_sided = True
        voxels_preview.append(v)
    
    limite_area.enabled = estado['modo_ghost']
    cursor_3d.enabled = estado['modo_ghost']
    for ref in referencias_visuais: ref.enabled = estado['modo_ghost']

def atualizar_grade_2d():
    for y in range(TAMANHO):
        for x in range(TAMANHO): pixels_grade[y][x].color = color.hex('#1a1a1a')
    for pos, cor in voxels_data.items():
        visivel = False
        gx, gy = 0, 0
        if estado['eixo'] == 'z' and pos[2] == estado['camada']: gx, gy = pos[0], pos[1]; visivel = True
        elif estado['eixo'] == 'y' and pos[1] == estado['camada']: gx, gy = pos[0], pos[2]; visivel = True
        # CORREÇÃO EIXO X: Mapeia Z para X da grade e Y para Y da grade
        elif estado['eixo'] == 'x' and pos[0] == estado['camada']: gx, gy = pos[2], pos[1]; visivel = True
        if visivel and 0 <= gx < TAMANHO and 0 <= gy < TAMANHO: pixels_grade[gy][gx].color = cor

# --- UI GERAL ---
seletor_bg = Entity(parent=camera.ui, model='quad', scale=(0.9, 0.5), color=color.hex('#111111'), z=-1, enabled=False)
seletor_titulo = Text(parent=seletor_bg, text="SELECIONE A COR", origin=(0,0), y=0.45, scale=2, z=-0.1)
seletor_grid = []
seletor_highlight = Entity(parent=seletor_bg, model='quad', color=color.white, scale=0.11, z=-0.1, enabled=False)

def criar_seletor_ui():
    start_x, start_y = -0.4, 0.3; gap_x, gap_y = 0.11, 0.2
    for i, cor in enumerate(PALETA):
        cy, cx = divmod(i, 8)
        btn = Entity(parent=seletor_bg, model='quad', color=cor, scale=0.09,
                     position=(start_x + cx*gap_x, start_y - cy*gap_y, -0.1))
        seletor_grid.append(btn)
criar_seletor_ui()

def abrir_fechar_seletor(abrir):
    estado['seletor_aberto'] = abrir; seletor_bg.enabled = abrir; seletor_highlight.enabled = abrir
    if abrir:
        idx = estado['cor_idx']; cy, cx = divmod(idx, 8); estado['seletor_cursor'] = [cx, cy]; atualizar_cursor_seletor()

def atualizar_cursor_seletor():
    cx, cy = estado['seletor_cursor']; start_x, start_y = -0.4, 0.3; gap_x, gap_y = 0.11, 0.2
    seletor_highlight.position = (start_x + cx*gap_x, start_y - cy*gap_y, -0.12)

# --- UI: MENU DE AJUDA ---
ajuda_bg = Entity(parent=camera.ui, model='quad', scale=(1.8, 0.9), color=color.hex('#000000ee'), z=-2, enabled=False)
texto_comandos = """
 -- COMANDOS CYBERVOXEL --

 [SETAS]     Mover Cursor
 [SPACE]     Pintar Voxel
 [E]         Apagar Voxel
 [I]         Conta-Gotas (Pipette)
 [C]         Menu de Cores
 [TAB]       Modo Solido/Fantasma
 [R]         Carregar Refs (PNG)
 [S]         Salvar JSON
 [L]         Carregar JSON
 [O]         EXPORTAR OBJ (OTIMIZADO)
 [X, Y, Z]   Mudar Eixo de Corte
 [ . ] [ , ] Avanca/Recua Camada
 [Shift+Dir] Girar Modelo 3D
 [H]         Fechar Ajuda
"""
Text(parent=ajuda_bg, text=texto_comandos, origin=(0,0), scale=1.2, position=(0,0.05), color=color.green, z=-0.1)

def toggle_ajuda():
    estado['ajuda_aberta'] = not estado['ajuda_aberta']
    ajuda_bg.enabled = estado['ajuda_aberta']

# --- HUD ---
texto_info = Text(text="INIT", position=(-0.45, 0.45), scale=1) 
texto_cor = Entity(parent=camera.ui, model='quad', scale=(0.05, 0.05), position=(0.45, 0.45), color=PALETA[0])
texto_msg = Text(text="", position=(0, 0), origin=(0,0), scale=2, color=color.white, enabled=False)

def atualizar_hud():
    e = estado['eixo'].upper(); c = estado['camada'] + 1; modo = "GHOST" if estado['modo_ghost'] else "SOLID"
    texto_info.text = f"EIXO:[{e}] CAMADA:{c:02d} [{modo}]"
    texto_cor.color = PALETA[estado['cor_idx']]

def mostrar_mensagem(texto, cor):
    texto_msg.text = texto; texto_msg.color = cor; texto_msg.enabled = True
    invoke(setattr, texto_msg, 'enabled', False, delay=1.5)

def usar_conta_gotas():
    cx, cy = estado['cursor']; pz = estado['camada']
    pos = (cx, cy, pz) if estado['eixo'] == 'z' else ((cx, pz, cy) if estado['eixo'] == 'y' else (pz, cy, cx))
    if pos in voxels_data:
        try: idx = PALETA.index(voxels_data[pos]); estado['cor_idx'] = idx; atualizar_hud(); mostrar_mensagem("COR CAPTURADA", voxels_data[pos])
        except: mostrar_mensagem("COR DESCONHECIDA", color.orange)
    else: mostrar_mensagem("VAZIO", color.gray)

# --- INPUT ---
def input(key):
    if key == 'h': toggle_ajuda(); return
    if estado['ajuda_aberta']: return

    if estado['seletor_aberto']:
        cx, cy = estado['seletor_cursor']
        if key == 'left arrow': cx = max(0, cx - 1)
        if key == 'right arrow': cx = min(7, cx + 1)
        if key == 'up arrow': cy = max(0, cy - 1)
        if key == 'down arrow': cy = min(3, cy + 1)
        if key == 'enter' or key == 'space': estado['cor_idx'] = cy * 8 + cx; abrir_fechar_seletor(False); atualizar_hud()
        if key == 'c' or key == 'escape': abrir_fechar_seletor(False)
        estado['seletor_cursor'] = [cx, cy]; atualizar_cursor_seletor(); return

    if key == 'c': abrir_fechar_seletor(True); return
    if key == 'tab': estado['modo_ghost'] = not estado['modo_ghost']; atualizar_preview(); atualizar_hud()
    if key == 's': salvar_modelo()
    if key == 'l': carregar_modelo()
    if key == 'o': exportar_obj_otimizado()
    if key == 'r': carregar_referencias()
    if key == 'i': usar_conta_gotas()

    if held_keys['shift']:
        if key == 'up arrow': preview_pivot.rotation_x += 15
        if key == 'down arrow': preview_pivot.rotation_x -= 15
        if key == 'left arrow': preview_pivot.rotation_y += 15
        if key == 'right arrow': preview_pivot.rotation_y -= 15
        return

    dx, dy = 0, 0
    if key == 'up arrow': dy = 1
    elif key == 'down arrow': dy = -1
    elif key == 'right arrow': dx = 1
    elif key == 'left arrow': dx = -1
    if dx or dy:
        estado['cursor'][0] = clamp(estado['cursor'][0] + dx, 0, TAMANHO-1)
        estado['cursor'][1] = clamp(estado['cursor'][1] + dy, 0, TAMANHO-1)
        cursor_visual.x = (estado['cursor'][0]/TAMANHO) - 0.5 + (0.5/TAMANHO)
        cursor_visual.y = (estado['cursor'][1]/TAMANHO) - 0.5 + (0.5/TAMANHO)
        atualizar_posicao_cursor_3d()

    if key == 'space' or key == 'e':
        cx, cy = estado['cursor']; pz = estado['camada']
        # CORREÇÃO EIXO X: Agora cx mapeia para Z e cy mapeia para Y
        pos = (cx, cy, pz) if estado['eixo'] == 'z' else ((cx, pz, cy) if estado['eixo'] == 'y' else (pz, cy, cx))
        if key == 'space': voxels_data[pos] = PALETA[estado['cor_idx']]
        else: 
            if pos in voxels_data: del voxels_data[pos]
        atualizar_grade_2d(); atualizar_preview()

    if key in ['x', 'y', 'z']: 
        estado['eixo'] = key
        snap_rotacao_camera() # Alinha a câmera
        atualizar_grade_2d(); atualizar_preview(); atualizar_posicao_cursor_3d()
        
    delta = 1 if key == '.' else (-1 if key == ',' else 0)
    if delta:
        if held_keys['x']: estado['eixo'] = 'x'; snap_rotacao_camera()
        elif held_keys['y']: estado['eixo'] = 'y'; snap_rotacao_camera()
        elif held_keys['z']: estado['eixo'] = 'z'; snap_rotacao_camera()
        estado['camada'] = clamp(estado['camada'] + delta, 0, TAMANHO-1)
        atualizar_grade_2d(); atualizar_preview(); atualizar_posicao_cursor_3d()
    atualizar_hud()

atualizar_hud(); atualizar_grade_2d(); atualizar_posicao_cursor_3d(); app.run()
