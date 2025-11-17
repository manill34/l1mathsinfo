# C'est la fonction d'évaluation.
# C'est le "cerveau" le plus profond de l'IA.
# Nous allons la rendre beaucoup plus intelligente.

# 1. Le score matériel (ce que vous aviez déjà)
# Une Reine vaut 9 points, un Pion 1 point, etc.
piece_values = {
    'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 1000,
    'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': -1000,
    '.': 0
}

# 2. Les "Tables de Poids par Case" (La grande amélioration)
# Manil: Ce sont les "cartes de chaleur".
# Ce sont des bonus/malus pour chaque pièce, vus du côté BLANC.
# L'IA lira cette table "à l'envers" pour les Noirs.

# Bonus pour les Pions : avancer et contrôler le centre
PAWN_POS_TABLE = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
    [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
    [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
    [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
    [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
    [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0], # Grosse motivation pour avancer
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
]

# Bonus pour les Cavaliers : rester au centre, éviter les bords
KNIGHT_POS_TABLE = [
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
    [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
    [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
    [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
    [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
    [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
]

# Bonus pour les Fous : longues diagonales, éviter les coins
BISHOP_POS_TABLE = [
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
    [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
    [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
    [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
    [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
]

# Bonus pour les Tours : colonnes ouvertes (le '0.5' au centre)
ROOK_POS_TABLE = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
]

# Bonus pour la Reine : léger bonus pour être au centre
QUEEN_POS_TABLE = [
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
]

# Bonus pour le Roi : rester en sécurité (roque)
KING_POS_TABLE = [
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
    [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
    [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0], # Bonus pour les cases de roque
    [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]  # Bonus pour les cases de roque
]

# Dictionnaire pour accéder facilement aux tables
POSITIONAL_TABLES = {
    'p': PAWN_POS_TABLE,
    'n': KNIGHT_POS_TABLE,
    'b': BISHOP_POS_TABLE,
    'r': ROOK_POS_TABLE,
    'q': QUEEN_POS_TABLE,
    'k': KING_POS_TABLE
}

def evaluate_board(board):
    """
    C'est la nouvelle fonction d'évaluation.
    Elle combine le score matériel ET le score positionnel.
    """
    total_score = 0
    
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == '.':
                continue

            # 1. Calculer le score Matériel (ancienne méthode)
            total_score += piece_values[piece]

            # 2. Calculer le score Positionnel (nouvelle méthode)
            piece_type = piece.lower()
            is_white = piece.isupper()
            
            # Récupère la bonne table de position
            table = POSITIONAL_TABLES.get(piece_type)
            
            if table:
                if is_white:
                    # Pour les Blancs, on lit la table normalement
                    pos_score = table[r][c]
                else:
                    # Pour les Noirs, on lit la table "à l'envers"
                    # La 7ème ligne pour les Noirs (r=7) est la 0ème pour les Blancs (7-r)
                    pos_score = table[7-r][c]
                
                # On ajoute le bonus pour les Blancs, on le soustrait pour les Noirs
                total_score += pos_score if is_white else -pos_score

    return total_score