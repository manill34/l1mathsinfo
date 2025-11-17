# Ce fichier est le "moteur" du jeu.
from copy import deepcopy

# Cette variable globale stockera la case cible
# pour une capture "en passant". Elle est gérée par make_move
# et lue par get_moves_for_piece.
en_passant_target_square = None

board = [
    ["r","n","b","q","k","b","n","r"],
    ["p","p","p","p","p","p","p","p"],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    ["P","P","P","P","P","P","P","P"],
    ["R","N","B","Q","K","B","N","R"]
]

def make_move(b, move):
    """Applique un coup et retourne un NOUVEAU plateau."""
    global en_passant_target_square # --- On modifie l'état global
    
    x1, y1, x2, y2 = move
    new_board = deepcopy(b)
    piece = new_board[x1][y1] 

    # Mouvement standard
    new_board[x2][y2] = piece
    new_board[x1][y1] = "."
    
    # --- LOGIQUE ROQUE ---
    if piece.lower() == 'k' and abs(y2 - y1) == 2:
        if y2 > y1: # Petit roque
            rook_from_col, rook_to_col = 7, 5
        else: # Grand roque
            rook_from_col, rook_to_col = 0, 3
        
        rook_piece = new_board[x1][rook_from_col]
        new_board[x1][rook_to_col] = rook_piece
        new_board[x1][rook_from_col] = "."
    
    # ---  NOUVELLE LOGIQUE "EN PASSANT" ---
    
    # 1. Gérer la CAPTURE "en passant"
    if piece.lower() == 'p' and (x2, y2) == en_passant_target_square:
        # Le pion capturé est sur notre ligne de départ (x1),
        # et sur notre colonne d'arrivée (y2)
        new_board[x1][y2] = "." 

    # 2. Gérer la CRÉATION d'une cible "en passant"
    if piece.lower() == 'p' and abs(x2 - x1) == 2:
        en_passant_target_square = ((x1 + x2) // 2, y1) # La case *derrière* lui
    else:
        en_passant_target_square = None # Pour tout autre coup, on réinitialise
    # --- FIN DE L'AJOUT ---
    
    # --- LOGIQUE PROMOTION ---
    if piece == 'P' and x2 == 0:
        new_board[x2][y2] = 'Q' 
    if piece == 'p' and x2 == 7:
        new_board[x2][y2] = 'q'
        
    return new_board

# --- Logique de détection d'échec  ---

def find_king(b, player):
    """ Trouve les coordonnées (ligne, col) du roi du joueur."""
    king_symbol = "K" if player == "white" else "k"
    for x in range(8):
        for y in range(8):
            if b[x][y] == king_symbol:
                return (x, y)
    return None 

def is_in_check(b, player):
    """ Vérifie si le roi du 'player' est en échec."""
    king_pos = find_king(b, player)
    if not king_pos:
        return True 
    
    opponent = "black" if player == "white" else "white"
    return is_square_attacked(b, king_pos[0], king_pos[1], opponent)

def is_square_attacked(b, x, y, attacker_player):
    """
    Version "bête" et rapide.
    Regarde dans les 8 directions depuis la case (x,y)
    pour voir si une pièce ennemie l'attaque.
    Ne fait PAS d'appels récursifs.
    """
    is_white_attacker = (attacker_player == "white")
    
    # 1. Vérifier les attaques de Pions
    pawn_direction = 1 if is_white_attacker else -1
    pawn_symbol = 'P' if is_white_attacker else 'p'
    for dy in [-1, 1]:
        px, py = x + pawn_direction, y + dy
        if 0 <= px < 8 and 0 <= py < 8 and b[px][py] == pawn_symbol:
            return True
            
    # 2. Vérifier les attaques de Cavaliers
    knight_symbol = 'N' if is_white_attacker else 'n'
    for dx, dy in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 8 and 0 <= ny < 8 and b[nx][ny] == knight_symbol:
            return True
            
    # 3. Vérifier les attaques de Roi
    king_symbol = 'K' if is_white_attacker else 'k'
    for dx, dy in [(1,0),(-1,0),(0,1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
        kx, ky = x + dx, y + dy
        if 0 <= kx < 8 and 0 <= ky < 8 and b[kx][ky] == king_symbol:
            return True

    # 4. Vérifier les attaques glissantes (Tour, Fou, Reine)
    queen_symbol = 'Q' if is_white_attacker else 'q'
    rook_symbol = 'R' if is_white_attacker else 'r'
    bishop_symbol = 'B' if is_white_attacker else 'b'

    for dx, dy in [(1,0),(-1,0),(0,1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
        nx, ny = x + dx, y + dy
        while 0 <= nx < 8 and 0 <= ny < 8:
            target = b[nx][ny]
            if target != ".":
                if (target.isupper() and is_white_attacker) or \
                   (target.islower() and not is_white_attacker):
                    if (dx == 0 or dy == 0): 
                        if target == rook_symbol or target == queen_symbol:
                            return True
                    else: 
                        if target == bishop_symbol or target == queen_symbol:
                            return True
                    break 
                else:
                    break
            nx += dx
            ny += dy
            
    return False

# --- Fonctions de Mouvement ---

def get_all_legal_moves(b, player):
    """
    Retourne UNIQUEMENT les coups qui sont légaux.
    C'est la version corrigée qui gère la simulation "en passant".
    """
    global en_passant_target_square #  --- On a besoin de l'état global
    
    #  On sauvegarde l'état "en passant" AVANT de simuler
    current_en_passant_state = en_passant_target_square
    
    legal_moves_final = []
    pseudo_moves = get_all_pseudo_legal_moves(b, player)
    
    for move in pseudo_moves:
        #  On restaure l'état "en passant" AVANT chaque simulation
        en_passant_target_square = current_en_passant_state
        
        piece = b[move[0]][move[1]]
        
        # 1. Gérer le cas spécial du ROQUE
        if piece.lower() == 'k' and abs(move[3] - move[1]) == 2:
            pass_col = 5 if move[3] > move[1] else 3
            arrival_col = 6 if move[3] > move[1] else 2
            opponent = "black" if player == "white" else "white"
            # On vérifie la case de passage ET la case d'arrivée
            if is_square_attacked(b, move[0], pass_col, opponent) or \
               is_square_attacked(b, move[0], arrival_col, opponent):
                continue # Le roque n'est pas légal (passe par l'échec ou atterrit en échec)
        
        # 2. Simuler le coup
        # Cette fonction MODIFIE le global 'en_passant_target_square'
        temp_board = make_move(b, move) 
        
        # 3. Vérifier si, après ce coup, notre roi est en sécurité
        if not is_in_check(temp_board, player):
            legal_moves_final.append(move)
            
    # Manil: On restaure l'état "en passant" global à sa valeur d'origine
    en_passant_target_square = current_en_passant_state
    return legal_moves_final

def is_game_over(b, player):
    """ La partie est finie si le joueur n'a plus aucun coup légal."""
    moves = get_all_legal_moves(b, player)
    return len(moves) == 0

def get_all_pseudo_legal_moves(b, player):
    """ Retourne tous les coups "possibles" (sans vérifier l'échec)."""
    moves = []
    for x in range(8):
        for y in range(8):
            piece = b[x][y]
            if piece == ".":
                continue
            if (player == "white" and piece.isupper()) or \
               (player == "black" and piece.islower()):
                moves.extend(get_moves_for_piece(b, x, y))
    return moves

def generate_sliding_moves(b, x, y, piece, directions):
    """ Fonction helper pour les pièces qui glissent (Tour, Fou, Reine)."""
    moves = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        while 0 <= nx < 8 and 0 <= ny < 8:
            target = b[nx][ny]
            if target == ".":
                moves.append((x, y, nx, ny))
            else:
                if target.isupper() != piece.isupper():
                    moves.append((x, y, nx, ny)) 
                break 
            nx += dx
            ny += dy
    return moves

def get_moves_for_piece(b, x, y):
    """
     Génère les coups pour une seule pièce (sans vérifier l'échec).
    """
    global en_passant_target_square #  --- On a besoin de savoir s'il existe
    
    if not (0 <= x < 8 and 0 <= y < 8):
        return []
    piece = b[x][y]
    if piece == ".":
        return []

    moves = []
    is_white = piece.isupper()

    if piece.lower() == "p":  # PION
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1

        # Avance simple
        nx, ny = x + direction, y
        if 0 <= nx < 8 and b[nx][ny] == ".":
            moves.append((x, y, nx, ny))
            # Double pas
            nx2 = x + 2*direction
            if x == start_row and 0 <= nx2 < 8 and b[nx2][y] == ".":
                moves.append((x, y, nx2, y))

        # Captures
        for dy in (-1, 1):
            cx, cy = x + direction, y + dy
            if 0 <= cx < 8 and 0 <= cy < 8:
                target = b[cx][cy]
                if target != "." and target.isupper() != is_white:
                    moves.append((x, y, cx, cy))
                    
        #  ---   Capture "En Passant" ---
        if en_passant_target_square:
            # Est-ce que la cible 'en passant' est bien une diagonale ?
            if en_passant_target_square[0] == x + direction and abs(en_passant_target_square[1] - y) == 1:
                moves.append((x, y, en_passant_target_square[0], en_passant_target_square[1]))
        # --- FIN DE L'AJOUT ---

    elif piece.lower() == "n":  # CAVALIER
        deltas = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for dx, dy in deltas:
            nx, ny = x+dx, y+dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = b[nx][ny]
                if target == "." or target.isupper() != is_white:
                    moves.append((x,y,nx,ny))

    elif piece.lower() == "k":  # ROI
        # Mouvements normaux
        deltas = [(1,0),(-1,0),(0,1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        for dx, dy in deltas:
            nx, ny = x+dx, y+dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = b[nx][ny]
                if target == "." or target.isupper() != is_white:
                    moves.append((x,y,nx,ny))
        
        # Logique Roque (Pseudo-légale, sans vérif d'échec)
        if (is_white and x == 7 and y == 4 and b[7][4] == 'K') or \
           (not is_white and x == 0 and y == 4 and b[0][4] == 'k'):
            
            # Côté Roi (petit roque)
            if b[x][5] == "." and b[x][6] == "." and b[x][7] == ('R' if is_white else 'r'):
                moves.append((x, 4, x, 6))
                
            # Côté Dame (grand roque)
            if b[x][3] == "." and b[x][2] == "." and b[x][1] == "." and b[x][0] == ('R' if is_white else 'r'):
                moves.append((x, 4, x, 2))

    elif piece.lower() == "r":  # TOUR
        directions = [(1,0),(-1,0),(0,1),(0,-1)] # (-1,-1) était faux
        moves.extend(generate_sliding_moves(b, x, y, piece, directions))

    elif piece.lower() == "b":  # FOU
        directions = [(1,1),(1,-1),(-1,1),(-1,-1)]
        moves.extend(generate_sliding_moves(b, x, y, piece, directions))

    elif piece.lower() == "q":  # REINE
        directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        moves.extend(generate_sliding_moves(b, x, y, piece, directions))

    return moves