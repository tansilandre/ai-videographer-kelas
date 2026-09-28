"""kie.ai provider.

Verified 2026-09-24 against docs.kie.ai and live calls:
- Base https://api.kie.ai, header `Authorization: Bearer <key>`.
- POST /api/v1/jobs/createTask {model, input} -> data.taskId
- GET  /api/v1/jobs/recordInfo?taskId= -> data.state in waiting|queuing|generating|success|fail,
  data.resultJson is a JSON string with resultUrls, data.creditsConsumed.
- GET  /api/v1/chat/credit -> data is the balance.
- Uploads live on https://kieai.redpandaai.co (the api.kie.ai host 404s for uploads).
  Uploaded files are deleted after about 24 h.
- Gemini Omni identity endpoints are synchronous and take top-level fields:
  POST /api/v1/omni/audio/create -> data.audioId (the docs say kieAudioId; the live field is audioId)
  POST /api/v1/omni/character/create -> data.characterId
"""
import base64
import json
import mimetypes
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from vglib.errors import ProviderError

BASE_URL = "https://api.kie.ai"
UPLOAD_BASE_URL = "https://kieai.redpandaai.co"

ERROR_HINTS = {
    400: "bad request or invalid parameters",
    401: "missing or invalid API key",
    402: "insufficient credits",
    404: "not found",
    422: "validation error: a field name, type or value is wrong",
    429: "rate limited: max 20 new requests per 10 seconds",
    433: "request rejected",
    455: "service under maintenance",
    500: "server error",
    501: "generation failed",
    505: "feature disabled",
}

PENDING_STATES = ("waiting", "queuing", "generating")


class KieProvider:
    name = "kie"
    upload_ttl_s = 20 * 3600

    def __init__(self, api_key, timeout=90):
        self._key = api_key
        self.timeout = timeout

    # ------------------------------------------------------------------ http

    def _request(self, method, url, body=None, query=None, data=None, content_type=None):
        if query:
            url = url + "?" + urllib.parse.urlencode(query)
        headers = {"Authorization": "Bearer " + self._key, "Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            content_type = "application/json"
        if content_type:
            headers["Content-Type"] = content_type
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                status = response.status
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            status = exc.code
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError("Network error calling %s: %s" % (url.split("?")[0], exc))
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except ValueError:
            raise ProviderError("Non-JSON response (HTTP %s): %s" % (status, raw[:300]))
        return status, payload

    def _fail(self, what, status, payload):
        code = payload.get("code")
        hint = ERROR_HINTS.get(code) or ERROR_HINTS.get(status) or "unknown error"
        if "not authorized to use this model" in str(payload.get("msg", "")).lower():
            hint = ("the key works, but its model allowlist excludes this model: the human enables it for this key "
                    "at kie.ai/api-key, then the same command can run again")
        raise ProviderError(
            "%s failed: code=%s http=%s msg=%r (%s)" % (what, code, status, payload.get("msg"), hint),
            code=code or status,
            payload=payload,
        )

    def _checked(self, what, status, payload):
        if status >= 400 or payload.get("code") not in (None, 200):
            self._fail(what, status, payload)
        return payload

    # ------------------------------------------------------------------ account

    def credits(self):
        status, payload = self._request("GET", BASE_URL + "/api/v1/chat/credit")
        self._checked("Balance check", status, payload)
        return float(payload.get("data") or 0)

    # ------------------------------------------------------------------ tasks

    def create_task(self, model, input_payload):
        body = {"model": model, "input": input_payload}
        for attempt in range(4):
            status, payload = self._request("POST", BASE_URL + "/api/v1/jobs/createTask", body=body)
            if payload.get("code") == 429 or status == 429:
                time.sleep(3 * (attempt + 1))
                continue
            self._checked("createTask", status, payload)
            task_id = (payload.get("data") or {}).get("taskId")
            if not task_id:
                raise ProviderError("createTask returned no taskId: %s" % payload, payload=payload)
            return task_id
        self._fail("createTask", 429, {"code": 429, "msg": "still rate limited after retries"})

    def get_task(self, task_id):
        last_error = None
        for attempt in range(3):
            try:
                status, payload = self._request(
                    "GET", BASE_URL + "/api/v1/jobs/recordInfo", query={"taskId": task_id}
                )
                self._checked("recordInfo", status, payload)
                break
            except ProviderError as exc:
                last_error = exc
                time.sleep(2 * (attempt + 1))
        else:
            raise last_error
        data = payload.get("data") or {}
        result = data.get("resultJson") or {}
        if isinstance(result, str):
            try:
                result = json.loads(result) if result.strip() else {}
            except ValueError:
                result = {}
        urls = list(result.get("resultUrls") or [])
        state = data.get("state") or "waiting"
        return {
            "state": state if state in PENDING_STATES + ("success", "fail") else "waiting",
            "urls": urls,
            "credits": data.get("creditsConsumed"),
            "fail_code": data.get("failCode") or "",
            "fail_msg": data.get("failMsg") or "",
            "progress": data.get("progress"),
        }

    # ------------------------------------------------------------------ files

    def upload(self, path, upload_path="vg"):
        size = os.path.getsize(path)
        name = os.path.basename(path)
        if size <= 8 * 1024 * 1024:
            mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
            with open(path, "rb") as handle:
                encoded = base64.b64encode(handle.read()).decode("ascii")
            body = {
                "base64Data": "data:%s;base64,%s" % (mime, encoded),
                "uploadPath": upload_path,
                "fileName": name,
            }
            status, payload = self._request("POST", UPLOAD_BASE_URL + "/api/file-base64-upload", body=body)
        else:
            boundary = "vg" + uuid.uuid4().hex
            with open(path, "rb") as handle:
                content = handle.read()
            parts = []
            for field, value in (("uploadPath", upload_path), ("fileName", name)):
                parts.append(
                    ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                     % (boundary, field, value)).encode("utf-8")
                )
            mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
            parts.append(
                ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
                 "Content-Type: %s\r\n\r\n" % (boundary, name, mime)).encode("utf-8")
            )
            parts.append(content)
            parts.append(("\r\n--%s--\r\n" % boundary).encode("utf-8"))
            status, payload = self._request(
                "POST", UPLOAD_BASE_URL + "/api/file-stream-upload", data=b"".join(parts),
                content_type="multipart/form-data; boundary=" + boundary,
            )
        ok = status < 400 and (payload.get("success") is True or payload.get("code") == 200)
        url = (payload.get("data") or {}).get("downloadUrl")
        if not ok or not url:
            self._fail("Upload of %s" % name, status, payload)
        return url

    def download(self, url, dest):
        tmp = str(dest) + ".part"
        request = urllib.request.Request(url, headers={"User-Agent": "vg/1.0"})
        last_error = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=300) as response, open(tmp, "wb") as out:
                    while True:
                        chunk = response.read(1 << 20)
                        if not chunk:
                            break
                        out.write(chunk)
                os.replace(tmp, str(dest))
                return
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = exc
                time.sleep(3 * (attempt + 1))
        raise ProviderError("Download failed for %s: %s" % (url, last_error))

    # ------------------------------------------------------------------ omni identity

    def _omni(self, what, path, body):
        status, payload = self._request("POST", BASE_URL + path, body=body)
        data = payload.get("data")
        if status < 400 and isinstance(data, dict) and data:
            return data
        if status < 400 and payload.get("code") in (0, 200) and isinstance(data, dict):
            return data
        self._fail(what, status, payload)

    def create_voice(self, preset, name, description=None, example=None):
        body = {"audio_id": preset, "name": name}
        if description:
            body["voice_description"] = description
        if example:
            body["example_dialogue"] = example
        data = self._omni("Voice create", "/api/v1/omni/audio/create", body)
        voice_id = data.get("audioId") or data.get("kieAudioId")
        if not voice_id:
            raise ProviderError("Voice create returned no audioId: %s" % data)
        return voice_id

    def create_character(self, descriptions, image_urls, audio_ids=None, name=None):
        body = {"descriptions": descriptions, "image_urls": list(image_urls)}
        if audio_ids:
            body["audio_ids"] = list(audio_ids)
        if name:
            body["character_name"] = name
        data = self._omni("Character create", "/api/v1/omni/character/create", body)
        character_id = data.get("characterId")
        if not character_id:
            raise ProviderError("Character create returned no characterId: %s" % data)
        return character_id
