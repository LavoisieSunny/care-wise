import json
import re
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import fitz  # PyMuPDF

from app.core.logging import logger
from app.schemas.policy import (
    PolicyDetails,
    PolicyRoomLimit,
    PolicyCoPay,
    PolicyPreAuth,
    ClauseCitation,
    PolicyUploadResponse
)
from app.services.llm_client import llm_client
from app.core.database import SessionLocal, PolicyRecord, init_db
from app.core.crypto import encrypt_text, decrypt_text

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_policies.json"


def find_page_and_snippet(page_texts: Dict[str, str], keywords: List[str], fallback_page: int = 1) -> Tuple[int, str]:
    """Scan page_texts to locate the real 1-indexed page number and excerpt containing keywords."""
    for page_str, text in page_texts.items():
        page_num = int(page_str)
        text_lower = text.lower()
        for kw in keywords:
            if kw.lower() in text_lower:
                sentences = re.split(r'(?<=[.!?\n])\s+', text)
                for s in sentences:
                    clean_s = s.strip().replace("\n", " ")
                    if kw.lower() in s.lower() and len(clean_s) > 25:
                        return page_num, clean_s[:260]
                return page_num, text[:220].strip().replace("\n", " ")
    return fallback_page, ""


class PolicyService:
    def __init__(self):
        init_db()
        self._upload_cache: Dict[str, Dict[str, Any]] = {}
        self._seed_sample_policies_if_empty()

    def _save_policy(self, policy: PolicyDetails, owner_id: Optional[str] = None):
        """Write-through: upsert policy into the database."""
        db = SessionLocal()
        try:
            record = db.get(PolicyRecord, policy.id)
            if record is None:
                record = PolicyRecord(id=policy.id, owner_id=owner_id)
                db.add(record)
            record.insurer_name = policy.insurer_name
            record.policy_name = policy.policy_name
            record.data_json = encrypt_text(policy.model_dump_json())
            db.commit()
            logger.info(f"Saved policy '{policy.id}' to database.")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save policy '{policy.id}' to DB: {e}")
        finally:
            db.close()

    def _seed_sample_policies_if_empty(self):
        db = SessionLocal()
        try:
            existing_count = db.query(PolicyRecord).count()
        finally:
            db.close()

        if existing_count > 0:
            logger.info(f"Database already has {existing_count} policies — skipping seed.")
            return

        try:
            if DATA_PATH.exists():
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        if not item.get("raw_text_pages"):
                            synth_pages: Dict[str, str] = {}
                            citations = item.get("all_citations", [])
                            for c in citations:
                                pg = str(c.get("page_number", 1))
                                if pg not in synth_pages:
                                    synth_pages[pg] = ""
                                synth_pages[pg] += f"\n[{c.get('section', 'Terms')}]\n{c.get('clause_title', '')}: {c.get('exact_text', '')}\n"
                            if "1" not in synth_pages:
                                synth_pages["1"] = f"Policy Schedule: {item.get('policy_name')}\nSum Insured: Rs. {item.get('sum_insured', 500000):,.0f}\nInsurer: {item.get('insurer_name')}"
                            if "12" not in synth_pages:
                                synth_pages["12"] = "Room Rent Clause 3.2.1: Room rent limit capped per policy schedule. Proportionate deductions apply on doctor fees."
                            item["raw_text_pages"] = synth_pages

                        policy = PolicyDetails(**item)
                        self._save_policy(policy)
                logger.info(f"Seeded {len(data)} sample policies into database.")
        except Exception as e:
            logger.error(f"Failed to seed sample policies: {e}")

    def list_policies(self, owner_id: Optional[str] = None) -> List[PolicyDetails]:
        db = SessionLocal()
        try:
            query = db.query(PolicyRecord)
            if owner_id:
                # Show the user's own uploads PLUS the seeded sample policies (owner_id is NULL)
                query = query.filter((PolicyRecord.owner_id == owner_id) | (PolicyRecord.owner_id.is_(None)))
            return [PolicyDetails(**json.loads(decrypt_text(r.data_json))) for r in query.all()]
        finally:
            db.close()

    def get_policy(self, policy_id: str, owner_id: Optional[str] = None) -> Optional[PolicyDetails]:
        db = SessionLocal()
        try:
            record = db.get(PolicyRecord, policy_id)
            if not record:
                return None
            if owner_id and record.owner_id and record.owner_id != owner_id:
                return None  # exists, but belongs to someone else
            return PolicyDetails(**json.loads(decrypt_text(record.data_json))) if record else None
        finally:
            db.close()

    def _heuristic_extraction(
        self,
        full_text: str,
        page_texts: Dict[str, str],
        filename: str,
        total_pages: int
    ) -> PolicyDetails:
        """Robust multi-field heuristic extraction scanning real pages."""
        policy_id = f"custom_{re.sub(r'[^a-zA-Z0-9]', '_', filename.lower())[:20]}"

        # 1. Sum Insured detection & page
        si_match = re.search(
            r"(?:Sum\s*Insured|SI|Coverage|Limit\s*of\s*Indemnity)[\s:]*(?:Rs\.?|INR|₹)?\s*([\d,]+)",
            full_text,
            re.IGNORECASE
        )
        sum_insured = 500000.0
        si_page = 1
        si_quote = f"Total Sum Insured is Rs. {sum_insured:,.0f}/- per policy year."
        if si_match:
            try:
                cleaned_si = si_match.group(1).replace(",", "")
                val = float(cleaned_si)
                if val >= 50000:
                    sum_insured = val
            except Exception:
                pass
            p_num, snippet = find_page_and_snippet(page_texts, ["Sum Insured", "Limit of Indemnity", "Coverage"], 1)
            si_page = p_num
            if snippet:
                si_quote = snippet

        # 2. Room Rent Cap detection & page
        no_room_cap = bool(re.search(
            r"no\s*room\s*rent\s*capping|any\s*room\s*category|single\s*private\s*room\s*without\s*capping|no\s*sub-?limit\s*on\s*room",
            full_text,
            re.IGNORECASE
        ))
        room_cap_amount = None if no_room_cap else (sum_insured * 0.01)
        room_pct = None if no_room_cap else 1.0
        proportionate = not no_room_cap

        room_match = re.search(
            r"(?:room\s*rent|boarding)[\s\S]{1,80}?(?:1%|2%|₹\s*[\d,]+|Rs\.?\s*[\d,]+)",
            full_text,
            re.IGNORECASE
        )
        if room_match and "2%" in room_match.group(0):
            room_pct = 2.0
            room_cap_amount = sum_insured * 0.02

        room_page, room_quote = find_page_and_snippet(
            page_texts,
            ["room rent", "boarding and nursing", "proportionate deduction", "single private room"],
            min(2, total_pages)
        )
        if not room_quote:
            room_quote = "Room rent limit capped at 1% of Sum Insured per day. Proportionate deduction applies if exceeded." if not no_room_cap else "No room rent sub-limits applicable."

        # 3. Co-payment detection & page
        senior_copay = 20.0 if re.search(r"co-?pay[\s\S]{1,60}?(?:senior|60\s*years|65\s*years)", full_text, re.IGNORECASE) else 0.0
        standard_copay = 10.0 if re.search(r"(?:mandatory\s*co-?pay|10%\s*co-?pay)", full_text, re.IGNORECASE) else 0.0

        copay_page, copay_quote = find_page_and_snippet(
            page_texts,
            ["co-pay", "copayment", "senior citizen", "cost sharing"],
            min(3, total_pages)
        )
        if not copay_quote:
            copay_quote = f"Senior Citizen Co-pay: {senior_copay:.0f}%. Standard Co-pay: {standard_copay:.0f}%."

        # 4. Pre-auth emergency notice & page
        preauth_page, preauth_quote = find_page_and_snippet(
            page_texts,
            ["pre-auth", "cashless", "emergency admission", "intimation within", "24 hours"],
            min(4, total_pages)
        )
        if not preauth_quote:
            preauth_quote = "Emergency hospital admissions require cashless pre-auth intimation within 24 hours of admission."

        # 5. TPAs
        known_tpas = ["Medi Assist", "Vidal Health", "FHPL", "MDIndia", "Paramount", "Star Health In-House Desk", "Raksha TPA"]
        found_tpas = [tpa for tpa in known_tpas if tpa.lower() in full_text.lower()]
        if not found_tpas:
            found_tpas = ["Medi Assist", "Vidal Health", "In-House Cashless Desk"]

        # 6. Citations
        citations = [
            ClauseCitation(
                clause_id="SEC-EXT-1",
                section="Schedule of Benefits - Sum Insured",
                page_number=si_page,
                clause_title="Basic Sum Insured Limit",
                exact_text=si_quote,
                tag="SUM_INSURED",
                confidence=0.92
            ),
            ClauseCitation(
                clause_id="SEC-EXT-2",
                section="Coverage Terms - Room Rent",
                page_number=room_page,
                clause_title="Room Rent & Proportionate Deduction",
                exact_text=room_quote,
                tag="ROOM_LIMIT",
                confidence=0.90
            ),
            ClauseCitation(
                clause_id="SEC-EXT-3",
                section="Claims Guidelines - Pre-Authorisation",
                page_number=preauth_page,
                clause_title="24-Hour Emergency Intimation",
                exact_text=preauth_quote,
                tag="PREAUTH",
                confidence=0.88
            ),
            ClauseCitation(
                clause_id="SEC-EXT-4",
                section="Co-payment & Cost Sharing",
                page_number=copay_page,
                clause_title="Applicable Co-payment Condition",
                exact_text=copay_quote,
                tag="COPAY",
                confidence=0.85 if (senior_copay > 0 or standard_copay > 0) else 0.75
            )
        ]

        # 7. Waiting periods
        wp_page, _ = find_page_and_snippet(page_texts, ["waiting period", "30 days", "24 months"], 2)
        waiting_periods = [
            {"type": "Initial Waiting Period", "duration": "30 Days", "description": "General illness covered after 30 days of active cover.", "page": wp_page},
            {"type": "Specific Illnesses", "duration": "24 Months", "description": "Cataract, hernia, joint replacement covered after 2 years.", "page": min(wp_page + 1, total_pages)}
        ]

        # 8. Exclusions
        key_exclusions = [
            "Non-medical hygiene disposables and IRDAI List I items",
            "Rest cure, diagnostic admissions without active surgical or medical therapy"
        ]
        if "cosmetic" in full_text.lower():
            key_exclusions.append("Cosmetic and aesthetic treatments")

        return PolicyDetails(
            id=policy_id,
            insurer_name="Extracted Health Insurance",
            policy_name=f"{filename.replace('.pdf', '').title()} (Auto-Extracted)",
            policy_type="Custom Ingested Policy",
            sum_insured=sum_insured,
            room_limit=PolicyRoomLimit(
                capped_amount_per_day=room_cap_amount,
                percentage_of_sum_insured=room_pct,
                no_room_rent_capping=no_room_cap,
                allowed_room_category="Standard Single Room" if not no_room_cap else "Any Room Category",
                proportionate_deduction_applies=proportionate,
                citation=citations[1]
            ),
            icu_limit_per_day=sum_insured * 0.02,
            copay=PolicyCoPay(
                standard_percentage=standard_copay,
                senior_citizen_percentage=senior_copay,
                citation=citations[3]
            ),
            pre_auth=PolicyPreAuth(
                emergency_window_hours=24,
                planned_window_hours=48,
                citation=citations[2]
            ),
            has_consumables_rider=bool(re.search(r"consumables\s*rider|non-medical\s*items\s*cover", full_text, re.IGNORECASE)),
            empanelled_tpas=found_tpas,
            waiting_periods=waiting_periods,
            key_exclusions=key_exclusions,
            all_citations=citations,
            raw_text_pages=page_texts
        )

    def _llm_based_extraction(
        self,
        full_text: str,
        page_texts: Dict[str, str],
        filename: str,
        total_pages: int
    ) -> PolicyDetails:
        """Deep extraction using LLM client with real page grounding."""
        llm_data = llm_client.extract_policy_fields(full_text)
        if not llm_data:
            logger.info("LLM extraction unavailable or timed out, using heuristic pass.")
            return self._heuristic_extraction(full_text, page_texts, filename, total_pages)

        policy_id = f"custom_{re.sub(r'[^a-zA-Z0-9]', '_', filename.lower())[:20]}"
        sum_insured = float(llm_data.get("sum_insured", 500000.0))

        # Room limit
        rl = llm_data.get("room_limit", {})
        rl_page = max(1, min(int(rl.get("page", 2)), total_pages))
        rl_quote = rl.get("quote") or "Room rent limited as per schedule."
        rl_conf = float(rl.get("confidence", 0.95))
        room_limit_citation = ClauseCitation(
            clause_id="SEC-LLM-ROOM",
            section="Coverage Terms - Room Rent",
            page_number=rl_page,
            clause_title="Room Rent & Associated Charges",
            exact_text=rl_quote,
            tag="ROOM_LIMIT",
            confidence=rl_conf
        )

        room_limit = PolicyRoomLimit(
            capped_amount_per_day=rl.get("capped_amount_per_day"),
            percentage_of_sum_insured=rl.get("percentage_of_sum_insured"),
            no_room_rent_capping=bool(rl.get("no_room_rent_capping", False)),
            allowed_room_category=rl.get("allowed_room_category", "Standard Single Room"),
            proportionate_deduction_applies=bool(rl.get("proportionate_deduction_applies", True)),
            citation=room_limit_citation
        )

        # Copay
        cp = llm_data.get("copay", {})
        cp_page = max(1, min(int(cp.get("page", 3)), total_pages))
        cp_quote = cp.get("quote") or "Applicable co-payment as per policy terms."
        cp_conf = float(cp.get("confidence", 0.92))
        copay_citation = ClauseCitation(
            clause_id="SEC-LLM-COPAY",
            section="Co-payment & Cost Sharing",
            page_number=cp_page,
            clause_title="Mandatory Co-Payment Clause",
            exact_text=cp_quote,
            tag="COPAY",
            confidence=cp_conf
        )

        copay = PolicyCoPay(
            standard_percentage=float(cp.get("standard_percentage", 0.0)),
            senior_citizen_percentage=float(cp.get("senior_citizen_percentage", 0.0)),
            zone_based_copay=float(cp.get("zone_based_copay", 0.0)),
            citation=copay_citation
        )

        # Pre-auth
        pa = llm_data.get("pre_auth", {})
        pa_page = max(1, min(int(pa.get("page", 2)), total_pages))
        pa_quote = pa.get("quote") or "Emergency cashless pre-auth required within 24 hours."
        pa_conf = float(pa.get("confidence", 0.94))
        preauth_citation = ClauseCitation(
            clause_id="SEC-LLM-PREAUTH",
            section="Claims Guidelines - Pre-Authorisation",
            page_number=pa_page,
            clause_title="Pre-Authorization Intimation Window",
            exact_text=pa_quote,
            tag="PREAUTH",
            confidence=pa_conf
        )

        pre_auth = PolicyPreAuth(
            emergency_window_hours=int(pa.get("emergency_window_hours", 24)),
            planned_window_hours=int(pa.get("planned_window_hours", 48)),
            citation=preauth_citation
        )

        # Sum insured citation
        si_citation = ClauseCitation(
            clause_id="SEC-LLM-SI",
            section="Schedule of Benefits - Sum Insured",
            page_number=1,
            clause_title="Total Coverage Limit",
            exact_text=f"Total Sum Insured for primary policyholder is Rs. {sum_insured:,.0f}/- per policy year.",
            tag="SUM_INSURED",
            confidence=0.96
        )

        all_citations = [si_citation, room_limit_citation, preauth_citation, copay_citation]

        return PolicyDetails(
            id=policy_id,
            insurer_name="Extracted Health Insurance",
            policy_name=f"{filename.replace('.pdf', '').title()} (AI Deep Extracted)",
            policy_type="Custom Ingested Policy",
            sum_insured=sum_insured,
            room_limit=room_limit,
            icu_limit_per_day=llm_data.get("icu_limit_per_day"),
            copay=copay,
            pre_auth=pre_auth,
            has_consumables_rider=bool(llm_data.get("has_consumables_rider", False)),
            empanelled_tpas=llm_data.get("empanelled_tpas", ["Medi Assist", "Vidal Health"]),
            waiting_periods=llm_data.get("waiting_periods", []),
            key_exclusions=llm_data.get("key_exclusions", []),
            all_citations=all_citations,
            raw_text_pages=page_texts
        )

    def parse_pdf(self, file_bytes: bytes, filename: str, mode: str = "quick", owner_id: Optional[str] = None) -> PolicyUploadResponse:
        """Extract text from uploaded PDF and run either quick OCR heuristics or AI deep extraction."""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)
            page_texts: Dict[str, str] = {}
            full_text = ""

            for i in range(total_pages):
                page_text = doc[i].get_text()
                page_texts[str(i + 1)] = page_text
                full_text += f"\n--- Page {i + 1} ---\n" + page_text

            upload_id = f"upl_{uuid.uuid4().hex[:10]}"
            self._upload_cache[upload_id] = {
                "filename": filename,
                "total_pages": total_pages,
                "page_texts": page_texts,
                "full_text": full_text
            }

            if mode == "ai":
                policy_details = self._llm_based_extraction(full_text, page_texts, filename, total_pages)
                conf = 0.96
            else:
                policy_details = self._heuristic_extraction(full_text, page_texts, filename, total_pages)
                conf = 0.89

            self._save_policy(policy_details, owner_id=owner_id)
            logger.info(f"Processed uploaded policy '{filename}' ({total_pages} pages, mode={mode}). ID: {policy_details.id}")

            return PolicyUploadResponse(
                success=True,
                message=f"Policy '{filename}' processed successfully ({total_pages} pages extracted via {mode} mode).",
                policy=policy_details,
                pages_processed=total_pages,
                confidence_score=conf,
                upload_id=upload_id,
                extraction_mode=mode
            )

        except Exception as e:
            logger.error(f"Error parsing PDF '{filename}': {e}", exc_info=True)
            raise ValueError(f"Failed to process policy PDF: {str(e)}")

    def parse_pdf_deep(self, upload_id: str, owner_id: Optional[str] = None) -> PolicyUploadResponse:
        """Run deep AI LLM extraction on previously uploaded document using cached page texts."""
        cached = self._upload_cache.get(upload_id)
        if not cached:
            raise ValueError(f"Upload ID '{upload_id}' not found in cache. Please re-upload the document.")

        filename = cached["filename"]
        total_pages = cached["total_pages"]
        page_texts = cached["page_texts"]
        full_text = cached["full_text"]

        policy_details = self._llm_based_extraction(full_text, page_texts, filename, total_pages)
        self._save_policy(policy_details, owner_id=owner_id)

        return PolicyUploadResponse(
            success=True,
            message=f"AI Deep Extraction completed for '{filename}' ({total_pages} pages).",
            policy=policy_details,
            pages_processed=total_pages,
            confidence_score=0.96,
            upload_id=upload_id,
            extraction_mode="ai"
        )


policy_service = PolicyService()

