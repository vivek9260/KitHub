import json
import os
import yaml
import argparse
import javalang


def process_file(filepath):
    """
    Process the code file and extract the parsed tree and tokens
    :return the parsed tree, tokens, lines and comments
    """
    with open(filepath, 'r') as f:
        content = f.read()
    with open(filepath, 'r') as f:
        lines = f.readlines()

    javatok = javalang.tokenizer.JavaTokenizer(content)
    tok = javatok.tokenize()
    tokens = list(tok)
    comments = javatok.comments
    tree = javalang.parser.Parser(tokens).parse()

    return tree, tokens, lines, comments


def get_end_line_tokens(start_line, tokens, abstract):
    """
    Given tokens and the starting line number of the function/class in the file
    :return the ending line number of that function and all the tokens present in the function
    """
    count = 0
    line = -1
    tlist = []
    for i in range(len(tokens)):
        token = tokens[i]
        line = token.position[0]
        if line >= start_line:
            tlist.append(token.value)
            if token.__class__.__name__ == 'Separator' and token.value == '{':
                count += 1
            if token.__class__.__name__ == 'Separator' and token.value == '}':
                count -= 1
                if count == 0:
                    return line, set(tlist)
            if count < 0:
                if abstract:
                    line = start_line
                else:
                    print("Error in format....")
                    print(start_line, line)
                    raise ValueError

    return line, set(tlist)


def get_attached_functions(comments, functions):
    """
    Get the functions attached to the comments
    :param comments: list of comments
    :param functions: list of functions
    :return: the functions attached to the comments
    """
    function_track = 0
    function_comments = {}
    for line in comments:
        for i in range(function_track, len(functions)):
            if i == 0:
                if line < functions[0]['start_line']:
                    function_comments[functions[0]['name']] = comments[line]
                    function_track += 1

            else:
                if functions[i - 1]['end_line'] < line < functions[i]['start_line']:
                    function_comments[functions[i]['name']] = comments[line]
                    function_track += 1
    return function_comments


def process_tree(tree, tokens, lines):
    """
    Process the tree and retrieves the functions and classes
    :return
        classes the list of classes retrieved
        functions the list of functions retrieved
    """
    interface = False
    abstract = False
    classes = []
    functions = []
    for _, node in tree:
        cdict = {}
        fdict = {}
        if str(node) == "ClassDeclaration":
            cdict["name"] = node.name
            cdict["start_line"] = node.position[0]
            cdict["end_line"], _ = get_end_line_tokens(node.position[0], tokens, abstract)

            classes.append(cdict)
            if 'abstract' in node.modifiers:
                abstract = True

            cdict['input_type'] = ''
            cdict['modifiers'] = ''
            cdict['content'] = ""
            cdict['javadoc'] = ''
            cdict['return_type'] = ''

        if str(node) == 'InterfaceDeclaration':
            if str(node) == "InterfaceDeclaration":
                interface = True

        if str(node) == "MethodDeclaration":
            if interface:
                fdict["end_line"] = node.position[0]
            else:
                fdict["end_line"], _ = get_end_line_tokens(node.position[0], tokens, abstract)

            fdict["name"] = node.name
            fdict["start_line"] = node.position[0]

            if str(node) != "InterfaceDeclaration":
                fdict["input_type"] = [i.type.name for i in node.parameters]
            else:
                fdict['input_type'] = ''
            fdict["modifiers"] = [i for i in node.modifiers]
            fdict["content"] = "".join(lines[fdict["start_line"] - 1:fdict["end_line"]])

            """
            if node.documentation is None:
                fdict["comments"] = set()
            else:
                fdict["comments"] = set(node.documentation.split())  ## change to list if count and order is important
            """
            if str(node) == "MethodDeclaration":
                if node.return_type is None:
                    fdict["return_type"] = "void"
                else:
                    fdict["return_type"] = node.return_type.name
            else:
                fdict['return_type'] = ''
            functions.append(fdict)
    return classes, functions


def get_class(function, classes):
    """
    Clean the data and get the class of the function
    :return name the name of the class
    """
    name = 'interface'
    for clas in classes:
        end = clas['end_line']
        begin = clas['start_line']
        if begin <= function['start_line'] < end:
            name = clas['name']
    return name


def iterate_list(liste, function_comment, metadata, classes, repo, url, complete_json, repo_id):
    """
    Iterate through the list of functions and store the indexed information
    :return
        complete_json the function information
        repo_id the id of the repository
    """
    for i in range(0, len(liste)):
        dic = liste[i]

        # discard all empty functions
        if dic['start_line'] == dic['end_line']:
            continue

        if dic['name'] in function_comment:
            dic['javadoc'] = function_comment[dic['name']]
        else:
            dic['javadoc'] = ''

        dic['content'] = dic['content']
        dic['github_url'] = url
        dic['stars'] = metadata['stars']
        dic['forks'] = metadata['forks']
        dic['watchers'] = metadata['watchers']

        if 'input_type' in dic:
            dic['variables'] = dic['input_type']
            dic.pop('input_type', None)
        else:
            dic['variables'] = ''

        if 'modifiers' not in dic:
            dic['modifiers'] = ''
        if 'return_type' not in dic:
            dic['return_type'] = ''

        dic['class_name'] = get_class(dic, classes)

        dic['repo_name'] = repo

        complete_json[repo_id] = dic
        repo_id += 1

    return complete_json, repo_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, dest="code")
    args = parser.parse_args()

    example_path = args.code
    paths_not_found = []
    paths_404 = 0

    repo_id = 0
    complete_json = {}
    for subdir, dirs, files in os.walk(example_path):
        for ymlfile in files:
            if ymlfile.split('.')[-1] == 'yml' and ymlfile != 'repositories.yml':
                path = os.path.join(subdir, ymlfile).replace('\\', '/').replace('\\', '/')
                with open(path, 'r') as fp:
                    metadata = yaml.load(fp)

                repo_name = path.split('/')[10] + '/' + path.split('/')[11]
                print('Repository:', repo_name, 'at index', repo_id)

                for file in metadata['files']:
                    java_file = os.path.join(subdir, file).replace('\\', '/')
                    try:
                        tree, tokens, lines, comments = process_file(java_file)
                        classes, functions = process_tree(tree, tokens, lines)
                        function_comment = get_attached_functions(comments, functions)
                        url = metadata['files'][file]
                        complete_json, repo_id = iterate_list(functions, function_comment, metadata, classes, repo_name,
                                                              url, complete_json, repo_id)

                    except javalang.parser.JavaSyntaxError:
                        print('Java syntax error, cannot parse file', file)
                    except FileNotFoundError:
                        print("File not found", file)
                        paths_404 += 1
                        paths_not_found.append(java_file)

                    except UnicodeDecodeError:
                        print('Could not decode', java_file)
                    except javalang.tokenizer.LexerError:
                        print('Could not decode', java_file)

                    except ValueError:
                        print("Submitted non working file", java_file)

    with open('./records.json', 'w') as fp:
        json.dump(complete_json, fp)
    with open('./not_found.json', 'w') as fp:
        json.dump(paths_not_found, fp)


if __name__ == '__main__':
    main()
