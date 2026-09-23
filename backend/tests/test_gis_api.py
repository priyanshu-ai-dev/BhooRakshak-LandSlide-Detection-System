"""
tests/test_gis_api.py — Unit tests for GET /api/v1/gis/layers endpoints.

All tests use synthetic fixture data (see conftest.py).
No live PostgreSQL or PostGIS instance is required.

⚠  Fixture data is SYNTHETIC — labelled [TEST FIXTURE] in event titles.
   It does not represent real geographic events.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ─────────────────────────────────────────────────────────────────────────────
# /api/v1/gis/layers  (layer catalogue)
# ─────────────────────────────────────────────────────────────────────────────

class TestLayersList:
    def test_layers_returns_200(self, client: TestClient) -> None:
        resp = client.get("/api/v1/gis/layers")
        assert resp.status_code == 200, resp.text

    def test_layers_response_has_layers_key(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers").json()
        assert "layers" in data, f"Expected 'layers' key, got: {list(data.keys())}"

    def test_layers_list_is_nonempty(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers").json()
        assert len(data["layers"]) >= 1

    def test_landslide_events_layer_present(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers").json()
        ids = [layer["id"] for layer in data["layers"]]
        assert "landslide-events" in ids

    def test_layer_meta_schema(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers").json()
        layer = next(l for l in data["layers"] if l["id"] == "landslide-events")

        required_keys = {"id", "name", "description", "geometry_type", "crs_epsg", "attribution", "data_notice"}
        assert required_keys.issubset(layer.keys()), (
            f"Missing keys: {required_keys - set(layer.keys())}"
        )

    def test_layer_crs_is_4326(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers").json()
        layer = next(l for l in data["layers"] if l["id"] == "landslide-events")
        assert layer["crs_epsg"] == 4326

    def test_layer_geometry_type_is_point(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers").json()
        layer = next(l for l in data["layers"] if l["id"] == "landslide-events")
        assert layer["geometry_type"] == "Point"

    def test_layer_attribution_present(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers").json()
        layer = next(l for l in data["layers"] if l["id"] == "landslide-events")
        assert "text" in layer["attribution"]
        assert "url" in layer["attribution"]
        assert "nasa" in layer["attribution"]["text"].lower() or \
               "kirschbaum" in layer["attribution"]["text"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# /api/v1/gis/layers/landslide-events  (GeoJSON endpoint)
# ─────────────────────────────────────────────────────────────────────────────

class TestLandslideEventsLayer:
    def test_geojson_returns_200(self, client: TestClient) -> None:
        resp = client.get("/api/v1/gis/layers/landslide-events")
        assert resp.status_code == 200, resp.text

    def test_response_is_feature_collection(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        assert data["type"] == "FeatureCollection"

    def test_features_key_present(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        assert "features" in data

    def test_features_is_list(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        assert isinstance(data["features"], list)

    def test_meta_key_present(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        assert "_meta" in data

    def test_meta_layer_id_correct(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        assert data["_meta"]["layer_id"] == "landslide-events"

    def test_meta_crs_is_epsg4326(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        assert data["_meta"]["crs"] == "EPSG:4326"

    def test_feature_geometry_type_is_point(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        for feature in data["features"]:
            assert feature["geometry"]["type"] == "Point", (
                f"Expected Point geometry, got {feature['geometry']['type']}"
            )

    def test_feature_coordinates_are_valid(self, client: TestClient) -> None:
        """Coordinates must be [lon, lat] with valid ranges (GeoJSON CRS EPSG:4326)."""
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        for feature in data["features"]:
            coords = feature["geometry"]["coordinates"]
            assert len(coords) == 2, f"Expected 2 coordinates, got {coords}"
            lon, lat = coords
            assert -180 <= lon <= 180, f"Longitude out of range: {lon}"
            assert -90 <= lat <= 90, f"Latitude out of range: {lat}"

    def test_feature_coordinates_within_ner_bbox(self, client: TestClient) -> None:
        """Synthetic fixture data must fall within the NER bounding box."""
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        for feature in data["features"]:
            lon, lat = feature["geometry"]["coordinates"]
            assert 88.0 <= lon <= 98.0, f"Lon {lon} outside NER bbox"
            assert 21.0 <= lat <= 30.0, f"Lat {lat} outside NER bbox"

    def test_feature_properties_schema(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        required_props = {
            "id", "event_date", "event_title", "country_name", "country_code",
            "landslide_type", "landslide_size", "trigger",
            "fatalities", "injuries", "source_dataset_slug",
        }
        for feature in data["features"]:
            props = feature["properties"]
            missing = required_props - set(props.keys())
            assert not missing, f"Feature missing properties: {missing}"

    def test_data_notice_present(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        notice = data["_meta"]["data_notice"]
        # Notice must warn it is historical, not a live warning
        assert "historical" in notice.lower() or "inventory" in notice.lower()

    def test_attribution_present(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/landslide-events").json()
        attr = data["_meta"]["attribution"]
        assert "text" in attr
        assert "url" in attr


# ─────────────────────────────────────────────────────────────────────────────
# bbox parameter validation
# ─────────────────────────────────────────────────────────────────────────────

class TestBboxValidation:
    def test_valid_bbox_accepted(self, client: TestClient) -> None:
        resp = client.get(
            "/api/v1/gis/layers/landslide-events",
            params={"bbox": "90.0,23.0,97.0,29.0"},
        )
        assert resp.status_code == 200

    def test_missing_bbox_uses_ner_default(self, client: TestClient) -> None:
        resp = client.get("/api/v1/gis/layers/landslide-events")
        assert resp.status_code == 200
        data = resp.json()
        assert data["_meta"]["bbox_filter"] == [88.0, 21.0, 98.0, 30.0]

    def test_bbox_wrong_count_returns_400(self, client: TestClient) -> None:
        resp = client.get(
            "/api/v1/gis/layers/landslide-events",
            params={"bbox": "90.0,23.0"},
        )
        assert resp.status_code == 400

    def test_bbox_non_numeric_returns_400(self, client: TestClient) -> None:
        resp = client.get(
            "/api/v1/gis/layers/landslide-events",
            params={"bbox": "a,b,c,d"},
        )
        assert resp.status_code == 400

    def test_bbox_inverted_lon_returns_400(self, client: TestClient) -> None:
        resp = client.get(
            "/api/v1/gis/layers/landslide-events",
            params={"bbox": "97.0,23.0,90.0,29.0"},  # minlon > maxlon
        )
        assert resp.status_code == 400

    def test_bbox_inverted_lat_returns_400(self, client: TestClient) -> None:
        resp = client.get(
            "/api/v1/gis/layers/landslide-events",
            params={"bbox": "90.0,29.0,97.0,23.0"},  # minlat > maxlat
        )
        assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# limit parameter validation
# ─────────────────────────────────────────────────────────────────────────────

class TestLimitValidation:
    def test_limit_too_large_returns_422(self, client: TestClient) -> None:
        resp = client.get(
            "/api/v1/gis/layers/landslide-events",
            params={"limit": 99999},
        )
        assert resp.status_code == 422  # FastAPI validation

    def test_limit_zero_returns_422(self, client: TestClient) -> None:
        resp = client.get(
            "/api/v1/gis/layers/landslide-events",
            params={"limit": 0},
        )
        assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# Unknown layer
# ─────────────────────────────────────────────────────────────────────────────

class TestUnknownLayer:
    def test_unknown_layer_returns_404(self, client: TestClient) -> None:
        resp = client.get("/api/v1/gis/layers/non-existent-layer")
        assert resp.status_code == 404

    def test_404_body_has_detail(self, client: TestClient) -> None:
        data = client.get("/api/v1/gis/layers/fake-layer").json()
        assert "detail" in data


# ─────────────────────────────────────────────────────────────────────────────
# Ingestion script unit tests (no DB required)
# ─────────────────────────────────────────────────────────────────────────────

class TestIngestionValidation:
    """Tests for the import_nasa_glc validation logic (pure Python, no I/O)."""

    def _import_module(self):
        import importlib.util, sys
        from pathlib import Path
        spec = importlib.util.spec_from_file_location(
            "import_nasa_glc",
            Path(__file__).parent.parent.parent / "ingestion" / "import_nasa_glc.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_valid_ner_row_passes(self) -> None:
        mod = self._import_module()
        row = {
            "id": "12345",
            "latitude": "26.1",
            "longitude": "91.5",
            "event_date": "2021-07-10",
            "event_title": "Assam landslide",
            "location_description": "NH-37",
            "country_name": "India",
            "country_code": "IN",
            "admin_division_name": "Assam",
            "landslide_type": "Landslide",
            "landslide_size": "large",
            "trigger": "Rain",
            "fatalities": "3",
            "injuries": "",
            "source_link": "",
        }
        record = mod.validate_record(row)
        assert record.id == 12345
        assert record.geom_wkt == "POINT(91.5 26.1)"
        assert record.landslide_size == "large"

    def test_missing_id_raises_validation_error(self) -> None:
        mod = self._import_module()
        row = {"id": "", "latitude": "26.1", "longitude": "91.5"}
        with pytest.raises(mod.ValidationError):
            mod.validate_record(row)

    def test_lat_out_of_range_raises(self) -> None:
        mod = self._import_module()
        row = {"id": "1", "latitude": "200.0", "longitude": "91.5"}
        with pytest.raises(mod.ValidationError):
            mod.validate_record(row)

    def test_lon_out_of_range_raises(self) -> None:
        mod = self._import_module()
        row = {"id": "1", "latitude": "26.1", "longitude": "999.0"}
        with pytest.raises(mod.ValidationError):
            mod.validate_record(row)

    def test_outside_ner_bbox_raises_outside_bbox_error(self) -> None:
        mod = self._import_module()
        row = {"id": "2", "latitude": "12.0", "longitude": "77.0"}  # South India
        with pytest.raises(mod._OutsideBboxError):
            mod.validate_record(row)

    def test_size_normalisation_catastrophic(self) -> None:
        mod = self._import_module()
        assert mod.normalise_size("Catastrophic") == "catastrophic"

    def test_size_normalisation_very_large(self) -> None:
        mod = self._import_module()
        assert mod.normalise_size("Very Large") == "very_large"

    def test_size_normalisation_empty_becomes_unknown(self) -> None:
        mod = self._import_module()
        assert mod.normalise_size("") == "unknown"

    def test_is_within_ner(self) -> None:
        mod = self._import_module()
        assert mod.is_within_ner(91.5, 26.0) is True   # Assam
        assert mod.is_within_ner(77.0, 12.0) is False  # South India
        assert mod.is_within_ner(95.0, 27.5) is True   # Arunachal Pradesh

    def test_geom_wkt_format(self) -> None:
        mod = self._import_module()
        row = {
            "id": "999",
            "latitude": "25.5",
            "longitude": "93.2",
            "event_date": "",
            "event_title": "",
            "location_description": "",
            "country_name": "India",
            "country_code": "IN",
            "admin_division_name": "",
            "landslide_type": "",
            "landslide_size": "",
            "trigger": "",
            "fatalities": "",
            "injuries": "",
            "source_link": "",
        }
        record = mod.validate_record(row)
        # WKT must be POINT(lon lat) — lon before lat per GeoJSON convention
        assert record.geom_wkt.startswith("POINT(93.2 25.5)")
