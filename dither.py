from PIL import Image
import sys
import random

color_data = '''252 4 21
191 6 20
251 241 209
178 137 90
247 255 0
251 195 13
7 255 6
9 199 7
8 255 243
11 9 249
191 108 255
149 5 195
250 193 253
191 4 152
192 190 192
0 0 0
255 255 255'''

palette = map(lambda x: tuple(map(int, x.split(' '))), color_data.split('\n'))

def closest_palette_color(in_color):
	return palette[closest_palette_index(in_color)]

def closest_palette_index((r,g,b)):
	# larger than any real distance^2
	min_square_dist = float('inf')
	index = None
	for i,(r2,g2,b2) in enumerate(palette):
		dr = r - r2
		dg = g - g2
		db = b - b2
		square_dist = dr*dr + dg*dg + db*db
		if square_dist < min_square_dist:
			min_square_dist = square_dist
			index = i
	
	return index

def add_to_pixel(pixels, (x,y), scale, values):
	if y < 0 or y >= len(pixels): return
	if x < 0 or x >= len(pixels[0]): return

	r,g,b = pixels[y][x]
	r += scale * values[0]
	g += scale * values[1]
	b += scale * values[2]
	pixels[y][x] = (r,g,b)

def dither(pixels, image):
	max_dist = 128
	for y in xrange(len(pixels)):
		for x in xrange(len(pixels[0])):
			old_pixel = pixels[y][x]
			og_pixel = image.getpixel((x,y))[:3]
			
			diffs = tuple(a-b for a,b in zip(old_pixel,og_pixel))
			dist = sum(d*d for d in diffs) ** 0.5
			if dist > max_dist:
				old_pixel = tuple(a+d*max_dist/dist for (a,d) in zip(og_pixel, diffs))
			
			new_pixel = closest_palette_color(old_pixel)
			pixels[y][x] = new_pixel
			quant_error = tuple(a-b for a,b in zip(old_pixel, new_pixel))
			add_to_pixel(pixels, (x+1,y  ), 7.0/16.0, quant_error)
			add_to_pixel(pixels, (x-1,y+1), 3.0/16.0, quant_error)
			add_to_pixel(pixels, (x  ,y+1), 5.0/16.0, quant_error)
			add_to_pixel(pixels, (x+1,y+1), 1.0/16.0, quant_error)
	
def map_to_nearest(pixels):
	for y in xrange(len(pixels)):
		for x in xrange(len(pixels[0])):
			pixels[y][x] = closest_palette_color(pixels[y][x])
	return pixels

def load_palette_indices(filename):
	image = Image.open(filename)
	pixels = [[image.getpixel((x,y))[:3] for x in xrange(image.width)] for y in xrange(image.height)]
	dither(pixels, image)
	#map_to_nearest(pixels)
	image_palette_indices = [[0 for x in xrange(image.width)] for y in xrange(image.height)]
	
	for y in xrange(image.height):
		for x in xrange(image.width):
			image_palette_indices[y][x] = closest_palette_index(pixels[y][x])
			image.putpixel((x,y), tuple(int(v) for v in pixels[y][x]))
	
	parts = filename.split('.')
	extension = parts[-1]
	name = ''.join(parts[:-1])
	
	image.save(name + '_dithered.' + extension, 'png')
	
	return image_palette_indices
	