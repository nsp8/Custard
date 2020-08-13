import re

execution_result = None


class Node(object):
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = list()
        self.level = 0
        self.is_root = False

    def add_child(self, child):
        if child:
            self.children.append(child)

    def to_dict(self):
        return {
            self.value: {
                "parent": self.parent,
                "children": self.children,
                "level": self.level,
                "is_root": self.is_root,
            }
        }

    def __repr__(self):
        return f"{self.to_dict()}"


class Tree(object):
    def __init__(self):
        self.depth = 0
        self.nodes = dict()
        self.root = None
        self.leaves = list()
        self.metadata = dict()

    def __repr__(self):
        return f"Tree: {self.to_dict()}"

    def to_dict(self):
        return {
            "root": self.root,
            "depth": self.depth,
            "nodes": self.nodes,
            "leaves": self.leaves,
            "metadata": self.metadata,
        }

    def add_node(self, node: Node):
        if isinstance(node, Node):
            if self.nodes:
                
                if node.level not in self.nodes:
                    self.nodes[node.level] = [node]
                else:
                    self.nodes[node.level].append(node)
            else:
                self.nodes[node.level] = [node]


def process_string_test(string):
    regex = r"((\w+)(\()(.*)(\)))"
    tree = Tree()

    def recursive_lookup(_string):
        match = re.search(regex, _string)
        tree.metadata[tree.depth] = dict()
        tree.metadata[tree.depth].setdefault("processed_string", _string)
        if match:
            _group = match.group()
            tree.metadata[tree.depth].setdefault("matched_group", _group)
            function_name, contents = match.groups()[1], match.groups()[3]
            node = Node(value=function_name)
            if not tree.root:
                node.is_root = True
                tree.root = node
                tree.depth = 1
                tree.leaves.append(node)
                tree.add_node(node)
            else:
                node.parent = tree.leaves.pop()
                node.parent.children.append(node)
                node.level = node.parent.level + 1
                tree.add_node(node)
                tree.leaves.append(node)
                tree.depth += 1
            recursive_lookup(contents)
        else:
            split_pattern = r"\s*,\s*"
            args_match = re.search(split_pattern, _string)
            if args_match:
                arguments = re.split(split_pattern, _string)
                last_node = tree.leaves.pop()
                last_node.children.extend(arguments)
                tree.leaves.extend(arguments)
                tree.depth += 1
    recursive_lookup(string)
    return tree


def parse_lookup_tree(lookup_tree: Tree):
    def stringify_params(params):
        split_pattern = r"\s*,\s*"
        args_match = re.search(split_pattern, params)
        if args_match:
            arguments = re.split(split_pattern, params)
            return ",".join([f"'{leaf}'" for leaf in arguments])
        return params

    from copy import deepcopy
    new_tree = deepcopy(lookup_tree)
    init_str = new_tree.metadata[new_tree.depth - 1]["processed_string"]
    new_tree.metadata[new_tree.depth - 1]["matched_group"] = init_str
    new_tree.metadata[new_tree.depth - 1]["processed_string"] = init_str

    for i in range(new_tree.depth - 2, -1, -1):
        _params = new_tree.metadata[i + 1]["processed_string"]
        last_processed = stringify_params(_params)
        last_matched = new_tree.metadata[i + 1]["matched_group"]
        prev_match = new_tree.metadata[i + 1].get("previous_match")
        prev_match = prev_match if prev_match else last_matched
        this_matched = new_tree.metadata[i]["matched_group"]
        this_processed = new_tree.metadata[i]["processed_string"]
        new_tree.metadata[i].setdefault("previous_match", this_processed)
        new_tree.metadata[i]["matched_group"] = this_matched.replace(
            prev_match, last_processed)
        _rvalue = new_tree.metadata[i]["matched_group"]
        _execute = f"execution_result = {_rvalue}"
        exec(compile(_execute, "<string>", "exec"), globals())
        processed = this_processed.replace(this_matched, execution_result)
        new_tree.metadata[i]["processed_string"] = processed
    return new_tree


def parse_lookup_tree_temp(lookup_tree: Tree):
    from copy import deepcopy
    new_tree = deepcopy(lookup_tree)
    leaves = [f"'{leaf}'" for leaf in new_tree.leaves]
    leaves = ",".join(leaves)
    init_str = new_tree.metadata[new_tree.depth - 1]["processed_string"]
    metadata = deepcopy(new_tree.metadata)
    metadata[new_tree.depth - 1]["processed_string"] = leaves
    for i in range(new_tree.depth - 1, 0, -1):
        level, data = i, metadata[i]
        if "matched_group" in data:
            matched = data["matched_group"]
            processed = data["processed_string"]
            _execute = f"execution_result = {matched}"
            exec(compile(_execute, "<string>", "exec"), globals())
            processed = processed.replace(matched, execution_result)
            metadata[level]["processed_string"] = processed
        else:
            last_index = max(metadata.keys()) - 1
            last_match = metadata[last_index]["matched_group"]
            last_processed = metadata[last_index]["processed_string"]
            new_string = last_match.replace(init_str,
                                            data['processed_string'])
            metadata[last_index]["matched_group"] = new_string
            new_string = last_processed.replace(init_str,
                                                data['processed_string'])
            metadata[last_index]["processed_string"] = new_string

    return new_tree


def process_string(string):
    regex = r"((\w+)(\()(.*)(\)))"
    tree = Tree()

    def recursive_lookup(_string):
        match = re.search(regex, _string)
        if match:
            function_name, contents = match.groups()[1], match.groups()[3]
            node = Node(value=function_name)
            if not tree.root:
                node.is_root = True
                tree.root = node
                tree.depth = 1
                tree.leaves.append(node)
            else:
                node.parent = tree.leaves.pop()
                node.level = node.parent.level + 1
                if isinstance(node, Node):
                    if tree.nodes:
                        tree.nodes[node.level].append(node)
                    else:
                        tree.nodes[node.level].append(node)
                tree.leaves.append(node)
            recursive_lookup(contents)
    recursive_lookup(string)
    return tree
