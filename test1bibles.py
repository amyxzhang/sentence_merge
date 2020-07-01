from nltk.tokenize import word_tokenize
from collections import defaultdict      

import networkx as nx
import matplotlib.pyplot as plt 

# Bible verses dataset
bibles = {
'JUB': "Behold, the pain of my iniquity has caused me to writhe; my mother conceived me so that sin might be removed from me.",
'ASV': "Behold, I was brought forth in iniquity; And in sin did my mother conceive me.",
'BBE': "Truly, I was formed in evil, and in sin did my mother give me birth.",
'CEB': "Yes, I was born in guilt, in sin, from the moment my mother conceived me.",
'SJB': "True, I was born guilty, was a sinner from the moment my mother conceived me.",
'NCV': "I was brought into this world in sin. In sin my mother gave birth to me.",
'NIV': "Surely I was sinful at birth, sinful from the time my mother conceived me.",
'NLT': "For I was born a sinner- yes, from the moment my mother conceived me.",
'GNT': "I have been evil from the day I was born; from the time I was conceived, I have been sinful.",
'KJV': "Behold, I was shapen in iniquity; and in sin did my mother conceive me.",
'MSG': "I've been out of step with you for a long time, in the wrong since before I was born.",
'NIRV': "I know I've been a sinner ever since I was born. I've been a sinner ever since my mother became pregnant with me."
}


# Node for creating merged representation
class Node:
    def __init__(self, text):
        self.text = text
        self.size = 1
        self.bibles = []
        self.next_word = {} 
        self.next_links = []
        self.prev_links = []
        
    def __str__(self):
#         return self.text
        x = ','.join(self.bibles)
        return x + ': ' + self.text
    
    # recursive print
    def print_list(self):
        print str(self)
        for l in self.next_links:
            l.print_list()
        if len(self.next_links) == 0:
            print '======='
            
    # recursive drawing
    def draw_graph(self, graph, pos, link_length, y, fixed):
        graph.add_node(self)
        pos[self] = (link_length, y*20)
        for i, next_link in enumerate(self.next_links):
            G.add_edge(self, next_link)
            next_link.draw_graph(graph, pos, link_length+20, y+i, fixed)
            
# populate merged_verses with initial graph (list of linked lists) of verses
merged_verses = []
cursors = {}

for bible in bibles:
    text =  bibles[bible]
    tokens = word_tokenize(text)

    n = Node(tokens[0])
    n.bibles.append(bible)
    merged_verses.append(n)
    
    # set initial cursor for each bible on the first word
    cursors[bible] = n
    
    # create linked list for each verse
    for token in tokens[1:]:
        n2 = Node(token)
        n2.bibles.append(bible)
        n.next_links.append(n2)
        n.next_word[n.bibles[0]] = n2
        n2.prev_links.append(n)
        n = n2


# continually loop until all merges have happened
for q in range(6):
    
    # looking at all the cursors, find the token with highest frequency
    token_counter = defaultdict(int)
    token_list = defaultdict(list)
     
    for c in cursors:
        token = cursors[c].text
        token_counter[token] += 1
        token_list[token].append(cursors[c])
         
    sorted_counter = sorted(token_counter.items(), key=lambda x: x[1], reverse=True)
     
    merge_point = sorted_counter[0]
    print merge_point
    
    # if the merge point is simply a continuation of a previous merge point w/ same verses, just add them together
    replace = False
    prevs = []
    for token in token_list[merge_point[0]]:
        if len(token.prev_links) == 1:
            prevs.append(token.prev_links[0])

    if len(prevs) > 0:
        if prevs.count(prevs[0]) == len(prevs):
            if len(prevs[0].next_links) == len(prevs):
                replace = True
                prevs[0].text = prevs[0].text + ' ' + merge_point[0]
                prevs[0].next_links = []
                for token in token_list[merge_point[0]]:
                    prevs[0].next_links += token.next_links
                    main_token = prevs[0]
    
    
    # get all the cursor nodes that have the merge point token and combine them into one node
    if not replace:
        main_token = token_list[merge_point[0]][0]
    
        for token in token_list[merge_point[0]][1:]:
            for prev_token in token.prev_links:
                main_token.prev_links.append(prev_token)
                prev_token.next_links.remove(token)
                prev_token.next_links.append(main_token)
        
            for next_token in token.next_links:
                main_token.next_links.append(next_token)
                next_token.prev_links.remove(token)
                next_token.prev_links.append(main_token)
             
            main_token.bibles = list(set(main_token.bibles + token.bibles))
            main_token.size += 1
            if token in merged_verses:
                merged_verses.remove(token)
        
    # move cursors for all the merge point nodes forward one node
    for bible in main_token.bibles:
        cursors[bible] = cursors[bible].next_word[bible]
     
     
     
    # graph what the graph looks like at each iteration
    merged_verses = sorted(merged_verses, key=lambda x: x.size)
    
    G = nx.DiGraph()
    
    fixed = []
    pos = {}
    
    for i, node in enumerate(merged_verses):
        node.draw_graph(G, pos, 0, i, fixed)
        fixed.append(node)
        pos[node] = (0 + (i*10),i*100)
       
    # cursor nodes are in red
    gray_nodes = [node for node in G.nodes() if node not in cursors.values()] 
    cursor_nodes = [node for node in G.nodes() if node in cursors.values()]
    
    pos = nx.spring_layout(G, pos=pos, fixed=fixed)
    nx.draw_networkx_nodes(G, pos, nodelist=gray_nodes, node_color='#cccccc', node_size=400)
    nx.draw_networkx_nodes(G, pos,  nodelist=cursor_nodes, node_color='#ff0000', node_size=400)
    nx.draw_networkx_labels(G, pos, font_size=8)
    nx.draw_networkx_edges(G, pos, arrows=True)
    plt.show()



    