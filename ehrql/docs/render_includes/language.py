def render_language_section(data):
    return "\n\n".join(render_item(details) for details in data)


def render_item(item):
    if item["type"] == "class":
        return render_class(item)
    if item["type"] == "function":
        return render_function(item)
    if item["type"] == "namedtuple":
        return render_namedtuple(item)
    else:
        assert False, f"Unhandled type: {item['type']}"


CLASS_TEMPLATE = """\
<h4 class="attr-heading" id="{id}" data-toc-label="{name}" markdown>
  <tt><em>class</em> {signature}</tt>
</h4>

<div markdown="block" class="indent">
{docstring}
{methods}
</div>
"""


def render_class(details):
    return CLASS_TEMPLATE.format(
        name=details["name"],
        id=details["name"],
        signature=render_signature(
            details["name"],
            # Hide the `qm_node` and `_qm_node` init arguments from the user to avoid confusion
            {
                k: v
                for k, v in details["init_arguments"].items()
                if k not in ["qm_node", "_qm_node"]
            },
        ),
        docstring=details["docstring"],
        methods="\n".join(
            render_method(details["name"], method_details)
            for method_details in details["methods"]
        ),
    )


METHOD_TEMPLATE = """\
<div class="attr-heading" id="{id}">
  <tt>{signature}</tt>
  <a class="headerlink" href="#{id}" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
{docstring}
</div>
"""


def render_method(classname, details):
    if details["operator"]:
        arg_count = len(details["arguments"])
        if arg_count == 0:
            prefix, suffix = "", "self"
        elif arg_count == 1:
            first_arg = list(details["arguments"].keys())[0]
            prefix, suffix = "self", first_arg
        else:
            assert False
        signature = f"<em>{prefix}</em> <strong>{details['operator']}</strong> <em>{suffix}</em>"
    elif details["is_property"]:
        signature = f"<strong>{details['name']}</strong>"
    else:
        signature = render_signature(details["name"], details["arguments"])
    return METHOD_TEMPLATE.format(
        id=f"{classname}.{details['name']}".replace("__", ""),
        signature=signature,
        docstring=details["docstring"],
    )


def render_signature(name, arguments):
    args = [
        render_argument(arg_name, arg_details)
        for arg_name, arg_details in arguments.items()
    ]
    return f"<strong>{name}</strong>({', '.join(args)})"


def render_argument(name, details):
    default = f"={details['default']}" if details["default"] is not None else ""
    prefix = "*" if details["repeatable"] else ""
    return f"<em>{prefix}{name}{default}</em>"


FUNCTION_TEMPLATE = """
<h4 class="attr-heading" id="{id}" data-toc-label="{name}" markdown>
  <tt>{signature}</tt>
</h4>
<div markdown="block" class="indent">
{docstring}
</div>
"""


def render_function(details):
    return FUNCTION_TEMPLATE.format(
        name=details["name"],
        id=details["name"],
        signature=render_signature(details["name"], details["arguments"]),
        docstring=details["docstring"],
    )


NAMEDTUPLE_TEMPLATE = """
<h4 class="attr-heading" id="{id}" data-toc-label="{name}" markdown>
  <tt><strong>{name}</strong></tt>
</h4>
<div markdown="block" class="indent">
{docstring}
{fields}
</div>
"""


def render_namedtuple(details):
    return NAMEDTUPLE_TEMPLATE.format(
        name=details["name"],
        id=details["name"],
        docstring=details["docstring"],
        fields="\n".join(
            render_namedtuple_field(details["name"], field_details)
            for field_details in details["fields"]
        ),
    )


NAMEDTUPLE_FIELD_TEMPLATE = """\
<div class="attr-heading" id="{id}">
  <tt><strong>{name}</strong></tt>
  <a class="headerlink" href="#{id}" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
{docstring}
</div>
"""


def render_namedtuple_field(tuple_name, details):
    return NAMEDTUPLE_FIELD_TEMPLATE.format(
        id=f"{tuple_name}.{details['name']}",
        name=details["name"],
        docstring=details["docstring"],
    )
