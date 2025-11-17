# Manil: Ce fichier utilise networkx et matplotlib
# pour dessiner l'arbre de décision que l'IA a exploré.
import networkx as nx
# import matplotlib.pyplot as plt ◀️ --- Manil: Supprimé (inutilisé)
from matplotlib.figure import Figure 
import chessboard
import evaluation
import minimax 

def get_move_str(move):
    """ Convertit (x1,y1,x2,y2) en '(x1,y1)->(x2,y2)'."""
    return f"({move[0]},{move[1]}) -> ({move[2]},{move[3]})"

def create_tree_figure(board, player, depth=2):
    """
    Construit un arbre de décision (jusqu'à 'depth')
    et RETOURNE une Figure matplotlib (pas un plt.show()).
    """
    print(f"Construction de l'arbre (profondeur {depth}) pour {player}...")
    
    tree_nodes = {} # Dictionnaire pour stocker les nœuds
    node_counter = 0

    def build_recursive(current_board, current_player, current_depth, parent_node_id):
        """La fonction récursive qui construit l'arbre."""
        nonlocal node_counter
        is_max_player = (current_player == "white")
        
        # Condition d'arrêt
        if current_depth == 0 or chessboard.is_game_over(current_board, current_player):
            # C'est une feuille, on l'évalue
            if chessboard.is_game_over(current_board, current_player):
                score = minimax.CHECKMATE_SCORE if not is_max_player else -minimax.CHECKMATE_SCORE
            else:
                score = evaluation.evaluate_board(current_board)
            tree_nodes[parent_node_id]['score'] = score
            return

        next_player = "black" if current_player == "white" else "white"
        moves = chessboard.get_all_legal_moves(current_board, current_player)
        
        if not moves:
            tree_nodes[parent_node_id]['score'] = evaluation.evaluate_board(current_board)
            return

        children_scores = []
        max_children_to_show = 4 # Limite pour la visibilité de l'arbre
        
        for move in moves[:max_children_to_show]:
            new_board = chessboard.make_move(current_board, move)
            node_counter += 1
            child_node_id = f"Nœud {node_counter}"
            tree_nodes[child_node_id] = {'score': 0, 'children': []} 
            tree_nodes[parent_node_id]['children'].append((child_node_id, get_move_str(move)))
            
            # Appel récursif
            build_recursive(new_board, next_player, current_depth - 1, child_node_id)
            children_scores.append(tree_nodes[child_node_id]['score'])

        # Remontée du score (Minimax)
        if not children_scores:
             tree_nodes[parent_node_id]['score'] = evaluation.evaluate_board(current_board)
        elif is_max_player:
            tree_nodes[parent_node_id]['score'] = max(children_scores)
        else:
            tree_nodes[parent_node_id]['score'] = min(children_scores)

    # --- Point de départ de la construction ---
    root_id = "Racine (Actuel)"
    tree_nodes[root_id] = {'score': 0, 'children': []}
    build_recursive(board, player, depth, root_id)

    # --- Création du graphe NetworkX ---
    G_viz = nx.DiGraph()
    labels_nodes = {}
    labels_edges = {}

    for parent_id, data in tree_nodes.items():
        score = data.get('score', 0)
        labels_nodes[parent_id] = f"{parent_id}\n(Score: {score:.0f})"
        G_viz.add_node(parent_id)
        for child_id, move_label in data.get('children', []):
            G_viz.add_edge(parent_id, child_id)
            labels_edges[(parent_id, child_id)] = move_label

    # --- Création de la FIGURE ---
    fig = Figure(figsize=(8, 6), dpi=100) 
    ax = fig.add_subplot(111) 
    
    try:
        # Tente d'utiliser le layout 'graphviz' (le joli)
        pos = nx.nx_agraph.graphviz_layout(G_viz, prog="dot")
    except:
        # Si graphviz n'est pas installé, utilise le layout 'moche'
        print("Layout Graphviz non trouvé. Utilisation d'un layout simple.")
        pos = nx.spring_layout(G_viz) 
    
    nx.draw(G_viz, pos, ax=ax, 
            labels=labels_nodes, 
            with_labels=True, 
            node_color="skyblue", 
            node_size=2000, 
            font_size=8)
            
    nx.draw_networkx_edge_labels(G_viz, pos, ax=ax,
                                 edge_labels=labels_edges, 
                                 font_color='red',
                                 font_size=7)
    
    ax.set_title(f"Arbre d'analyse pour {player} (profondeur {depth})")
    
    return fig # Retourne la figure pour main.py