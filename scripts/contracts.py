"""Catalog and report contracts. Never interpret photos or produce aesthetic scores."""
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
DEFAULT_CATALOG = ROOT / "references" / "catalog.json"
FAMILY = "family"
EXPRESSION = "expression"
RECIPE = "recipe"
READY = "ready"
NEEDS_INPUT = "needs_input"
USER_PHOTO = "user_photo"
UNKNOWN = "unknown"
REFERENCE_ROLES = frozenset({"reference", "expected_effect"})
BLOCKING_ISSUES = frozenset({"blur", "occluded", "extreme_pose", "no_face"})
READY_BLOCKING_ISSUES = frozenset({
    "caption_present",
    "role_unknown",
    "filter_uncertain",
    "lighting_uncertain",
    "preferences_missing",
})
SKIP = "skip"
FACE = "face"


class ContractError(ValueError):
    """Human-readable validation failure."""


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ContractError("Duplicate JSON key: " + key)
        value[key] = item
    return value


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError("Cannot read JSON: " + str(exc)) from exc


def check_schema(value: Any, schema_name: str) -> None:
    schema = read_json(SCHEMA_DIR / schema_name)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        messages = ["/" + "/".join(map(str, e.absolute_path)) + ": " + e.message
                    for e in errors[:10]]
        raise ContractError("\n".join(messages))


def indexed(items: List[Dict], label: str) -> Dict[str, Dict]:
    result = {}
    for item in items:
        key = item["id"]
        if key in result:
            raise ContractError("Duplicate " + label + " ID: " + key)
        result[key] = item
    return result


@dataclass(frozen=True)
class Catalog:
    data: Dict
    styles: Dict[str, Dict]
    dimensions: Dict[str, Dict]

    def require(self, style_id: str, kind: str) -> Dict:
        style = self.styles.get(style_id)
        if style is None or style["kind"] != kind:
            raise ContractError("Unknown " + kind + " style: " + str(style_id))
        return style


def validate_catalog(data: Dict) -> Catalog:
    check_schema(data, "catalog.schema.json")
    dimensions = indexed(data["dimensions"], "dimension")
    styles = indexed(data["styles"], "style")
    catalog = Catalog(data, styles, dimensions)
    for style in styles.values():
        if set(style["ranges"]) != set(dimensions):
            raise ContractError("Dimension coverage mismatch: " + style["id"])
        if any(low > high for low, high in style["ranges"].values()):
            raise ContractError("Reversed dimension range: " + style["id"])
        if style["kind"] != RECIPE and style["families"]:
            raise ContractError("Only recipes specify families: " + style["id"])
        if style["kind"] == RECIPE and not style["families"]:
            raise ContractError("Recipe needs a family: " + style["id"])
        if len(style["families"]) != len(set(style["families"])):
            raise ContractError("Duplicate recipe family: " + style["id"])
        for family_id in style["families"]:
            catalog.require(family_id, FAMILY)
    if not any(s["kind"] == FAMILY for s in styles.values()):
        raise ContractError("Catalog needs at least one family")
    return catalog


def load_catalog(path: Path = DEFAULT_CATALOG) -> Catalog:
    return validate_catalog(read_json(path))


def usable(image: Dict) -> bool:
    count = image["face_count"]
    return (count is not None and count > 0
            and (count == 1 or image["target_selected"])
            and not BLOCKING_ISSUES.intersection(image["issues"]))


def check_observations(report: Dict, images: Dict) -> Dict:
    observations = indexed(report["observations"], "observation")
    for observation in observations.values():
        image = images.get(observation["image_id"])
        if image is None:
            raise ContractError("Observation references missing image: " + observation["id"])
        if observation["scope"] == FACE:
            if image["role"] in REFERENCE_ROLES:
                raise ContractError("Reference/effect faces are not user face evidence")
            if image["role"] == UNKNOWN and observation["confidence"] != "low":
                raise ContractError("Unknown-role face evidence must be low confidence")
    return observations


def check_status(report: Dict, images: Dict) -> None:
    if report["status"] != READY:
        if not report["uncertainties"] or not report["questions"]:
            raise ContractError("Unresolved reports need uncertainties and questions")
    if report["status"] == NEEDS_INPUT:
        if report["recommendations"] or report["experiments"]:
            raise ContractError("needs_input cannot contain personal recommendations/experiments")
        return
    if not report["recommendations"]:
        raise ContractError("A consultation needs a recommendation")
    if not any(usable(i) and i["role"] in {USER_PHOTO, UNKNOWN} for i in images.values()):
        raise ContractError("Personal recommendations need a usable user/unknown photo")
    if report["status"] == READY:
        ready_images = [i for i in images.values() if usable(i) and i["role"] == USER_PHOTO]
        if not ready_images:
            raise ContractError("ready needs a usable user-declared photo")
        if any(READY_BLOCKING_ISSUES.intersection(i["issues"]) for i in ready_images):
            raise ContractError("ready cannot contain unresolved photo or preference issues")


def check_recommendations(report: Dict, catalog: Catalog, observations: Dict) -> None:
    for recommendation in report["recommendations"]:
        catalog.require(recommendation["family_id"], FAMILY)
        if recommendation["expression_id"] is not None:
            catalog.require(recommendation["expression_id"], EXPRESSION)
        if recommendation["recipe_id"] is not None:
            recipe = catalog.require(recommendation["recipe_id"], RECIPE)
            if recommendation["family_id"] not in recipe["families"]:
                raise ContractError("Recipe does not support this family")
        for observation_id in recommendation["evidence_ids"]:
            if observation_id not in observations:
                raise ContractError("Missing recommendation evidence: " + observation_id)
        for module in recommendation["plan"].values():
            skipped = module["status"] == SKIP
            if skipped != (not module["actions"]):
                raise ContractError("skip needs empty actions; propose needs nonempty actions")


def validate_report(data: Dict, catalog: Catalog) -> Dict:
    check_schema(data, "report.schema.json")
    images = indexed(data["images"], "image")
    observations = check_observations(data, images)
    if set(data["presentation_dimensions"]) != set(catalog.dimensions):
        raise ContractError("Report dimensions must exactly match catalog dimensions")
    check_status(data, images)
    check_recommendations(data, catalog, observations)
    return data
