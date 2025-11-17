import tkinter as tk
from PIL import Image, ImageTk
import os
import math


CELL_SIZE = 60
images_refs = {}  #  Dictionnaire pour garder les images en mémoire

# -----------------------------------------------------------------
# SUPPRESSION de la fonction resource_path
# -----------------------------------------------------------------


def load_images():
    """ Charge les images des pièces depuis le dossier /piece."""
    global images_refs
    images_refs.clear()

    pieces = {
        "P": "wP.png", "R": "wR.png", "N": "wN.png", "B": "wB.png", "Q": "wQ.png", "K": "wK.png",
        "p": "bP.png", "r": "bR.png", "n": "bN.png", "b": "bB.png", "q": "bQ.png", "k": "bK.png"
    }

    #  CHEMIN D'ACCÈS (chemin simple) ---
    base_dir = "piece" # Chemin relatif direct
    if not os.path.isdir(base_dir):
        print(f"[ERREUR] Dossier 'piece' introuvable à {base_dir}")
        return
    else:
        print(f"[INFO] Dossier d'images utilisé : {base_dir}")


    for symbol, filename in pieces.items():
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            img = Image.open(path).resize((CELL_SIZE - 8, CELL_SIZE - 8))
            images_refs[symbol] = ImageTk.PhotoImage(img)
        else:
            print(f"[ERREUR] Image introuvable pour {symbol} : {path}")


def draw_arrow(canvas, from_coords, to_coords, color, width=5, head_width=10, head_length=15):
    """Une fonction helper pour dessiner une belle flèche."""
    fx, fy = from_coords[1] * CELL_SIZE + CELL_SIZE // 2, from_coords[0] * CELL_SIZE + CELL_SIZE // 2
    tx, ty = to_coords[1] * CELL_SIZE + CELL_SIZE // 2, to_coords[0] * CELL_SIZE + CELL_SIZE // 2

    angle = math.atan2(ty - fy, tx - fx)
    offset = (CELL_SIZE / 2) - 10 
    tx_adjusted = tx - offset * math.cos(angle)
    ty_adjusted = ty - offset * math.sin(angle)

    canvas.create_line(fx, fy, tx_adjusted, ty_adjusted, fill=color, width=width, arrow=tk.LAST,
                       arrowshape=(head_width, head_width, head_length))


def draw_board(canvas, b, selected=None, legal_moves=None, check_pos=None, analysis_moves=None, last_move=None):
    """
    C'est la fonction principale de dessin.
    Elle dessine TOUT sur l'échiquier, couche par couche.
    """
    canvas.delete("all")

    legal_targets = set()
    if legal_moves:
        for mv in legal_moves:
            legal_targets.add((mv[2], mv[3]))

    analysis_sources = {} 
    analysis_targets = {} 
    moves_to_draw_arrows = [] 

    if analysis_moves:
        for move, color in analysis_moves:
            from_coords = (move[0], move[1])
            to_coords = (move[2], move[3])
            
            analysis_sources[from_coords] = color
            analysis_targets[to_coords] = color
            moves_to_draw_arrows.append((from_coords, to_coords, color))

    # --- Dessin des cases, indicateurs et pièces ---
    for i in range(8):
        for j in range(8):
            # Couche 1: Le damier
            color = "#EEE" if (i + j) % 2 == 0 else "#555"
            
            #  ---Surlignage dernier coup ---
            highlight_color = "#4E5D6C" # Un gris-bleu du thème
            if last_move:
                if (i, j) == (last_move[0], last_move[1]) or (i, j) == (last_move[2], last_move[3]):
                    color = highlight_color
            # --- FIN DE L'AJOUT ---
                    
            canvas.create_rectangle(
                j * CELL_SIZE, i * CELL_SIZE,
                (j + 1) * CELL_SIZE, (i + 1) * CELL_SIZE,
                fill=color, outline=""
            )

            # Couche 2: Indicateur d'échec (carré rouge sous la pièce)
            if (i, j) == check_pos:
                canvas.create_rectangle(
                    j * CELL_SIZE, i * CELL_SIZE,
                    (j + 1) * CELL_SIZE, (i + 1) * CELL_SIZE,
                    fill="#FF6060", outline="" 
                )

            # Couche 3: Indicateur d'analyse (SOURCE)
            if (i, j) in analysis_sources:
                canvas.create_rectangle(
                    j * CELL_SIZE + 2, i * CELL_SIZE + 2,
                    (j + 1) * CELL_SIZE - 2, (i + 1) * CELL_SIZE - 2,
                    outline=analysis_sources[(i, j)], width=4
                )

            # Couche 4: Indicateur de sélection (carré jaune)
            if selected == (i, j):
                canvas.create_rectangle(
                    j * CELL_SIZE, i * CELL_SIZE,
                    (j + 1) * CELL_SIZE, (i + 1) * CELL_SIZE,
                    outline="yellow", width=3
                )

            # Couche 5: Indicateur de coup légal (point vert)
            if (i, j) in legal_targets:
                canvas.create_oval(
                    j * CELL_SIZE + 25, i * CELL_SIZE + 25,
                    j * CELL_SIZE + 35, i * CELL_SIZE + 35,
                    fill="green", outline=""
                )

            # Couche 6: Indicateur d'analyse (DESTINATION)
            if (i, j) in analysis_targets:
                canvas.create_oval(
                    j * CELL_SIZE + 20, i * CELL_SIZE + 20,
                    j * CELL_SIZE + 40, i * CELL_SIZE + 40,
                    fill=analysis_targets[(i, j)], outline="", stipple="gray50"
                )

            # Couche 7: La pièce (par-dessus tout)
            piece = b[i][j]
            if piece != ".":
                if piece in images_refs:
                    canvas.create_image(
                        j * CELL_SIZE + CELL_SIZE // 2,
                        i * CELL_SIZE + CELL_SIZE // 2,
                        image=images_refs[piece]
                    )
                else:
                    canvas.create_text(
                        j * CELL_SIZE + 30, i * CELL_SIZE + 30,
                        text=piece, font=("Arial", 24), fill="black"
                    )
    
    # Couche 8: Les flèches d'analyse (par-dessus TOUT)
    for from_coords, to_coords, color in moves_to_draw_arrows:
        draw_arrow(canvas, from_coords, to_coords, color)