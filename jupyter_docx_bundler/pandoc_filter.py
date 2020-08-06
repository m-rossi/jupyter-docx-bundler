from pandocfilters import toJSONFilter, Null


def remove_empty_input(key, value, format, meta):
    if key == 'CodeBlock' and value[1] == 'jupyter-docx-bundler-remove-input':
        return Null()


if __name__ == "__main__":
    toJSONFilter(remove_empty_input)
