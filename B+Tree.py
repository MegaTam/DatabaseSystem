class Node:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf  # Whether the node is a leaf node
        self.keys = []  # List of keys in the node
        self.children = []  # List of child nodes (for internal nodes) or pointers to data (for leaf nodes)


class B_Plus_Tree:
    def __init__(self, degree=4):
        self.degree = degree  # Maximum number of keys a node can have
        self.root = Node(is_leaf=True)  # Initially, the root is a leaf node(only 1 node)

    def insert(self, key):
        if self.is_root_full():
            self.insert_full()
        self.insert_not_full(self.root, key)

    def is_root_full(self):     # whether the root is full
        return len(self.root.keys) == 2 * self.degree - 1

    def insert_full(self):
        # if the root is full, we should first divide then insert      
        new_root = Node()
        new_root.children.append(self.root)
        self.split_node(new_root, 0)
        self.root = new_root

    def insert_not_full(self, node, key):
        # if the root is not full, insert the key into the leaf node
        if node.is_leaf:
            node.keys.append(key)
            node.keys.sort()
        else:
            # Find the correct child to recurse into
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1  # The index of the child to insert into
            child = node.children[i]
            if len(child.keys) == 2 * self.degree - 1:
                self.split_node(node, i)
                if key > node.keys[i]:
                    i += 1
            self.insert_not_full(node.children[i], key)

    def split_node(self, parent, index):
        # method to split the node
        node = parent.children[index]
        mid_index = len(node.keys) // 2
        mid_key = node.keys[mid_index]
        # Create a new node for the right half
        new_node = Node(is_leaf=node.is_leaf)
        new_node.keys = node.keys[mid_index + 1:]
        node.keys = node.keys[:mid_index]
        if not node.is_leaf:
            new_node.children = node.children[mid_index + 1:]
            node.children = node.children[:mid_index + 1]
        # Insert the middle key into the parent node
        parent.keys.insert(index, mid_key)
        parent.children.insert(index + 1, new_node)

    def search(self, key):
        node = self.root
        while True:
            if node.is_leaf:
                if key in node.keys:
                    print(True)
                    return True
                else:
                    print(False)
                    return False
            else:
                i = len(node.keys) - 1
                while i >= 0 and key < node.keys[i]:
                    i -= 1
                i += 1
                node = node.children[i]

    def delete(self, key):
        if self.delete_method(self.root, key):
            print(f"Key {key} deleted.")
        else:
            print(f"Key {key} not found.")

    def delete_method(self, node, key):
        if node.is_leaf:
            if key in node.keys:
                node.keys.remove(key)
                return True
            return False
        else:
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            child = node.children[i]
            if self.delete_method(child, key):
                if len(child.keys) < self.degree - 1:
                    self.re_balance_method(node, i)
                return True
            return False

    def re_balance_method(self, parent, index):
        child = parent.children[index]
        if index > 0 and len(parent.children[index - 1].keys) > self.degree - 1:
            # Borrow from the left sibling
            left_sibling = parent.children[index - 1]
            child.keys.insert(0, parent.keys[index - 1])
            parent.keys[index - 1] = left_sibling.keys.pop()
            if not left_sibling.is_leaf:
                child.children.insert(0, left_sibling.children.pop())
        elif index < len(parent.children) - 1 and len(parent.children[index + 1].keys) > self.degree - 1:
            # Borrow from the right sibling
            right_sibling = parent.children[index + 1]
            child.keys.append(parent.keys[index])
            parent.keys[index] = right_sibling.keys.pop(0)
            if not right_sibling.is_leaf:
                child.children.append(right_sibling.children.pop(0))
        else:
            # Merge with a sibling
            if index > 0:
                left_sibling = parent.children[index - 1]
                left_sibling.keys.append(parent.keys[index - 1])
                left_sibling.keys.extend(child.keys)
                if not left_sibling.is_leaf:
                    left_sibling.children.extend(child.children)
                parent.children.pop(index)
                parent.keys.pop(index - 1)
            else:
                right_sibling = parent.children[index + 1]
                child.keys.append(parent.keys[index])
                child.keys.extend(right_sibling.keys)
                if not child.is_leaf:
                    child.children.extend(right_sibling.children)
                parent.children.pop(index + 1)
                parent.keys.pop(index)

    def display(self):
        display_result = []
        self.display_method(self.root, display_result)
        print(" ".join(map(str, display_result)))

    def display_method(self, node, result_output):
        if node.is_leaf:
            result_output.extend(node.keys)
        else:
            for i in range(len(node.children)):
                self.display_method(node.children[i], result_output)
                if i < len(node.keys):
                    result_output.append(node.keys[i])


'''Test Part'''
# Create a B+ Tree with a specified degree.
tree = B_Plus_Tree(degree=4)
# Insertion
tree.insert(10)
tree.insert(20)
tree.insert(5)
tree.insert(15)
# Search
result = tree.search(15)
# Deletion
tree.delete(10)
# Display the elements in the tree
tree.display()
