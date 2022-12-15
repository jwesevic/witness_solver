import sys

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

def printPath(lines, rows, cols):      #checks x, s, e variables for correctness
    path = [[0]*(2*cols+1) for i in range(2*rows+1)]   #initialize 2d array of dimensions [2*rows+1][2*cols+1] filled w/ 0s
    for line in lines:
        if line[0]=='x':
            if int(line[-2])==1:
                variantInfo=line.split(" ")[0].split(".")
                if variantInfo[3]=='h':
                    path[2*int(variantInfo[1])][2*int(variantInfo[2])+1]=1
                elif variantInfo[3]=='v':
                    path[2*int(variantInfo[1])+1][2*int(variantInfo[2])]=1
        
        if line[0]=='s':
            if int(line[-2])==1:
                variantInfo=line.split(" ")[0].split(".")
                path[2*int(variantInfo[1])][2*int(variantInfo[2])]=2

        if line[0]=='e':
            if int(line[-2])==1:
                variantInfo=line.split(" ")[0].split(".")
                path[2*int(variantInfo[1])][2*int(variantInfo[2])]=3


    with open("path.txt", 'w') as f:
        for i in range(len(path)):
            for j in range(len(path[0])):
                if path[i][j]==0:
                    f.write(" ")
                elif path[i][j]==1:
                    if i%2==0:
                        f.write("-")
                    else:
                        f.write("|")
                elif path[i][j]==2:
                    f.write('s')
                elif path[i][j]==3:
                    f.write('e')
                
            f.write('\n')


def printPoints(lines, rows, cols):
    points = [[0]*(cols+1) for i in range(rows+1)]   #initialize 2d array of dimensions [rows+1][cols+1] filled w/ 0s
    for line in lines:
        if line[0]=='z':
            if int(line[-2])==1:
                variantInfo=line.split(" ")[0].split(".")
                points[int(variantInfo[1])][int(variantInfo[2])]=1
    
    with open("points.txt", 'w') as f:
        for i in range(len(points)):
            for j in range(len(points[0])):
                if points[i][j]==0:
                    f.write(" ")
                else:
                    f.write("*")  
            f.write('\n')


def printComponents(lines, rows, cols):
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
            if found==0:
                components.append([p])
  
    with open("components.txt","w") as f:
        for i in range(rows):
            for j in range(cols):
                p=[i,j]
                for k in range(len(components)):
                    if p in components[k]:
                        f.write(f"{k:02d} ")     #assuming no more than 99 components
            f.write("\n")


def printAll(lines, rows, cols):
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

    with open("tempSol.txt","w") as sol:
        for row in puzzleSol:
            for character in row:
                sol.write(character)
            sol.write("\n")


def main():
    filename=sys.argv[1]
    lines=getLines(filename)
    rows,cols=getSize(lines)
    # printPath(lines,rows,cols)
    # printPoints(lines, rows, cols)
    # printComponents(lines, rows, cols)
    printAll(lines,rows,cols)
main()