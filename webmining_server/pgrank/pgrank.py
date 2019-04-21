from sentiment_analyzer.models import Page, SearchTerm

num_iterations = 100
#Sum of different between old and new rankings divided by total number of pages
eps = 0.0001
#Probability of following the transition matrix. As defined in the original model.
D = 0.85
'''
    Ranks the pages crawled by the spider using a basic version of the PageRank algorithm.
    The total rank is constant throughout all iterations.

    The original formula is R_new = ((1 - d)*E/N + d*A.T).dot(R_curr);

    However if we normalize the ranks by having each page rank 1, then e.T.dot(P) = N. The total rank is N. 
    And the formula changes as follows.

    R_new = (1 - d)*e + d*A.T.dot(R_curr)
'''
def pg_rank(search_id):
    print("Search id is ", search_id)
    s = SearchTerm.objects.get(id=int(search_id))
    links = s.links.all()
    print('len', len(links), ' search term', s.term)
    from_idxs = [i.from_id for i in links]
    # Find the idxs that receive page rank 
    links_received = []
    to_idxs = []
    for l in links:
        from_id = l.from_id
        to_id = l.to_id
        #We restrict the output nodes to come from the same set as the input nodes.
        if to_id not in from_idxs:
            continue
        links_received.append([from_id, to_id])
        if to_id not in to_idxs:
            to_idxs.append(to_id)

    #At this point I have three lists:
    #links_received - Trasition matrix
    #from_idxs - Ids of pages that have at least one output link
    #to_idxs - Ids of pages that have at least one input link

    pages = s.pages.all()

    #Dictionary of ranks.
    #Key - Page id
    #Value - Rank
    #Initialize the dictionary with the default ranking assigned to each page.
    curr_ranks = dict()
    for node in from_idxs:
        tmp_page = Page.objects.get(id=node)
        curr_ranks[node] = tmp_page.rank

    # print 'prev_ranks:',len(prev_ranks)
    conv = 1.
    i = 0
    while conv > eps or i < num_iterations:
        next_ranks = dict()
        total_curr_rank = 0.0
        for node, curr_rank in curr_ranks.items():
            total_curr_rank += curr_rank
            next_ranks[node] = 0.0

        # Get the current rank of a given node and pass it down to each of its output links.
        for (node, curr_rank) in curr_ranks.items():
            out_idxs = []
            for (from_id, to_id) in links_received:
                if from_id != node:
                    continue
                out_idxs.append(to_id)
            if (len(out_idxs) == 0):
                continue
            amount = D * curr_rank / len(out_idxs)
            for id in out_idxs:
                next_ranks[id] += amount

        const = (1 - D)

        #Pass down a constant rank to each node.
        for id in next_ranks:
            next_ranks[id] += const

        total_next_rank = 0
        for (node, next_rank) in next_ranks.items():
            total_next_rank += next_rank

        #Check convergence
        tot_diff = 0
        for (id, curr_rank) in curr_ranks.items():
            next_rank = next_ranks[id]
            diff = abs(curr_rank - next_rank)
            tot_diff += diff
        conv = tot_diff / len(curr_ranks)
        i += 1
        curr_ranks = next_ranks
        print('convergence:', conv, ' iteration:', i, " old_total", total_curr_rank, " new total", total_next_rank)

    print('final convergence:', conv, ' iteration:', i)
    for (id, new_rank) in next_ranks.items():
        ptmp = Page.objects.get(id=id)
        url = ptmp.url
        print(id, ' url:', url)

    #Save final rank
    for (id, new_rank) in next_ranks.items():
        ptmp = Page.objects.get(id=id)
        ptmp.rank = new_rank
        ptmp.save()