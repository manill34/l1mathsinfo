# C'est le "cerveau" de l'IA.
# Il implémente l'algorithme Minimax avec élagage Alpha-Beta.
from evaluation import evaluate_board
import chessboard

# Scores extrêmes pour Mat et Pat
CHECKMATE_SCORE = 10000 
STALEMATE_SCORE = 0

def minimax_alpha_beta(b, depth, alpha, beta, player_is_maximizing):
    """
    C'est la fonction récursive qui explore l'arbre des coups.
    - depth: Combien de coups à l'avance regarder.
    - alpha: Le meilleur score trouvé pour le joueur Max.
    - beta: Le meilleur score (le plus bas) trouvé pour le joueur Min.
    - player_is_maximizing: 'True' si c'est le tour des Blancs (Max), 'False' pour les Noirs (Min).
    """
    player_str = "white" if player_is_maximizing else "black"
    
    # --- Condition d'arrêt 1: Profondeur 0 ou Partie Finie ---
    if depth == 0 or chessboard.is_game_over(b, player_str):
        
        if chessboard.is_game_over(b, player_str):
            if chessboard.is_in_check(b, player_str):
                # Échec et Mat ! C'est très mauvais pour le joueur actuel.
                return -CHECKMATE_SCORE if player_is_maximizing else CHECKMATE_SCORE, None
            else:
                # Pat (Match Nul)
                return STALEMATE_SCORE, None
        
        # Si profondeur 0, on évalue simplement le plateau
        return evaluate_board(b), None

    best_move = None
    legal_moves = chessboard.get_all_legal_moves(b, player_str)

    if player_is_maximizing: # --- Tour du joueur MAX (Blancs) ---
        value = float('-inf') # On cherche le plus haut score possible
        for move in legal_moves:
            new_b = chessboard.make_move(b, move)
            # Appel récursif pour le joueur suivant (Min)
            eval_val, _ = minimax_alpha_beta(new_b, depth-1, alpha, beta, False)
            
            if eval_val > value:
                value, best_move = eval_val, move
            
            alpha = max(alpha, value)
            if beta <= alpha:
                # C'est l'élagage ALPHA-BETA.
                # Si le score MIN (beta) est plus petit que notre score MAX (alpha),
                # l'adversaire (Min) ne choisira jamais cette branche. On arrête de chercher.
                break 
        return value, best_move

    else: # --- Tour du joueur MIN (Noirs) ---
        value = float('inf') # On cherche le plus bas score possible
        for move in legal_moves:
            new_b = chessboard.make_move(b, move)
            # Appel récursif pour le joueur suivant (Max)
            eval_val, _ = minimax_alpha_beta(new_b, depth-1, alpha, beta, True)
            
            if eval_val < value:
                value, best_move = eval_val, move
            
            beta = min(beta, value)
            if beta <= alpha:
                # Manil: Élagage ALPHA-BETA.
                break
        return value, best_move

def get_sorted_moves(b, player, depth=3):
    """
    C'est la fonction "racine" que main.py appelle.
    Elle analyse TOUS les premiers coups et les retourne triés du meilleur au pire.
    """
    is_max = (player == "white")
    legal_moves = chessboard.get_all_legal_moves(b, player)
    
    if not legal_moves:
        return []

    move_scores = []
    
    # Pour chaque coup légal à la racine...
    for move in legal_moves:
        new_b = chessboard.make_move(b, move)
        # ...on lance une évaluation minimax complète
        eval_val, _ = minimax_alpha_beta(new_b, depth - 1, float('-inf'), float('inf'), not is_max)
        move_scores.append((eval_val, move))

    # On trie la liste
    # Si c'est Max (Blanc), on veut le score le plus ÉLEVÉ (reverse=True)
    # Si c'est Min (Noir), on veut le score le plus BAS (reverse=False)
    move_scores.sort(key=lambda x: x[0], reverse=is_max) 
    
    return move_scores