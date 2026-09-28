# Model registry

One JSON file per model. `vg` builds, validates and prices every request from these files, so
adding a model on an existing provider is a new file here and nothing else. A new provider (a
different API shape) also needs a module in `../providers/` and one line in `providers/__init__.py`.

Run `python3 2_Tools/vg/vg.py models` to list what is loaded.

## Fields

| Field | Kind | Meaning |
|---|---|---|
| `id` | all | registry id used in `.env` (`VG_IMAGE_MODEL`, `VG_VIDEO_MODEL`) and `Shotlist.json` `models` |
| `kind` | all | `image` or `video` |
| `provider` | all | provider module name, e.g. `kie` |
| `status` | all | `live-tested` or `untested`. Untested models are refused unless `--allow-untested` |
| `notes` | all | what was verified, when, and known traps |
| `model` | video | the provider's model string |
| `variants.t2i.model` / `variants.i2i.model` | image | model string without and with reference images |
| `variants.i2i.refs_field` / `max_refs` | image | field name for reference image URLs and its limit |
| `prompt_max` | all | prompt length limit in characters |
| `params` | all | `{name: {type: string\|integer, enum, min, max, default}}`. Values are cast to `type` before sending |
| `constraints` | all | `[{when: {param: value}, forbid: {param: [values]}}]` — invalid combinations |
| `modes` | video | how each shot mode maps to fields: `first_frame`, `last_frame`, `frames_list` (both frames as one list), `refs`, `characters`, `voices`, `set` (constant fields) |
| `exclusive` | video | `{field: [fields that may not be sent with it]}` |
| `requires` | video | `{field: field it needs}` |
| `limits` | video | max list length per field |
| `media_quota` | video | `{limit, weights: {field: units per item}}` — summed across fields |
| `dialogue_fit` | video | `chars_per_second` and `lead_s` for the fit rule `chars <= (duration - lead_s) * chars_per_second` |
| `identity` | video | which identity services the model supports (`voice`, `character`) |
| `pricing` | all | `{keys: [param, ...], aliases: {param: {value: key}}, table: nested by keys}` — credits per task |

## Adding a model

1. Copy the closest existing file, change `id`, `model`, fields and prices from the provider's docs.
2. Set `"status": "untested"`.
3. `vg models` to check it loads; `--dry-run` a shot to see the payload.
4. Run one paid pilot, compare `creditsConsumed` in `project.json` with the table, then set
   `"status": "live-tested"` and note the date in `notes`.
