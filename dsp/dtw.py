## Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

'''
	Dynamic Time Warping (DTW) for Audio Synchronization
	Given: Two audio recordings of the same musical piece
	Goal: Find the points of musical correspondence between the two pieces
	Algorithm:
		1. Convert recordings to appropriate representation (we choose chromagrams).
			Chroma X: 12 x N
			Chroma Y: 12 x M
		2. Create a cost/similarity matrix ('C') using cosine distance.
			Cost Matrix C: N x M
		3. Find the optimal path ('P*') through this matrix: this will give us the correspondence points.
			* optimal: lowest acculumated cost
			To find efficiently: introduce acculumated cost matrix ('D') and backtracking matrix ('B')
			Accumulated Cost Matrix D: N x M
			Backtracking Matrix B: N x M
'''		

# TODO(smritip): look into DTW optimizations like Sakoe-Chiba bound

import numpy as np
from constants import *

# Create cost matrix between two sequences x and y, using cosine distance.
def get_cost_matrix(x, y, normalized_chromagrams=True) :
	if normalized_chromagrams:
		return 1 - np.dot(x.T, y)

	# without normalized chromagrams
	N = x.shape[1]
	M = y.shape[1]
	max_range= max(N, M)
	cost = np.empty((N, M))
	for i in range(N):
		for j in range(M):
			cost[i, j] = 1 - np.true_divide(np.dot(x[:, i], y[:, j]), (np.linalg.norm(x[:, i]) * np.linalg.norm(y[:, j])))

	return cost

# Calculate the accumulated cost and backtracking matrices based on the cost matrix.
def run_dtw(C):
    n = C.shape[0]
    m = C.shape[1]
    D = np.empty((n, m))
    
    # each entry in B will be like a "pointer" to the point it came from
    # (0 = origin, 1 = from left, 2 = from diagonal, 3 = from below)
    B = np.empty((n, m))
    
    # initialize origin
    D[0, 0] = C[0, 0]
    B[0, 0] = 0
    
    # initialize first column
    cost = C[0, 0]
    for i in range(1, n):
        cost += C[i, 0]
        D[i, 0] = cost
        B[i, 0] = 3
    
    # initialize first row
    cost = C[0, 0]
    for i in range(1, m):
        cost += C[0, i]
        D[0, i] = cost
        B[0, i] = 1
    
    # calculate accumulated cost for rest of matrix
    # TODO(smritip): take a look at optimizations (code without loop, use argmin)
    for i in range(1, n):
        for j in range(1, m):
            p_costs = [(i-1, j), (i, j-1), (i-1, j-1)]
            min_cost = D[p_costs[0][0], p_costs[0][1]]
            min_indices = p_costs[0]
            for k in range(1, len(p_costs)):  # code without loop (argmin)
                c = D[p_costs[k][0], p_costs[k][1]]
                if c < min_cost:
                    min_cost = D[p_costs[k][0], p_costs[k][1]]
                    min_indices = p_costs[k]
        
            D[i, j] = min_cost + C[i, j]
            
            ptr = {(i-1, j): 3, (i, j-1): 1, (i-1, j-1): 2}
            B[i, j] = ptr[min_indices]
            
    return D, B

# Return a path from the backtraing matrix B. 
# Return this as an np.array that is an Lx2 matrix (where L is the length of the path)
def find_path(B) :
    n = B.shape[0]
    m = B.shape[1]
    current = (n-1, m-1)
    path = [current]
    goal = (0, 0)
    while current != goal:
        ptr = B[current[0], current[1]]

        # TODO(smritip): without if: just apply -1, 0, -1, etc

        if ptr == 1:  # go left
            next_pt = (current[0], current[1] - 1)    
        elif ptr == 2:  # go diagonal
            next_pt = (current[0] - 1, current[1] - 1)
        elif ptr == 3:  # go down
            next_pt = (current[0] - 1, current[1])
            
        path.append(next_pt)
        current = next_pt
    
    path.reverse()
        
    return path


# DTW for audio matching
# dtw_match_cost calculates warping paths that best match a query to a database by running DTW

STEPS = ((-1, -1), (-1, -2), (-2, -1))

def dtw_match_cost(C):
    N, M = C.shape
    
    # create accumulated cost matrix. Make D larger so that D[:,-1] and D[-1,:] are valid
    # and have inifinite cost. (this is due to STEPS having -2 in their step size)
    D = np.zeros((N + 1, M + 1))
    D[N, :] = 10000000
    D[:, M] = 10000000
    
    # backtracking index matrix - fill with zeros
    B = np.zeros(C.shape, dtype=np.int)

    # Initial values for D:
    D[0, 0] = C[0, 0]
    
    # first column
    for n in range(1, N):
        D[n, 0] = C[n, 0] + D[n - 1, 0]

    # first row - here we do not accumulate costs.
    D[0, 0:M] = C[0, :]

    # compute accumulated cost, and keep track of steps
    for m in range(1, M):
        for n in range(1, N):
            # find minimal cost to reach (n,m). Accumulate into D. Remember step
            costs = (D[n - 1, m - 1], D[n - 1, m - 2], D[n - 2, m - 1])
            best_step  = np.argmin(costs)
            D[n, m] = costs[best_step] + C[n, m]
            B[n, m] = best_step

    # return accumulated cost and backtracking. 
    # Do not return that extra row/column of D.
    return D[:-1, :-1], B

def find_top_n_troughs(x, n, win_hlen):
    troughs = []
    signal = x.copy()
    maximum = np.amax(signal)
    for i in range(n):
        minimum_index = np.argmin(signal)
        troughs.append(minimum_index)
        left = max(minimum_index - win_hlen, 0)
        right = min(minimum_index + win_hlen, len(signal) - 1)
        signal[left : right] = maximum
    return troughs, signal

def get_match_regions(d_dtw, B, num_matches):
    N = B.shape[0]
    end_pts, new_sig = find_top_n_troughs(d_dtw, num_matches, N)
    matches = []
    for pt in end_pts:
        current = (N-1, pt)
        while current[0] >= 0:
            ptr = B[current[0], current[1]]
            step = STEPS[ptr]
            current = (current[0] + step[0], current[1] + step[1])
        ff = fs / hop_size
        start = current[1] / ff
        end = pt / ff
        cost = d_dtw[pt]
        matches.append((start, end))
        
    return matches
