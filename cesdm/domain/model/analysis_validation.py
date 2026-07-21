"""cesdm.domain.model.analysis_validation — CESDM addon: view_family
resolution for analysis-profile checks

The generic, schema-agnostic core of analysis-profile validation lives
in `ear.model.analysis_validation.AnalysisValidationMixin` -- entities,
attributes, relations, and constraints are core EAR concepts, so that
part works for any EAR-based schema, not just CESDM. This mixin adds
the one CESDM-specific capability the generic core deliberately
doesn't and shouldn't know about: resolving an attribute/relation
against one of an asset's representation views (`view_family`) when
it isn't declared directly on the entity itself -- explicitly
requested in the check, or auto-detected the same way `.dispatch`/
`.powerflow` resolve on the proxy API.

It does this by overriding `_resolve_check_beyond_entity()`, the
generic mixin's one designed extension point -- called only when a
check's `attribute` isn't found among the entity's own direct
attributes/relations. This class must appear before `ear.model.Model`
in `CesdmModel`'s MRO (see `cesdm/domain/model/core.py`) for the
override to actually take effect; Python's normal method resolution
already guarantees this from the mixin declaration order.

See `docs/architecture/analysis_validation.md` for the full design and
`analysis_profiles/optimal_dispatch.yaml` for a worked example.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


class CesdmAnalysisValidationMixin:
    """CESDM addon -- see module docstring."""

    def _find_existing_view_for_family(self, entity_id: str, family: str) -> Optional[str]:
        """Read-only counterpart to AssetProxy._view() (cesdm/proxy.py):
        find an existing view of the given view_family for entity_id,
        without creating one if missing. Unlike the proxy layer's
        `.dispatch` etc, which auto-creates a view on first access,
        validation must never have a side effect on the model it's
        checking -- a missing view should be reported as a missing
        view, not silently created to paper over the gap.
        """
        for vcls, vid in (self.views_for_asset(entity_id) or {}).items():
            cdef = self.classes.get(vcls)
            if (cdef is not None and getattr(cdef, "view_family", None) == family
                    and not getattr(cdef, "abstract", False)):
                return vid
        return None

    def _find_view_family_for_attribute(self, entity_class: str, attribute: str) -> Optional[str]:
        """Given an entity class and an attribute/relation id that isn't
        declared directly on the entity itself, find which single
        view_family (if any) declares it -- so a profile only has to
        say "GenerationUnit needs nominal_power_capacity", not which
        of its several possible representation views that actually
        lives on. Returns None if the attribute isn't found on any
        view class for this entity, *or* if it's found on more than
        one distinct family (ambiguous -- in practice this only
        happens for structural, every-view-has-one fields like
        representsAsset, never for a real domain attribute someone
        would put in an analysis profile; an explicit `view_family` in
        the check is the escape hatch for that rare case).
        """
        candidates = (self._discover_view_map() or {}).get(entity_class, [])
        families_found: set = set()
        for vcls in candidates:
            cdef = self.classes.get(vcls)
            if cdef is None or getattr(cdef, "abstract", False):
                continue
            family = getattr(cdef, "view_family", None)
            if not family:
                continue
            if attribute in (self.class_attributes(vcls) or []) or \
                    attribute in (self.class_relations(vcls) or []):
                families_found.add(family)
        return families_found.pop() if len(families_found) == 1 else None

    def _resolve_check_beyond_entity(self, real_class: str, entity_id: str, attribute: str,
                                     check: Dict[str, Any]) -> Tuple[bool, Any, Optional[str], Optional[str]]:
        """Overrides the generic hook (ear.model.analysis_validation):
        before giving up, try resolving `attribute` against one of the
        entity's representation views -- explicit `view_family` in the
        check, or auto-detected if exactly one of the entity's view
        classes declares it.
        """
        view_family = check.get("view_family")
        if view_family is None:
            view_family = self._find_view_family_for_attribute(real_class, attribute)
            if view_family is None:
                return False, None, None, (
                    f"'{attribute}' is not a known attribute or relation of {real_class!r}, "
                    f"or of any of its representation views (or it's ambiguous across "
                    f"more than one -- add an explicit 'view_family' to this check to "
                    f"disambiguate)"
                )

        location = f"{attribute} (view: {view_family})"
        view_id = self._find_existing_view_for_family(entity_id, view_family)
        if view_id is None:
            required = bool(check.get("required", False))
            if required:
                return False, None, None, f"has no {view_family!r} view to check '{attribute}' on"
            # Not required and the view doesn't exist -- report as
            # "found, but empty", so the generic required-check (which
            # only fires when required=True anyway) correctly does
            # nothing here, exactly as if the attribute were merely unset.
            return True, None, location, None

        value = self.get_attribute_value(view_id, attribute)
        return True, value, location, None
