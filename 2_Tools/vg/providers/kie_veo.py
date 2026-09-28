"""kie.ai legacy Veo 3.1 endpoint — the only way to pick the Lite / Fast / Quality tier.

Verified 2026-09-24 against docs.kie.ai/old-model/veo3-api (raw OpenAPI):
- POST /api/v1/veo/generate, top-level body fields (no `input` wrapper): prompt, imageUrls (1 image =
  first frame, 2 = first + last), model (veo3 | veo3_fast | veo3_lite), generationType
  (TEXT_2_VIDEO | FIRST_AND_LAST_FRAMES_2_VIDEO | REFERENCE_2_VIDEO), aspect_ratio (16:9 | 9:16 | Auto),
  resolution (720p | 1080p | 4k), duration (integer 4 | 6 | 8), enableTranslation, callBackUrl, watermark.
- GET /api/v1/veo/record-info?taskId= -> data.successFlag 0 generating, 1 success, 2 failed,
  3 upstream generation failed; data.response.resultUrls; data.errorCode / data.errorMessage.
Uploads, balance and downloads are the same as the unified kie.ai API, so they are inherited.
"""
from providers.kie import BASE_URL, KieProvider
from vglib.errors import ProviderError


class KieVeoProvider(KieProvider):
    name = "kie-veo"

    def create_task(self, model, input_payload):
        body = dict(input_payload)
        body["model"] = model
        body.setdefault("enableTranslation", False)  # keep dialogue in its own language
        status, payload = self._request("POST", BASE_URL + "/api/v1/veo/generate", body=body)
        self._checked("Veo generate", status, payload)
        task_id = (payload.get("data") or {}).get("taskId")
        if not task_id:
            raise ProviderError("Veo generate returned no taskId: %s" % payload, payload=payload)
        return task_id

    def get_task(self, task_id):
        status, payload = self._request("GET", BASE_URL + "/api/v1/veo/record-info", query={"taskId": task_id})
        self._checked("Veo record-info", status, payload)
        data = payload.get("data") or {}
        flag = data.get("successFlag")
        response = data.get("response") or {}
        state = {0: "generating", 1: "success", 2: "fail", 3: "fail"}.get(flag, "generating")
        return {
            "state": state,
            "urls": list(response.get("resultUrls") or []),
            "credits": None,  # not reported by this endpoint; the ledger keeps the listed price
            "fail_code": str(data.get("errorCode") or ""),
            "fail_msg": data.get("errorMessage") or "",
            "progress": None,
        }
