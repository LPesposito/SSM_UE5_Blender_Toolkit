def find_image_node(input_pin):
    if not input_pin or not input_pin.is_linked: return None
    link = input_pin.links[0]
    node = link.from_node
    if node.type == 'TEX_IMAGE': return node
    for inp in node.inputs:
        if inp.is_linked:
            res = find_image_node(inp)
            if res: return res
    return None