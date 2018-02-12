import pygraphviz
import pygraphviz as pgz
import os
# currentst = "ST_1"











def changepartbpng(st):

	if st == 1:
		currentst = "ST_1"
	elif st == 0:
		currentst = "ST_0"
	elif st == -1:
		currentst = "ST_err"
	f = open("partb.dot","r")
	content = f.read()
	f.close()
	c = content.split('\n')
	'''
	line 3 - 5 is the line of ST
	3:ST_0
	4:ST_1
	5:ST_err
	'''
	c[3] = "\tnode[style = filled, shape = doublecircle, color = white]; ST_0;"
	c[4] = "\tnode[style = filled, shape = circle, color = white] ST_1;"
	c[5] = "\tnode[style = filled, shape = circle, color = white] ST_err;"

	if currentst == "ST_0":
		c[3] = "\tnode[style = filled, shape = doublecircle, color = red]; ST_0;"
	elif currentst == "ST_1":
		c[4] = "\tnode[style = filled, shape = circle, color = red]; ST_1;"
	elif currentst == "ST_err":
		c[5] = "\tnode[style = filled, shape = circle, color = red]; ST_err;"
	else:
		pass
	f= open("partb.dot","w")
	f.write("\n".join(c))
	f.close()
	G = pgz.AGraph("partb.dot")
	G.layout(prog= "dot")
	# G.write("file.dot")
	G.draw("partb.ps")
	G.clear()
	os.system("sh ./convert.sh partb.ps partb.png")


def changepartapng(st):
	if st == 1:
		currentst = "ST_1"
	elif st == 0:
		currentst = "ST_0"
	elif st == -1:
		currentst = "ST_err"
	f = open("parta.dot","r")
	content = f.read()
	f.close()
	c = content.split('\n')
	'''
	line 3 - 5 is the line of ST
	3:ST_0
	4:ST_1
	5:ST_err
	'''
	c[3] = "\tnode[style = filled, shape = circle, color = white]; ST_0;"
	c[4] = "\tnode[style = filled, shape = circle, color = white] ST_1;"
	c[5] = "\tnode[style = filled, shape = circle, color = white] ST_err;"

	if currentst == "ST_0":
		c[3] = "\tnode[style = filled, shape = circle, color = red]; ST_0;"
	elif currentst == "ST_1":
		c[4] = "\tnode[style = filled, shape = circle, color = red]; ST_1;"
	elif currentst == "ST_err":
		c[5] = "\tnode[style = filled, shape = circle, color = red]; ST_err;"
	else:
		pass
	f= open("parta.dot","w")
	f.write("\n".join(c))
	f.close()
	G = pgz.AGraph("parta.dot")
	G.layout(prog= "dot")
	# G.write("file.dot")
	G.draw("parta.ps")
	G.clear()
	os.system("sh ./convert.sh parta.ps parta.png")

changepartbpng(0)

changepartapng(0)
