##INIT Rules
#f=open("Rule.txt", "r")
#lines=f.readlines()
rule_int=0
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    from treelib import Node, Tree

from tqdm import tqdm
import json
func_parent_nodes={}
import ast
from ast import AST
import unicodedata



unprintable_classes={"Cc","Cf","Cs","Co","Cn"}

class Rule_collection:
    def __init__(self):
        self.active_id=0
        self.Rules={}

    def add_rule(self,parent,child):
        parent=parent.strip()
        parent="".join(c for c in parent if unicodedata.category(c) not in unprintable_classes)
        if type(child)==list:
            child=" ".join(child).strip()
        child="".join(c for c in child if unicodedata.category(c) not in unprintable_classes)
        if self.Rules.get(f"{parent} {child}"):
            return self.Rules.get(f"{parent} {child}")
        else:
            rul=Rule(parent,child,self.active_id)
            self.Rules[f"{parent} {child}"]=rul
            self.active_id+=1
            return rul

    def writetofile(self,file_name="Rule.txt"):
        f=open(file_name,"w")
        rules_list_sorted=sorted(self.Rules.values(), key=lambda x: x.ruleno)
        for Rule_obj in rules_list_sorted:
            f.write(str(Rule_obj)+"\n")

class Rule:
    def __init__(self,parent_node,child_nodes,id):

        self.ruleno=id
        self.parent=parent_node

        if type(child_nodes)==list:
            self.child_nodes=child_nodes
        else:
            self.child_nodes=[child_nodes]

    def __str__(self):
        children_list=" ".join(self.child_nodes)
        return f"{self.parent} true {children_list}"


    def __repr__(self):
        return  self.__str__()


def create_node(node):
    children_list=[]
    for children in node._fields:
        if isinstance(getattr(node,children),AST):
            children_list.append(True)
        else:
            if getattr(node,children)==None or getattr(node,children)==[] :
                children_list.append(False)
            else:
                children_list.append(True)

    return children_list

def traverse(node,parent,tree):
    bad_nodes=["ctx","defaults", "decorator_list"]
    if isinstance(node,AST):
        name=node.__class__.__name__
        children_list=create_node(node)
        if len(children_list)==0: # Last node is a non generated object. Valid because its parents have been checked
            tree.create_node(name,parent=parent)
        if any(children_list):
            parent_n=tree.create_node(name,parent=parent)
        for tocreate, children in zip(children_list,node._fields):
            if tocreate and children not in bad_nodes:
                parent_c=tree.create_node(children,parent=parent_n)
                try:
                    value=getattr(node,children)
                    traverse(value,parent_c,tree)
                except AttributeError:
                    print("exception reached")
                    print(node,children)
                    exit()
    elif isinstance(node,list):
        for val in node:
            traverse(val,parent,tree)
    else:
        tree.create_node(f"{node}_fu_nc_na_me",parent=parent)

def generate_tree_from_code(code_str):
    if code_str:
        try:
            module=ast.parse(code_str)
        except SyntaxError:
            return None

        tree=Tree()
        root=tree.create_node("root")
        traverse(module,root,tree)
        #tree.show()
        return tree

def generate_tree_from_str(ast_str):
    try:
        tree=Tree()
        asts_split=ast_str.strip().split()
        depth=0
        tree.create_node(asts_split[0],-1)
        depth_dict={}
        depth_dict[0]=-1
        for j,token in enumerate(asts_split[1:]):
            if token[-1]=="^":
                depth-=1
            else:
                tree.create_node(token,j,parent=depth_dict[depth])
                depth+=1
                depth_dict[depth]=j

                if token[-12:]=="_fu_nc_na_me":
                    parent_name=tree.get_node(depth_dict[depth-1]).tag
                    if parent_name[-12:]=="_fu_nc_na_me":
                        print(parent_name)
                        print(token)
                        print(ast_str)
                        tree.show()

                    func_parent_nodes[parent_name]=func_parent_nodes.get(parent_name,0)+1
        #tree.show()
        return tree
    except KeyError:
        return 0


def delete_func_string(word):
    return word[:-12]

rules_collection=Rule_collection()

def get_tree_path(tree :Tree,node,tree_path,tree_path_str):
    if type(node)==int or type(node)==str:
        node=tree.get_node(node)


    if not ("_fu_nc_na_me" in node.tag or "node_gen" in node.tag):
        tree_path.append(node.tag)
        tree_path_str.append(" ".join(tree_path[::-1])+"\n")
        for children in tree.children(node.identifier):
            get_tree_path(tree,children,tree_path,tree_path_str)
        tree_path.pop()
        return tree_path_str
    else:
        return tree_path_str

def find_parent_rule(rules_list,tree,grandchild):

    child=tree.parent(grandchild.identifier)
    parent=tree.parent(child.identifier)
    for i,rule in enumerate(rules_list[::-1]):

        if type(rule)!=int:
            if rule.parent==parent.tag and child.tag in rule.child_nodes[0]:
                return len(rules_list)-i-1
    return -1

def create_rules(nl_snippet,tree,rules_collection : Rule_collection):

    rules_list=[]
    marked_nodes=[]
    adjacency_matrix=[-1]
    nodes=tree.all_nodes()

    for node in nodes:
        try:
            if (tree.depth(node)>1) and (node not in marked_nodes):
                adjacency_matrix.append(find_parent_rule(rules_list,tree,node))
                marked_nodes+=tree.children(tree.parent(node.identifier).identifier)
        except:
            raise

        children=tree.children(node.identifier)
        if children:
            if len(children)>1:
                rules_list.append(rules_collection.add_rule(node.tag,[x.tag for x in children]))
            else:
                children=children[0]
                if "fu_nc_na_me" in children.tag:
                    var_name=delete_func_string(children.tag)
                    nl_tokens=nl_snippet.strip().split()

                    found=False
                    for i,nl in enumerate(nl_tokens):
                        if var_name.lower()==nl.lower():
                            rules_list.append(1000000+i) ## first word in the nl token in encdoded as 10001
                            found=True
                            break

                    if not found:
                        rules_list.append(rules_collection.add_rule(node.tag,children.tag))

                else:
                    rules_list.append(rules_collection.add_rule(node.tag,children.tag))

    if len(rules_list)!=len(adjacency_matrix):
        print("Not equal")
        exit()

    for i, j in enumerate(adjacency_matrix):
        if i==j:
            return [],[]

    return rules_list, adjacency_matrix

def train_input():
    f=open("train_trans.txt","w")
    tree_f=open("train_tree.txt","w")

    #json_obj=json.load(open("train_our_input.json","r",encoding="utf-8"))

    #train_file=open("conala-mined.jsonl","r",encoding="utf-8")

    #for i,line in enumerate(tqdm(train_file)):
        #code_dict=json.loads(line)
    json_obj=json.load(open('conala-train.json',"r",encoding="utf-8"))

    for code_dict in tqdm(json_obj[200:]):
        nl=code_dict["intent"]
        snippet=code_dict["snippet"]
        #print(snippet)

        tree=generate_tree_from_code(snippet)

        if tree:
            ast=tree.to_json()
            tree_query=get_tree_path(tree,tree.root,[],[])
            rules_list,adjacency_mat=create_rules(nl,tree,rules_collection)

            if rules_list:
                f.write(nl+"\n")
                f.write(ast+"\n")

                #Pa nodes
                f.write(" "+"\n")
                #Grandpa nodes
                f.write(" "+"\n")

                j=-1
                while True:
                    if tree_query[j]:
                        f.write(tree_query[j])
                        break
                    else:
                        j-=1

                for query in tree_query:
                    tree_f.write(query)

                rules_no_list=[]
                for x in rules_list:
                    if type(x)==int:
                        rules_no_list.append(x)
                    else:
                        rules_no_list.append(x.ruleno)

                f.write(" ".join([str(x+1) for x in rules_no_list])+"\n")
                f.write(" ".join([str(x) for x in rules_no_list])+"\n")
                f.write("Not used \n")
                f.write(" ".join([str(x) for x in adjacency_mat])+"\n")

                leaves=tree.leaves()
                for i in leaves:
                    papa_node=tree.get_node(i.bpointer).tag
                    func_parent_nodes[papa_node]=func_parent_nodes.get(papa_node,0)+1


def test_input():
    f=open("test_trans.txt","w")
    tree_f=open("test_tree.txt","w")

    json_obj=json.load(open("conala-test.json","r",encoding="utf-8"))


    for code_dict in tqdm(json_obj) :
        nl=code_dict["intent"]
        snippet=code_dict["snippet"]

        tree=generate_tree_from_code(snippet)
        ast=tree.to_json()

        f.write(nl+"\n")
        f.write(ast+"\n")


        #Pa nodes
        f.write(" "+"\n")

        #Grandpa nodes
        f.write(" "+"\n")

        tree_query=get_tree_path(tree,tree.root,[],[])
        rules_list,adjacency_mat=create_rules(nl,tree,rules_collection)

        j=-1
        while True:
            if tree_query[j]:
                f.write(tree_query[j])
                break
            else:
                j-=1

        for query in tree_query:
            tree_f.write(query)

        rules_no_list=[]
        for x in rules_list:
            if type(x)==int:
                rules_no_list.append(x)
            else:
                rules_no_list.append(x.ruleno)

        f.write(" ".join([str(x+1) for x in rules_no_list])+"\n")
        f.write(" ".join([str(x) for x in rules_no_list])+"\n")
        f.write("Not used \n")
        f.write(" ".join([str(x) for x in adjacency_mat])+"\n")

def dev_input():
    f=open("dev_trans.txt","w")
    tree_f=open("dev_tree.txt","w")

    json_obj=json.load(open('conala-train.json',"r",encoding="utf-8"))

    for code_dict in tqdm(json_obj[:200]):
        nl=code_dict["intent"]
        snippet=code_dict["snippet"]
        f.write(nl+"\n")
        tree=generate_tree_from_code(snippet)
        ast=tree.to_json()
        f.write(ast+"\n")

        #Pa nodes
        f.write(" "+"\n")
        #Grandpa nodes
        f.write(" " +"\n")

        tree_query=get_tree_path(tree,tree.root,[],[])
        rules_list,adjacency_mat=create_rules(nl,tree,rules_collection)

        j=-1
        while True:
            if tree_query[j]:
                f.write(tree_query[j])
                break
            else:
                j-=1

        for query in tree_query:
            tree_f.write(query)

        rules_no_list=[]
        for x in rules_list:
            if type(x)==int:
                rules_no_list.append(x)
            else:
                rules_no_list.append(x.ruleno)

        f.write(" ".join([str(x+1) for x in rules_no_list])+"\n")
        f.write(" ".join([str(x) for x in rules_no_list])+"\n")
        f.write("Not used \n")
        f.write(" ".join([str(x) for x in adjacency_mat])+"\n")

train_input()
test_input()
dev_input()
rules_collection.writetofile()

print(func_parent_nodes)
"""
ast_str="root Module body Expr value Call func Attribute value Call func Attribute value Name id Image_fu_nc_na_me ^ ^ ^ ^ attr open_fu_nc_na_me ^ ^ ^ ^ args Str s pathToFile_fu_nc_na_me ^ ^ ^ ^ keywords ^ ^ ^ attr show_fu_nc_na_me ^ ^ ^ ^ args ^ keywords ^ ^ ^ ^ ^ ^ ^"
NL_snippet="How to display a jpg file in Python?"

tree=generate_tree_from_str(ast_str)
rules,adj=create_rules(ast_str,NL_snippet,tree,rules_collection)
print(rules)

for i,line in enumerate(lines):
    print(i)
    line.split("true")
    rules_children=rules_header.get(line[0],{})
    for word in line[1].split():
        rules_children[word]=i

    rules_header[line[0]]=rules_children

def get_rule_number(parent,child):
    try:
        rules_children=rules_header[parent]
        return rules_children[child]
    except KeyError:
        print(f"Key Error in finding rule:{parent}---{child}")
        return -1


train_len=1000
train_list=[]
write_file=open("train_trans.txt","w")
for i in range(1,train_len):

    nl_f=open(f"train_input/{i}.txt","r")
    nl=nl_f.readline()
    print(nl)
    bfs_f=open(f"train_output_our_ast_bfs/{i}",'r',encoding="utf-8")
    bfs_str=bfs_f.readlines()
    index= len(bfs_str) -10
    asts=bfs_str[index]

    asts_split=asts.strip().split()



    pa_nodes=bfs_str[index+1]
    granpa_nodes=bfs_str[index+2]
    reverse_nodes=bfs_str[index+5]

    rules=bfs_str[index+6]
    rules_split=rules.strip().split()
    new_rules=[]
    active_node=0
    for rule in rules:

        if rule==-1:

        else:
            while True:
                if asts_split[active_node][-1]=="^":
                    active_node+=1
                else:
                    active_node+=1
                    break

            new_rules.append(rule)


    write_file.writelines([nl,index,pa_nodes,granpa_nodes,])

print(get_rule_number("id" ,"subprocess_fu_nc_na_me"))
"""
