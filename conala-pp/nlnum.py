f=open("dev_trans.txt","r")
lines=f.readlines()
copylst=[]
count=0
l=[]

for i,line in enumerate(lines):
    if i% 9 == 5:
        count+=1
        l+=[count]*len(line.split())

        rules=line.split()

        for rule in rules:
            if int(rule) > 1000000:
                copylst.append(1)
                print("ruled")
            else:
                copylst.append(0)

f1=open("copylst.txt","w")
f2=open("nlnum.txt","w")
f1.write(str(copylst))
f2.write(str(l))