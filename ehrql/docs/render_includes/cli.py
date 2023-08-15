CLI_TEMPLATE = """\
```
{usage}
```
{description}

{arguments}

{subcommands}
"""


def render_cli(data):
    return CLI_TEMPLATE.format(
        usage=render_cmd_usage(data["argument_groups"]),
        description=data["description"],
        arguments=render_argument_groups(data["argument_groups"]),
        subcommands="\n".join(render_subcommand(cmd) for cmd in data["subcommands"]),
    )


def render_cmd_usage(argument_groups, subcommand_name=None):
    parts = ["ehrql"]
    if subcommand_name is not None:
        parts.append(subcommand_name)
    for group in argument_groups:
        parts.extend(render_arg_usage(arg) for arg in group["arguments"])
    return wrap_strings(
        parts,
        width=79,
        # Indent subsequent lines by the length of the command name plus a space to
        # align arguments
        subsequent_indent=" " * (len(parts[0]) + 1),
    )


def wrap_strings(parts, width, subsequent_indent=""):
    lines = []
    next_line = parts[0]
    for part in parts[1:]:
        if len(next_line) + 1 + len(part) <= width:
            next_line += " " + part
        else:
            lines.append(next_line)
            next_line = subsequent_indent + part
    lines.append(next_line)
    return "\n".join(lines)


def render_arg_usage(arg):
    return arg["usage_short"]


ARGUMENT_GROUP_ORDER = ["positional arguments", "options", "user_args"]


def render_argument_groups(argument_groups, parent_id=None):
    groups = {group["name"]: group for group in argument_groups}
    lines = []
    # We render the default groups in a fixed order, without separate headings for each
    # group
    for group_name in ARGUMENT_GROUP_ORDER:
        if group := groups.get(group_name):
            lines.extend(render_argument(arg, parent_id) for arg in group["arguments"])
    # Any remaining groups get rendered with their group name and description
    for name, group in groups.items():
        if name not in ARGUMENT_GROUP_ORDER:
            lines.append(render_argument_group(group, parent_id))
    return "\n".join(lines)


ARGUMENT_GROUP_TEMPLATE = """\
<div class="attr-heading">
  <strong>{name}</strong>
</div>
<div markdown="block" class="indent">
{description}
{arguments}
</div>
"""


def render_argument_group(group, parent_id=None):
    return ARGUMENT_GROUP_TEMPLATE.format(
        name=group["name"],
        description=group["description"],
        arguments="\n".join(
            render_argument(arg, parent_id) for arg in group["arguments"]
        ),
    )


ARGUMENT_TEMPLATE = """\
<div class="attr-heading" id="{id}">
  <tt>{usage_long}</tt>
  <a class="headerlink" href="#{id}" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
{description}
{subcommands}
</div>
"""


def render_argument(arg, parent_id=None):
    id_prefix = f"{parent_id}." if parent_id is not None else "ehrql."
    return ARGUMENT_TEMPLATE.format(
        id=id_prefix + arg["id"],
        usage_long=arg["usage_long"],
        description=arg["description"],
        subcommands="\n".join(
            render_subcommand_list_item(item) for item in arg.get("subcommands", ())
        ),
    )


SUBCOMMAND_LIST_ITEM_TEMPLATE = """\
<div class="attr-heading">
  <a href="#{name}"><tt>{name}</tt></a>
</div>
<p class="indent">
{description}
</p>
"""


def render_subcommand_list_item(item):
    return SUBCOMMAND_LIST_ITEM_TEMPLATE.format(
        name=item["name"],
        description=item["description"].partition("\n\n")[0],
    )


SUBCOMMAND_TEMPLATE = """\
<h2 id="{id}" data-toc-label="{name}" markdown>
  {name}
</h2>
```
{usage}
```
{description}

{arguments}
"""


def render_subcommand(cmd):
    return SUBCOMMAND_TEMPLATE.format(
        id=cmd["id"],
        name=cmd["name"],
        usage=render_cmd_usage(cmd["argument_groups"], subcommand_name=cmd["name"]),
        description=cmd["description"],
        arguments=render_argument_groups(cmd["argument_groups"], parent_id=cmd["id"]),
    )
