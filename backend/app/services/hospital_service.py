import json
from pathlib import Path
from typing import List, Optional, Dict
from app.core.logging import logger
from app.schemas.hospital import Hospital, HospitalFilterRequest, HospitalListResponse
from app.services.policy_service import policy_service

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "hospitals.json"

class HospitalService:
    def __init__(self):
        self._hospitals: Dict[str, Hospital] = {}
        self._load_hospitals()

    def _load_hospitals(self):
        try:
            if DATA_PATH.exists():
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        h = Hospital(**item)
                        self._hospitals[h.id] = h
                logger.info(f"Loaded {len(self._hospitals)} hospitals into memory.")
        except Exception as e:
            logger.error(f"Failed to load hospitals data: {e}")

    def get_hospital(self, hospital_id: str) -> Optional[Hospital]:
        return self._hospitals.get(hospital_id)

    def filter_hospitals(self, filter_req: HospitalFilterRequest) -> HospitalListResponse:
        results = list(self._hospitals.values())
        policy = policy_service.get_policy(filter_req.policy_id) if filter_req.policy_id else None

        # Determine cashless status against active policy's TPAs
        evaluated_hospitals: List[Hospital] = []
        for h in results:
            h_copy = h.model_copy()
            if policy:
                # Check if hospital has any overlapping TPA with the policy
                common_tpas = set(h.empanelled_tpas).intersection(set(policy.empanelled_tpas))
                if len(common_tpas) > 0 and h.network_status != "NON_NETWORK":
                    h_copy.network_status = "CASHLESS_NETWORK"
                elif h.network_status != "NON_NETWORK":
                    h_copy.network_status = "REIMBURSEMENT_ONLY"
            evaluated_hospitals.append(h_copy)

        filtered = evaluated_hospitals

        # Filter by distance
        if filter_req.max_distance_km:
            filtered = [h for h in filtered if h.distance_km <= filter_req.max_distance_km]

        # Filter by specialty
        if filter_req.specialty and filter_req.specialty.lower() != "all":
            filtered = [
                h for h in filtered
                if any(filter_req.specialty.lower() in s.lower() for s in h.specialties)
            ]

        # Filter by cashless only
        if filter_req.only_cashless:
            filtered = [h for h in filtered if h.network_status == "CASHLESS_NETWORK"]

        # Emergency 2 AM sorting: prioritizes 24x7 emergency, available ICU beds, and lowest ETA
        if filter_req.emergency_mode:
            filtered = [h for h in filtered if h.emergency_24x7 and h.bed_availability.icu > 0]
            filtered.sort(key=lambda h: (
                0 if h.network_status == "CASHLESS_NETWORK" else 1,
                h.estimated_ambulance_eta_mins,
                h.distance_km
            ))
        else:
            filtered.sort(key=lambda h: (
                0 if h.network_status == "CASHLESS_NETWORK" else 1,
                h.distance_km
            ))

        nearest_cashless_id = None
        for h in filtered:
            if h.network_status == "CASHLESS_NETWORK" and h.bed_availability.icu > 0:
                nearest_cashless_id = h.id
                break

        return HospitalListResponse(
            hospitals=filtered,
            total=len(filtered),
            active_policy_id=policy.id if policy else None,
            nearest_cashless_id=nearest_cashless_id
        )

hospital_service = HospitalService()
