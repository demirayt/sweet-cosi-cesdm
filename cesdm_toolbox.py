"""
cesdm_toolbox
=============

Core data structures and utilities for the Common Energy System Domain Model (CESDM).

This module provides:

- dataclasses for schema metadata (Constraint, RelationDef, AttributeDef, EntityClass)
- the in-memory entity representation (Entity)
- the central Model class for:
  - loading CESDM schemas from YAML
  - creating and modifying entity instances
  - validating attributes and relations
  - exporting and importing data in JSON/CSV/Data Package formats
- a convenience function ``build_model_from_yaml`` to construct a Model from a schema folder.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple
from difflib import get_close_matches
import os, pathlib
import yaml
import re

@dataclass
class Constraint:
    """
    Validation constraints for a single attribute.

    Parameters
    ----------
    enum :
        Optional list of allowed values for the attribute.
    minimum :
        Minimum allowed value for numeric attributes.
    maximum :
        Maximum allowed value for numeric attributes.
    pattern :
        Optional regular expression pattern the value must match.
    ref :
        Optional relation string for more complex/indirect constraints
        (currently used only in limited contexts).
    """
    enum: Optional[List[Any]] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    pattern: Optional[str] = None
    ref: Optional[str] = None

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Constraint":
        if not d:
            return Constraint()
        return Constraint(
            enum=d.get("enum"),
            minimum=d.get("minimum"),
            maximum=d.get("maximum"),
            pattern=d.get("pattern"),
            ref=d.get("ref"),
        )

@dataclass
class RelationDef:
    """
    Definition of a relation from one entity to another in the schema.
    """
    name: str
    targets: List[str]          # list of allowed target class names
    cardinality: str = "1"
    required: Optional[bool] = None
    description: str = ""

    @property
    def target(self) -> str:
        """
        Backwards-compatible view: the first declared target, or ''.
        Existing code that expects a single string still works.
        """
        return self.targets[0] if self.targets else ""

    @staticmethod
    def from_dict(name: str, d: Dict[str, Any]) -> "RelationDef":
        """
        Create a RelationDef from YAML.

        Supports both:
          target: EnergyNode
        and:
          target: [EnergyConversionTechnology1x1, EnergyConversionTechnology1x2]
        """
        raw = d.get("target") or d.get("ref") or ""
        if isinstance(raw, list):
            targets = [str(x).strip() for x in raw if x]
        elif raw:
            targets = [str(raw).strip()]
        else:
            targets = []

        return RelationDef(
            name=name,
            targets=targets,
            cardinality=str(d.get("cardinality", "1")),
            required=d.get("required"),
            description=str(d.get("description", "")) if d.get("description") is not None else "",
        )


@dataclass
class AttributeDef:
    """
    Definition of a single attribute in a CESDM class.

    Parameters
    ----------
    name :
        Name of the attribute (e.g. ``conversion_efficiency``).
    type :
        Expected CESDM type (``string``, ``float``, ``integer``, ``boolean``, ...).
    required :
        Whether the attribute must be present on an entity.
    description :
        Human-readable description of the attribute.
    default :
        Optional default value used when creating new entities.
    constraints :
        Optional :class:`Constraint` object with enum/min/max/pattern rules.
    """

    name: str
    type: str
    required: bool = False
    description: str = ""
    default: Optional[Any] = None
    constraints: Constraint = field(default_factory=Constraint)

    unit: Optional[Any] = None  # default unit schema (string or nested dict from YAML)
    group: Optional[str] = None   # z.B. "master_data", "power_flow", "cost", "dynamic"
    order: Optional[int] = None   # Reihenfolge innerhalb der Gruppe

        # Optional: Validierung der Gruppe
        # if group is not None and group not in ATTRIBUTE_GROUPS:
        #     raise ValueError(f"Unknown attribute group '{group}' in attribute '{name}'")



    @staticmethod
    def from_dict(name: str, d: Dict[str, Any]) -> "AttributeDef":
        """
        Create an ``AttributeDef`` from a dictionary parsed from YAML.

        This supports both the legacy flat style::

            attributes:
              foo:
                type: float
                required: true
                constraints:
                  minimum: 0.0

        and the newer nested style::

            attributes:
              foo:
                description: Some value.
                value:
                  type: float
                  required: true
                  constraints:
                    minimum: 0.0
                unit:
                  type: string
                  constraints:
                    enum: [MWh]

        Parameters
        ----------
        name :
            Attribute name in the YAML.
        d :
            Mapping of attribute properties.

        Returns
        -------
        AttributeDef
            The constructed attribute definition.
        """
        # --- detect nested "value" style --------------------------------
        if "value" in d and isinstance(d.get("value"), dict):
            vdef = d.get("value") or {}
            cons_dict = vdef.get("constraints") or {}
            cons_dict = dict(cons_dict)

            # allow enum at value-level for convenience
            if "enum" in vdef and "enum" not in cons_dict:
                cons_dict["enum"] = vdef["enum"]

            group = d.get("group")
            order = d.get("order")

            # import pdb
            # pdb.set_trace()

            return AttributeDef(
                name=name,
                type=vdef.get("type", "string"),
                required=bool(d.get("required", False)),
                description=d.get("description", ""),
                default=vdef.get("default"),
                constraints=Constraint.from_dict(cons_dict),
                group=group,
                order=order,
                unit=d.get("unit"),  # may be string or nested dict
            )

        # # --- legacy flat style ------------------------------------------
        # cons_dict = d.get("constraints") or {}
        # cons_dict = dict(cons_dict)

        # if "enum" in d and "enum" not in cons_dict:
        #     cons_dict["enum"] = d["enum"]

        # group = d.get("group")
        # order = d.get("order")

        # return AttributeDef(
        #     name=name,
        #     type=d.get("type", "string"),
        #     required=bool(d.get("required", False)),
        #     description=d.get("description", ""),
        #     default=d.get("default"),
        #     constraints=Constraint.from_dict(cons_dict),
        #     group=group,
        #     order=order,
        #     unit=d.get("unit"),
        # )

class AttributeValueDict(dict):
    """Marker-Typ für AttributeValue-Objekte, die im YAML inline (flow style) ausgegeben werden sollen."""
    pass

def attributevalue_representer(dumper, data):
    # Schreibe als Mapping im Flow-Style: { key: value, ... }
    return dumper.represent_mapping(
        u"tag:yaml.org,2002:map",
        data,
        flow_style=True,
    )

yaml.add_representer(AttributeValueDict, attributevalue_representer)
# falls du SafeDumper verwendest:
yaml.add_representer(AttributeValueDict, attributevalue_representer, Dumper=yaml.SafeDumper)


@dataclass
class EntityClass:
    """
    Schema-level description of a CESDM class.

    Parameters
    ----------
    name :
        Name of the class (e.g. ``Generator``, ``Load``).
    parents :
        Optional name(s) of the base class(es) this class inherits from.
    abstract :
        Whether this class is abstract (no instances should be created).
    description :
        Human-readable description of the class.
    attributes :
        Mapping of attribute name → :class:`AttributeDef`.
    relations :
        Mapping of relation name → :class:`RelationDef`.
    """

    name: str
    attributes: Dict[str, AttributeDef]
    description: str = ""
    parents: Union[None, str, List[str]] = None
    abstract: bool = False
    relations: Dict[str, RelationDef] = field(default_factory=dict)

    @staticmethod
    def from_dict(name: str, d: Dict[str, Any]) -> "EntityClass":
        """
        Build an :class:`EntityClass` from a dictionary parsed from a YAML schema.

        Supports both:

        attributes:
          foo:
            description: ...
            value: ...
            unit: ...

        and:

        attributes:
          - id: foo
            description: ...
            value: ...
            unit: ...
        """

        # --- attributes: support dict AND list-of-objects with "id" ---
        raw_attrs = d.get("attributes") or {}
        attrs: Dict[str, AttributeDef] = {}

        if isinstance(raw_attrs, list):
            # new style: list of {id: ..., ...}
            for item in raw_attrs:
                if not isinstance(item, dict):
                    continue
                attr_id = item.get("id")
                if not attr_id:
                    continue
                spec = {k: v for k, v in item.items() if k != "id"}
                attrs[attr_id] = AttributeDef.from_dict(attr_id, spec)
        elif isinstance(raw_attrs, dict):
            # old style: mapping attr_name -> spec
            for attr_id, spec in raw_attrs.items():
                attrs[attr_id] = AttributeDef.from_dict(attr_id, spec or {})

        # --- relations: support dict AND list-of-objects with "id" ---
        raw_refs = d.get("relations") or {}
        refs: Dict[str, RelationDef] = {}

        if isinstance(raw_refs, list):
            # new style: list of {id: ..., ...}
            for item in raw_refs:
                if not isinstance(item, dict):
                    continue
                ref_id = item.get("id")
                if not ref_id:
                    continue
                spec = {k: v for k, v in item.items() if k != "id"}
                refs[ref_id] = RelationDef.from_dict(ref_id, spec)
        elif isinstance(raw_refs, dict):
            # old style: mapping ref_name -> spec
            for ref_id, spec in raw_refs.items():
                refs[ref_id] = RelationDef.from_dict(ref_id, spec or {})

        return EntityClass(
            name=name,
            attributes=attrs,
            description=d.get("description", ""),
            parents=d.get("parents"),
            abstract=bool(d.get("abstract", False)),
            relations=refs,
        )


@dataclass
class Entity:
    """
    Runtime instance of a CESDM class.

    Parameters
    ----------
    id :
        Globally unique identifier of the entity.
    class_name :
        Name of the class this entity belongs to.
    data :
        Mapping of attribute and relation names to stored values.
        The internal representation is a flat dictionary; access helpers
        in :class:`Model` know which fields are attributes vs. relations.
    """

    cls: str
    id: str
    data: Dict[str, Any]

@dataclass
class Model:
    """
    In-memory representation of a CESDM model.

    A ``Model`` holds:

    - class definitions loaded from YAML (:class:`EntityClass`),
    - entity instances (:class:`Entity`),
    - the inheritance graph between classes.

    It provides methods to:

    - load and resolve schema definitions,
    - create and modify entities,
    - validate attribute values and relations,
    - import/export data to various formats.
    """

    def __init__(self):
        self.classes: Dict[str, EntityClass] = {}
        self.entities: Dict[str, Dict[str, Entity]] = {}
        self.inheritance: Dict[str, Union[str, List[str], None]] = {}

    ##  schema loading & introspection


    def resolve_inheritance(self):

        """
        Resolve inheritance between all loaded classes.

        This method:

        - checks for missing base classes,
        - detects cycles in the inheritance graph,
        - merges attributes and relations from parent classes into child classes
          (child definitions override parent definitions in case of name clashes).

        After calling this, :attr:`classes` contains fully merged class definitions
        and :attr:`inheritance` is a mapping::

            {child_class_name: [parent_class_name, ...]}.
        """

        # Normalize/canonicalize the ``parents`` names and coerce to lists
        for cname, c in self.classes.items():
            ext = getattr(c, "parents", None)
            # Accept single string, list/tuple/set of strings, or None/False/""
            if not ext:
                parents: List[str] = []
            elif isinstance(ext, str):
                parents = [ext]
            elif isinstance(ext, (list, tuple, set)):
                parents = [p for p in ext if p]
            else:
                parents = [str(ext)]

            canon_parents: List[str] = []
            for p in parents:
                try:
                    canon_parents.append(self._canonicalize_class(p))
                except Exception:
                    # keep as-is if canonicalization fails
                    canon_parents.append(p)

            c.parents = canon_parents

        # Topological order over possibly multiple parents
        order: List[str] = []
        temp: set[str] = set()
        perm: set[str] = set()

        def visit(name: str) -> None:
            if name in perm:
                return
            if name in temp:
                raise ValueError(f"Inheritance cycle at {name}")
            temp.add(name)

            c = self.classes[name]
            parents = getattr(c, "parents", []) or []
            if isinstance(parents, str):
                parents = [parents]
            for parent in parents:
                if parent not in self.classes:
                    raise ValueError(f"Unknown parent class '{parent}' for '{name}'")
                visit(parent)

            temp.remove(name)
            perm.add(name)
            order.append(name)

        for name in list(self.classes.keys()):
            if name not in perm:
                visit(name)

        # Merge in topo order so all parents are processed before the child
        for name in order:
            c = self.classes[name]
            parents: List[str] = getattr(c, "parents", []) or []
            if isinstance(parents, str):
                parents = [parents]
            if not parents:
                continue

            # Start with a fresh dict and merge parents from left to right.
            merged_attrs: Dict[str, AttributeDef] = {}
            merged_refs: Dict[str, RelationDef] = {}
            abstract_flag = bool(getattr(c, "abstract", False))

            for pname in parents:
                p = self.classes[pname]

                # attributes: first parent wins, then later parents, then child
                for an, a in getattr(p, "attributes", {}).items():
                    if an not in merged_attrs:
                        merged_attrs[an] = a

                # relations: same strategy
                pref = getattr(p, "relations", {}) or {}
                for rn, r in pref.items():
                    if rn not in merged_refs:
                        merged_refs[rn] = r

                # propagate abstract: a non-abstract child becomes abstract if any parent is abstract
                if not abstract_flag and bool(getattr(p, "abstract", False)):
                    abstract_flag = True

            # Finally, child overrides everything
            child_attrs = getattr(c, "attributes", {}) or {}
            child_refs = getattr(c, "relations", {}) or {}

            merged_attrs.update(child_attrs)
            merged_refs.update(child_refs)

            c.attributes = merged_attrs
            c.relations = merged_refs
            c.abstract = abstract_flag

        # Update the public inheritance mapping: always a list of parents
        inh: Dict[str, List[str]] = {}
        for cname, c in self.classes.items():
            parents = getattr(c, "parents", []) or []
            if isinstance(parents, str):
                parents = [parents] if parents else []
            inh[cname] = list(parents)

        self.inheritance = inh


    def build_class_indexes(self):

        """
        Build internal indexes for fast class lookup and introspection.

        This is typically called automatically after loading and resolving the schema.
        It may create helper structures such as:

        - maps from canonical class names to definitions,
        - reverse inheritance mappings,
        - lists of concrete subclasses for abstract base classes.
        """

        # Children map: parent -> set(children)
        children: Dict[str, set] = {c: set() for c in self.classes}
        for cname, ec in self.classes.items():
            parents = getattr(ec, "parents", []) or []
            if isinstance(parents, str):
                parents = [parents]
            for p in parents:
                if p in children:
                    children[p].add(cname)

        # All descendants (transitive closure)
        self.descendants = {c: set() for c in self.classes}

        def dfs(c: str) -> set:
            for ch in children.get(c, ()):
                if ch not in self.descendants[c]:
                    self.descendants[c].add(ch)
                    self.descendants[c] |= dfs(ch)
            return self.descendants[c]

        for c in self.classes:
            dfs(c)

    def debug_schema(self):

        """
        Print a human-readable summary of the loaded schema to stdout.

        Useful for debugging or exploring which classes, attributes and relations
        are available.
        """

        out = {}
        for cname, cdef in self.classes.items():
            out[cname] = {
                "attributes": list(getattr(cdef, "attributes", {}).keys()),
                "relations": list(getattr(cdef, "relations", {}).keys()),
                "parents": getattr(cdef, "parents", None),
                "abstract": getattr(cdef, "abstract", False),
            }
        return out


    



    def add_entity(self, entity_class: str, entity_id: str):

        """
        Create a new entity of a given class with a globally unique ID.

        Parameters
        ----------
        entity_class :
            Name of the CESDM class to instantiate (as defined in the YAML schema).
        entity_id :
            Globally unique identifier for this entity. The ID must not be used
            by any other entity in the model.

        Returns
        -------
        Entity
            The newly created entity.

        Raises
        ------
        ValueError
            If the class does not exist or the entity ID is already used
            in any class.
        """

        cname = self._canonicalize_class(entity_class)

        # global uniqueness prüfen
        for other_cls, ents in self.entities.items():
            if entity_id in ents:
                raise ValueError(
                    f"Duplicate id '{entity_id}' already exists in class '{other_cls}'. "
                    "Entity IDs must be globally unique."
                )

        # Klassen-Definition (inkl. vererbter Attribute – wird in resolve_inheritance gemerged)
        cdef = self.classes.get(cname)
        if cdef is None:
            raise ValueError(f"Unknown entity class: {entity_class}")

        # Daten-Dict mit Defaults initialisieren
        init_data: Dict[str, Any] = {}

        if cname not in self.entities:
            self.entities[cname] = {}
        self.entities[cname][entity_id] = Entity(cls=cname, id=entity_id, data=init_data)

        # now apply defaults via add_attribute so they become AttributeValue
        for aname, adef in cdef.attributes.items():
            if adef.default is not None:
                self.add_attribute(entity_id, aname, adef.default)
        # # Alle Attribute der Klasse durchgehen
        # for aname, adef in cdef.attributes.items():
        #     if adef.default is not None:
        #         # nur Attribute mit Default setzen
        #         init_data[aname] = adef.default
        #     # Wenn du *alle* Attribute sehen willst, selbst ohne Default:
        #     # else:
        #     #     init_data[aname] = None

        # # Entity anlegen
        # if cname not in self.entities:
        #     self.entities[cname] = {}
        # self.entities[cname][entity_id] = Entity(cls=cname, id=entity_id, data=init_data)

    # def _unwrap_attributevalue(self, val):
    #     """
    #     Helper: take either a scalar or an AttributeValue-like dict and return
    #     (value, unit, provenance_ref).
    #     """
    #     if isinstance(val, dict) and "value" in val:
    #         return val.get("value"), val.get("unit"), val.get("provenance_ref")
    #     return val, None, None

    def _find_existing_target_class(self, ref_def: RelationDef, tid: str) -> Optional[str]:
        for cls_name in ref_def.targets:
            if cls_name in self.entities and tid in self.entities[cls_name]:
                return cls_name
        return None

    def _unwrap_attributevalue(self, val):
        """
        Helper: take either a scalar or an AttributeValue-like dict and return
        (value, unit, provenance_ref).
        """
        if isinstance(val, dict) and "value" in val:
            return val.get("value"), val.get("unit"), val.get("provenance_ref")
        return val, None, None

    def add_attribute(
        self,
        entity_id: str,
        attribute_id: str,
        value,
        unit: str | None = None,
        provenance_ref: str | None = None,
    ):
        """
        Set or update an attribute_id on an existing entity.

        Internally attributes are stored as AttributeValue objects::

            {
              "value": <typed value>,
              "unit": "<unit or '-'>",           # optional
              "provenance_ref": "<source-id>",  # optional
            }

        Behaviour:

        - Reads the attribute *type* and *constraints* from the class schema
          (AttributeDef) and coerces the value accordingly.
        - Supports both scalar values and full AttributeValue dicts.
        - Derives default + allowed units from the nested ``unit`` definition
          in the schema (via constraints.enum).
        - Checks both value-constraints (enum/min/max/pattern) and
          unit-constraints (allowed units) before storing.
        """
        ent, cdef = self._get_entity_and_class(entity_id)

        attrs = getattr(cdef, "attributes", {}) or {}
        if attribute_id not in attrs:
            known = list(attrs.keys()) if hasattr(attrs, "keys") else []
            raise KeyError(
                f"[{getattr(cdef, 'name', type(cdef).__name__)}:{entity_id}] "
                f"Unknown attribute '{attribute_id}'. Known: {known}"
            )

        ad = attrs[attribute_id]

        # ---------- derive default & allowed units from ad.unit ----------
        default_unit = None
        allowed_units = None

        udef = getattr(ad, "unit", None)
        if isinstance(udef, str):
            default_unit = udef or None
        elif isinstance(udef, dict):
            cons = udef.get("constraints") or {}
            enum = cons.get("enum")
            if isinstance(enum, (list, tuple)) and enum:
                allowed_units = list(enum)
                default_unit = allowed_units[0]

        if default_unit == "":
            default_unit = None

        # ---------- normalize incoming to AttributeValue dict ------------
        if isinstance(value, dict) and "value" in value:
            raw_value = value.get("value")
            attr_value = dict(value)  # shallow copy
            if unit is not None:
                attr_value["unit"] = unit
            if provenance_ref is not None:
                attr_value["provenance_ref"] = provenance_ref
        else:
            raw_value = value
            attr_value = {"value": value}
            if unit is not None:
                attr_value["unit"] = unit
            if provenance_ref is not None:
                attr_value["provenance_ref"] = provenance_ref

        # ---------- type coercion on VALUE -------------------------------
        atype = self._field(ad, "type")

        # handle numpy scalars gracefully
        try:
            import numpy as _np  # type: ignore
            if isinstance(raw_value, _np.generic):
                raw_value = raw_value.item()
        except Exception:
            pass

        if atype in ("float", "number", "double", "decimal", float):
            if raw_value not in (None, ""):
                raw_value = float(raw_value)
        elif atype in ("int", int, "integer"):
            if raw_value not in (None, ""):
                raw_value = int(raw_value)
        elif atype in ("bool", "boolean", bool):
            if isinstance(raw_value, bool):
                pass
            else:
                s = str(raw_value).strip().lower()
                if s in ("true", "1", "yes"):
                    raw_value = True
                elif s in ("false", "0", "no"):
                    raw_value = False
                else:
                    raise ValueError(
                        f"[{getattr(cdef, 'name', '?')}:{entity_id}] "
                        f"Cannot coerce '{raw_value}' to bool for '{attribute_id}'."
                    )
        # else: leave strings / other types as-is

        attr_value["value"] = raw_value

        # ---------- constraint checks on VALUE ---------------------------
        cons = ad.constraints or Constraint()

        if cons.enum is not None:
            if raw_value not in cons.enum:
                print(
                    f"[{getattr(cdef, 'name', '?')}:{entity_id}] "
                    f"Value '{raw_value}' is not allowed for '{attribute_id}'. "
                    f"Allowed: {cons.enum}"
                )

        if isinstance(raw_value, (int, float)):
            if cons.minimum is not None and raw_value < cons.minimum:
                print(
                    f"[{getattr(cdef, 'name', '?')}:{entity_id}] "
                    f"Value {raw_value} for '{attribute_id}' is below minimum {cons.minimum}."
                )
            if cons.maximum is not None and raw_value > cons.maximum:
                print(
                    f"[{getattr(cdef, 'name', '?')}:{entity_id}] "
                    f"Value {raw_value} for '{attribute_id}' is above maximum {cons.maximum}."
                )

        if cons.pattern is not None:
            import re as _re
            s = "" if raw_value is None else str(raw_value)
            if not _re.fullmatch(cons.pattern, s):
                raise ValueError(
                    f"[{getattr(cdef, 'name', '?')}:{entity_id}] "
                    f"Value '{raw_value}' for '{attribute_id}' does not match pattern '{cons.pattern}'."
                )

        # ---------- determine final UNIT --------------------------------
        current_unit = attr_value.get("unit")
        if current_unit in ("", None):
            if unit is not None:
                current_unit = unit
            elif default_unit is not None:
                current_unit = default_unit
            else:
                current_unit = None

        if current_unit is not None and allowed_units:
            if current_unit not in allowed_units:
                raise ValueError(
                    f"[{getattr(cdef, 'name', '?')}:{entity_id}] "
                    f"Unit '{current_unit}' is not allowed for '{attribute_id}'. "
                    f"Allowed: {allowed_units}"
                )

        if current_unit is not None:
            attr_value["unit"] = current_unit
        else:
            attr_value.pop("unit", None)

        # ---------- store on entity -------------------------------------
        if hasattr(ent, "data") and isinstance(ent.data, dict):
            ent.data[attribute_id] = attr_value
        else:
            setattr(ent, attribute_id, attr_value)

    def add_relation(self, entity_id: str, relation_id: str, target_entity_id: str, **kwargs):

        """
        Set or update a relation on an existing entity.

        Parameters
        ----------
        entity_id :
            Identifier of the entity to modify.
        relation_id :
            Name of the relation field (must be defined in the entity's class).
        target_entity_id :
            Identifier of the target entity.

        Raises
        ------
        KeyError
            If the source entity does not exist.
        ValueError
            If the relation name is unknown, the target does not exist,
            or the target has an incompatible class.
        """

        relation_id = relation_id or kwargs.pop('attribute', None) or kwargs.pop('ref', None)
        target_entity_id = target_entity_id or kwargs.pop('target', None) or kwargs.pop('value', None)
        if relation_id is None or target_entity_id is None:
            print(f"entity_id={entity_id},relation_id={relation_id} and target_entity_id={target_entity_id}.")
            raise TypeError("add_relation requires `relation` and `target_entity_id`.")
        ent, cdef = self._get_entity_and_class(entity_id)
        refs = getattr(cdef, 'relations', {}) or {}
        if relation_id not in refs:
            cname = getattr(cdef, 'name', type(cdef).__name__)
            known = list(refs.keys()) if hasattr(refs, "keys") else []
            raise KeyError(f"[{cname}:{entity_id}] Unknown relation '{relation_id}' (declare it under `relations`). Known relations {known}")
        cls_name = getattr(cdef, 'name', type(cdef).__name__)
        self._set_entity_field(cls_name, entity_id, ent, relation_id, target_entity_id)
        return ent

    def add(self, cls_name: str | None = None, id=None, *values, **kwargs):

        """
        High-level helper to create an entity and set multiple fields at once.

        Parameters
        ----------
        class_name :
            Name of the CESDM class to instantiate.
        id :
            Globally unique entity identifier.
        **fields :
            Attribute and relation name/value pairs. The toolbox determines
            from the schema whether each key is an attribute or relation.

        Returns
        -------
        Entity
            The newly created entity with the given fields populated.

        Raises
        ------
        ValueError
            If the class does not exist, the ID is not unique, an unknown field
            is provided, or a value cannot be coerced/validated.
        """
        if cls_name is None:
            cls_name = kwargs.pop("entityclass", kwargs.pop("class", None))
        if id is None and "id" in kwargs:
            id = kwargs.pop("id")
        if cls_name is None or id is None:
            raise ValueError("add requires class/entityclass and id")
        cname = self._canonicalize_class(cls_name)
        cdef = self.classes[cname]
        order = list(cdef.attributes.keys())
        assembled = dict(kwargs)
        if len(values) > len(order):
            raise ValueError(f"Too many positional values for class '{cname}'. Expected <= {len(order)}")
        for i, v in enumerate(values):
            an = order[i]
            if an not in assembled:
                assembled[an] = v
        return self._add_raw(cname, id=id, **assembled)

    ## Validation

    def validate(self):

        """
        Validate all entities in the model against the loaded schema.

        Checks performed include:

        - presence of required attributes,
        - type correctness of attribute values,
        - compliance with numeric constraints (min/max),
        - compliance with enumerations and patterns,
        - existence and class compatibility of relation targets.

        Returns
        -------
        list of str
            List of human-readable error messages. The list is empty if the
            model passes all validation checks.
        """

        errors = []

        class_map = getattr(self, "classes", {}) or {}
        entity_map = getattr(self, "entities", {}) or {}

        for cname, cdef in class_map.items():
            attrs_def, refs_def = self._collect_inherited_fields(cdef)
            known_fields = set(attrs_def.keys()) | set(refs_def.keys())
            ents = entity_map.get(cname, {}) or {}

            for eid, ent in ents.items():
                data = getattr(ent, "data", {}) or {}

                # 2) Attribute: required + type + constraints
                for aname, adef in attrs_def.items():
                    required = bool(self._get_meta(adef, "required", False))

                    # if aname=="input_origin":
                    #     import pdb
                    #     pdb.set_trace()
                    atype = self._get_meta(adef, "type", None)
                    constraints = self._constraints_to_dict(self._get_meta(adef, "constraints", {}))

                    present = aname in data and data[aname] not in ("", None)

                    if required and not present:
                        errors.append(f"[{cname}:{eid}] Missing required attribute '{aname}'")
                        continue

                    if present:
                        val = data[aname]
                        ok, coerced, msg = self._coerce_and_check_type(val, atype)
                        if not ok:
                            errors.append(f"[{cname}:{eid}] Attribute '{aname}' type error: {msg}")
                        else:
                            # numerical constraints
                            # Only apply numeric constraints for numeric types and when coercion succeeded
                            atype_norm = (str(atype).lower() if atype is not None else None)
                            is_numeric_type = atype_norm in {"float", "number", "integer", "int", "double", "decimal"}

                            if is_numeric_type and ok:
                                if "minimum" in constraints and constraints["minimum"] is not None:
                                    try:
                                        if float(coerced) < float(constraints["minimum"]):
                                            errors.append(
                                                f"[{cname}:{eid}] Attribute '{aname}' violates minimum {constraints['minimum']}: {coerced}"
                                            )
                                    except Exception:
                                        # value couldn’t be compared numerically — treat as type error
                                        errors.append(
                                            f"[{cname}:{eid}] Attribute '{aname}' cannot be compared numerically for minimum"
                                        )

                                if "maximum" in constraints and constraints["maximum"] is not None:
                                    try:
                                        if float(coerced) > float(constraints["maximum"]):
                                            errors.append(
                                                f"[{cname}:{eid}] Attribute '{aname}' violates maximum {constraints['maximum']}: {coerced}"
                                            )
                                    except Exception:
                                        errors.append(
                                            f"[{cname}:{eid}] Attribute '{aname}' cannot be compared numerically for maximum"
                                        )
                            # If the schema accidentally defines numeric constraints on a non-numeric type,
                            # we silently ignore them (or log a warning if you prefer).

                            # enum
                            enum_vals = constraints.get("enum")
                            if enum_vals:
                                try:
                                    if coerced not in enum_vals:
                                        errors.append(
                                            f"[{cname}:{eid}] Attribute '{aname}' not in enum {enum_vals}: {coerced}"
                                        )
                                except Exception:
                                    errors.append(f"[{cname}:{eid}] Attribute '{aname}': cannot evaluate enum against '{val}'")

                            # regex (only meaningful for strings)
                            regex_pat = constraints.get("regex")
                            if regex_pat:
                                import re as _re
                                s = str(coerced)
                                if _re.fullmatch(regex_pat, s) is None:
                                    errors.append(
                                        f"[{cname}:{eid}] Attribute '{aname}' does not match regex '{regex_pat}': '{s}'"
                                    )

                            # length constraints (for strings)
                            if isinstance(coerced, str):
                                min_len = constraints.get("min_length")
                                max_len = constraints.get("max_length")
                                if min_len is not None and len(coerced) < int(min_len):
                                    errors.append(
                                        f"[{cname}:{eid}] Attribute '{aname}' length<{min_len}"
                                    )
                                if max_len is not None and len(coerced) > int(max_len):
                                    errors.append(
                                        f"[{cname}:{eid}] Attribute '{aname}' length>{max_len}"
                                    )

                # 3) Referenzen: required + kardinalität (optional)
                # if cname=="Generator":
                #     pdb.set_trace()
                for rname, rdef in refs_def.items():
                    r_required = bool(self._get_meta(rdef, "required", False))
                    r_constraints = self._constraints_to_dict(self._get_meta(rdef, "constraints", {}))
                    present = rname in data and data[rname] not in ("", None)

                    if r_required and not present:
                        errors.append(f"[{cname}:{eid}] Missing required relation '{rname}'")
                        continue

                    if present:
                        # normalize to list for cardinality checks
                        val = data[rname]
                        targets = val if isinstance(val, (list, tuple)) else [val]

                        # min/max items
                        min_items = r_constraints.get("min_items")
                        max_items = r_constraints.get("max_items")
                        if min_items is not None and len(targets) < int(min_items):
                            errors.append(f"[{cname}:{eid}] Relation '{rname}' has <{min_items} targets")
                        if max_items is not None and len(targets) > int(max_items):
                            errors.append(f"[{cname}:{eid}] Relation '{rname}' has >{max_items} targets")

                        # uniqueness
                        if r_constraints.get("unique", False):
                            if len(set(targets)) != len(targets):
                                errors.append(f"[{cname}:{eid}] Relation '{rname}' contains duplicate target ids")
                        
                        ref_cls = refs_def[rname].target
                        ref_par = ref_cls;
                        # self.inheritance[ref_cls]

                        ref_def = refs_def[rname]
                        allowed_targets = ref_def.targets or []

                        ref_entry, cdef = self._get_entity_and_class(val)

                        if ref_entry is None:
                            # id not found in any class at all
                            tgt_desc = ", ".join(allowed_targets) if allowed_targets else "<any>"
                            errors.append(
                                f"[{cname}:{eid}] Relation '{rname}' with '{val}' not among entities "
                                f"of allowed classes [{tgt_desc}]"
                            )
                        else:
                            if allowed_targets:
                                # entity exists, but check that its class is compatible with at least one target
                                if not any(self.is_class_derived_from(ref_entry.cls, tgt, self.inheritance)
                                           for tgt in allowed_targets):
                                    tgt_desc = ", ".join(allowed_targets)
                                    errors.append(
                                        f"[{cname}:{eid}] Relation '{rname}' with '{val}' is of class '{ref_entry.cls}' "
                                        f"not compatible with any of [{tgt_desc}]"
                                    )

        return errors

    ## Export methods

    def export_json(self, path: str):
        """
        Export all entities to a nested JSON file grouped by class.

        Parameters
        ----------
        path :
            Output file path. Parent directories must exist.

        Notes
        -----
        The JSON structure has the form::

            {
              "ClassName": {
                "entity_id": {
                  "attributes": [
                    {
                      "id": "<attr_name>",
                      "value": ...,
                      "unit": "...",
                      "provenance_ref": "..."
                    },
                    ...
                  ],
                  "relations": [
                    {
                      "id": "<ref_name>",
                      "target_entity_ids": ["...", "..."]
                    },
                    ...
                  ]
                },
                ...
              },
              ...
            }
        """
        import json

        # only folder part:
        directory = os.path.dirname(path)   # -> "./path/folder"
        # create the folder if does not exist
        os.makedirs(directory, exist_ok=True)

        out = {}

        class_map = getattr(self, "classes", {}) or {}
        entity_map = getattr(self, "entities", {}) or {}

        for cname, cdef in class_map.items():
            class_name = getattr(cdef, "name", cname)
            ents = entity_map.get(cname, {}) or {}

            # Collect inherited attributes and relations for that class
            attr_defs, ref_defs = self._collect_inherited_fields(cdef)
            attr_names = list(attr_defs.keys())
            ref_names = list(ref_defs.keys())

            class_blob = {}
            for eid, ent in ents.items():
                data = getattr(ent, "data", {}) or {}

                # attributes block as list-of-objects with "id"
                attrs_list = []
                for a in attr_names:
                    if a in data and data[a] not in ("", None):
                        raw = data[a]
                        if isinstance(raw, dict):
                            spec = dict(raw)
                        else:
                            spec = {"value": raw}
                        attrs_list.append({"id": a, **spec})

                # relations block as list-of-objects with "id"
                refs_list = []
                for r in ref_names:
                    if r in data and data[r] not in ("", None):
                        val = data[r]
                        if isinstance(val, (list, tuple)):
                            targets = [v for v in val if v not in ("", None)]
                        else:
                            targets = [val]
                        if targets:
                            refs_list.append({"id": r, "target_entity_ids": targets})

                if attrs_list or refs_list:
                    class_blob[eid] = {"attributes": attrs_list, "relations": refs_list}

            if class_blob:
                out[class_name] = class_blob

        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    def export_yaml(self, path: str):
            """
            Export all entities to a nested YAML file grouped by class.

            Parameters
            ----------
            path :
                Output file path. Parent directories must exist.

            Notes
            -----
            The YAML structure mirrors :meth:`export_json`, i.e.::

                {
                  "ClassName": {
                    "entity_id": {
                      "attributes": [
                        { "id": "<attr_name>", "value": ..., "unit": "...", "provenance_ref": "..." },
                        ...
                      ],
                      "relations": [
                        { "id": "<ref_name>", "target_entity_ids": ["...", "..."] },
                        ...
                      ]
                    },
                    ...
                  },
                  ...
                }
            """
            # only folder part:
            directory = os.path.dirname(path)   # -> "./path/folder"
            # create the folder if does not exist
            os.makedirs(directory, exist_ok=True)

            out = {}

            class_map = getattr(self, "classes", {}) or {}
            entity_map = getattr(self, "entities", {}) or {}


            for cname, cdef in class_map.items():
                class_name = getattr(cdef, "name", cname)
                ents = entity_map.get(cname, {}) or {}

                # Collect inherited attributes and relations for that class
                attr_defs, ref_defs = self._collect_inherited_fields(cdef)
                attr_names = list(attr_defs.keys())
                ref_names = list(ref_defs.keys())


                class_blob = {}
                for eid, ent in ents.items():
                    data = getattr(ent, "data", {}) or {}

                    # attributes block as list-of-objects with "id"
                    attrs_list = []
                    for a in attr_names:
                        if a in data and data[a] not in ("", None):
                            raw = data[a]
                            if isinstance(raw, dict):
                                spec = dict(raw)
                            else:
                                spec = {"value": raw}
                            attrs_list.append({"id": a, **spec})

                    # relations block as list-of-objects with "id"
                    refs_list = []
                    for r in ref_names:
                        if r in data and data[r] not in ("", None):
                            val = data[r]
                            if isinstance(val, (list, tuple)):
                                targets = [v for v in val if v not in ("", None)]
                            else:
                                targets = [val]
                            if targets:
                                refs_list.append({"id": r, "target_entity_ids": targets})

                    if attrs_list or refs_list:
                        class_blob[eid] = {"attributes": attrs_list, "relations": refs_list}

                if class_blob:
                    out[class_name] = class_blob

            from pathlib import Path
            objpath = Path(path)
            new_path = objpath.with_suffix(".yaml")

            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(out, f, sort_keys=False)

    def export_json_schema(self, path: Union[str, pathlib.Path]):
            """
            Export a JSON Schema describing the structure produced by :meth:`export_json`.

            Parameters
            ----------
            path :
                Output file path for the JSON Schema document.

            Notes
            -----
            The schema is derived from the loaded class definitions, including types,
            required flags and simple constraints.

            It assumes that export_json() produces, per entity:

                {
                  "attributes": {
                    "<attr_name>": {
                      "value": <typed value>,
                      "unit": "<unit or '-'>",
                      "provenance_ref": "<source-id>"
                    },
                    ...
                  },
                  "relations": { ... }
                }
            """
            import json as _json
            import pathlib as _pl

            schema_path = _pl.Path(path)

            class_map = getattr(self, "classes", {}) or {}

            # --- helpers -----------------------------------------------------

            def _jsonschema_type_for_attribute(t: Optional[str]) -> str:
                """Map CESDM/YAML attribute type string to JSON Schema type."""
                if not t:
                    return "string"
                t = str(t).lower()
                if t in ("float", "number", "double", "decimal"):
                    return "number"
                if t in ("integer", "int", "long"):
                    return "integer"
                if t in ("bool", "boolean"):
                    return "boolean"
                # default: string (including datetime, etc. for now)
                return "string"

            def _jsonschema_constraints_for_attribute(ad: AttributeDef) -> Dict[str, Any]:
                """Build JSON Schema constraint keywords from AttributeDef."""
                cons: Dict[str, Any] = {}
                c = ad.constraints or Constraint()
                if c.enum is not None:
                    cons["enum"] = c.enum
                if c.minimum is not None:
                    cons["minimum"] = c.minimum
                if c.maximum is not None:
                    cons["maximum"] = c.maximum
                if c.pattern is not None:
                    cons["pattern"] = c.pattern
                return cons

            def _jsonschema_schema_for_relation(rd: RelationDef) -> (Dict[str, Any], bool):
                """
                Build JSON Schema for a relation value based on cardinality,
                and return (field_schema, is_required).
                """
                card = (rd.cardinality or "1").strip()

                # parse cardinality like "0..1", "1..*", "2..5", "1", "0", "*"
                lower = None
                upper = None
                if ".." in card:
                    lo, hi = card.split("..", 1)
                    lower = int(lo) if lo.isdigit() else 0
                    if hi in ("*", "n"):
                        upper = None
                    else:
                        upper = int(hi) if hi.isdigit() else None
                else:
                    if card in ("*", "n"):
                        lower, upper = 0, None
                    elif card.isdigit():
                        n = int(card)
                        lower, upper = n, n

                # build JSON Schema for the relation value
                if rd.targets:
                    if len(rd.targets) == 1:
                        desc_target = f"'{rd.targets[0]}'"
                    else:
                        desc_target = ", ".join(f"'{t}'" for t in rd.targets)
                        desc_target = f"one of {desc_target}"
                else:
                    desc_target = "any class (no target constraint)"

                base = {
                    "type": "string",
                    "description": f"ID of target class {desc_target}."
                }
                is_required = False

                if lower is None:
                    lower = 0

                if upper is None:
                    # unbounded upper → array of strings
                    field_schema: Dict[str, Any] = {
                        "type": "array",
                        "items": base,
                    }
                    if lower > 0:
                        field_schema["minItems"] = lower
                        is_required = True
                else:
                    if lower == upper == 1:
                        field_schema = base
                        if lower > 0:
                            is_required = True
                    else:
                        field_schema = {
                            "type": "array",
                            "items": base,
                        }
                        field_schema["minItems"] = lower
                        field_schema["maxItems"] = upper
                        if lower > 0:
                            is_required = True

                desc = f"Relation to '{rd.target}' (cardinality {rd.cardinality})."
                field_schema["description"] = desc

                return field_schema, is_required

            # --- build the full JSON Schema ---------------------------------

            schema: Dict[str, Any] = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": "CESDM export_json()",
                "description": (
                    "JSON Schema for the export_json() representation of this CESDM model. "
                    "Top-level keys are class names; second-level keys are entity ids."
                ),
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            }

            for cname, cdef in class_map.items():
                # collect attributes + relations including inheritance
                attrs_def, refs_def = self._collect_inherited_fields(cdef)

                # ---- attributes schema for this class ----
                attr_props: Dict[str, Any] = {}
                attr_required: list[str] = []

                for an, ad in attrs_def.items():
                    # "value" sub-field schema
                    f_type = _jsonschema_type_for_attribute(ad.type)
                    value_field: Dict[str, Any] = {
                        "type": f_type,
                        "description": ad.description
                        or f"Value of attribute '{an}' of class '{cname}'.",
                    }

                    cons = _jsonschema_constraints_for_attribute(ad)
                    value_field.update(cons)

                    if ad.default is not None:
                        value_field["default"] = ad.default

                    # inner object: { value, unit, provenance_ref }
                    inner_props: Dict[str, Any] = {
                        "value": value_field,
                    }

                    # unit sub-schema derived from ad.unit (string or nested dict)
                    unit_schema: Dict[str, Any] = {
                        "type": "string",
                        "description": f"Unit for attribute '{an}' of class '{cname}'.",
                    }
                    udef = getattr(ad, "unit", None)
                    if isinstance(udef, str) and udef:
                        # simple default unit → enum of one
                        unit_schema["enum"] = [udef]
                        unit_schema["default"] = udef
                    elif isinstance(udef, dict):
                        ucons = (udef.get("constraints") or {}) if isinstance(udef, dict) else {}
                        uenum = ucons.get("enum")
                        if isinstance(uenum, (list, tuple)) and uenum:
                            unit_schema["enum"] = list(uenum)
                            unit_schema["default"] = uenum[0]
                        if udef.get("description"):
                            unit_schema["description"] = udef["description"]

                    inner_props["unit"] = unit_schema

                    # provenance_ref (optional)
                    inner_props["provenance_ref"] = {
                        "type": "string",
                        "description": f"Provenance relation for attribute '{an}' of class '{cname}'.",
                    }

                    attr_field: Dict[str, Any] = {
                        "type": "object",
                        "properties": inner_props,
                        "additionalProperties": False,
                    }

                    # inside the attribute object, require "value" if attribute is required
                    if ad.required:
                        attr_field["required"] = ["value"]
                        # and the attributes map must contain this attribute key
                        attr_required.append(an)

                    attr_props[an] = attr_field

                attr_schema: Dict[str, Any] = {
                    "type": "object",
                    "properties": attr_props,
                    "additionalProperties": False,
                }
                if attr_required:
                    # required keys in the attributes map
                    attr_schema["required"] = attr_required

                # ---- relations schema for this class ----
                ref_props: Dict[str, Any] = {}
                ref_required: list[str] = []

                for rn, rd in refs_def.items():
                    ref_field_schema, is_req = _jsonschema_schema_for_relation(rd)
                    ref_props[rn] = ref_field_schema
                    if is_req:
                        ref_required.append(rn)

                ref_schema: Dict[str, Any] = {
                    "type": "object",
                    "properties": ref_props,
                    "additionalProperties": False,
                }
                if ref_required:
                    ref_schema["required"] = ref_required

                # ---- entity schema for this class ----
                entity_schema: Dict[str, Any] = {
                    "type": "object",
                    "properties": {
                        "attributes": attr_schema,
                        "relations": ref_schema,
                    },
                    "required": ["attributes", "relations"],
                    "additionalProperties": False,
                }

                # ---- class-level map: { "<entity_id>": <entity_schema> } ----
                class_entities_schema: Dict[str, Any] = {
                    "type": "object",
                    "description": f"Entities of class '{cname}', keyed by entity id.",
                    "patternProperties": {
                        "^[^\\s]+$": entity_schema  # any non-empty, non-whitespace id
                    },
                    "additionalProperties": False,
                }

                schema["properties"][cname] = class_entities_schema

            with open(schema_path, "w", encoding="utf-8") as f:
                _json.dump(schema, f, indent=2, ensure_ascii=False)

    def export_csv_by_class(self, dir_path: Union[str, pathlib.Path], include_placeholders: bool = True):
        """
        Export entities as narrow CSV tables, one file per class.

        Parameters
        ----------
        dir_path :
            Directory where the CSV files will be written.
        include_placeholders :
            If True, include placeholder rows/fields for attributes that are not set
            on a given entity (useful for templates).
        include_ref_meta :
            If True, include extra metadata columns for relations.

        Notes
        -----
        The exact column layout is documented in the module level docstring
        and in the Frictionless Table Schema created by
        :meth:`export_csv_by_class_with_schema`.
        """
        import csv, pathlib, json as _json

         # create the folder if does not exist
        os.makedirs(dir_path, exist_ok=True)

        p = pathlib.Path(dir_path)
        p.mkdir(parents=True, exist_ok=True)

        # Iterate over all classes so we also export placeholder tables for classes
        # without any entity instances (required for stable schemas/foreign keys).
        for cname, cdef in self.classes.items():
            ents = self.entities.get(cname, {})
            rows = []
            for eid, ent in ents.items():
                wrote_any = False
                for an, ad in cdef.attributes.items():
                    if an in ent.data:
                        raw = ent.data[an]
                        v, unit, prov = self._unwrap_attributevalue(raw)

                        ref = ad.constraints.ref if ad.constraints and ad.constraints.ref else ""

                        # In narrow CSV we only export the core value;
                        # unit/provenance are available via schema or other exports.
                        if isinstance(v, (dict, list)):
                            sval = _json.dumps(v, ensure_ascii=False)
                        else:
                            sval = v

                        rows.append({
                            "entity_id": eid,
                            "attribute": an,
                            "value": sval,
                            "relation": ref,
                        })
                        wrote_any = True

                # optional placeholder for attribute-less classes (e.g., Region)
                if include_placeholders and not wrote_any:
                    rows.append({
                        "entity_id": eid,
                        "attribute": "__exists__",
                        "value": "",
                        "relation": ""
                    })

            # Always write a file (with header), even if empty → helps round-trips
            with open(p / f"{cname}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["entity_id", "attribute", "value", "relation"])
                w.writeheader()
                for r in rows:
                    w.writerow(r)

    def export_csv_by_class_with_schema(self, dir_path: Union[str, pathlib.Path], include_placeholders: bool = True,):
        """
        Export narrow per-class CSV files together with Frictionless Table Schemas.

        Parameters
        ----------
        dir_path :
            Directory for the CSV and ``*.schema.json`` files.
        include_placeholders :
            Passed through to :meth:`export_csv_by_class`.
        """

        import json as _json
        import pathlib as _pl

        p = _pl.Path(dir_path)
        # run the existing exporter
        self.export_csv_by_class(p, include_placeholders=include_placeholders)

        for cname, cdef in self.classes.items():
            csv_path = p / f"{cname}.csv"
            if not csv_path.exists():
                continue

            attrs_def = cdef.attributes or {}
            attr_names = sorted(attrs_def.keys())
            attr_enum = list(attr_names)
            if include_placeholders:
                attr_enum.append("__exists__")

            # collect possible ref-target class names used on attributes
            ref_targets = sorted(
                {ad.constraints.ref for ad in attrs_def.values()
                 if ad.constraints and ad.constraints.ref}
            )

            fields = [
                {
                    "name": "entity_id",
                    "type": "string",
                    "description": f"ID of the entity within class '{cname}'.",
                    "constraints": {"required": True},
                },
                {
                    "name": "attribute",
                    "type": "string",
                    "description": "Attribute name for this entity.",
                    "constraints": {"enum": attr_enum},
                },
                {
                    "name": "value",
                    "type": "string",
                    "description": (
                        "Attribute value; complex values (dict/list) are JSON-encoded. "
                        "Different attributes have different types/constraints; see YAML."
                    ),
                },
                {
                    "name": "relation",
                    "type": "string",
                    "description": (
                        "Target class for the attribute's ref constraint, if any; otherwise empty."
                    ),
                    **({"constraints": {"enum": ref_targets}} if ref_targets else {}),
                },
            ]

            schema = {
                "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
                "name": cname.lower(),
                "title": f"CESDM per-class export: {cname}",
                "fields": fields,
                "primaryKey": ["entity_id", "attribute"],
            }

            schema_path = csv_path.with_suffix(csv_path.suffix + ".schema.json")
            schema_path.write_text(
                _json.dumps(schema, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def export_csv_by_class_wide(self, dir_path: Union[str, pathlib.Path], include_placeholders: bool = True, include_ref_meta: bool = True,):

        """
        Export entities as wide CSV tables, one file per class.

        Parameters
        ----------
        dir_path :
            Directory where the CSV files will be written.
        include_placeholders :
            If True, also create columns for attributes not used by any entity.
        include_ref_meta :
            If True, include extra metadata columns for relations.

        Notes
        -----
        Each CSV contains one row per entity and one column per attribute/relation.
        """
        import csv, pathlib, json as _json
        p = pathlib.Path(dir_path)
        p.mkdir(parents=True, exist_ok=True)

        for cname, cdef in self.classes.items():
            ents = self.entities.get(cname, {})

            # Inheritance-aware merged fields
            attrs_def, refs_def = self._collect_inherited_fields(cdef)
            attr_names = list(attrs_def.keys())
            ref_names  = list(refs_def.keys())

            # Build header
            header = ["entity_id"]
            for rn in ref_names:
                header.append(rn)
                # if include_ref_meta:
                #     header.append(f"{rn}__ref")
            for an in attr_names:
                header.append(an)
                ad = attrs_def[an]
                # if include_ref_meta and ad.constraints and ad.constraints.ref:
                #     header.append(f"{an}__ref")

            rows = []
            for eid, ent in ents.items():
                row = {h: "" for h in header}
                row["entity_id"] = eid
                wrote_any = False

                data = getattr(ent, "data", {}) or {}

                # explicit relations
                for rn in ref_names:
                    if rn in data and data[rn] not in ("", None):
                        val = data[rn]
                        sval = _json.dumps(val, ensure_ascii=False) if isinstance(val, (list, dict, tuple)) else str(val)
                        row[rn] = sval
                        wrote_any = True
                        # if include_ref_meta:
                        #     tgt = refs_def[rn].target if hasattr(refs_def[rn], "target") else ""
                        #     row[f"{rn}__ref"] = tgt

                # attributes
                for an in attr_names:
                    if an in data and data[an] not in ("", None):
                        raw = data[an]
                        v, unit, prov = self._unwrap_attributevalue(raw)

                        # store only the core value into the wide CSV cell
                        if isinstance(v, (dict, list)):
                            sval = _json.dumps(v, ensure_ascii=False)
                        else:
                            sval = str(v)

                        row[an] = sval
                        wrote_any = True
                        ad = attrs_def[an]


                if wrote_any or include_placeholders:
                    rows.append(row)

            with open(p / f"{cname}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=header)
                w.writeheader()
                for r in rows:
                    w.writerow(r)

    def export_csv_by_class_wide_with_schema(self, dir_path: Union[str, pathlib.Path], include_placeholders: bool = True,):

        """
        Convenience wrapper:
        - calls export_csv_by_class_wide(dir_path, include_placeholders=...)
        - for each <ClassName>.csv, writes <ClassName>.csv.schema.json
          with a Frictionless Table Schema describing the *wide* format:
            - entity_id
            - one column per relation (including inherited)
            - one column per attribute (including inherited)
        Types and constraints (enum, min, max, pattern, required, default)
        are derived from the YAML schema (AttributeDef / RelationDef).
        """

        import json as _json
        import pathlib as _pl

        p = _pl.Path(dir_path)
        # run the existing exporter (no __ref meta columns in CSV itself)
        self.export_csv_by_class_wide(
            dir_path=p,
            include_placeholders=include_placeholders,
            include_ref_meta=False,
        )

        class_map = getattr(self, "classes", {}) or {}
        entity_map = getattr(self, "entities", {}) or {}

        for cname, cdef in class_map.items():
            ents = entity_map.get(cname, {})

            attrs_def, refs_def = self._collect_inherited_fields(cdef)
            attr_names = list(attrs_def.keys())
            ref_names  = list(refs_def.keys())

            fields = [
                {
                    "name": "entity_id",
                    "type": "string",
                    "description": f"ID of the entity within class '{cname}'.",
                    "constraints": {"required": True},
                }
            ]

            foreign_keys = []

            # Relations: one column per ref (id or JSON array of ids)
            for rn in ref_names:
                rd = refs_def[rn]
                ref_cons = self._frictionless_constraints_for_relation(rd)
                ref_field = {
                    "name": rn,
                    "type": "string",  # IDs (or JSON array) are serialized as strings
                    "description": (
                        f"Relationd entity id(s) for relation '{rn}' "
                        f"targeting class '{rd.target}'. "
                        "Multi-valued relations are encoded as a JSON array."
                    ),
                }
                if ref_cons:
                    ref_field["constraints"] = ref_cons
                fields.append(ref_field)

                # Add Frictionless foreign key for single-valued relations with exactly one target
                if (rd.cardinality in ("1", "0..1", "1..1") and len(getattr(rd, "targets", []) or []) == 1):
                    tgt = rd.targets[0]
                    foreign_keys.append({
                        "fields": rn,
                        "reference": {"resource": self._slugify_resource_name(f"{tgt}"), "fields": "entity_id"},
                    })

            # Attributes: one column per attribute
            for an in attr_names:
                ad = attrs_def[an]
                ftype = self._frictionless_type_for_attribute(ad.type)
                cons = self._frictionless_constraints_for_attribute(ad)

                desc = ad.description or f"Attribute '{an}' of class '{cname}'."
                if ad.constraints and ad.constraints.ref:
                    desc += f" (Relation to class '{ad.constraints.ref}'.)"

                field = {
                    "name": an,
                    "type": ftype,
                    "description": desc,
                }
                if cons:
                    field["constraints"] = cons
                if ad.default is not None:
                    field["default"] = ad.default

                # CESDM-specific metadata (units, grouping) as an extension
                cesdm_meta = {}
                if getattr(ad, "unit", None) is not None:
                    if isinstance(ad.unit, str):
                        cesdm_meta["unit"] = {"constraints": {"enum": [ad.unit]}}
                    else:
                        cesdm_meta["unit"] = ad.unit
                if getattr(ad, "group", None) is not None:
                    cesdm_meta["group"] = ad.group
                if getattr(ad, "order", None) is not None:
                    cesdm_meta["order"] = ad.order
                if cesdm_meta:
                    field["cesdm"] = cesdm_meta

                fields.append(field)

            schema = {
                "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
                "name": self._slugify_name(cname),
                "title": f"CESDM per-class wide export: {cname}",
                "fields": fields,
                "primaryKey": ["entity_id"],
            }

            if foreign_keys:
                schema["foreignKeys"] = foreign_keys

            csv_path = p / f"{cname}.csv"
            schema_path = csv_path.with_suffix(csv_path.suffix + ".schema.json")
            schema_path.write_text(
                _json.dumps(schema, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def export_csv_by_class_wide_meta(
        self,
        dir_path: str,
        include_placeholders: bool = False,
    ):
        """
        Export entities as wide CSV tables (one file per class), including
        attribute unit and provenance alongside each attribute.

        Columns per class:

            entity_id,
            <attr1>, <attr1>__unit, <attr1>__prov,
            <attr2>, <attr2>__unit, <attr2>__prov,
            ...,
            <ref1>, <ref2>, ...

        Parameters
        ----------
        dir_path :
            Directory where the CSV files will be written.
        include_placeholders :
            If True, include placeholder rows for entities with no attributes
            set (useful for templates).
        """
        import csv, pathlib, json as _json

        p = pathlib.Path(dir_path)
        p.mkdir(parents=True, exist_ok=True)

        for cname, ents in self.entities.items():
            cdef = self.classes[cname]

            # Collect inherited attributes and relations
            attrs_def, refs_def = self._collect_inherited_fields(cdef)
            attr_names = list(attrs_def.keys())
            ref_names = list(refs_def.keys())

            # Build fieldnames: entity_id, then triples per attribute, then refs
            fieldnames = ["entity_id"]
            for an in attr_names:
                fieldnames.append(an)
                fieldnames.append(f"{an}__unit")
                fieldnames.append(f"{an}__prov")
            fieldnames.extend(ref_names)

            rows = []

            for eid, ent in ents.items():
                data = getattr(ent, "data", {}) or {}
                row = {fn: "" for fn in fieldnames}
                row["entity_id"] = eid

                wrote_any = False

                # Attributes (value + unit + provenance_per_attr)
                for an in attr_names:
                    if an in data and data[an] not in ("", None):
                        raw = data[an]
                        v, unit, prov = self._unwrap_attributevalue(raw)

                        # value stringification
                        if isinstance(v, (dict, list)):
                            sval = _json.dumps(v, ensure_ascii=False)
                        else:
                            sval = "" if v is None else str(v)

                        row[an] = sval
                        row[f"{an}__unit"] = "" if unit is None else str(unit)
                        row[f"{an}__prov"] = "" if prov is None else str(prov)
                        wrote_any = True

                # Relations (same as export_csv_by_class_wide)
                for rn in ref_names:
                    if rn not in data or data[rn] in ("", None):
                        continue
                    val = data[rn]
                    if isinstance(val, (list, tuple, set)):
                        row[rn] = _json.dumps(list(val), ensure_ascii=False)
                    else:
                        row[rn] = str(val)
                    wrote_any = True

                if wrote_any or include_placeholders:
                    rows.append(row)

            # Always write file with header
            with open(p / f"{cname}_wide_meta.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                for r in rows:
                    w.writerow(r)
    def export_long_csv(self, path: str):
        """
        Write a 'long' CSV with columns:
        entity_class, entity_id, attribute_id, attribute_value, relation_type, relation_id

        - One row per attribute (value + optional unit)
        - One row per relation target (relation_type + relation_id)
        - Includes inherited attributes & relations
        """
        import csv

        # only folder part:
        directory = os.path.dirname(path)   # -> "./path/folder"
        # create the folder if does not exist
        os.makedirs(directory, exist_ok=True)

        class_map = getattr(self, "classes", {}) or {}
        entity_map = getattr(self, "entities", {}) or {}

        fieldnames = [
            "entity_class",
            "entity_id",
            "attribute_id",
            "attribute_value",
            "attribute_unit",
            "attribute_provenance",
            "relation_type",
            "relation_id",
        ]

        rows = []
        for class_name, cdef in class_map.items():
            attrs, refs = self._collect_inherited_fields(cdef)
            attr_names = list(attrs.keys())
            ref_names  = list(refs.keys())

            ents = entity_map.get(class_name, {}) or {}
            for eid, ent in ents.items():
                data = getattr(ent, "data", {}) or {}

                # Attributes (1 row per attribute)
                for a in attr_names:
                    if a not in data or data[a] in ("", None):
                        continue
                    raw = data[a]
                    v, unit, prov = self._unwrap_attributevalue(raw)

                    rows.append({
                        "entity_class": class_name,
                        "entity_id": eid,
                        "attribute_id": a,
                        "attribute_value": v,
                        "attribute_unit": unit or "",
                        "attribute_provenance": prov or "",
                        "relation_type": "",
                        "relation_id": "",
                    })

                # Relations (1 row per target id)
                for r in ref_names:
                    if r not in data or data[r] in ("", None):
                        continue
                    value = data[r]
                    targets = value if isinstance(value, (list, tuple)) else [value]
                    for tgt in targets:
                        if tgt in ("", None):
                            continue
                        rows.append({
                            "entity_class": class_name,
                            "entity_id": eid,
                            "attribute_id": "",
                            "attribute_value": "",
                            "attribute_unit": "",
                            "attribute_provenance": "",
                            "relation_type": r,
                            "relation_id": tgt,
                        })

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def export_long_csv_with_schema(self, path: Union[str, pathlib.Path]):
        """
        Export a long CSV together with a Frictionless Table Schema.

        Parameters
        ----------
        path :
            Output CSV file path. The corresponding schema will be written
            to ``<path>.schema.json`` or a similar name.
        """

        import json as _json
        import pathlib as _pl

        p = _pl.Path(path)
        # run the existing exporter
        self.export_long_csv(str(p))

        class_map = getattr(self, "classes", {}) or {}

        all_attr_names = set()
        all_ref_names = set()
        for cname, cdef in class_map.items():
            attrs_def, refs_def = self._collect_inherited_fields(cdef)
            all_attr_names.update(attrs_def.keys())
            all_ref_names.update(refs_def.keys())

        schema = {
            "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
            "name": self._slugify_name(p.stem),
            "title": f"CESDM long export: {p.name}",
            "fields": [
                {
                    "name": "entity_class",
                    "type": "string",
                    "description": "Name of the entity class.",
                    "constraints": {
                        "required": True,
                        "enum": sorted(class_map.keys()),
                    },
                },
                {
                    "name": "entity_id",
                    "type": "string",
                    "description": "ID of the entity within the class.",
                    "constraints": {
                        "required": True,
                    },
                },
                {
                    "name": "attribute_id",
                    "type": "string",
                    "description": "Name of the attribute (empty when row represents a relation).",
                    "constraints": {
                        "enum": sorted(all_attr_names),
                    },
                },
                {
                    "name": "attribute_value",
                    "type": "string",
                    "description": "Serialized attribute value (empty for relation rows).",
                },
                {
                    "name": "relation_type",
                    "type": "string",
                    "description": "Relation name / role (empty for attribute rows).",
                    "constraints": {
                        "enum": sorted(all_ref_names),
                    },
                },
                {
                    "name": "relation_id",
                    "type": "string",
                    "description": "Target entity id for the relation (empty for attribute rows).",
                },
            ],
            "primaryKey": [
                "entity_class",
                "entity_id",
                "attribute_id",
                "relation_type",
                "relation_id",
            ],
        }

        schema_path = p.with_suffix(p.suffix + ".schema.json")
        schema_path.write_text(
            _json.dumps(schema, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def export_datapackage(self, dir_path):
        """
        Export a Frictionless datapackage.json ONLY for by_class_wide resources,
        embedding each schema inline (no external schema files required).
        """
        import json
        import pathlib


        base = pathlib.Path(dir_path)
        bcw_dir = base / "energy_system_data"
        bcw_dir.mkdir(parents=True, exist_ok=True)

        self.export_csv_by_class_wide_with_schema(bcw_dir)

        resources = []

        for cname in sorted(self.classes.keys()):
            csv_path = bcw_dir / f"{cname}.csv"
            schema_path = bcw_dir / f"{cname}.csv.schema.json"

            if not csv_path.exists():
                continue
            if not schema_path.exists():
                raise FileNotFoundError(f"Missing schema file: {schema_path}")

            schema_obj = json.loads(schema_path.read_text(encoding="utf-8"))

            rname = f"{cname.lower()}"
            cdef = self.classes.get(cname)
            desc = getattr(cdef, "description", None) if cdef else None

            resources.append({
                "name": rname,
                "path": str((pathlib.Path("energy_system_data") / f"{cname}.csv").as_posix()),
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "title": cname,
                "description": desc or "",
                "schema": schema_obj,
            })

        pkg = {
            "profile": "data-package",
            "name": base.name.lower().replace(" ", "-"),
            "resources": resources,
        }

        out_path = base / "datapackage.json"
        out_path.write_text(json.dumps(pkg, indent=2, ensure_ascii=False), encoding="utf-8")
        return out_path

    # def export_datapackage(
    #     self,
    #     base_dir: Union[str, pathlib.Path],
    #     name: str = "cesdm-model",
    #     title: Optional[str] = None,
    #     description: str = "",
    #     include_long: bool = False,
    #     include_by_class: bool = False,
    #     include_by_class_wide: bool = True,
    #     include_placeholders: bool = True,) -> pathlib.Path:
    #     """
    #     Export the model as a Frictionless Data Package.

    #     Parameters
    #     ----------
    #     base_dir :
    #         Output directory for ``datapackage.json`` and CSV resources.
    #     name :
    #         Machine-readable name of the data package.
    #     title :
    #         Optional human-readable title.
    #     include_long :
    #         Whether to include the long CSV representation as a resource.
    #     include_by_class :
    #         Whether to include narrow per-class CSVs.
    #     include_by_class_wide :
    #         Whether to include wide per-class CSVs (default).
    #     """

    #     import json as _json
    #     import pathlib as _pl

    #     base = _pl.Path(base_dir)
    #     base.mkdir(parents=True, exist_ok=True)

    #     resources = []

    #     # ---- 1) Long CSV ----
    #     if include_long:
    #         long_path = base / "long.csv"
    #         # uses helper that also writes long.csv.schema.json
    #         self.export_long_csv_with_schema(long_path)

    #         resources.append({
    #             "name": "long",
    #             "path": long_path.name,  # "long.csv"
    #             "profile": "tabular-data-resource",
    #             "schema": long_path.name + ".schema.json",  # "long.csv.schema.json"
    #         })

    #     # ---- 2) Per-class narrow CSVs ----
    #     if include_by_class:
    #         bc_dir = base / "by_class"
    #         bc_dir.mkdir(exist_ok=True)

    #         # will write <ClassName>.csv + .schema.json in bc_dir
    #         self.export_csv_by_class_with_schema(
    #             bc_dir,
    #             include_placeholders=include_placeholders,
    #         )

    #         for cname in sorted(self.classes.keys()):
    #             csv_path = bc_dir / f"{cname}.csv"
    #             if not csv_path.exists():
    #                 continue

    #             schema_path = csv_path.with_suffix(csv_path.suffix + ".schema.json")

    #             res_name = self._slugify_resource_name(f"{cname}_by_class_wide")

    #             resources.append({
    #                 "name": res_name,                           # e.g. "servicedemandmodel_by_class"
    #                 "path": str(csv_path.relative_to(base)),    # path may keep CamelCase
    #                 "profile": "tabular-data-resource",
    #                 "schema": str(schema_path.relative_to(base)),
    #             })

    #     # ---- 3) Per-class wide CSVs ----
    #     if include_by_class_wide:
    #         bcw_dir = base / "by_class_wide"
    #         bcw_dir.mkdir(exist_ok=True)

    #         # will write <ClassName>.csv + .schema.json in bcw_dir
    #         self.export_csv_by_class_wide_with_schema(
    #             bcw_dir,
    #             include_placeholders=include_placeholders,
    #         )

    #         for cname in sorted(self.classes.keys()):
    #             csv_path = bcw_dir / f"{cname}.csv"
    #             if not csv_path.exists():
    #                 continue

    #             schema_path = csv_path.with_suffix(csv_path.suffix + ".schema.json")

    #             res_name = self._slugify_resource_name(f"{cname}_by_class")

    #             resources.append({
    #                 "name": res_name,                           # e.g. "servicedemandmodel_by_class"
    #                 "path": str(csv_path.relative_to(base)),    # path may keep CamelCase
    #                 "profile": "tabular-data-resource",
    #                 "schema": str(schema_path.relative_to(base)),
    #             })

    #     # ---- 4) Build datapackage.json ----
    #     dp = {
    #         "profile": "data-package",
    #         "name": name,
    #         "title": title or name,
    #         "description": description,
    #         "resources": resources,
    #     }

    #     dp_path = base / "datapackage.json"
    #     dp_path.write_text(
    #         _json.dumps(dp, indent=2, ensure_ascii=False),
    #         encoding="utf-8",
    #     )

    #     return dp_path





        """
        Export all entities as a single long CSV table.

        Parameters
        ----------
        path :
            Output CSV file path.

        Notes
        -----
        The long format has one row per attribute or relation and is suited for
        generic ETL pipelines and graph-oriented processing.
        """
        import csv

        class_map = getattr(self, "classes", {}) or {}
        entity_map = getattr(self, "entities", {}) or {}

        fieldnames = [
            "entity_class",
            "entity_id",
            "attribute_id",
            "attribute_value",
            "relation_type",
            "relation_id",
        ]

        rows = []
        for class_name, cdef in class_map.items():
            attrs, refs = self._collect_inherited_fields(cdef)
            attr_names = list(attrs.keys())
            ref_names  = list(refs.keys())

            ents = entity_map.get(class_name, {}) or {}
            for eid, ent in ents.items():
                data = getattr(ent, "data", {}) or {}

                # Attributes
                for a in attr_names:
                    has_val  = a in data and data[a] not in ("", None)
                    if has_val:
                        rows.append({
                            "entity_class": class_name,
                            "entity_id": eid,
                            "attribute_id": a if has_val else "",
                            "attribute_value": data.get(a, "") if has_val else "",
                            "relation_type": "",
                            "relation_id": "",
                        })

                # Relations (1 row per target id)
                for r in ref_names:
                    if r not in data or data[r] in ("", None):
                        continue
                    value = data[r]
                    targets = value if isinstance(value, (list, tuple)) else [value]
                    for tgt in targets:
                        if tgt in ("", None):
                            continue
                        rows.append({
                            "entity_class": class_name,
                            "entity_id": eid,
                            "attribute_id": "",
                            "attribute_value": "",
                            "relation_type": r,
                            "relation_id": tgt,
                        })

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


    ## Import methods

    def import_json(self, path: str, *, strict_unknown: bool = False):
        """
        Import entities from a nested JSON file (as produced by :meth:`export_json`).

        Parameters
        ----------
        path :
            Input JSON file path.
        strict_unknown :
            If True, raise errors for unknown classes/attributes/relations.
            If False, unknowns are collected in the summary.

        Returns
        -------
        dict
            Summary dictionary with counts of created entities, set attributes,
            set relations, and a list of unknown fields encountered.

        Notes
        -----
        The JSON is expected to follow the export format, where each attribute
        entry under "attributes" is either:

        - a raw scalar value (legacy format), or
        - a full AttributeValue object with keys 'value', 'unit', 'provenance_ref'.
        """
        import json

        class_map = getattr(self, "classes", {}) or {}

        # Precompute known inherited fields per class
        known_attrs = {}
        known_refs  = {}
        for cname, cdef in class_map.items():
            a, r = self._collect_inherited_fields(cdef)
            known_attrs[cname] = set(a.keys())
            known_refs[cname]  = set(r.keys())

        created = set_attr = set_ref = 0
        unknowns = []

        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f) or {}

        for class_name, items in (payload or {}).items():
            if class_name not in class_map:
                unknowns.append((class_name, None, "unknown class"))
                if strict_unknown:
                    continue
                else:
                    continue

            cdef = class_map[class_name]

            for eid, block in (items or {}).items():
                # ensure entity exists
                exists = any(eid in ents_by_cls for ents_by_cls in self.entities.values())
                if not exists:
                    self.add_entity(entity_class=class_name, entity_id=eid)
                    created += 1

                # -------- attributes: dict OR list-of-objects-with-id --------
                attrs_block = block.get("attributes") or {}
                if isinstance(attrs_block, dict):
                    attr_items = attrs_block.items()
                elif isinstance(attrs_block, list):
                    attr_items = []
                    for rec in attrs_block:
                        if not isinstance(rec, dict):
                            continue
                        aname = rec.get("id") or rec.get("name")
                        if not aname:
                            continue
                        # pass everything except "id" to add_attribute
                        aval = {k: v for k, v in rec.items() if k != "id"}
                        # if it's just {"value": scalar}, that's fine; add_attribute
                        # already knows how to handle dicts with "value"/"unit"/"provenance_ref".
                        if not aval:
                            continue
                        attr_items.append((aname, aval))
                else:
                    attr_items = []

                for aname, aval in attr_items:
                    if aname in known_attrs[class_name]:
                        if aval not in ("", None):
                            # aval may be a scalar or an AttributeValue dict:
                            # add_attribute handles both cases.
                            self.add_attribute(eid, aname, aval)
                            set_attr += 1
                    else:
                        unknowns.append((class_name, eid, f"unknown attribute: {aname}"))
                        if strict_unknown:
                            continue

                # -------- relations: dict OR list-of-objects-with-id --------
                refs_block = block.get("relations") or {}
                ref_items = []

                if isinstance(refs_block, dict):
                    # old style: { ref_name: id_or_list }
                    ref_items = list(refs_block.items())
                elif isinstance(refs_block, list):
                    # new style: [ {id: ref_name, target_entity_ids: [...]}, ... ]
                    for rec in refs_block:
                        if not isinstance(rec, dict):
                            continue
                        rname = rec.get("id") or rec.get("name")
                        if not rname:
                            continue
                        raw_ids = (
                            rec.get("target_entity_ids")
                            or rec.get("targets")
                            or rec.get("value")
                            or rec.get("target_entity_id")
                        )
                        if raw_ids in ("", None):
                            continue
                        if isinstance(raw_ids, (list, tuple)):
                            ids = [v for v in raw_ids if v not in ("", None)]
                        else:
                            ids = [raw_ids]
                        ref_items.append((rname, ids))

                for rname, rid in ref_items:
                    if rname in known_refs[class_name]:
                        targets = rid if isinstance(rid, (list, tuple)) else [rid]
                        for tgt in targets:
                            if tgt not in ("", None):
                                self.add_relation(entity_id=eid, relation_id=rname, target_entity_id=tgt)
                                set_ref += 1
                    else:
                        unknowns.append((class_name, eid, f"unknown relation: {rname}"))
                        if strict_unknown:
                            continue


        return {
            "created_entities": created,
            "set_attributes": set_attr,
            "set_relations": set_ref,
            "unknowns": unknowns,
        }

    def import_yaml(self, path: str, *, strict_unknown: bool = False):
        """
        Import entities from a nested YAML file with a structure similar to the JSON export.

        Supports both:

        Old style (attributes/relations as dicts):

            ClassName:
              entity_id:
                attributes:
                  attr_name: <scalar or {value,unit,provenance_ref}>
                relations:
                  ref_name: target_entity_id_or_list

        New style (attributes/relations as list-of-objects with "id"):

            ClassName:
              entity_id:
                attributes:
                  - id: attr_name
                    value: ...
                    unit: ...
                    provenance_ref: ...
                relations:
                  - id: ref_name
                    target_entity_ids: ["...", "..."]

        Parameters
        ----------
        path :
            Input YAML file path.
        strict_unknown :
            Same semantics as in :meth:`import_json`.

        Returns
        -------
        dict
            Summary information about created and updated entities.
        """
        import yaml

        def _normalize_section(section, key_candidates=("id", "name"), prefix="item"):
            """
            Accept dict or list and always return dict keyed by id/name/fallback.

            This is mainly here to allow for a future list-of-entities format,
            but for current exports (dict of entity_id -> block) it just passes through.
            """
            if not section:
                return {}
            if isinstance(section, dict):
                return section
            if isinstance(section, list):
                out = {}
                for i, rec in enumerate(section):
                    if not isinstance(rec, dict):
                        raise TypeError(f"Expected dict entries, got {type(rec)}: {rec!r}")
                    key = None
                    for kc in key_candidates:
                        v = rec.get(kc)
                        if v not in ("", None):
                            key = v
                            break
                    if key is None:
                        key = f"{prefix}_{i}"
                    out[key] = rec
                return out
            raise TypeError(f"Unsupported section type: {type(section)}")

        class_map = getattr(self, "classes", {}) or {}

        # Precompute known inherited fields per class
        known_attrs: dict[str, set[str]] = {}
        known_refs: dict[str, set[str]] = {}
        for cname, cdef in class_map.items():
            attrs_def, refs_def = self._collect_inherited_fields(cdef)
            known_attrs[cname] = set(attrs_def.keys())
            known_refs[cname] = set(refs_def.keys())

        created = 0
        set_attr = 0
        set_ref = 0
        unknowns: list[tuple[str, str | None, str]] = []

        with open(path, "r", encoding="utf-8") as f:
            payload = yaml.safe_load(f) or {}

        for class_name, section in (payload or {}).items():
            if class_name not in class_map:
                # unknown class
                unknowns.append((class_name, None, "unknown class"))
                if strict_unknown:
                    continue
                else:
                    continue

            # section is either:
            # - dict: {entity_id: {...}}
            # - list: [ {id: "...", ...}, ... ]
            entities = _normalize_section(section, key_candidates=("id", "name"), prefix=class_name)

            for eid, block in (entities or {}).items():
                # ensure entity exists
                if class_name not in self.entities:
                    self.entities[class_name] = {}
                if eid not in self.entities[class_name]:
                    self.add_entity(class_name, eid)
                    created += 1

                # -------- attributes: dict OR list-of-objects-with-id --------
                attrs_block = block.get("attributes") or {}
                if isinstance(attrs_block, dict):
                    attr_items = attrs_block.items()
                elif isinstance(attrs_block, list):
                    attr_items = []
                    for rec in attrs_block:
                        if not isinstance(rec, dict):
                            continue
                        aname = rec.get("id") or rec.get("name")
                        if not aname:
                            continue
                        aval = {k: v for k, v in rec.items() if k != "id"}
                        # If user only provided "value", that's fine; add_attribute handles dicts
                        if not aval:
                            continue
                        attr_items.append((aname, aval))
                else:
                    attr_items = []

                for aname, aval in attr_items:
                    if aname in known_attrs[class_name]:
                        if aval not in ("", None):
                            self.add_attribute(eid, aname, aval)
                            set_attr += 1
                    else:
                        unknowns.append((class_name, eid, f"unknown attribute: {aname}"))
                        if strict_unknown:
                            continue

                # -------- relations: dict OR list-of-objects-with-id --------
                refs_block = block.get("relations") or {}
                ref_items: list[tuple[str, list[str]]] = []

                if isinstance(refs_block, dict):
                    # old style: { ref_name: id_or_list }
                    for rname, rid in refs_block.items():
                        if rid in ("", None):
                            continue
                        if isinstance(rid, (list, tuple)):
                            ids = [v for v in rid if v not in ("", None)]
                        else:
                            ids = [rid]
                        ref_items.append((rname, ids))
                elif isinstance(refs_block, list):
                    # new style: [ {id: ref_name, target_entity_ids: [...]}, ... ]
                    for rec in refs_block:
                        if not isinstance(rec, dict):
                            continue
                        rname = rec.get("id") or rec.get("name")
                        if not rname:
                            continue
                        raw_ids = (
                            rec.get("target_entity_ids")
                            or rec.get("targets")
                            or rec.get("value")
                            or rec.get("target_entity_id")
                        )
                        if raw_ids in ("", None):
                            continue
                        if isinstance(raw_ids, (list, tuple)):
                            ids = [v for v in raw_ids if v not in ("", None)]
                        else:
                            ids = [raw_ids]
                        ref_items.append((rname, ids))

                for rname, ids in ref_items:
                    if rname in known_refs[class_name]:
                        for tgt in ids:
                            if tgt not in ("", None):
                                self.add_relation(entity_id=eid, relation_id=rname, target_entity_id=tgt)
                                set_ref += 1
                    else:
                        unknowns.append((class_name, eid, f"unknown relation: {rname}"))
                        if strict_unknown:
                            continue

        return {
            "created_entities": created,
            "set_attributes": set_attr,
            "set_relations": set_ref,
            "unknowns": unknowns,
        }

    def import_csv_by_class(self, dir_path: Union[str, pathlib.Path], create_missing_refs: bool = False):

        """
        Import entities from narrow per-class CSV files.

        Parameters
        ----------
        dir_path :
            Directory containing per-class CSV files.
        create_missing_refs :
            If True, relationd entities that do not exist will be auto-created
            as empty shells.
        strict_unknown :
            If True, treat unknown columns/values as errors.

        Returns
        -------
        dict
            Summary of created/updated entities and encountered issues.
        """
        import csv, pathlib, os
        p = pathlib.Path(dir_path)
        if not p.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        # --- pass 1: create all entities we see in files that match known classes
        for file in sorted(p.glob("*.csv")):
            cname = file.stem
            if cname not in self.classes:
                # ignore files that don't correspond to a known class
                continue
            with open(file, "r", encoding="utf-8") as f:
                rdr = csv.DictReader(f)
                for row in rdr:
                    eid = row.get("entity_id")
                    if not eid:
                        continue
                    # already exists anywhere?
                    exists = any(eid in ents_by_cls for ents_by_cls in self.entities.values())
                    if not exists:
                        self.add_entity(entity_class=cname, entity_id=eid)

        # --- pass 2: populate attributes and relations
        for file in sorted(p.glob("*.csv")):
            cname = file.stem
            if cname not in self.classes:
                continue
            cdef = self.classes[cname]
            with open(file, "r", encoding="utf-8") as f:
                rdr = csv.DictReader(f)
                for row in rdr:
                    eid       = row.get("entity_id")
                    attr      = row.get("attribute")
                    val       = row.get("value")
                    ref_meta  = (row.get("relation") or "").strip()

                    if not eid or not attr:
                        continue
                    # skip placeholders
                    if attr.startswith("__"):
                        continue

                    ad = cdef.attributes.get(attr)
                    if not ad:
                        raise ValueError(f"[{cname}:{eid}] Unknown attribute in {file.name}: {attr}")

                    # Relation attribute?
                    if ad.constraints and ad.constraints.ref:
                        ref_cls_expected = ad.constraints.ref
                        # Convention: relationd ID is in 'value'
                        target_entity_id = (val or "").strip()
                        # If someone placed the ID in 'relation' instead (and it's not the class name), accept it
                        if ref_meta and ref_meta != ref_cls_expected:
                            target_entity_id = ref_meta
                        if not target_entity_id:
                            raise ValueError(
                                f"[{cname}:{eid}] Missing relationd id for '{attr}' "
                                f"(expected {ref_cls_expected} id in 'value' or 'relation')."
                            )
                        # Optionally auto-create the relationd entity (covers empty classes like Region)
                        if create_missing_refs and (ref_cls_expected not in self.entities or target_entity_id not in self.entities[ref_cls_expected]):
                            self.add_entity(entity_class=ref_cls_expected, entity_id=target_entity_id)

                        self.add_relation(entity_id=eid, attribute=attr, relation=target_entity_id)
                    else:
                        # Normal value; best-effort coerce based on schema type
                        coerced = self._coerce_for_attr(cname, attr, val)
                        self.add_attribute(entity_id=eid, attribute_id=attr, value=coerced)

    def import_csv_by_class_wide(
            self,
            dir_path: Union[str, pathlib.Path],
            create_missing_refs: bool = False,
        ):
            """
            Read one wide CSV per entity class (file name <ClassName>.csv).
            Columns accepted:
              - entity_id
              - one column per attribute (including inherited)
              - one column per explicit relation (including inherited)
              - optional <name>__ref columns are ignored on import (metadata only)
            Relation cells may contain a single id or a JSON array of ids for multi-cardinality.
            """
            import csv, pathlib, json as _json
            p = pathlib.Path(dir_path)
            if not p.exists():
                return  # nothing to read

            for cname, cdef in self.classes.items():
                file = p / f"{cname}.csv"
                if not file.exists():
                    continue

                attrs_def, refs_def = self._collect_inherited_fields(cdef)
                attr_names = list(attrs_def.keys())
                ref_names  = list(refs_def.keys())

                with open(file, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    if "entity_id" not in reader.fieldnames:
                        raise ValueError(f"{file.name} missing 'entity_id' column")

                    for row in reader:
                        eid = str(row.get("entity_id", "")).strip()
                        if not eid:
                            continue

                        if cname not in self.entities or eid not in self.entities[cname]:
                            self.add_entity(entity_class=cname, entity_id=eid)

                        # explicit relations
                        for rn in ref_names:
                            if rn not in row:
                                continue
                            raw_val = row.get(rn, "")
                            if raw_val in ("", None):
                                continue

                            # parse single or list
                            targets = None
                            txt = str(raw_val).strip()
                            try:
                                parsed = _json.loads(txt)
                                if isinstance(parsed, list):
                                    targets = [str(v).strip() for v in parsed if v not in ("", None)]
                                else:
                                    targets = [str(parsed).strip()]
                            except Exception:
                                if ";" in txt:
                                    targets = [t.strip() for t in txt.split(";") if t.strip()]
                                elif "," in txt:
                                    targets = [t.strip() for t in txt.split(",") if t.strip()]
                                else:
                                    targets = [txt]

                            if not targets:
                                continue

                            ref_def = refs_def[rn]
                            if create_missing_refs:
                                for tid in targets:
                                    if not ref_def.targets:
                                        continue  # no constraint → nothing to auto-create

                                    existing_cls = self._find_existing_target_class(ref_def, tid)
                                    if existing_cls is None:
                                        # create in the first allowed class
                                        primary_cls = ref_def.targets[0]
                                        self.add_entity(entity_class=primary_cls, entity_id=tid)

                            if len(targets) == 1:
                                self.add_relation(entity_id=eid, relation_id=rn, target_entity_id=targets[0])
                            else:
                                ent = self.entities[cname][eid]
                                self._set_entity_field(cname, eid, ent, rn, targets)

                        # attributes
                        for an in attr_names:
                            if an not in row:
                                continue
                            raw_val = row.get(an, "")
                            if raw_val in ("", None):
                                continue
                            ad = attrs_def[an]
                            coerced = self._coerce_for_attr(cname, an, raw_val)
                            self.add_attribute(entity_id=eid, attribute=an, value=coerced)

    def import_csv_by_class_wide_meta(
        self,
        dir_path: str,
        create_missing_refs: bool = False,
        strict_unknown: bool = False,
    ):
        """
        Import entities and attributes from wide+meta CSV tables (one file per class).

        Expected column pattern per file:

            entity_id,
            <attr1>, <attr1>__unit, <attr1>__prov,
            <attr2>, <attr2>__unit, <attr2>__prov,
            ...,
            <ref1>, <ref2>, ...

        Parameters
        ----------
        dir_path :
            Directory containing per-class *_wide_meta.csv files.
        create_missing_refs :
            If True, relationd entities that do not exist will be auto-created
            as empty shells.
        strict_unknown :
            If True, treat unknown columns/values as errors.

        Returns
        -------
        dict
            Summary of created/updated entities and encountered issues.
        """
        import csv, pathlib, os, json as _json

        dir_path = pathlib.Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        class_map = self.classes
        created_entities = 0
        set_attributes = 0
        set_relations = 0
        unknowns: list[tuple[str, str, str]] = []

        for cname, cdef in class_map.items():
            file = dir_path / f"{cname}_wide_meta.csv"
            if not file.exists():
                continue

            # Collect known attrs/refs for this class
            attrs_def, refs_def = self._collect_inherited_fields(cdef)
            attr_names = list(attrs_def.keys())
            ref_names = list(refs_def.keys())

            with open(file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if "entity_id" not in reader.fieldnames:
                    raise ValueError(f"{file.name} missing 'entity_id' column")

                for row in reader:
                    eid = str(row.get("entity_id", "")).strip()
                    if not eid:
                        continue

                    # ensure entity exists
                    if cname not in self.entities or eid not in self.entities[cname]:
                        self.add_entity(entity_class=cname, entity_id=eid)
                        created_entities += 1

                    # attributes: value + meta per attribute
                    for an in attr_names:
                        if an not in row:
                            continue
                        raw_val = row.get(an, "")
                        if raw_val in ("", None):
                            continue

                        # Pick up unit/provenance if present
                        unit = (row.get(f"{an}__unit") or "").strip() or None
                        prov = (row.get(f"{an}__prov") or "").strip() or None

                        # Coerce type according to schema
                        coerced = self._coerce_for_attr(cname, an, raw_val)
                        self.add_attribute(
                            entity_id=eid,
                            attribute=an,
                            value=coerced,
                            unit=unit,
                            provenance_ref=prov,
                        )
                        set_attributes += 1

                    # relations (same as import_csv_by_class_wide)
                    for rn in ref_names:
                        if rn not in row:
                            continue
                        raw_val = row.get(rn, "")
                        if raw_val in ("", None):
                            continue

                        # parse single or list
                        targets = None
                        txt = str(raw_val).strip()
                        try:
                            parsed = _json.loads(txt)
                            if isinstance(parsed, list):
                                targets = [str(v).strip() for v in parsed if v not in ("", None)]
                            else:
                                targets = [str(parsed).strip()]
                        except Exception:
                            targets = [txt]

                        for tgt in targets:
                            if not tgt:
                                continue
                            if create_missing_refs:
                                # create shell if missing
                                if rn in refs_def:
                                    rdef = refs_def[rn]
                                    tgt_class = rdef.target
                                    if tgt_class and tgt_class not in self.entities:
                                        self.add_entity(entity_class=tgt_class, entity_id=tgt)
                            self.add_relation(eid, rn, tgt)
                            set_relations += 1

        return {
            "created_entities": created_entities,
            "set_attributes": set_attributes,
            "set_relations": set_relations,
            "unknowns": unknowns,
        }

    def import_long_csv(self, path: str, *, strict_unknown: bool = False):
        """
        Read a 'long' CSV with columns:
        entity_class, entity_id, attribute_id, attribute_value, relation_type, relation_id

        - Sets attributes and relations
        - Matches against inherited schema per class
        - Unknown fields: skipped (collectable) unless strict_unknown=True
        Returns a small summary dict.
        """
        import csv
        from collections import defaultdict

        class_map = getattr(self, "classes", {}) or {}

        # Pre-compute known (inherited) fields per class
        known_attrs = {}
        known_refs  = {}
        for cname, cdef in class_map.items():
            attrs, refs = self._collect_inherited_fields(cdef)
            known_attrs[cname] = set(attrs.keys())
            known_refs[cname]  = set(refs.keys())

        required_cols = {
            "entity_class",
            "entity_id",
            "attribute_id",
            "attribute_value",
            "relation_type",
            "relation_id",
        }

        created_entities = 0
        set_attr = set_ref = 0
        unknowns = []
        per_class_rows = defaultdict(int)

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not required_cols.issubset(reader.fieldnames or []):
                raise ValueError(f"CSV must contain columns exactly: {', '.join(sorted(required_cols))}")

            for i, row in enumerate(reader, start=2):  # header is line 1
                cname = (row.get("entity_class") or "").strip()
                eid   = (row.get("entity_id") or "").strip()

                if not cname or not eid:
                    continue

                if cname not in class_map:
                    msg = "unknown class"
                    unknowns.append((i, cname, eid, "", msg))
                    if strict_unknown:
                        continue
                    else:
                        continue

                # ensure entity exists
                if cname not in self.entities:
                    self.entities[cname] = {}
                if eid not in self.entities[cname]:
                    self.add_entity(cname, eid)
                    created_entities += 1

                # --- Attribute branch ---
                aname = (row.get("attribute_id") or "").strip()
                aval  = row.get("attribute_value")

                if aname:
                    if aname in known_attrs[cname]:
                        if aval not in ("", None):
                            unit = (row.get("attribute_unit") or "").strip() or None
                            prov = (row.get("attribute_provenance") or "").strip() or None

                            # Let add_attribute handle type-coercion and wrapping
                            self.add_attribute(
                                entity_id=eid,
                                attribute=aname,
                                value=aval,
                                unit=unit,
                                provenance_ref=prov,
                            )
                            set_attr += 1
                    else:
                        unknowns.append((i, cname, eid, aname, "unknown attribute"))
                        if strict_unknown:
                            # continue to next row (don't process relation in same row)
                            per_class_rows[cname] += 1
                            continue

                # --- Relation branch ---
                rtype = (row.get("relation_type") or "").strip()
                rid   = (row.get("relation_id") or "").strip()

                if rtype:
                    if rtype in known_refs[cname]:
                        if rid not in ("", None):
                            # If a row encodes multiple ids separated by commas, split them:
                            targets = [t.strip() for t in rid.split(",")] if ("," in rid) else [rid]
                            for tgt in targets:
                                if tgt:
                                    self.add_relation(entity_id=eid, relation_id=rtype, target_entity_id=tgt)
                                    set_ref += 1
                    else:
                        unknowns.append((i, cname, eid, rtype, "unknown relation"))
                        if strict_unknown:
                            per_class_rows[cname] += 1
                            continue

                per_class_rows[cname] += 1

        return {
            "created_entities": created_entities,
            "set_attributes": set_attr,
            "set_relations": set_ref,
            "unknowns": unknowns,  # list of (line, class, id, field, reason)
            "per_class_rows": dict(per_class_rows),
        }

    ## Advanced / utilities

    # ---------- Pydantic bindings ----------
    def build_pydantic_models(self):
        """
        Build Pydantic models (v2) for all classes (inheritance-aware).
        Exposes self.py_models[class_name] for non-abstract classes.
        """
        from typing import Optional, Literal
        try:
            from pydantic import BaseModel, Field, ConfigDict, field_validator, create_model, conint, confloat  # type: ignore
        except Exception as e:
            raise RuntimeError("Pydantic is required for build_pydantic_models()") from e

        self.py_models = {}
        bases = {}

        # topo order
        seen, out = set(), []
        def dfs(cn):
            if cn in seen:
                return
            seen.add(cn)
            c = self.classes[cn]
            parents = getattr(c, "parents", []) or []
            if isinstance(parents, str):
                parents = [parents]
            for p in parents:
                dfs(p)
            out.append(cn)
        for cn in self.classes:
            dfs(cn)

        type_map = {"string": str, "int": int, "float": float, "bool": bool}

        def pyd_type(a: AttributeDef):
            base = type_map.get(a.type, str)
            ann = base
            cons = a.constraints or Constraint()

            if cons.enum:
                ann = Literal[tuple(cons.enum)]  # type: ignore

            if base is int:
                ge, le = cons.minimum, cons.maximum
                if ge is not None or le is not None:
                    ann = conint(ge=ge if ge is not None else None, le=le if le is not None else None)  # type: ignore
            elif base is float:
                ge, le = cons.minimum, cons.maximum
                if ge is not None or le is not None:
                    ann = confloat(ge=ge if ge is not None else None, le=le if le is not None else None)  # type: ignore

            default = ... if a.required and a.default is None else (a.default)
            if not a.required and a.default is None:
                from typing import Optional as _Opt
                ann = _Opt[ann]  # type: ignore
                default = None

            fld = Field(default, description=a.description)
            return ann, fld

        for cname in out:
            c = self.classes[cname]
            fields = { an: pyd_type(ad) for an, ad in c.attributes.items() }

            parents = getattr(c, "parents", []) or []
            if isinstance(parents, str):
                parents = [parents]
            # For Pydantic we take the first parent as base; all attributes from
            # additional parents are already merged into ``c.attributes``.
            base = BaseModel
            if parents:
                base = bases.get(parents[0], BaseModel)

            mdl = create_model(cname, __base__=base, **fields)  # type: ignore
            mdl.model_config = ConfigDict(extra="forbid", validate_default=True)

            # ref_fields = [an for an, ad in c.attributes.items() if ad.constraints and ad.constraints.ref]
            # if ref_fields:
            #     @field_validator(*ref_fields)
            #     def _check_refs(cls, v, info):
            #         if v is None:
            #             return v
            #         an = info.field_name
            #         ref_cls = c.attributes[an].constraints.ref
            #         if ref_cls and (ref_cls not in self.entities or str(v) not in self.entities[ref_cls]):
            #             raise ValueError(f"Relation '{an}': id '{v}' not found in '{ref_cls}'")
            #         return v
            #     setattr(mdl, "_check_refs", _check_refs)

            bases[cname] = mdl
            if not c.abstract:
                self.py_models[cname] = mdl

    ## Internal helper methods

    ### Type coercion & validation:

    def _coerce_and_check_type(self, value, expected_type: str):
        """
        Versucht value in expected_type zu überführen und gibt (ok, coerced_value, err_msg) zurück.
        expected_type (case-insensitive): float|number, integer|int, string, boolean.

        NEU: wenn `value` ein AttributeValue-Dict ist ({"value": ..., "unit": ...}),
        wird intern nur der `value`-Teil geprüft.
        """
        if expected_type is None:
            return True, value, None

        t = str(expected_type).lower()

        # already None/empty is handled außerhalb (required)
        # --- NEU: AttributeValue entpacken ---
        if isinstance(value, dict) and "value" in value:
            inner = value.get("value")
        else:
            inner = value

        v = inner

        # accept numbers given as strings "123" / "3.14"
        if t in ("float", "number", "double", "decimal"):
            # allow bools? usually no; convert True/False -> 1/0 only if string
            try:
                if isinstance(v, str):
                    v = v.strip().replace(",", ".")
                return True, float(v), None
            except Exception:
                return False, value, f"cannot parse '{inner}' as {t}"

        if t in ("integer", "int"):
            try:
                if isinstance(v, str):
                    v = v.strip()
                    # allow "3.0" -> 3
                    return True, int(float(v.replace(",", "."))), None
                return True, int(v), None
            except Exception:
                return False, value, f"cannot parse '{inner}' as integer"

        if t in ("boolean", "bool"):
            if isinstance(v, bool):
                return True, v, None
            s = str(v).strip().lower()
            if s in ("true", "1", "yes"):
                return True, True, None
            if s in ("false", "0", "no"):
                return True, False, None
            return False, value, f"cannot parse '{inner}' as boolean"

        # strings / unknown types: stringify (but validate with other constraints later)
        return True, str(inner) if inner is not None else "", None

    def _coerce_for_attr(self, cls_name: str, attr: str, value):
        """
        Best-effort coercion based on schema type.

        In the AttributeValue world:

        - If `value` is already an AttributeValue dict (has "value"),
          we do NOT coerce it here; add_attribute() will handle it.
        - If `value` is a string that looks like a dict with "value",
          we parse it to a dict first and return that.
        - Otherwise we apply the legacy scalar coercion (float/int/bool).
        """
        cdef = self.classes[cls_name]
        attrs, _ = self._collect_inherited_fields(cdef)
        ad = attrs.get(attr)
        if not ad or value is None:
            return value

        # 1) Already an AttributeValue dict → pass through
        if isinstance(value, dict) and "value" in value:
            return value

        # 2) String that looks like a dict → try to parse
        if isinstance(value, str):
            s = value.strip()
            if s.startswith("{") and "value" in s:
                import ast
                try:
                    maybe = ast.literal_eval(s)
                except Exception:
                    maybe = None
                if isinstance(maybe, dict) and "value" in maybe:
                    return maybe
            # empty string -> no value
            if s == "":
                return None

        # 3) Legacy scalar coercion
        s = value
        t = (ad.type or "").lower()

        # floats
        if t in ("float", "number", "double", "decimal"):
            try:
                if isinstance(s, str):
                    s2 = s.strip().replace(",", ".")
                    return float(s2)
                return float(s)
            except Exception:
                print(
                    f"Attribute '{attr}' type error: "
                    f"cannot parse '{value}' as float"
                )
                raise

        # ints
        if t in ("int", "integer", "long"):
            try:
                if isinstance(s, str):
                    s2 = s.strip()
                    return int(float(s2.replace(",", ".")))
                return int(s)
            except Exception:
                print(
                    f"Attribute '{attr}' type error: "
                    f"cannot parse '{value}' as int"
                )
                raise

        # bools
        if t in ("bool", "boolean"):
            if isinstance(s, bool):
                return s
            txt = str(s).strip().lower()
            if txt in ("true", "1", "yes"):
                return True
            if txt in ("false", "0", "no"):
                return False
            print(
                f"Attribute '{attr}' type error: "
                f"cannot parse '{value}' as bool"
            )
            raise ValueError(f"cannot parse '{value}' as bool")

        # default: leave as-is (string, etc.)
        return value


    def _coerce_type(self, value: Any, type_name: str) -> Any:
        if value is None:
            return None
        if type_name == "string":
            return str(value)
        if type_name in ("float", "number", "double", "decimal"):
            return float(value)
        if type_name == "int":
            return int(value)
        if type_name == "bool":
            if isinstance(value, bool):
                return value
            s = str(value).lower()
            if s in ("true", "1", "yes"):
                return True
            if s in ("false", "0", "no"):
                return False
            raise ValueError(f"Cannot coerce '{value}' to bool")
        return value

    ### Frictionless schema helpers:

    def _frictionless_type_for_attribute(self, t: Optional[str]) -> str:
        """Map CESDM/YAML attribute type string to Frictionless field type."""
        if not t:
            return "string"
        t = str(t).lower()
        if t in ("float", "number", "double", "decimal"):
            return "number"
        if t in ("integer", "int", "long"):
            return "integer"
        if t in ("boolean", "bool"):
            return "boolean"
        # for dates etc. we still export as string; the unit carries semantic
        return "string"

    def _frictionless_constraints_for_attribute(self, ad: AttributeDef) -> Dict[str, Any]:
        """Build Frictionless constraints dict from AttributeDef."""
        cons: Dict[str, Any] = {}
        if ad.required:
            cons["required"] = True

        c = ad.constraints or Constraint()
        if c.enum is not None:
            cons["enum"] = c.enum
        if c.minimum is not None:
            cons["minimum"] = c.minimum
        if c.maximum is not None:
            cons["maximum"] = c.maximum
        if c.pattern is not None:
            cons["pattern"] = c.pattern

        # Note: c.ref is a semantic ref to another class; we don't put this
        # into "constraints" directly but may reflect it in the description.
        return cons

    def _frictionless_constraints_for_relation(self, rd: RelationDef) -> Dict[str, Any]:
        """Build Frictionless constraints dict from RelationDef."""
        cons: Dict[str, Any] = {}
        if rd.required:
            cons["required"] = True
        # We could interpret cardinality here, but since the data is stored
        # as a string/JSON array in a single field, we keep it descriptive only.
        return cons

    ### Schema/meta helpers:

    def _get_meta(self, node, key, default=None):
        """
        Read field from an attr/ref definition (dict or object).
        """
        if node is None:
            return default
        if isinstance(node, dict):
            return node.get(key, default)
        return getattr(node, key, default)

    def _get_parent_name(self, cdef):
        """Return the parent class name, regardless of the field name used."""
        return (
            getattr(cdef, "parents", None)
            or getattr(cdef, "parents", None)
            or getattr(cdef, "base_class", None)
        )

    def _lookup_class(self, name):
        """Find a class by full or short name in self.classes."""
        if not name:
            return None

        if name in self.classes:
            return self.classes[name]
        short = str(name).split(".")[-1]
        return self.classes.get(short)

    def _to_name_map(self, container):
        """
        Normalize attributes/relations into a {name: def} dict, accepting:
        - dict: {name: def}
        - list[object with .name] or list[dict with 'name']
        """
        out = {}
        if not container:
            return out
        if isinstance(container, dict):
            return dict(container)
        if isinstance(container, (list, tuple)):
            for it in container:
                if it is None:
                    continue
                if isinstance(it, dict):
                    nm = it.get("name")
                    if nm:
                        out[nm] = it
                else:
                    nm = getattr(it, "name", None)
                    if nm:
                        out[nm] = it
        return out

    def _collect_inherited_fields(self, class_def):
        """
        Collect attributes + relations along the inheritance chain (child wins).
        Uses any pre-resolved containers if present, otherwise walks parents.
        """
        # Prefer already-resolved fields if your loader provides them


        for cand in ("all_attributes", "attributes_resolved", "resolved_attributes"):
            attrs = self._to_name_map(getattr(class_def, cand, None))
            if attrs:
                break
        else:
            attrs = self._to_name_map(getattr(class_def, "attributes", None))

        for cand in ("all_relations", "relations_resolved", "resolved_relations"):
            refs = self._to_name_map(getattr(class_def, cand, None))
            if refs:
                break
        else:
            refs = self._to_name_map(getattr(class_def, "relations", None))

        # If resolved containers were non-empty, we can return now
        if attrs and refs:
            return attrs, refs

        # Otherwise, walk up the chain: child -> parent -> ...
        seen = set()
        attrs = {}
        refs = {}

        # Use a stack (DFS) or queue for BFS.
        stack = [class_def]

        while stack:
            cdef = stack.pop()

            cname = getattr(cdef, "name", None)
            if cname in seen:
                continue
            seen.add(cname)

            # Merge attributes/relations for this class (including the starting one)
            p_attrs = self._to_name_map(getattr(cdef, "attributes", None))
            p_refs  = self._to_name_map(getattr(cdef, "relations", None))

            for k, v in p_attrs.items():
                attrs.setdefault(k, v)  # first (nearest child) wins

            for k, v in p_refs.items():
                refs.setdefault(k, v)   # first (nearest child) wins

            # ---- Handle parent_name being a list OR scalar ----
            parent_names = self._get_parent_name(cdef)

            if parent_names:
                if isinstance(parent_names, str):
                    parent_names = [parent_names]

                for pname in parent_names:
                    parent_class = self._lookup_class(pname)
                    if parent_class:
                        stack.append(parent_class)

        return attrs, refs

    def _known_fields(self, class_def):
        """Return the set of all attribute+relation names for the class (incl. parents)."""
        a, r = self._collect_inherited_fields(class_def)
        return set(a.keys()) | set(r.keys())

    def _canonicalize_class(self, cls_name: str) -> str:
        if cls_name in self.classes:
            return cls_name
        for k in self.classes:
            if k.lower() == str(cls_name).lower():
                return k
        cand = str(cls_name).replace("-", "_").replace(" ", "_")
        cand = (cand[:1].upper() + cand[1:]) if cand else cand
        if cand in self.classes:
            return cand
        raise ValueError(f"Unknown entity class: {cls_name}")

    ### Entity field setters:

    def _get_entity_and_class(self, entity_id: str):
        for cname, ents in self.entities.items():
            if entity_id in ents:
                return ents[entity_id], self.classes[cname]
        return None, self.classes[cname]
        print(f"No entity with id '{entity_id}' found.")
        # raise KeyError(f"No entity with id '{entity_id}' found.")

    def _set_entity_field(self, cls_name: str, entity_id: str, entity_obj, attr: str, value):
        # 1) If the backing store in self.entities is a dict, write there
        store = self.entities.get(cls_name, {}).get(entity_id)
        if isinstance(store, dict):
            store[attr] = value
            return

        # 2) If the entity is your dataclass with .data
        if hasattr(entity_obj, "data") and isinstance(entity_obj.data, dict):
            entity_obj.data[attr] = value
            return

        # 3) Fallbacks for other shapes
        if hasattr(entity_obj, "values") and isinstance(entity_obj.values, dict):
            entity_obj.values[attr] = value
            return
        if hasattr(entity_obj, "attributes") and isinstance(entity_obj.attributes, dict):
            entity_obj.attributes[attr] = value
            return

        raise TypeError("Unsupported entity storage for attribute assignment")

    def _field(self, ad, name, default=None):
        """Return attribute field from either a dict or an object.
        Robust to accidental arg swapping or non-string field names.
        """
        if not isinstance(name, str):
            # if the third arg is a string, assume args were swapped
            if isinstance(default, str):
                name, default = default, None
            else:
                return default  # fail-soft
        if isinstance(ad, dict):
            return ad.get(name, default)
        return getattr(ad, name, default)

    ## Helpers for Entity and Attribute listings


    def format_class_tree(self) -> str:
        """
        Baut einen Vererbungsbaum aller Klassen im Model.

        Erwartet: ``model.classes = {class_name: ClassDef}``, und jede ClassDef hat
        ``.parents`` entweder als Liste von Elternamen, einen einzelnen String oder ``None``.
        """
        # Parent-Map: child -> [parent_name, ...]
        parents: Dict[str, List[str]] = {}
        for name, cdef in self.classes.items():
            ext = getattr(cdef, "parents", []) or []
            if isinstance(ext, str):
                ext = [ext]
            parents[name] = list(ext)

        # Kinder-Map: parent_name -> [child_names]
        children: Dict[str, List[str]] = {}
        for cls, parent_list in parents.items():
            if not parent_list:
                continue
            for parent in parent_list:
                children.setdefault(parent, []).append(cls)

        # Kinder alphabetisch sortieren
        for lst in children.values():
            lst.sort()

        lines: List[str] = []

        def walk(node: str, prefix: str = "", is_last: bool = True):
            connector = "└─" if is_last else "├─"
            lines.append(f"{prefix}{connector} {node}")

            child_list = children.get(node, [])
            for i, child in enumerate(child_list):
                last_child = (i == len(child_list) - 1)
                new_prefix = prefix + ("   " if is_last else "│  ")
                walk(child, new_prefix, last_child)

        # Wurzeln (Klassen ohne Parent)
        roots = [name for name, plist in parents.items() if not plist]
        roots.sort()

        for i, root in enumerate(roots):
            walk(root, prefix="", is_last=(i == len(roots) - 1))

        return "\n".join(lines)

    def print_class_tree(self):
        print(self.format_class_tree())

    def format_attribute_tree(self, groups: Dict[str, List]):  # List[AttributeDef] in echt
        """
        Nimmt ein Dict[group_name -> List[AttributeDef]] und
        gibt einen Tree-String zurück.
        """
        lines = []

        # in stabile Reihenfolge bringen (optional: nach Gruppenname sortieren)
        group_items = list(groups.items())
        # wenn du explizite Reihenfolge willst, lass das sort() weg
        # group_items.sort(key=lambda kv: kv[0])

        for gi, (group_name, attrs) in enumerate(group_items):
            is_last_group = gi == len(group_items) - 1
            group_prefix = "└─" if is_last_group else "├─"
            lines.append(f"{group_prefix} {group_name}")

            # Attribute sortieren (erst nach order, dann Name)
            attrs_sorted = sorted(
                attrs,
                key=lambda a: (
                    getattr(a, "order", 0) if getattr(a, "order", None) is not None else 0,
                    a.name,
                ),
            )

            for ai, attr in enumerate(attrs_sorted):
                is_last_attr = ai == len(attrs_sorted) - 1
                connector = "└─" if is_last_attr else "├─"
                indent = "   " if is_last_group else "│  "
                required_mark = "*" if getattr(attr, "required", False) else ""
                attr_type = getattr(attr, "type", "?")
                lines.append(f"{indent}{connector} {attr.name}{required_mark} : {attr_type}")

        return "\n".join(lines)

    def print_attribute_tree(self, groups: Dict[str, List]):
        """
        Convenience-Funktion, die den Tree direkt auf stdout ausgibt.
        """
        print(self.format_attribute_tree(groups))

    def get_attributes_grouped(self, class_name: str) -> Dict[str, List[AttributeDef]]:
        """
        Liefert Attribute einer Klasse inkl. geerbter Attribute,
        gruppiert nach .group und sortiert nach .order / Name.
        """
        # class_def holen
        cdef = self.classes[class_name]

        # <-- HIER: Inheritance berücksichtigen
        attrs_def, _ = self._collect_inherited_fields(cdef)

        groups: Dict[str, List[AttributeDef]] = {}

        for ad in attrs_def.values():
            g = getattr(ad, "group", None) or "master_data"   # Default-Gruppe
            groups.setdefault(g, []).append(ad)

        # sortieren innerhalb der Gruppe
        for g, lst in groups.items():
            lst.sort(
                key=lambda a: (
                    getattr(a, "order", 0) if getattr(a, "order", None) is not None else 0,
                    a.name,
                )
            )

        return groups


    ### Other Helpers 

    def _constraints_to_dict(self, obj):
        """
        Normalize a constraints object to a plain dict.
        Works if obj is None, dict, or an object (e.g., pydantic/dataclass) with attributes.
        """
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return obj
        # probe common keys
        keys = (
            "minimum", "maximum", "enum", "regex",
            "min_length", "max_length",
            "min_items", "max_items", "unique"
        )
        out = {}
        for k in keys:
            if hasattr(obj, k):
                out[k] = getattr(obj, k)
        return out


    def is_class_derived_from(
        self,
        subclass_name: str,
        parent_name: str,
        inheritance: Dict[str, Union[str, List[str], None]],
    ) -> bool:
        """
        Check whether a class is derived from a given base class.

        Parameters
        ----------
        subclass_name :
            Name of the class to check.
        parent_name :
            Name of the potential base class.

        Returns
        -------
        bool
            ``True`` if ``subclass_name`` is the same as or inherits (directly or
            indirectly) from ``parent_name``, otherwise ``False``.
        """

        # Trivial case
        if subclass_name == parent_name:
            return True

        # Walk up all parents; ``inheritance`` may map to a single parent string,
        # a list of parents, or None for root classes.
        visited: set[str] = set()
        stack: List[str] = [subclass_name]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)

            parents = inheritance.get(current)
            if parents is None:
                continue
            if isinstance(parents, str):
                parents = [parents]

            for p in parents:
                if not p:
                    continue
                if p == parent_name:
                    return True
                if p not in visited:
                    stack.append(p)

        return False

    def obj_is_instance_of(
        obj: dict,
        parent_name: str,
        inheritance: dict[str, str | None],
        class_key: str = "class",) -> bool:

        """
        Returns True if `obj`'s class (e.g. obj["class"]) is derived from
        `parent_name` according to the inheritance map.
        """
        cls_name = obj.get(class_key)
        if cls_name is None:
            return False
        return self.is_class_derived_from(cls_name, parent_name, inheritance)

    def load_classes_from_yaml(self, path: Union[str, pathlib.Path]):

        """
        Load class definitions from all ``*.yaml`` schema files in a directory.

        Parameters
        ----------
        schema_dir :
            Path to a folder containing CESDM class definition YAML files.

        Notes
        -----
        This method populates :attr:`classes` and :attr:`inheritance`,
        but does not resolve inherited attributes/relations yet.
        Call :meth:`resolve_inheritance` afterwards.
        """
        
        import pathlib, yaml
        path = pathlib.Path(path)

        docs = []

        def _load_all(pth):
            with open(pth, "r", encoding="utf-8") as f:
                return list(yaml.safe_load_all(f))

        if path.is_dir():
            for f in sorted(path.rglob("*.y*ml")):
                docs.extend(_load_all(f))
        else:
            docs.extend(_load_all(path))

        merged: Dict[str, Dict[str, Any]] = {}

        def _merge_class(into: Dict[str, Any], src: Dict[str, Any]):
            # copy common keys
            for k in ("description", "parents", "abstract"):
                if k in src:
                    into[k] = src[k]

            # --- attributes: merge dict OR list-of-objects with "id" ---
            into.setdefault("attributes", {})
            raw_attrs = src.get("attributes")
            if isinstance(raw_attrs, dict):
                # old style
                into["attributes"].update(raw_attrs)
            elif isinstance(raw_attrs, list):
                # new style: list of {id: ..., ...}
                for item in raw_attrs:
                    if not isinstance(item, dict):
                        continue
                    attr_id = item.get("id")
                    if not attr_id:
                        continue
                    spec = {k: v for k, v in item.items() if k != "id"}
                    into["attributes"][attr_id] = spec

            # --- relations: merge dict OR list-of-objects with "id" ---
            into.setdefault("relations", {})
            raw_refs = src.get("relations")
            if isinstance(raw_refs, dict):
                # old style
                into["relations"].update(raw_refs)
            elif isinstance(raw_refs, list):
                # new style: list of {id: ..., ...}
                for item in raw_refs:
                    if not isinstance(item, dict):
                        continue
                    ref_id = item.get("id")
                    if not ref_id:
                        continue
                    spec = {k: v for k, v in item.items() if k != "id"}
                    into["relations"][ref_id] = spec

        for d in docs:
            if not d:
                continue
            # Case 1: collection file
            if isinstance(d.get("entity_classes"), dict):
                for cname, cdef in d["entity_classes"].items():
                    merged.setdefault(cname, {})
                    _merge_class(merged[cname], cdef or {})
            # Case 2: single-class file
            elif "name" in d:
                cname = d["name"]
                merged.setdefault(cname, {})
                _merge_class(merged[cname], d)
            else:
                continue

        # Build class objects
        for cname, cdef in merged.items():
            ec = EntityClass.from_dict(cname, cdef)
            self.classes[cname] = ec
            if cname not in self.entities:
                self.entities[cname] = {}

        self.inheritance = self.build_inheritance_map(path)
        # finalize inheritance
        self.resolve_inheritance()

    def build_inheritance_map(self, schema_dir: str | Path) -> Dict[str, List[str]]:
        """
        Reads all ``*.yaml`` in ``schema_dir`` and builds a *direct* inheritance map::

            { child_class_name: [parent_class_name, ...] }

        This is a lightweight helper used during schema loading.  It understands the
        schema keys ``parent``, ``inherits_from`` and ``parents`` where ``parents``
        may be either a single string or a list of base-class names.
        """
        from pathlib import Path
        import yaml

        schema_dir = Path(schema_dir)
        inheritance: Dict[str, List[str]] = {}

        for f in schema_dir.glob("*.yaml"):
            with f.open() as fp:
                data = yaml.safe_load(fp) or {}

            cls_name = data.get("class_name") or data.get("name") or f.stem

            if "parents" in data:
                raw = data.get("parents")
            elif "parents" in data:
                raw = data.get("parents")
            else:
                raw = data.get("inherits_from")

            parents: List[str] = []
            if raw:
                if isinstance(raw, str):
                    parents = [raw]
                elif isinstance(raw, (list, tuple, set)):
                    parents = [p for p in raw if p]
                else:
                    parents = [str(raw)]

            inheritance[cls_name] = parents

        return inheritance

    def _add_raw(self, cls: str, id: str, **kwargs):
        if cls not in self.classes:
            raise ValueError(f"Unknown entity class: {cls}")
        # global unique id
        for other_cls, ents in self.entities.items():
            if id in ents:
                raise ValueError(f"Duplicate id '{id}' already exists in class '{other_cls}'. Entity IDs must be globally unique.")
        cdef = self.classes[cls]
        data: Dict[str, Any] = {}
        # defaults
        for an, ad in cdef.attributes.items():
            if an in kwargs:
                data[an] = kwargs[an]
            elif ad.default is not None:
                data[an] = ad.default
        # extras (unknown checked later)
        for k, v in kwargs.items():
            data[k] = v
        self.entities[cls][id] = Entity(cls=cls, id=id, data=data)


    def _slugify_name(self,s: str) -> str:
        import re
        s = s.lower()
        s = re.sub(r'[^-a-z0-9._/]+', '-', s)
        return s.strip('-')

    def _slugify_resource_name(self, s: str) -> str:
        # lowercase
        s = s.lower()
        # replace invalid chars with '-'
        s = re.sub(r'[^-a-z0-9._/]+', '-', s)
        # strip leading/trailing '-'
        s = s.strip('-')
        return s


    @property
    def class_defs(self):
        """
        Return a mapping of all class names to their :class:`EntityClass` definitions.

        Returns
        -------
        dict[str, EntityClass]
            Dictionary of class name → class definition.
        """
        return getattr(self, "classes", {})

def build_model_from_yaml(schema_path: Union[str, pathlib.Path]) -> Model:
    m = Model()
    m.load_classes_from_yaml(schema_path)
    return m