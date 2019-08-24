import sys
import math
import random

import dither


if len(sys.argv) != 2:
	print 'usage: encode.py my_image.png'
	sys.exit(0)

print 'dithering...'
palette_indices = dither.load_palette_indices(sys.argv[1])
# uncomment for random image
#palette_indices = [[random.randint(0,16) for x in xrange(320)] for y in xrange(180)]

height = len(palette_indices)
width = 0 if height == 0 else len(palette_indices[0])

if width > 320 or height > 180:
	print 'Image must be 320x180 (yours is %d x %d)' % (image.width, image.height)
	sys.exit(0)

def color_diff(a,b):
	right_dist = b - a
	if right_dist < 0: right_dist += 17
	left_dist = 17 - right_dist
	if right_dist < left_dist:
		return right_dist
	else:
		return -left_dist

big_stroke_shape = [
	[0,0,1,1,1,1,0,0],
	[0,1,1,1,1,1,1,0],
	[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1],
	[0,1,1,1,1,1,1,0],
	[0,0,1,1,1,1,0,0],
]

def big_stroke_movement(width, height):
	min_x = -2
	max_x = width - 6
	max_y = height - 5

	cursor_x = -3
	cursor_y = -3
	for _ in xrange(3):
		cursor_y += 1
		yield ('D',cursor_x,cursor_y)
	
	while True:
		while cursor_x < max_x:
			cursor_x += 1
			yield ('R',cursor_x,cursor_y)
		
		if cursor_y + len(big_stroke_shape) >= height:
			break
		
		for _ in xrange(len(big_stroke_shape)):
			if cursor_y == max_y: break
			cursor_y += 1
			yield ('D',cursor_x,cursor_y)
		
		while cursor_x > min_x:
			cursor_x -= 1
			yield ('L',cursor_x,cursor_y)
			
		if cursor_y + len(big_stroke_shape) >= height:
			break
		
		for _ in xrange(len(big_stroke_shape)):
			if cursor_y == max_y: break
			cursor_y += 1
			yield ('D',cursor_x,cursor_y)
	

def big_stroke_presses(cur_image, target_image):
	height = len(target_image)
	width = len(target_image[0])
	
	affected_indices = [[None for x in xrange(width)] for y in xrange(height)]
	
	movement = list(big_stroke_movement(width, height))
	
	for index,(press, cursor_x, cursor_y) in enumerate(movement):
		for dy in xrange(len(big_stroke_shape)):
			for dx in xrange(len(big_stroke_shape[dy])):
				if not big_stroke_shape[dy][dx]: continue
				x = cursor_x + dx
				y = cursor_y + dy
				if x < 0 or x >= width or y < 0 or y >= height: continue
				affected_indices[y][x] = index
	
	affected_positions = [[] for index in xrange(len(movement))]
	
	for y in xrange(height):
		for x in xrange(width):
			affected_positions[affected_indices[y][x]].append((x,y))
	
	wrong_pixel_cost = 3
	change_color_cost = 1
	
	costs_by_index = []
	prev_costs = [(9999,16) for color in xrange(17)]
	prev_costs[15] = (0,16)
	
	for index,(press, cursor_x, cursor_y) in enumerate(movement):
		new_costs = []
		
		for new_color in xrange(17):
			min_cost = None
			min_old_color = None
			color_cost = 0
			for (pixel_x,pixel_y) in affected_positions[index]:
				if target_image[pixel_y][pixel_x] != new_color:
					color_cost += wrong_pixel_cost
			
			for old_color in xrange(17):
				cost = prev_costs[old_color][0] + color_cost + abs(color_diff(old_color,new_color))
				if min_cost == None or cost < min_cost:
					min_cost = cost
					min_old_color = old_color
			new_costs.append((min_cost,min_old_color))
		
		costs_by_index.append(new_costs)
		prev_costs = new_costs
	
	#print costs_by_index
	
	colors = [None for _ in xrange(len(movement))]
	
	cur_color = min(xrange(17), key=lambda color: prev_costs[color][0])
	
	for i in xrange(len(movement)-1, -1, -1):
		colors[i] = cur_color
		cur_color = costs_by_index[i][cur_color][1]
	
	#print colors
	
	cur_color = 15
	
	presses = []
	
	for _ in xrange(3):
		presses.append('}')
		presses.append('.')
	
	presses.append('+')
	
	for i in xrange(len(movement)):
		presses.append(movement[i][0])
		presses.append('.')
		d = color_diff(cur_color,colors[i])
		cur_color = colors[i]
		if d >= 0:
			for _ in xrange(d):
				presses.append('>')
				presses.append('.')
		else:
			for _ in xrange(-d):
				presses.append('<')
				presses.append('.')
		
		for (affected_x,affected_y) in affected_positions[i]:
			cur_image[affected_y][affected_x] = cur_color
	
	presses.append('+')
	presses.append('.')
	
	for _ in xrange(3):
		presses.append('{')
		presses.append('.')
	
	cursor_state = (width-2,height-1,cur_color)
	
	return presses,cursor_state
	

def cell_presses(cur_image, target_image, cursor_state):
	presses = []
	cursor_x,cursor_y,cursor_color = cursor_state
	
	cell_height = 20
	cell_width = 20
	
	is_right = False
	for y0 in range(0, len(target_image), cell_height)[::-1]:
		x_range = range(0, len(target_image[0]), cell_width)
		if not is_right:
			x_range = x_range[::-1]
		is_right = not is_right
		for x0 in x_range:
			while True:
				next_x = None
				next_y = None
				next_dist = None
				for dy in xrange(cell_height):
					for dx in xrange(cell_width):
						x = x0 + dx
						y = y0 + dy
						color = target_image[y][x]
						if color == cur_image[y][x]: continue
						
						color_dist = abs(color_diff(cursor_color, color))
						x_dist = abs(x - cursor_x)
						y_dist = abs(y - cursor_y)
						
						dist = max(color_dist, x_dist + y_dist)
						if next_dist == None or dist < next_dist:
							next_dist = dist
							next_x = x
							next_y = y
				if next_dist == None: break
				
				next_color = target_image[next_y][next_x]
				
				is_color_right = color_diff(cursor_color, next_color) > 0
				
				while cursor_x != next_x or cursor_y != next_y or cursor_color != next_color:
					new_presses = []
				
					if next_y < cursor_y:
						new_presses.append('U')
						cursor_y -= 1
					elif next_y > cursor_y:
						new_presses.append('D')
						cursor_y += 1
					elif next_x < cursor_x:
						new_presses.append('L')
						cursor_x -= 1
					elif next_x > cursor_x:
						new_presses.append('R')
						cursor_x += 1
					
					if cursor_color != next_color:
						if is_color_right:
							new_presses.append('>')
							cursor_color = (cursor_color + 1) % 17
						else:
							new_presses.append('<')
							cursor_color = (cursor_color + 16) % 17
					
					new_presses.append('.')
					presses.extend(new_presses)				
				
				presses.append('A')
				presses.append('.')
				
				cur_image[cursor_y][cursor_x] = cursor_color
	
	return presses


cur_palette_indices = [[16 for x in xrange(width)] for y in xrange(height)]

print 'generating sequence of button presses...'
presses,cursor_state = big_stroke_presses(cur_palette_indices, palette_indices)

#print 'end cursor state:', cursor_state
presses.extend(cell_presses(cur_palette_indices, palette_indices, cursor_state))

presses.append('#')

def huffman_tree(counts):
	nodes = [(x,counts[x]) for x in counts]
	while len(nodes) > 1:
		nodes = sorted(nodes, key=lambda(x,c):c)
		(a_x,a_c),(b_x,b_c) = nodes[:2]
		new_node = ((a_x,b_x), a_c+b_c)
		nodes = nodes[2:] + [new_node]
	return nodes[0][0]

def add_press_encodings(encodings, node, prefix=()):
	if type(node) == tuple:
		add_press_encodings(encodings, node[0], prefix + (0,))
		add_press_encodings(encodings, node[1], prefix + (1,))
	else:
		encodings[node] = prefix

def generate_press_encodings(node):
	encodings = {}
	add_press_encodings(encodings, node)
	return encodings

print 'encoding...'
prefix_length = 5

counts_by_prefix = {}
prefix = ''
for p in presses:
	if not (prefix in counts_by_prefix):
		counts_by_prefix[prefix] = {}
	if not (p in counts_by_prefix[prefix]):
		counts_by_prefix[prefix][p] = 0
	counts_by_prefix[prefix][p] += 1
	prefix = (prefix + p)[-prefix_length:]

trees_by_prefix = {prefix:huffman_tree(counts_by_prefix[prefix]) for prefix in counts_by_prefix}
encodings_by_prefix = {prefix:generate_press_encodings(trees_by_prefix[prefix]) for prefix in trees_by_prefix}

encodings_by_prefix = {}
for prefix in counts_by_prefix:
	encodings_by_prefix[prefix] = generate_press_encodings(huffman_tree(counts_by_prefix[prefix]))

prefix_indices = {prefix:i for i,prefix in enumerate(counts_by_prefix)}

def add_transitions(transitions, prefix, bits, node):
	cur_state = (prefix,bits)
	if not (cur_state in transitions):
		transitions[cur_state] = {}
	if type(node) == tuple:
		transitions[cur_state]['0'] = ((prefix, bits + (0,)), '')
		transitions[cur_state]['1'] = ((prefix, bits + (1,)), '')
		add_transitions(transitions, prefix, bits + (0,), node[0])
		add_transitions(transitions, prefix, bits + (1,), node[1])
	else:
		next_state = ((prefix + node)[-prefix_length:],())
		transitions[cur_state][''] = (next_state, node)

transitions = {}
for prefix in trees_by_prefix:
	add_transitions(transitions, prefix, (), trees_by_prefix[prefix])

transition_mappings = {}

for state in transitions:
	for maybe_bit in transitions[state]:
		next_state,output = transitions[state][maybe_bit]
		while next_state in transitions and '' in transitions[next_state]:
			new_next_state,new_output = transitions[next_state]['']
			next_state = new_next_state
			output += new_output
		transitions[state][maybe_bit] = (next_state, output)	


#The start state will always have an epsilon-transition, since it's unique
start_state = ('', ())
if not ('' in transitions[start_state]):
	print 'Error: start state doesn\'t have epsilon transition???'
	sys.exit(1)

# Change the start state so it needs to take a bit, then prepend a bit to the output.
# Otherwise we'd have to support epsilon-transitions on the Teensy
transitions[start_state]['0'] = transitions[start_state]['']
transitions[start_state]['1'] = transitions[start_state]['']
del transitions[start_state]['']

states_to_remove = [state for state in transitions if '' in transitions[state]]
for state in states_to_remove:
	del transitions[state]

def minimize_transitions_table(table):
	equivalences = set()
	
	for i in xrange(len(table)):
		for j in xrange(len(table)):
			equivalences.add((i, j))

	changed = True
	while changed:
		changed = False
		for state0 in xrange(len(table)):
			for state1 in xrange(len(table)):
				if state0 == state1: continue
				if not (state0,state1) in equivalences: continue
				
				is_different = False
				for bit in xrange(2):
					next0,output0 = table[state0][bit]
					next1,output1 = table[state1][bit]
					
					if output0 != output1 or not (next0,next1) in equivalences:
						is_different = True
						break
				
				if not is_different: continue
				
				equivalences.discard((state0,state1))
				equivalences.discard((state1,state0))
				changed = True
	
	class_count = 0
	classes = {}
	for classless_state in xrange(len(table)):
		new_class = None
		for classed_state in classes:
			if (classless_state,classed_state) in equivalences:
				new_class = classes[classed_state]
				break
		if new_class == None:
			classes[classless_state] = class_count
			class_count += 1
		else:
			classes[classless_state] = new_class
	
	new_table = [None]*class_count
	
	for state in xrange(len(table)):
		if classes[state] in new_table: continue
		
		new_table[classes[state]] = [(classes[next_state],output) for (next_state,output) in table[state]]
	
	return new_table

states = sorted(list(transitions), key=lambda s: 0 if s == start_state else 1)

state_indices = {state:i for i,state in enumerate(states)}

transitions_table = [None]*len(states)

for state_index,state in enumerate(states):
	transitions_table[state_index] = []
	for bit,key in enumerate('01'):
		if key in transitions[state]:
			next_state,output = transitions[state][key]
		else:
			next_state,output = (start_state,'')
		if not next_state in state_indices:
			next_state = start_state
		transitions_table[state_index].append((state_indices[next_state], output))

#for state_index in xrange(len(transitions_table)):
#	print state_index, '-->', transitions_table[state_index]

transitions_table = minimize_transitions_table(transitions_table)

#print '#####'

#for state_index in xrange(len(transitions_table)):
#	print state_index, '-->', transitions_table[state_index]


# Prepend a bit as explained above.
bits = [0]
prefix = ''
for p in presses:
	for b in encodings_by_prefix[prefix][p]:
		bits.append(b)
	prefix = (prefix + p)[-prefix_length:]

while len(bits) % 32: bits.append(0)

ints = []
for i in xrange(0, len(bits), 32):
	x = 0
	for j in xrange(32):
		x = x * 2 + bits[i+j]
	ints.append(x)

# verify output
cur_state = 0
output = []
for bit in bits:
	cur_state,s = transitions_table[cur_state][bit]
	is_terminated = False
	for c in s:
		output.append(c)
		if c == '#':
			is_terminated = True
			break
	if is_terminated:
		break

if ''.join(presses) != ''.join(output):
	print ''.join(presses)[-100:]
	print ''.join(output)[-100:]
	print 'Error: Compression resulted in bad output???'
	sys.exit(1)

#print ''.join(presses[:100])

pause_count = 0
for p in presses:
	if p == '.':
		pause_count += 1
		
print 'Commands:', len(presses)
print 'Button presses:',len(presses) - pause_count
		
duration_ms = pause_count * 35 * 2
duration_s = duration_ms / 1000.0
duration_m = duration_s / 60.0
total_minutes = int(math.ceil(duration_m))
minutes = total_minutes % 60
hours = total_minutes / 60
print 'Expected duration: %dh %02dm' % (hours, minutes)


state_bit_count = 8 if len(transitions_table) < 256 else 16

bit_length = len(bits)
for table_row in transitions_table:
	for (next_state,output) in table_row:
		bit_length += 8 * (len(output) + 1)
		bit_length += state_bit_count

print 'Encoded size:',int(math.ceil(bit_length / 8.0 / 1024.0)), 'KiB'

cpp_file = open('teensy/data.cpp', 'wb')

cpp_file.write('#include <stdint.h>\n')
cpp_file.write('const uint32_t COMMAND_DATA[] = { ')
cpp_file.write(','.join(str(x) + 'L' for x in ints))
cpp_file.write(' };\n');

cpp_file.write('struct TransitionItem { uint' + str(state_bit_count) + '_t next_state; const char *output; };\n')

cpp_file.write('const TransitionItem TRANSITION_TABLE[][2] = {\n')
for table_row in transitions_table:
	cpp_file.write('\t{ ')
	for (next_state,output) in table_row:
		cpp_file.write('{ ' + str(next_state) + ', "' + output + '" }, ')
	cpp_file.write('},\n')
cpp_file.write('};\n')

cpp_file.close()
