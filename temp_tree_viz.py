from treelib import Tree

tree_Str="root Module body Expr value Call func Attribute value Name id re_fu_nc_na_me ^ ^ ^ ^ attr findall_fu_nc_na_me ^ ^ ^ ^ args Str s -|\\_fu_nc_na_me | | |\\+| ^-+ \\s ^ ^ +' ^ ^ ^ ^ ^ ^ ^ Str s hello-_fu_nc_na_me _ +__there' ^ ^ ^ ^ ^ ^ keywords ^ ^ ^ ^ ^ ^ ^"

tree_str_2="root Module body Assign targets Name id my_words_fu_nc_na_me ^ ^ ^ ^ value Call func Attribute value Attribute value Name id Wiki_fu_nc_na_me ^ ^ ^ ^ attr objects_fu_nc_na_me ^ ^ ^ ^ attr order_by_fu_nc_na_me ^ ^ ^ ^ args Str s word_fu_nc_na_me ^ ^ ^ ^ keywords ^ ^ ^ ^ ^ ^ ^"

tree_str_3="root Module body Expr value Call func Attribute value Call func Attribute value Name id re_fu_nc_na_me ^ ^ ^ ^ attr search_fu_nc_na_me ^ ^ ^ ^ args Str s _fu_nc_na_me http:// ^ ? www\\. ^ ? vimeo\\.com/ ^ ? \\d+ ^ _fu_nc_na_me ^ ^ ^ ^ ^ ^ ^ Name id embed_url_fu_nc_na_me ^ ^ ^ ^ keywords ^ ^ ^ attr group_fu_nc_na_me ^ ^ ^ ^ args Num 4_fu_nc_na_me ^ ^ ^ keywords ^ ^ ^ ^ ^ ^ ^"


tree_str_4="root Module body Expr value Call func Name id print_fu_nc_na_me ^ ^ ^ ^ args Call func Name id list_fu_nc_na_me ^ ^ ^ ^ args Call func Name id map_fu_nc_na_me ^ ^ ^ ^ args Lambda args arg arg args_fu_nc_na_me ^ ^ annotation None ^ ^ ^ kwonlyargs ^ kw_ ^ body Call func Name id int_fu_nc_na_me ^ ^ ^ ^ args Subscript value Name id args_fu_nc_na_me ^ ^ ^ ^ slice Index value Num 1_fu_nc_na_me ^ ^ ^ ^ ^ ^ ^ keywords ^ ^ ^ ^ Call func Name id list_fu_nc_na_me ^ ^ ^ ^ args Call func Attribute value Name id ss_fu_nc_na_me ^ ^ ^ ^ attr items_fu_nc_na_me ^ ^ ^ ^ args ^ keywords ^ ^ ^ keywords ^ ^ ^ keywords ^ ^ ^ keywords ^ ^ ^ keywords ^ ^ ^ ^ ^ ^ ^"

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
        tree.show()
        return tree
    except KeyError:
        return 0

generate_tree_from_str(tree_str_4)

