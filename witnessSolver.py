import subprocess
import json
import sys

def readdata(filename):
    with open(filename) as f:
        data=json.load(f)
    return data

#ideally, this would all be refactored to work in terms of neighbor sets, that is, each point would have an associated set of edges which touch it
def createLP(data,filename):
    # name=filename.split(".")[-2]  #assuming no funny buisness with multiple file extensions like abc.py.txt
    # print(filename)
    # print("\n")
    # print(name)
    rows=data["size"][0]
    cols=data["size"][1]
    with open(f"puzzle.lp","w") as lp:
        lp.write("Minimize\n")

        #write ALL edge variants
        for i in range(rows):
            for j in range(cols):
                lp.write(f"\t+ x.{i}.{j}.h + x.{i}.{j}.v\n")
        for i in range(rows):
            lp.write(f"\t+ x.{i}.{cols}.v\n")
        for j in range(cols):
            lp.write(f"\t+ x.{rows}.{j}.h\n")

        lp.write("\nSubject To\n")

        #z_(p,dir) definition constraints
        lp.write("\t\\corner point exclusion\n")
        lp.write(f"\tx.0.0.h + x.0.0.v - z.0.0 >= 0\n")
        lp.write(f"\tx.0.{cols-1}.h + x.0.{cols}.v - z.0.{cols} >= 0\n")
        lp.write(f"\tx.{rows}.0.h + x.{rows-1}.0.v - z.{rows}.0 >= 0\n")
        lp.write(f"\tx.{rows}.{cols-1}.h + x.{rows-1}.{cols}.v - z.{rows}.{cols} >= 0\n")

        lp.write("\n\t\\corner point selection\n")
        lp.write(f"\tx.0.0.h - z.0.0 <= 0\n\tx.0.0.v - z.0.0 <= 0\n")
        lp.write(f"\tx.0.{cols-1}.h - z.0.{cols} <= 0\n\tx.0.{cols}.v - z.0.{cols} <= 0\n")
        lp.write(f"\tx.{rows}.0.h - z.{rows}.0 <= 0\n\tx.{rows-1}.0.v - z.{rows}.0 <= 0\n")
        lp.write(f"\tx.{rows}.{cols-1}.h - z.{rows}.{cols} <= 0\n\tx.{rows-1}.{cols}.v - z.{rows}.{cols} <= 0\n")

        lp.write("\n\t\\edge point exclusion\n")
        for i in range(1,rows):
            lp.write(f"\tx.{i-1}.0.v + x.{i}.0.v + x.{i}.0.h - z.{i}.0 >= 0\n")
            lp.write(f"\tx.{i-1}.{cols}.v + x.{i}.{cols}.v + x.{i}.{cols-1}.h - z.{i}.{cols} >= 0\n")

        for j in range(1,cols):
            lp.write(f"\tx.0.{j-1}.h + x.0.{j}.h + x.0.{j}.v - z.0.{j} >= 0\n")
            lp.write(f"\tx.{rows}.{j-1}.h + x.{rows}.{j}.h + x.{rows-1}.{j}.v - z.{rows}.{j} >= 0\n")
        
        lp.write("\n\t\\edge point selection\n")
        for i in range(1,rows):
            lp.write(f"\tx.{i-1}.0.v - z.{i}.0 <= 0\n")
            lp.write(f"\tx.{i}.0.v - z.{i}.0 <= 0\n")
            lp.write(f"\tx.{i}.0.h - z.{i}.0 <= 0\n")

            lp.write(f"\tx.{i-1}.{cols}.v - z.{i}.{cols} <= 0\n")
            lp.write(f"\tx.{i}.{cols}.v - z.{i}.{cols} <= 0\n")
            lp.write(f"\tx.{i}.{cols-1}.h - z.{i}.{cols} <= 0\n")
        
        lp.write("\n")
        
        for j in range(1,cols):
            lp.write(f"\tx.0.{j-1}.h - z.0.{j} <= 0\n")
            lp.write(f"\tx.0.{j}.h - z.0.{j} <= 0\n")
            lp.write(f"\tx.0.{j}.v - z.0.{j} <= 0\n")

            lp.write(f"\tx.{rows}.{j-1}.h - z.{rows}.{j} <= 0\n")
            lp.write(f"\tx.{rows}.{j}.h - z.{rows}.{j} <= 0\n")
            lp.write(f"\tx.{rows-1}.{j}.v - z.{rows}.{j} <= 0\n")

        lp.write("\n\t\\interior point exclusion\n")
        for i in range(1,rows):
            for j in range(1,cols):
                lp.write(f"\tx.{i}.{j-1}.h + x.{i-1}.{j}.v + x.{i}.{j}.h + x.{i}.{j}.v - z.{i}.{j} >= 0 \n")

        lp.write("\n\t\\interior point selection\n")
        for i in range(1,rows):
            for j in range(1,cols):
                lp.write(f"\tx.{i}.{j-1}.h - z.{i}.{j} <= 0\n")
                lp.write(f"\tx.{i-1}.{j}.v - z.{i}.{j} <= 0\n")
                lp.write(f"\tx.{i}.{j}.h - z.{i}.{j} <= 0\n")
                lp.write(f"\tx.{i}.{j}.v - z.{i}.{j} <= 0\n")

        #s_p and e_p constraints  (s_p and e_p only defined for points in set of starts and set of ends respectively)
        lp.write("\n\t\\start point selection\n\t")
        for point in data["starts"]:
            lp.write(f"+ s.{point[0]}.{point[1]} ")
        lp.write("= 1\n")

        lp.write("\n\t\\end point selection\n\t")
        for point in data["ends"]:
            lp.write(f"+ e.{point[0]}.{point[1]} ")
        lp.write("= 1\n")

        lp.write("\n\t\\start point exclusion\n\t")
        for i in range(rows+1):
            for j in range(cols+1):
                if [i,j] not in data["starts"]:         # no point can be both a start and an end, so there will always be at least one element here -> we'll never have an invalid constraint here (assuming proper puzzle)
                    lp.write(f"+ s.{i}.{j} ")
        lp.write("= 0\n")

        lp.write("\n\t\\end point exclusion\n\t")
        for i in range(rows+1):
            for j in range(cols+1):
                if [i,j] not in data["ends"]:
                    lp.write(f"+ e.{i}.{j} ")
        lp.write("= 0\n")


        #degree constraints
        lp.write("\n\t\\corner point degree constraints\n")
        lp.write(f"\tx.0.0.h + x.0.0.v + s.0.0 + e.0.0 - 2 z.0.0 = 0\n")
        lp.write(f"\tx.0.{cols-1}.h + x.0.{cols}.v + s.0.{cols} + e.0.{cols} - 2 z.0.{cols} = 0\n")
        lp.write(f"\tx.{rows}.0.h + x.{rows-1}.0.v + s.{rows}.0 + e.{rows}.0 - 2 z.{rows}.0 = 0\n")
        lp.write(f"\tx.{rows}.{cols-1}.h + x.{rows-1}.{cols}.v + s.{rows}.{cols} + e.{rows}.{cols} - 2 z.{rows}.{cols} = 0\n")

        
        lp.write("\n\t\\edge point degree constraints\n")
        for i in range(1,rows):
            lp.write(f"\tx.{i-1}.0.v + x.{i}.0.v + x.{i}.0.h + s.{i}.0 + e.{i}.0 - 2 z.{i}.0 = 0\n")
            lp.write(f"\tx.{i-1}.{cols}.v + x.{i}.{cols}.v + x.{i}.{cols-1}.h + s.{i}.{cols} + e.{i}.{cols} - 2 z.{i}.{cols} = 0\n")

        for j in range(1,cols):
            lp.write(f"\tx.0.{j-1}.h + x.0.{j}.h + x.0.{j}.v + s.0.{j} + e.0.{j} - 2 z.0.{j} = 0\n")
            lp.write(f"\tx.{rows}.{j-1}.h + x.{rows}.{j}.h + x.{rows-1}.{j}.v + s.{rows}.{j} + e.{rows}.{j} - 2 z.{rows}.{j} = 0\n")


        lp.write("\n\t\\interior point degree constraints\n")
        for i in range(1,rows):
            for j in range(1,cols):
                lp.write(f"\tx.{i}.{j-1}.h + x.{i-1}.{j}.v + x.{i}.{j}.h + x.{i}.{j}.v + s.{i}.{j} + e.{i}.{j} - 2 z.{i}.{j} = 0\n")

        lp.write("\n\t\\column tile adjacency\n")
        for i in range(rows-1):
            for j in range(cols):
                lp.write(f"\ty.{i}.{j}.{i+1}.{j} + x.{i+1}.{j}.h >= 1\n")

        lp.write("\n\t\\row tile adjacency\n")
        for i in range(rows):
            for j in range(cols-1):
                lp.write(f"\ty.{i}.{j}.{i}.{j+1} + x.{i}.{j+1}.v >= 1\n")

        lp.write("\n\t\\transitivity of connectedness\n")
        for i in range(rows):
            for j in range(cols):
                for l in range(j+1,cols):               #parse to end of current row
                    if i-1>=0:
                        lp.write(f"\t+ y.{i}.{j}.{i}.{l} + y.{i}.{j}.{i-1}.{l} - y.{i}.{l}.{i-1}.{l} <= 1\n")
                        lp.write(f"\t+ y.{i}.{j}.{i}.{l} - y.{i}.{j}.{i-1}.{l} + y.{i}.{l}.{i-1}.{l} <= 1\n")
                        lp.write(f"\t- y.{i}.{j}.{i}.{l} + y.{i}.{j}.{i-1}.{l} + y.{i}.{l}.{i-1}.{l} <= 1\n\n")
                    if l-1>=0:
                        lp.write(f"\t+ y.{i}.{j}.{i}.{l} + y.{i}.{j}.{i}.{l-1} - y.{i}.{l}.{i}.{l-1} <= 1\n")
                        lp.write(f"\t+ y.{i}.{j}.{i}.{l} - y.{i}.{j}.{i}.{l-1} + y.{i}.{l}.{i}.{l-1} <= 1\n")
                        lp.write(f"\t- y.{i}.{j}.{i}.{l} + y.{i}.{j}.{i}.{l-1} + y.{i}.{l}.{i}.{l-1} <= 1\n\n")
                    if i+1<rows:
                        lp.write(f"\t+ y.{i}.{j}.{i}.{l} + y.{i}.{j}.{i+1}.{l} - y.{i}.{l}.{i+1}.{l} <= 1\n")
                        lp.write(f"\t+ y.{i}.{j}.{i}.{l} - y.{i}.{j}.{i+1}.{l} + y.{i}.{l}.{i+1}.{l} <= 1\n")
                        lp.write(f"\t- y.{i}.{j}.{i}.{l} + y.{i}.{j}.{i+1}.{l} + y.{i}.{l}.{i+1}.{l} <= 1\n\n")
                    if l+1<cols:
                        lp.write(f"\t+ y.{i}.{j}.{i}.{l} + y.{i}.{j}.{i}.{l+1} - y.{i}.{l}.{i}.{l+1} <= 1\n")
                        lp.write(f"\t+ y.{i}.{j}.{i}.{l} - y.{i}.{j}.{i}.{l+1} + y.{i}.{l}.{i}.{l+1} <= 1\n")
                        lp.write(f"\t- y.{i}.{j}.{i}.{l} + y.{i}.{j}.{i}.{l+1} + y.{i}.{l}.{i}.{l+1} <= 1\n\n")

                for k in range(i+1,rows):               #parse all columns starting w next row
                    for l in range(cols):
                        if k-1>=0:
                            lp.write(f"\t+ y.{i}.{j}.{k}.{l} + y.{i}.{j}.{k-1}.{l} - y.{k}.{l}.{k-1}.{l} <= 1\n")
                            lp.write(f"\t+ y.{i}.{j}.{k}.{l} - y.{i}.{j}.{k-1}.{l} + y.{k}.{l}.{k-1}.{l} <= 1\n")
                            lp.write(f"\t- y.{i}.{j}.{k}.{l} + y.{i}.{j}.{k-1}.{l} + y.{k}.{l}.{k-1}.{l} <= 1\n\n")
                        if l-1>=0:
                            lp.write(f"\t+ y.{i}.{j}.{k}.{l} + y.{i}.{j}.{k}.{l-1} - y.{k}.{l}.{k}.{l-1} <= 1\n")
                            lp.write(f"\t+ y.{i}.{j}.{k}.{l} - y.{i}.{j}.{k}.{l-1} + y.{k}.{l}.{k}.{l-1} <= 1\n")
                            lp.write(f"\t- y.{i}.{j}.{k}.{l} + y.{i}.{j}.{k}.{l-1} + y.{k}.{l}.{k}.{l-1} <= 1\n\n")
                        if k+1<rows:
                            lp.write(f"\t+ y.{i}.{j}.{k}.{l} + y.{i}.{j}.{k+1}.{l} - y.{k}.{l}.{k+1}.{l} <= 1\n")
                            lp.write(f"\t+ y.{i}.{j}.{k}.{l} - y.{i}.{j}.{k+1}.{l} + y.{k}.{l}.{k+1}.{l} <= 1\n")
                            lp.write(f"\t- y.{i}.{j}.{k}.{l} + y.{i}.{j}.{k+1}.{l} + y.{k}.{l}.{k+1}.{l} <= 1\n\n")
                        if l+1<cols:
                            lp.write(f"\t+ y.{i}.{j}.{k}.{l} + y.{i}.{j}.{k}.{l+1} - y.{k}.{l}.{k}.{l+1} <= 1\n")
                            lp.write(f"\t+ y.{i}.{j}.{k}.{l} - y.{i}.{j}.{k}.{l+1} + y.{k}.{l}.{k}.{l+1} <= 1\n")
                            lp.write(f"\t- y.{i}.{j}.{k}.{l} + y.{i}.{j}.{k}.{l+1} + y.{k}.{l}.{k}.{l+1} <= 1\n\n")
        

        #puzzle constraints!!!

        lp.write(f"\n\t\\corner hexagon constriants\n")
        for hex in data["hexagons"]["corners"]:
            lp.write(f"\t z.{hex[0]}.{hex[1]} = 1\n")

        lp.write(f"\n\t\\edge hexagon constraints\n")
        for hex in data["hexagons"]["hedges"]:
            lp.write(f"\tx.{hex[0]}.{hex[1]}.h = 1\n")
        for hex in data["hexagons"]["vedges"]:
            lp.write(f"\tx.{hex[0]}.{hex[1]}.v = 1\n")

        lp.write(f"\n\t\\break constraints\n")
        for cut in data["breaks"]:
            lp.write(f"\t x.{cut[0]}.{cut[1]}.{cut[2]} = 0\n")

        lp.write(f"\n\t\\triangle constraints\n")
        i=0
        for row in data["grid"]:
            j=0
            for cell in row:
                if cell["component"]=="triangle":
                    lp.write(f"\t x.{i}.{j}.h + x.{i}.{j}.v + x.{i+1}.{j}.h + x.{i}.{j+1}.v = {cell['count']}\n")    
                j+=1
            i+=1


        #stating all variants are binary
        lp.write("\nBinary\n")
        lp.write("\n\t\\vertical edge variables\n\t")
        for i in range(rows):
            for j in range(cols+1):
                lp.write(f"x.{i}.{j}.v ")
        lp.write("\n\n\t\\horizontal edge variables\n\t")
        for i in range(rows+1):
            for j in range(cols):
                lp.write(f"x.{i}.{j}.h ")
        lp.write("\n\n\t\\connectedness variables\n\t")
        for i in range(rows):
            for j in range(cols):
                for l in range(j+1,cols):
                    lp.write(f"y.{i}.{j}.{i}.{l} ")
                for k in range(i+1,rows):
                    for l in range(cols):
                        lp.write(f"y.{i}.{j}.{k}.{l} ")
        lp.write("\n\n\t\\point use variables\n\t")
        for i in range(rows+1):
            for j in range(cols+1):
                lp.write(f"z.{i}.{j} ")

        lp.write("\n\n\t\\start marker variables\n\t")
        for i in range(rows+1):
            for j in range(cols+1):
                lp.write(f"s.{i}.{j} ")

        lp.write("\n\n\t\\end marker variables\n\t")
        for i in range(rows+1):
            for j in range(cols+1):
                lp.write(f"e.{i}.{j} ")

        lp.write("\nEnd")
    return None


def getLines(filename):
    sol=open(filename)
    lines=sol.readlines()
    lines=lines[1:]   #cut off objective value at top
    sol.close()
    return lines

def getSize(lines):
    rows=1
    cols=1
    for line in lines:
        if line[0]=='x':
            variant=line.split(" ")[0]
            variantInfo=variant.split(".")
            if int(variantInfo[1])>rows:
                rows+=1
            if int(variantInfo[2])>cols:
                cols+=1
    return rows, cols



def printAll(lines, rows, cols, outfile):
    puzzleSol = [[" "]*(3*cols+1) for i in range(2*rows+1)]   #initialize 2d array of dimensions [3*rows+1][2*cols+1] filled w/ 0s

    
    components=[]
    
    for line in lines:
        if line[0]=='y':
            if int(line[-2])==1:
                variantInfo=line.split(" ")[0].split(".")
                p=[int(variantInfo[1]),int(variantInfo[2])]
                q=[int(variantInfo[3]),int(variantInfo[4])]
                found=0
                for component in components:
                    if p in component and q not in component:
                        component.append(q)
                        found+=1
                    elif p not in component and q in component:
                        component.append(p)
                        found+=1
                    elif p in component and q in component:
                        found+=1
                if found==0:
                    components.append([p,q])

    for i in range(rows):
        for j in range(cols):
            p=[i,j]
            found=0
            for component in components:
                if p in component:
                    found+=1
            if found>1:
                    print(f"point {p} was found in multiple components. model must be examined.")
                    exit(1)
            if found==0:
                components.append([p])

    for i in range(rows):
            for j in range(cols):
                p=[i,j]
                for k in range(len(components)):
                    if p in components[k]:
                        index=f"{k:02d}"     #assuming no more than 99 components
                        puzzleSol[2*i+1][3*j+1]=index[0]
                        puzzleSol[2*i+1][3*j+2]=index[1]
                        
    for line in lines:
        if line[0]=='z':
            if int(line[-2])==1:
                variantInfo=line.split(" ")[0].split(".")
                puzzleSol[2*int(variantInfo[1])][3*int(variantInfo[2])]="*"
    
    for line in lines:
        if line[0]=='x':
            if int(line[-2])==1:
                variantInfo=line.split(" ")[0].split(".")
                if variantInfo[3]=='v':
                    puzzleSol[2*int(variantInfo[1])+1][3*int(variantInfo[2])]="|"
                elif variantInfo[3]=='h':
                    puzzleSol[2*int(variantInfo[1])][3*int(variantInfo[2])+1]="-"
                    puzzleSol[2*int(variantInfo[1])][3*int(variantInfo[2])+2]="-"
        
        if line[0]=='s':
            if int(line[-2])==1:
                variantInfo=line.split(" ")[0].split(".")
                puzzleSol[2*int(variantInfo[1])][3*int(variantInfo[2])]="s"

        if line[0]=='e':
            if int(line[-2])==1:
                variantInfo=line.split(" ")[0].split(".")
                puzzleSol[2*int(variantInfo[1])][3*int(variantInfo[2])]="e"

    with open(outfile,"w") as sol:
        for row in puzzleSol:
            for character in row:
                sol.write(character)
            sol.write("\n")




def main():
    filename=sys.argv[1]
    try:
        outfile=sys.argv[2]
    except:
        outfile="solution.txt"

    data=readdata(filename)
    createLP(data,filename)
    subprocess.run(["gurobi_cl", "ResultFile=puzzleSolution.sol", "puzzle.lp"])

    lines=getLines("puzzleSolution.sol")
    rows,cols=getSize(lines)

    printAll(lines,rows,cols,outfile)
main()