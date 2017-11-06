def get_attr_by_type(node, type):
    for attr in node.attributes:
        if attr.type == type:
            return attr
    return None
