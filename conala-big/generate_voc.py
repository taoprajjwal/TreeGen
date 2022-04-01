import json

f=open("train_trans.txt","r")
lines=f.readlines()

nl_voc={}
tree_voc={}
char_voc={}

copy_lists={}
"""
def read2file(dic, filename):
    f = open(filename, "w")
    l = []
    for i in dic:
        l.append([dic[i], i])
    l = sorted(l, reverse=True)
    for i in range(len(l)):
        f.write(l[i][1] + " " + str(l[i][0]) + '\n')

"""


def vocab_traverse(tree_json,sani_list):
    for key in tree_json:
        sani_list.append(key)
        for child in tree_json[key].get('children',[]):
            if type(child)==dict:
                vocab_traverse(child,sani_list)
            else:
                sani_list.append(child)

for i,line in enumerate(lines):
    if i % 9 ==0:
        words=line.strip().split()
        for word in words:
            if word[-1]!="^":
                nl_voc[word]=nl_voc.get(word,0)+1

            for char in word:
                char_voc[char]=char_voc.get(char,0)+1

    if i % 9 == 1:
        """
        words=line.strip().split()
        for idx,word in enumerate(words):
            if word[-1]!="^":
                tree_voc[word]=tree_voc.get(word,0)+1

                if word[-12:]=="_fu_nc_na_me" and words[idx-1][-1]!="^":
                    copy_lists[words[idx-1]]=copy_lists.get(words[idx-1],0)+1
        """
        vocab_list=[]
        json_obj=json.loads(line)
        vocab_traverse(json_obj,vocab_list)

        for word in vocab_list:
            tree_voc[word]=tree_voc.get(word,0)+1

f.close()


def read2file(dic,filename):

    f=open(filename,"w")
    list_dic=[v[0] for v in sorted(dic.items(), key=lambda x : x[1], reverse=True)]
    sorted_dic={}
    for i,val in enumerate(list_dic):
        sorted_dic[val]=i

    f.write(str(sorted_dic))
    f.close()


read2file(nl_voc, "nl_voc.txt")
read2file(tree_voc,"tree_voc.txt")
read2file(char_voc,"char_voc.txt")