"""Generate concrete CESDM ``add_<entity>`` convenience methods.

The generated file is regular Python source and contains no lazy ``__getattr__``
mechanism. Run after schema changes::

    cesdm-generate-api
"""
from __future__ import annotations

import argparse
import keyword
import re
from pathlib import Path
from typing import Iterable

from cesdm.helpers import build_model_from_yaml
from cesdm.default_library import DEFAULT_LIBRARY_IDS_BY_CLASS


HEADER = '''\
"""AUTO-GENERATED CESDM schema convenience API.

Do not edit manually. Run ``cesdm-generate-api`` after schema changes.
"""
from __future__ import annotations

from typing import Any, Iterable

from cesdm.proxy import AssetProxy
from cesdm.default_library import *
from cesdm.generated_proxies import *


class GeneratedBuildersMixin:
    """Concrete schema-derived ``add_<entity>`` methods."""
'''


def entity_class_to_snake(name: str) -> str:
    text = re.sub(r"[^0-9A-Za-z]+", "_", name)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    return text.strip("_").lower()


def safe_identifier(name: str) -> str:
    if name.isidentifier() and not keyword.iskeyword(name):
        return name
    value = re.sub(r"[^0-9A-Za-z_]", "_", name)
    value = re.sub(r"_+", "_", value).strip("_") or "field"
    if value[0].isdigit():
        value = f"field_{value}"
    if keyword.iskeyword(value):
        value += "_"
    return value



def python_class_name(schema_name: str, suffix: str = "") -> str:
    parts = re.split(r"[^A-Za-z0-9]+", schema_name)
    base = "".join(part[:1].upper() + part[1:] for part in parts if part)
    return f"{base}{suffix}"



def is_many_relation(definition: object) -> bool:
    cardinality = str(getattr(definition, "cardinality", "1") or "1")
    return "*" in cardinality or cardinality.endswith("..n")


def relation_input_annotation(definition: object) -> str:
    targets = list(getattr(definition, "targets", None) or [])
    proxy_types = [python_class_name(str(target), "Proxy") for target in targets]
    input_types = []
    for target in targets:
        target_name = str(target)
        input_types.append(python_class_name(target_name, "Proxy"))
        input_types.append(
            python_class_name(target_name, "Id")
            if target_name in DEFAULT_LIBRARY_IDS_BY_CLASS
            else "str"
        )
    target_type = " | ".join(dict.fromkeys(proxy_types)) or "AssetProxy"
    value_type = " | ".join(dict.fromkeys(input_types)) or f"str | {target_type}"
    if is_many_relation(definition):
        return f"{value_type} | Iterable[{value_type}]"
    return value_type


def unique_parameters(fields: list[tuple[str, object]]) -> list[tuple[str, str, object]]:
    used = {"self", "entity_id"}
    result = []
    for field_name, definition in fields:
        parameter = safe_identifier(field_name)
        base = parameter
        number = 2
        while parameter in used:
            parameter = f"{base}_{number}"
            number += 1
        used.add(parameter)
        result.append((parameter, field_name, definition))
    return result


def render_method(model, class_name: str) -> str:
    class_def = model.classes[class_name]
    attributes, relations = model._collect_inherited_fields(class_def)
    attr_fields = unique_parameters(list(attributes.items()))
    used = {p for p, _, _ in attr_fields} | {"self", "entity_id"}
    rel_fields = []
    for field_name, definition in relations.items():
        parameter = safe_identifier(field_name)
        base = parameter
        number = 2
        while parameter in used:
            parameter = f"{base}_{number}"
            number += 1
        used.add(parameter)
        rel_fields.append((parameter, field_name, definition))

    all_fields = attr_fields + rel_fields
    relation_names_for_split = {name for _, name, _ in rel_fields}

    def _is_python_required(field_name: str, definition) -> bool:
        # A schema-level default (attributes only -- relations have no
        # such concept, a relation target can't be "defaulted") means
        # the whole point was that callers don't have to pass this
        # explicitly, even if the attribute is separately marked
        # required: true for *validation* purposes (i.e. "this must
        # eventually have a value", which the default itself already
        # satisfies at creation time -- see ear.model.entity_ops.
        # add_entity()). Treating required: true as "must always be
        # passed as a Python argument" regardless of a default was a
        # real bug: every MACHINE_*/AVR_*/GOV_*/PSS_* attribute that
        # got a real IEEE/PSS-E default *and* was already required:
        # true (most of them) stayed a mandatory kwarg anyway, forcing
        # every caller to pass values a default already existed for --
        # found directly, from a user's own Pyright error, not by
        # testing. See CHANGELOG.md.
        if field_name not in relation_names_for_split and getattr(definition, "default", None) is not None:
            return False
        return bool(getattr(definition, "required", False))

    required = [x for x in all_fields if _is_python_required(x[1], x[2])]
    optional = [x for x in all_fields if not _is_python_required(x[1], x[2])]
    method_name = f"add_{entity_class_to_snake(class_name)}"
    proxy_name = python_class_name(class_name, "Proxy")

    lines = [f"    def {method_name}(", "        self,", "        entity_id: str,"]
    if required or optional:
        lines.append("        *,")
    relation_names = {name for _, name, _ in rel_fields}
    for parameter, field_name, definition in required:
        annotation = relation_input_annotation(definition) if field_name in relation_names else "Any"
        lines.append(f"        {parameter}: {annotation},")
    for parameter, field_name, definition in optional:
        annotation = relation_input_annotation(definition) if field_name in relation_names else "Any"
        lines.append(f"        {parameter}: {annotation} | None = None,")
    lines += [f"    ) -> {proxy_name}:", f'        """Create a ``{class_name}`` entity."""', "        return self._add_generated_schema_entity(", f'            "{class_name}",', "            entity_id,", f"            proxy_class={proxy_name},", "            attributes={"]
    for parameter, field_name, _ in attr_fields:
        lines.append(f'                "{field_name}": {parameter},')
    lines += ["            },", "            relations={"]
    for parameter, field_name, _ in rel_fields:
        lines.append(f'                "{field_name}": {parameter},')
    lines += ["            },", "        )", ""]
    return "\n".join(lines)


def render(schema_dir: Path) -> str:
    model = build_model_from_yaml(schema_dir)
    methods = []
    mapping = []
    for class_name, class_def in sorted(model.classes.items()):
        if getattr(class_def, "abstract", False):
            continue
        methods.append(render_method(model, class_name))
        mapping.append((f"add_{entity_class_to_snake(class_name)}", class_name))
    body = HEADER + "\n" + "\n".join(methods)
    body += "\n    GENERATED_ADD_METHODS = {\n"
    for method_name, class_name in mapping:
        body += f'        "{method_name}": "{class_name}",\n'
    body += "    }\n\n    def available_add_methods(self) -> dict[str, str]:\n        return dict(self.GENERATED_ADD_METHODS)\n"
    return body



def render_proxies(schema_dir: Path) -> str:
    model = build_model_from_yaml(schema_dir)
    lines = [
        '"""AUTO-GENERATED CESDM proxy subclasses.\n\nDo not edit manually. Run ``cesdm-generate-api`` after schema changes.\n"""',
        'from __future__ import annotations',
        '',
        'from cesdm.proxy import AssetProxy',
        '',
    ]
    emitted: set[str] = set()

    def emit(class_name: str) -> None:
        proxy_name = python_class_name(class_name, 'Proxy')
        if proxy_name in emitted:
            return
        class_def = model.classes[class_name]
        parents = [p for p in getattr(class_def, 'parents', []) if p in model.classes]
        for parent in parents:
            emit(parent)
        bases = [python_class_name(parent, 'Proxy') for parent in parents]
        if not bases:
            bases = ['AssetProxy']
        emitted.add(proxy_name)
        lines.extend([
            f'class {proxy_name}({", ".join(bases)}):',
            f'    """Proxy for CESDM entity class ``{class_name}``."""',
            '    pass',
            '',
        ])

    for class_name in sorted(model.classes):
        emit(class_name)
    return '\n'.join(lines).rstrip() + '\n'



def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)
    return True


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schemas", type=Path, default=Path("schemas"))
    parser.add_argument("--output", type=Path, default=Path("cesdm/domain/model/generated_builders.py"))
    parser.add_argument("--proxy-output", type=Path, default=Path("cesdm/generated_proxies.py"))
    args = parser.parse_args(argv)
    changed = write_if_changed(args.output, render(args.schemas))
    proxies_changed = write_if_changed(args.proxy_output, render_proxies(args.schemas))
    print(("Generated" if changed else "Already up to date:") + f" {args.output}")
    print(("Generated" if proxies_changed else "Already up to date:") + f" {args.proxy_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
