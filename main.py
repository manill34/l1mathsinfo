import tkinter as tk
import ttkbootstrap as tb 
from tkinter import ttk 
import chessboard
import gui
import minimax
import tree_visualizer
from chessboard import deepcopy
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# --- Constantes ---
BOARD_WIDTH = 8 * gui.CELL_SIZE # 480
BOARD_HEIGHT = 8 * gui.CELL_SIZE # 480
ANALYSIS_WIDTH = 500 
WINDOW_WIDTH = BOARD_WIDTH + ANALYSIS_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT + 50 

# --- Variables Globales ---
selected = None
legal_moves_for_selected = []
current_player = "white"
game_over = False
last_ai_analysis = [] 
tree_canvas_widget = None 
top_moves_to_show = [] 
analysis_highlights_active = False 
difficulty_var = None 
ai_move_count = 0 
last_move = None 

# --- Configuration de la fenêtre principale ---
root = tb.Window(themename="superhero") 
root.title("Chess.AI (Projet Arbres - L1 Miashs)")

# CORRECTION DU LOGO (chemin simple) ---
try:
    logo_path = "logo.png" # Chemin direct
    logo_img = tk.PhotoImage(file=logo_path)
    root.iconphoto(True, logo_img)
except Exception as e:
    print(f"Erreur chargement logo '{logo_path}': {e}. Utilisation de l'icône par défaut.")

root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
difficulty_var = tb.IntVar(value=2) 

# -----------------------------------------------------------------
#  BLOC DES DÉFINITIONS DE FONCTIONS 
# -----------------------------------------------------------------

def refresh_board():
    """Redessine l'échiquier avec l'état actuel."""
    global top_moves_to_show, last_move
    king_in_check_pos = None
    if chessboard.is_in_check(chessboard.board, current_player):
        king_in_check_pos = chessboard.find_king(chessboard.board, current_player)
    
    # On passe le "dernier coup" au dessinateur
    gui.draw_board(game_canvas, chessboard.board, 
                   selected=selected, 
                   legal_moves=legal_moves_for_selected,
                   check_pos=king_in_check_pos,
                   analysis_moves=top_moves_to_show,
                   last_move=last_move) #  --- AJOUT

def draw_tree_on_canvas(figure):
    """ Affiche la figure Matplotlib (l'arbre) dans le panneau d'analyse."""
    global tree_canvas_widget
    if tree_canvas_widget:
        tree_canvas_widget.get_tk_widget().destroy()
    
    figure.set_facecolor("#375a7f") 
    tree_canvas_widget = FigureCanvasTkAgg(figure, master=tree_frame)
    tree_canvas_widget.draw()
    tree_canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def update_top_moves_display():
    """ Met à jour le texte "Top 3 coups"."""
    if not last_ai_analysis:
        top_moves_text.config(text="-")
        return
    text = ""
    for i, (score, move) in enumerate(last_ai_analysis[:3]):
        move_str = tree_visualizer.get_move_str(move)
        text += f"{i+1}. {move_str} (Score: {score:.0f})\n"
    top_moves_text.config(text=text.strip())

def clear_analysis_display():
    """ Efface les flèches d'analyse et l'arbre."""
    global last_ai_analysis, top_moves_to_show, analysis_highlights_active, tree_canvas_widget
    last_ai_analysis = []
    top_moves_to_show = []
    analysis_highlights_active = False
    
    analysis_btn.config(text="Analyser", state=tk.NORMAL) # Texte raccourci
    top_moves_text.config(text="-")
    
    if tree_canvas_widget:
        tree_canvas_widget.get_tk_widget().destroy()
        tree_canvas_widget = None
    refresh_board() 

def toggle_analysis_panel():
    """ Cache ou affiche le panneau d'analyse de droite."""
    if right_frame.winfo_viewable():
        right_frame.pack_forget()
        root.geometry(f"{BOARD_WIDTH + 40}x{WINDOW_HEIGHT}")
        toggle_btn.config(text="Montrer l'analyse >")
    else:
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        toggle_btn.config(text="< Cacher l'analyse")

# --- Logique d'analyse (Threading) ---

def run_deep_analysis():
    """ Lance les calculs LOURDS dans un thread séparé."""
    global analysis_highlights_active
    
    if analysis_highlights_active:
        clear_analysis_display()
        return

    analysis_depth = difficulty_var.get() 
    tree_depth = 2 
    
    analysis_btn.config(text="Calcul...", state=tk.DISABLED)
    top_moves_text.config(text=f"L'IA réfléchit (depth {analysis_depth})...")
    root.update_idletasks() 

    board_copy = deepcopy(chessboard.board)
    player_copy = str(current_player)
    
    analysis_thread = threading.Thread(target=run_analysis_thread, 
                                       args=(board_copy, player_copy, analysis_depth, tree_depth))
    analysis_thread.start()

def run_analysis_thread(board, player, analysis_depth, tree_depth): 
    """ Fonction exécutée dans le thread."""
    
    print(f"Thread d'analyse (depth {analysis_depth}) démarré...")
    try:
        current_analysis = minimax.get_sorted_moves(board, player, depth=analysis_depth)
        if not current_analysis:
            root.after(0, on_analysis_complete, None, None)
            return

        print(f"Génération de l'arbre (depth {tree_depth})...")
        fig = tree_visualizer.create_tree_figure(board, player, depth=tree_depth)
        
        root.after(0, on_analysis_complete, current_analysis, fig)
        
    except Exception as e:
        print(f"Erreur dans le thread d'analyse: {e}")
        root.after(0, on_analysis_complete, None, None) 

def on_analysis_complete(analysis_results, figure):
    """ S'exécute quand le thread est fini."""
    global last_ai_analysis, top_moves_to_show, analysis_highlights_active

    analysis_btn.config(state=tk.NORMAL)

    if not analysis_results:
        top_moves_text.config(text="Aucun coup possible (Mat ou Pat).")
        analysis_btn.config(text="Analyser")
        return

    last_ai_analysis = analysis_results
    draw_tree_on_canvas(figure)
    update_top_moves_display()
    
    analysis_highlights_active = True
    analysis_btn.config(text="Cacher")
    
    colors = ["#FF4136", "#FF851B", "#0074D9"]
    top_moves_to_show = []
    
    for i, (score, move) in enumerate(last_ai_analysis[:3]):
        if i < len(colors):
            top_moves_to_show.append((move, colors[i]))
    
    refresh_board()

# --- Logique de jeu (RAPIDE) ---

def on_click(event):
    """ Gère tous les clics sur l'échiquier."""
    global selected, legal_moves_for_selected, current_player, game_over
    global analysis_highlights_active, last_move

    if game_over or current_player == "black":
        return 

    col = event.x // gui.CELL_SIZE
    row = event.y // gui.CELL_SIZE
    if not (0 <= row < 8 and 0 <= col < 8): return

    if analysis_highlights_active:
        clear_analysis_display()

    piece = chessboard.board[row][col]

    if selected is None:
        if piece == ".": return
        
        is_white_piece = piece.isupper()
        if (current_player == "white" and is_white_piece):
            selected = (row, col)
            all_legal = chessboard.get_all_legal_moves(chessboard.board, current_player)
            legal_moves_for_selected = [m for m in all_legal if m[0] == row and m[1] == col]
        else:
            return
    else:
        from_row, from_col = selected
        move = (from_row, from_col, row, col)
        
        if move in legal_moves_for_selected:
            chessboard.board = chessboard.make_move(chessboard.board, move)
            last_move = move 
            selected = None
            legal_moves_for_selected = []
            
            clear_analysis_display() 
            
            current_player = "black"
            refresh_board()

            if check_game_end(): return
            root.after(100, ai_move) 
            return
        else:
            selected = None
            legal_moves_for_selected = []
            on_click(event) 
            
    refresh_board()

def ai_move():
    """ L'IA joue VITE ou utilise son livre d'ouvertures."""
    global current_player, game_over, ai_move_count, last_move
    if game_over: return

    best_move = None 
    
    if ai_move_count == 0:
        print("L'IA utilise son livre d'ouvertures...")
        
        if chessboard.board[4][4] == 'P' and chessboard.board[6][4] == '.':
            best_move = (1, 2, 3, 2) # Joue ...c5 (Sicilienne)
        else:
            best_move = (1, 6, 2, 4) # Joue ...Nf6
        
        if best_move in chessboard.get_all_legal_moves(chessboard.board, "black"):
             print(f"L'IA (livre) a choisi {best_move}")
        else:
             best_move = None 
             print("Le coup du livre n'est pas légal, calcul...")

    if best_move is None: 
        current_ai_depth = difficulty_var.get()
        print(f"L'IA (depth {current_ai_depth}, coup n°{ai_move_count+1}) réfléchit...")
        
        quick_analysis = minimax.get_sorted_moves(chessboard.board, "black", depth=current_ai_depth)

        if not quick_analysis:
            print("♟️ L'IA ne trouve aucun coup (Mat ou Pat).")
            check_game_end()
            return
            
        best_move = quick_analysis[0][1]
        score = quick_analysis[0][0]
        print(f"L'IA (minimax) a choisi {best_move} (score: {score})")
    
    chessboard.board = chessboard.make_move(chessboard.board, best_move)
    last_move = best_move 
    ai_move_count += 1 
    
    current_player = "white"
    refresh_board()
    check_game_end()

def check_game_end():
    """ Vérifie si la partie est terminée (Mat ou Pat)."""
    global game_over
    if game_over: return True
    
    if chessboard.is_game_over(chessboard.board, current_player):
        game_over = True
        if chessboard.is_in_check(chessboard.board, current_player):
            winner = "NOIRS" if current_player == "white" else "BLANCS"
            show_game_over_animation(f"Les {winner} gagnent !")
        else:
            show_game_over_animation("Match Nul (Pat)")
        return True
    return False

def start_new_game():
    """ Réinitialise tout pour une nouvelle partie."""
    global selected, legal_moves_for_selected, current_player, game_over
    global tree_canvas_widget, ai_move_count, last_move
    
    print("--- NOUVELLE PARTIE ---")
    selected = None
    legal_moves_for_selected = []
    current_player = "white"
    game_over = False
    ai_move_count = 0 
    last_move = None 
    
    chessboard.en_passant_target_square = None 
    
    chessboard.board = [
        ["r","n","b","q","k","b","n","r"], ["p","p","p","p","p","p","p","p"],
        [".",".",".",".",".",".",".","."], [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."], [".",".",".",".",".",".",".","."],
        ["P","P","P","P","P","P","P","P"], ["R","N","B","Q","K","B","N","R"]
    ]
    
    clear_analysis_display()
    refresh_board()

def show_game_over_animation(winner_text):
    """ Affiche la fenêtre de fin de partie."""
    global game_over
    game_over = True
    
    overlay = tb.Toplevel(master=root, title="Partie Terminée")
    overlay.geometry(f"400x200+{root.winfo_x()+150}+{root.winfo_y()+150}")
    overlay.resizable(False, False)

    main_label = tb.Label(overlay, text="PARTIE TERMINÉE", font=("Helvetica", 20, "bold"), bootstyle="primary")
    main_label.pack(pady=20)
    
    sub_label = tb.Label(overlay, text=winner_text, font=("Helvetica", 14), bootstyle="info")
    sub_label.pack(pady=5)

    def restart_game():
        overlay.destroy()
        start_new_game()

    restart_btn = tb.Button(overlay, text="↻ Rejouer", bootstyle="success", command=restart_game)
    restart_btn.pack(pady=20, ipadx=10, ipady=5)

    overlay.transient(root)
    overlay.grab_set()
    
    overlay.protocol("WM_DELETE_WINDOW", restart_game)


# -----------------------------------------------------------------
#FIN DU BLOC DE FONCTIONS 
# -----------------------------------------------------------------

gui.load_images()

# --- Création des panneaux (Frames) ---

main_frame = tb.Frame(root) 
main_frame.pack(fill=tk.BOTH, expand=True)

# Panneau de GAUCHE (Jeu + Bouton Cacher)
left_frame = tb.Frame(main_frame, width=BOARD_WIDTH, height=WINDOW_HEIGHT)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10)

game_canvas = tk.Canvas(left_frame, width=BOARD_WIDTH, height=BOARD_HEIGHT)
game_canvas.pack(pady=10)

toggle_btn = tb.Button(left_frame, text="< Cacher l'analyse", command=toggle_analysis_panel, bootstyle="secondary-outline")
toggle_btn.pack(pady=5, fill=tk.X)

# Panneau de DROITE (Analyse)
right_frame = tb.Frame(main_frame, width=ANALYSIS_WIDTH, height=WINDOW_HEIGHT) 
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
right_frame.pack_propagate(False) 

# 1. Cadre de CONTRÔLE (en haut)
control_frame = tb.Frame(right_frame) 
control_frame.pack(fill=tk.X, padx=10, pady=10)

# J'ai raccourci le texte du bouton pour faire de la place
analysis_btn = tb.Button(control_frame, text="Analyser", command=run_deep_analysis, bootstyle="primary")
analysis_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

#  NOUVEAU BOUTON REDÉMARRER ---
restart_btn = tb.Button(control_frame, text="↻ Redémarrer", command=start_new_game, bootstyle="warning-outline")
restart_btn.pack(side=tk.LEFT, padx=5)



difficulty_label = tb.Label(control_frame, text="Difficulté:", font=("Helvetica", 10))
difficulty_label.pack(side=tk.LEFT, padx=(10, 0))

difficulty_scale = tb.Scale(
    control_frame, 
    from_=1, 
    to_=3, 
    variable=difficulty_var, 
    orient=tk.HORIZONTAL,
    length=120 # Raccourci pour faire de la place
)
difficulty_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

# 2. Cadre de RÉSULTATS (le reste de la place)
results_frame = tb.Frame(right_frame)
results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

tree_frame = tb.Frame(results_frame, bootstyle="secondary") 
tree_frame.pack(fill=tk.BOTH, expand=True)

top_moves_frame = tb.Frame(results_frame, height=100, bootstyle="dark") 
top_moves_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

top_moves_label = tb.Label(top_moves_frame, text="Analyse des meilleurs coups :", font=("Helvetica", 14, "bold")) 
top_moves_label.pack(anchor="w", padx=10)
top_moves_text = tb.Label(top_moves_frame, text="-", font=("Helvetica", 12)) 
top_moves_text.pack(anchor="w", padx=10)

# --- Démarrage ---
game_canvas.bind("<Button-1>", on_click)
start_new_game()
root.mainloop()