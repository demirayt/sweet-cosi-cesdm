"""ear.model.analysis_validation — Generic analysis-dependent validation

model.validate() (ear.model.validation.ValidationMixin) checks
structural completeness against the *schema*: required attributes/
relations present, types and constraints satisfied. That's necessary
but not sufficient for any particular use of a model -- different
analyses need different subsets of attributes from different entity
classes, often with value ranges narrower than the schema itself
demands.

This mixin adds that second, independent kind of check: fitness for a
specific *analysis*, declared in a YAML "analysis profile" file rather
than hard-coded in Python. It is deliberately generic and
schema-agnostic -- entities, attributes, relations, and constraints
are core EAR concepts, so this works for *any* EAR-based schema, not
just CESDM, and has no notion of CESDM's asset/representation-view
split at all.

CESDM adds exactly one extension on top: resolving a check against one
of an asset's representation views (`view_family`), explicitly
requested or auto-detected -- see
cesdm.domain.model.analysis_validation.CesdmAnalysisValidationMixin,
which overrides `_resolve_check_beyond_entity()` below to add it. A
plain `ear.model.Model` (no CESDM layer at all) only gets the generic
behaviour here: a check can look at an entity's own direct attributes/
relations, nothing more -- which is entirely correct for a schema that
has no concept of views to begin with.

See docs/architecture/analysis_validation.md for the full design and
analysis_profiles/optimal_dispatch.yaml for a worked (CESDM) example.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import yaml


class AnalysisValidationMixin:
    """Mixin -- see module docstring."""

    def load_analysis_profile(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load a single analysis-profile YAML file.

        `path` can be a file directly, or a directory -- in which case
        every `*.yaml`/`*.yml` file in it is merged into one profile
        (their `requirements` lists concatenated), the same convention
        `import_library()` uses for a directory of modular files.
        """
        path = Path(path)
        if path.is_dir():
            merged: Dict[str, Any] = {"name": path.name, "requirements": []}
            files = sorted(path.glob("*.yaml")) + sorted(path.glob("*.yml"))
            if not files:
                raise FileNotFoundError(f"{path}: no *.yaml/*.yml analysis profile files found")
            for file in files:
                data = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
                merged["requirements"].extend(data.get("requirements", []))
            return merged
        if not path.is_file():
            raise FileNotFoundError(f"{path}: analysis profile file not found")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if "requirements" not in data:
            raise ValueError(f"{path}: analysis profile has no 'requirements' key")
        return data

    def _resolve_analysis_profile(self, profile: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        """Accept an already-loaded profile dict, a path, or a bare name
        looked up as `analysis_profiles/<name>.yaml` relative to the
        current working directory."""
        if isinstance(profile, dict):
            return profile
        path = Path(profile)
        if path.is_file() or path.is_dir():
            return self.load_analysis_profile(path)
        candidate = Path("analysis_profiles") / f"{profile}.yaml"
        if candidate.is_file():
            return self.load_analysis_profile(candidate)
        raise FileNotFoundError(
            f"No analysis profile found for {profile!r} -- tried it directly as "
            f"a path and as 'analysis_profiles/{profile}.yaml'"
        )

    def _is_or_subclasses(self, class_name: str, base_class: str) -> bool:
        """True if class_name is base_class or a (transitive) subclass of
        it, walking self.inheritance (class -> list of direct parents)."""
        if class_name == base_class:
            return True
        seen = set()
        frontier = [class_name]
        while frontier:
            current = frontier.pop()
            if current in seen:
                continue
            seen.add(current)
            for parent in self.inheritance.get(current) or []:
                if parent == base_class:
                    return True
                frontier.append(parent)
        return False

    def _check_constraints(self, value: Any, constraints: Dict[str, Any]) -> List[str]:
        """Lightweight constraint checker -- minimum/maximum/enum, the
        subset of the schema's own constraint vocabulary meaningful for
        an already-typed value read back out of the model. (Unlike
        ear.model.validation's type-coercion machinery, not needed here
        -- get_attribute_value() already returns a proper Python value.)
        """
        problems: List[str] = []
        if not constraints:
            return problems
        numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
        if numeric:
            minimum = constraints.get("minimum")
            if minimum is not None and value < minimum:
                problems.append(f"value {value} is below the required minimum {minimum}")
            maximum = constraints.get("maximum")
            if maximum is not None and value > maximum:
                problems.append(f"value {value} is above the required maximum {maximum}")
        enum = constraints.get("enum")
        if enum and value not in enum:
            problems.append(f"value {value!r} is not one of {enum}")
        return problems

    def _generic_entity_class(self, entity_id: str) -> Optional[str]:
        """Generic equivalent of cesdm's entity_class() accessor, using
        only core EAR internals (self.entities) -- kept local here
        rather than depending on a CESDM-only convenience method, so
        this mixin genuinely works on a bare ear.model.Model too."""
        for cname, ents in (self.entities or {}).items():
            if entity_id in (ents or {}):
                return cname
        return None

    def _generic_known_fields(self, class_name: str) -> Tuple[List[str], List[str]]:
        """Generic equivalent of cesdm's class_attributes()/
        class_relations(), via _collect_inherited_fields() (core EAR,
        ear/model/schema_loading.py) -- returns (attribute ids, relation
        ids) declared for class_name, including inherited ones."""
        class_def = (self.classes or {}).get(class_name)
        if class_def is None:
            return [], []
        attrs, refs = self._collect_inherited_fields(class_def)
        return list(attrs.keys()), list(refs.keys())

    def _resolve_check_beyond_entity(self, real_class: str, entity_id: str, attribute: str,
                                     check: Dict[str, Any]) -> Tuple[bool, Any, Optional[str], Optional[str]]:
        """Extension hook: called only when `attribute` isn't a direct
        attribute or relation of the entity itself. The generic,
        schema-agnostic implementation here has nothing further to try
        -- plain EAR has no concept of anything "beyond the entity".
        CESDM overrides this (see cesdm.domain.model.
        analysis_validation.CesdmAnalysisValidationMixin) to also look
        on the entity's representation views.

        Returns (found, value, location, error_message_without_label).
        `location` is a short human-readable description of where the
        value was found (or would have been), used in constraint-
        violation messages.
        """
        return False, None, None, (
            f"'{attribute}' is not a known attribute or relation of {real_class!r}"
        )

    def _run_analysis_check(self, profile_name: str, entity_class: str,
                            entity_id: str, check: Dict[str, Any]) -> List[str]:
        attribute = check.get("attribute")
        if not attribute:
            return [f"[{profile_name}] check on {entity_class} is missing 'attribute'"]
        required = bool(check.get("required", False))
        constraints = check.get("constraints") or {}
        label = f"[{profile_name}] [{entity_class}:{entity_id}]"
        real_class = self._generic_entity_class(entity_id) or entity_class

        class_attrs, class_rels = self._generic_known_fields(real_class)

        if attribute in class_attrs or attribute in class_rels:
            value = self.get_attr_value(real_class, entity_id, attribute)
            location = attribute
        else:
            found, value, location, error = self._resolve_check_beyond_entity(
                real_class, entity_id, attribute, check)
            if not found:
                return [f"{label} {error}"]

        if value is None or value == "" or value == []:
            if required:
                return [f"{label} missing required '{location}'"]
            return []

        return [f"{label} '{location}' {problem}"
                for problem in self._check_constraints(value, constraints)]

    def validate_for_analysis(self, profile: Union[str, Path, Dict[str, Any]]) -> List[str]:
        """Validate the model against an analysis profile -- fitness for
        a specific analysis (e.g. "optimal dispatch"), not just
        structural schema completeness (see `validate()` for that).
        Returns a list of human-readable error strings, same convention
        as `validate()`: an empty list means the model has everything
        this analysis needs.

        `profile` can be an already-loaded dict (from
        `load_analysis_profile()`), a path to a profile file or
        directory, or a bare name looked up as
        `analysis_profiles/<name>.yaml`.

        See `analysis_profiles/optimal_dispatch.yaml` for the file
        format, and `docs/architecture/analysis_validation.md` for the
        full design.
        """
        data = self._resolve_analysis_profile(profile)
        profile_name = data.get("name", "analysis")
        errors: List[str] = []

        for requirement in data.get("requirements", []):
            entity_class = requirement.get("entity_class")
            if not entity_class:
                errors.append(f"[{profile_name}] a requirement block is missing 'entity_class'")
                continue
            checks = requirement.get("checks", [])
            if entity_class not in (self.classes or {}):
                errors.append(f"[{profile_name}] unknown entity_class {entity_class!r}")
                continue

            matching_entity_ids = [
                entity_id
                for cname, ents in self.entities.items()
                if self._is_or_subclasses(cname, entity_class)
                for entity_id in ents
            ]
            for entity_id in matching_entity_ids:
                for check in checks:
                    errors.extend(
                        self._run_analysis_check(profile_name, entity_class, entity_id, check)
                    )

        return errors

    def validate_for_analysis_or_raise(self, profile: Union[str, Path, Dict[str, Any]]) -> None:
        """Like `validate_for_analysis()`, but raises `ValueError` with
        every error listed if the model isn't fit for this analysis,
        instead of returning the list -- mirrors `validate_or_raise()`."""
        errors = self.validate_for_analysis(profile)
        if errors:
            name = errors[0].split("]")[0].lstrip("[") if errors else "analysis"
            raise ValueError(
                f"Model is not ready for {name!r} analysis:\n- " + "\n- ".join(errors)
            )
