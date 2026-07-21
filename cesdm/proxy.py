"""cesdm.proxy — object-oriented ergonomics over the EAR engine.

Everything here is a thin wrapper over the existing low-level API
(add_entity/add_attribute/add_relation, views_for_asset, ensure_view,
...) — the schema and the underlying EAR data model are completely
unchanged. This module exists so that most users never have to write
`add_relation(id, "representsAsset", ...)` or think about view class
strings directly.

Key design decision: :class:`AssetProxy` is a ``str`` subclass. It
*is* the entity id everywhere a plain string id is expected (dict
keys, `get_relation_targets(...)`, string formatting, `==` against a
plain string, ...), so every existing builder that starts returning an
`AssetProxy` instead of a bare `str` is a 100% backward-compatible
change — nothing that already worked with the plain-string return
value breaks, and new code additionally gets `.dispatch`, `.connect()`,
etc. for free on the same object.
"""

from __future__ import annotations

from difflib import get_close_matches
from typing import Any, Optional


def _known_view_families(model: Any) -> set:
    """Every distinct view_family value declared (directly or inherited)
    anywhere in the loaded schema -- used only to power the "Did you
    mean: dispatch?" suggestion when a keyword doesn't match anything."""
    return {
        getattr(cdef, "view_family", None)
        for cdef in (getattr(model, "classes", None) or {}).values()
        if getattr(cdef, "view_family", None)
    }


def _entity_proxy(model: Any, entity_id: str):
    """Return the schema-specific generated proxy for an entity id."""
    class_name = model.entity_class(str(entity_id))
    if not class_name:
        return AssetProxy(model, str(entity_id))
    try:
        from cesdm import generated_proxies
        proxy_name = "".join(
            part[:1].upper() + part[1:]
            for part in __import__("re").split(r"[^A-Za-z0-9]+", class_name)
            if part
        ) + "Proxy"
        proxy_class = getattr(generated_proxies, proxy_name, AssetProxy)
    except (ImportError, AttributeError):
        proxy_class = AssetProxy
    return proxy_class(model, str(entity_id))


def _relation_value(model: Any, targets: list[str]):
    proxies = [_entity_proxy(model, target) for target in targets]
    return proxies[0] if len(proxies) == 1 else proxies


class ViewProxy:
    """Wraps a single representation-view entity. Attribute access reads
    and writes the view's attributes directly, validated against the
    view's own class definition -- an unknown attribute name raises
    immediately with a suggestion, rather than silently doing nothing.
    """

    __slots__ = ("_model", "_view_id", "_view_class")

    def __init__(self, model: Any, view_id: str, view_class: str):
        object.__setattr__(self, "_model", model)
        object.__setattr__(self, "_view_id", view_id)
        object.__setattr__(self, "_view_class", view_class)

    @property
    def id(self) -> str:
        return self._view_id

    @property
    def view_class(self) -> str:
        return self._view_class

    def _known_fields(self) -> set:
        attrs = self._model.class_attributes(self._view_class) or []
        rels = self._model.class_relations(self._view_class) or []
        return set(attrs) | set(rels)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        model = self._model
        rels = model.class_relations(self._view_class) or {}
        if name in rels:
            targets = model.get_relation_targets(self._view_id, name)
            return _relation_value(model, targets)
        attrs = model.class_attributes(self._view_class) or {}
        if name in attrs:
            # Cascades to the represented asset's technology template
            # (GeneratorType/StorageType/...) when not explicitly set on
            # this view instance -- see
            # Model.get_effective_attribute_value's docstring.
            return model.get_effective_attribute_value(self._view_id, name)
        self._raise_unknown_field(name)

    def __setattr__(self, name: str, value: Any) -> None:
        model = self._model
        rels = model.class_relations(self._view_class) or {}
        if name in rels:
            model.add_relation_if_allowed(self._view_id, name, value, strict=True)
            return
        attrs = model.class_attributes(self._view_class) or {}
        if name in attrs:
            unit = None
            if isinstance(value, tuple) and len(value) == 2:
                value, unit = value
            else:
                # Auto-attach the unit when the attribute has exactly one
                # registered valid unit -- ambiguous (0 or 2+ valid units)
                # attributes are left without a unit rather than guessing.
                adef = model.global_attributes.get(name) or {}
                enum = ((adef.get("unit") or {}).get("constraints") or {}).get("enum") or []
                if len(enum) == 1:
                    unit = enum[0]
            model.set_attribute_if_allowed(self._view_id, name, value, unit=unit, strict=True)
            return
        self._raise_unknown_field(name)

    def _raise_unknown_field(self, name: str):
        known = sorted(self._known_fields())
        suggestion = get_close_matches(name, known, n=3)
        hint = f" Did you mean: {', '.join(suggestion)}?" if suggestion else ""
        raise AttributeError(
            f"{name!r} is not an attribute or relation of {self._view_class!r}.{hint}"
        )

    def __repr__(self) -> str:
        return f"<ViewProxy {self._view_class} id={self._view_id!r}>"


class AssetProxy(str):
    """A str subclass wrapping an entity id -- behaves as the plain id
    string everywhere (dict keys, equality, formatting, passing to any
    existing low-level model.* method), while additionally exposing
    `.dispatch`, `.powerflow`, etc. as lazily-created ViewProxy objects,
    `.connect(...)` for wiring topology relations, and direct attribute/
    relation assignment for whatever the asset class itself declares
    (typically just `name`/`description`/`long_name` -- CESDM's own
    asset/view split keeps most operational data on views instead, see
    docs/architecture/proxy_api.md).
    """

    _model: Any

    def __new__(cls, model: Any, entity_id: str):
        obj = str.__new__(cls, entity_id)
        object.__setattr__(obj, "_model", model)
        return obj

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_model":
            object.__setattr__(self, name, value)
            return
        model = self._model
        cname = self.entity_class
        entity_id = str(self)
        rels = (model.class_relations(cname) or []) if cname else []
        if name in rels:
            model.add_relation_if_allowed(entity_id, name, value, strict=True)
            return
        attrs = (model.class_attributes(cname) or []) if cname else []
        if name in attrs:
            unit = None
            if isinstance(value, tuple) and len(value) == 2:
                value, unit = value
            else:
                # Same "only auto-attach when unambiguous" rule as
                # ViewProxy -- see its __setattr__ for the reasoning.
                adef = model.global_attributes.get(name) or {}
                enum = ((adef.get("unit") or {}).get("constraints") or {}).get("enum") or []
                if len(enum) == 1:
                    unit = enum[0]
            model.set_attribute_if_allowed(entity_id, name, value, unit=unit, strict=True)
            return
        # Deliberately raise rather than silently falling through to a
        # normal Python instance-attribute assignment -- AssetProxy
        # being a str subclass means that would otherwise "work" with
        # no error (stored in the instance's own __dict__) while never
        # touching the actual model data at all: `bus.name = "X"`
        # would read back as "X" from the very same object, but
        # `model.get_attribute_value(bus, "name")` would still be
        # None, and the value would silently vanish from any export.
        # See CHANGELOG.md.
        known = sorted(set(attrs) | set(rels))
        suggestion = get_close_matches(name, known, n=3)
        hint = f" Did you mean: {', '.join(suggestion)}?" if suggestion else ""
        raise AttributeError(
            f"{name!r} is not an attribute or relation of {cname!r}.{hint}"
        )

    @property
    def id(self) -> str:
        return str(self)

    @property
    def entity_class(self) -> Optional[str]:
        return self._model.entity_class(str(self))

    def __getattr__(self, name: str) -> Any:
        # Only reached for names not already resolved as a real attribute/
        # method/str-builtin -- i.e. genuinely unknown names. Try resolving
        # as a view_family first (schema-driven, see _view()); it returns
        # None rather than raising if nothing matches, so an unrelated
        # unknown name still falls through to the checks below instead of
        # being swallowed by a view-specific error message.
        view = self._view(name)
        if view is not None:
            return view
        # Fall back to the asset's own direct attributes/relations (most
        # asset classes only carry identity fields like name/description
        # here -- CESDM's asset/view separation keeps operational data in
        # views by design).
        model = self._model
        cname = self.entity_class
        if cname:
            attrs = model.class_attributes(cname) or {}
            if name in attrs:
                return model.get_attribute_value(str(self), name)
            rels = model.class_relations(cname) or {}
            if name in rels:
                targets = model.get_relation_targets(str(self), name)
                return _relation_value(model, targets)
        known = sorted(_known_view_families(model) | set(model.class_attributes(cname) or {}) | set(model.class_relations(cname) or {})) if cname else sorted(_known_view_families(model))
        suggestion = get_close_matches(name, known, n=3)
        hint = f" Did you mean: {', '.join(suggestion)}?" if suggestion else ""
        raise AttributeError(f"{name!r} is not a view, attribute, or relation of {cname!r}.{hint}")

    def _view(self, keyword: str) -> Optional["ViewProxy"]:
        """Resolve `keyword` (e.g. "dispatch") against the schema's
        view_family metadata (see ear/entity_class.py) -- not a fixed
        Python keyword list. A view class's family is declared once on
        its abstract root (schemas/views/**/*.yaml, e.g.
        OperationalDispatchView: view_family: dispatch) and inherited by
        every concrete subclass, so adding a new view family that "just
        works" as a property here only requires tagging the schema, no
        Python change. Returns None when `keyword` isn't a recognized
        view_family at all, so callers can fall through to checking
        attributes/relations instead (see __getattr__). Raises
        AttributeError directly -- rather than returning None -- when
        `keyword` *is* a real family but genuinely has no matching view
        class for this particular asset's class, since that's a more
        specific, more useful error than the generic "not a view,
        attribute, or relation" fallback.
        """
        model = self._model
        asset_id = str(self)

        existing = model.views_for_asset(asset_id)
        for vcls, vid in existing.items():
            cdef = model.classes.get(vcls)
            if (cdef is not None and getattr(cdef, "view_family", None) == keyword
                    and not getattr(cdef, "abstract", False)):
                return ViewProxy(model, vid, vcls)

        # Not created yet -- find a valid view class for this asset class
        # matching the keyword, and create it (mirrors ensure_dispatch_view
        # for the "dispatch" case; generalized here for every keyword).
        cname = self.entity_class
        candidates = (model._discover_view_map() or {}).get(cname, [])
        matching = [
            vcls for vcls in candidates
            if (cdef := model.classes.get(vcls)) is not None
            and getattr(cdef, "view_family", None) == keyword
            and not getattr(cdef, "abstract", False)
        ]
        if matching:
            vid = model.ensure_view(asset_id, matching[0])
            return ViewProxy(model, vid, matching[0])

        if keyword in _known_view_families(model):
            raise AttributeError(
                f"{keyword!r} is a real view family in the schema, but no "
                f"matching view class exists for asset class {cname!r}. "
                f"Valid view classes for this asset: {candidates}"
            )
        return None

    def connect(self, *nodes: str):
        """gen.connect(bus) -> single-port connection (representsAsset-style
        topology, via connect_single_port). line.connect(bus1, bus2) ->
        two-port connection (fromNode/toNode, via connect_two_port)."""
        model = self._model
        asset_id = str(self)
        if len(nodes) == 1:
            model.connect_single_port(asset_id, str(nodes[0]))
        elif len(nodes) == 2:
            model.connect_two_port(asset_id, str(nodes[0]), str(nodes[1]))
        else:
            raise TypeError(f"connect() takes 1 or 2 node arguments, got {len(nodes)}")
        return self

    def __repr__(self) -> str:
        return f"<AssetProxy {self.entity_class} id={str(self)!r}>"
