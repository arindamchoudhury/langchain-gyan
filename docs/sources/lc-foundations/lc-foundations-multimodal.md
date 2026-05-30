---
name: lc-foundations-multimodal
description: LangChain Module 1.4 multimodal messages — text/image/audio content blocks, base64 encoding workflow, model requirements, DeepSeek vision limitation
---

# Module 1.4: Multimodal Messages

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 4)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `notebooks/module-1/1.4_multimodal_messages.ipynb`
> **Added:** 2026-05-30
> **Tags:** multimodal, image, audio, HumanMessage, content-blocks, base64, gpt-5-nano, gpt-4o-audio-preview
> **Type:** notebook / course lesson

> 📌 **Full explained chapter:** [[ch06-multimodal]]

## Summary

How to send text, images, and audio to agents using `HumanMessage` with a content block list. Covers the base64 encoding workflow for images (via Jupyter file upload) and audio (via microphone recording), and which models support each modality.

## Key points

- `HumanMessage.content` accepts a plain string or a list of typed content block dicts
- Image block: `{"type": "image", "base64": "...", "mime_type": "image/png"}`
- Audio block: `{"type": "audio", "base64": "...", "mime_type": "audio/wav"}`
- The model must support the modality — not all models accept images or audio
- `deepseek-chat` (DeepSeek V3) is text-only via the standard API; use GPT for multimodal
- `gpt-5-nano` handles text and images; `gpt-4o-audio-preview` is needed for audio
- `FileUpload` from `ipywidgets` returns `memoryview` — must convert to `bytes` before base64 encoding

## Notes

### Text input — content list format

`HumanMessage.content` can be a plain string (as used in earlier lessons) or a list of typed blocks. The text block in list form:

```python
# langchain 1.3.2 (May 2026)
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

agent = create_agent(
    model='gpt-5-nano',
    system_prompt="You are a science fiction writer, create a capital city at the users request.",
)

question = HumanMessage(content=[
    {"type": "text", "text": "What is the capital of The Moon?"}
])

response = agent.invoke({"messages": [question]})
print(response['messages'][-1].content)
```

Single-string `content="..."` and list `content=[{"type": "text", ...}]` are equivalent for text — the list form is required when mixing modalities.

### Image input — base64 workflow

```python
from ipywidgets import FileUpload
from IPython.display import display
import base64

# Step 1: Jupyter widget to upload a file
uploader = FileUpload(accept='.png', multiple=False)
display(uploader)

# Step 2: Extract bytes — .content is a memoryview, not bytes
uploaded_file = uploader.value[0]
img_bytes = bytes(uploaded_file["content"])  # memoryview → bytes

# Step 3: Base64 encode
img_b64 = base64.b64encode(img_bytes).decode("utf-8")

# Step 4: Build multimodal message
multimodal_question = HumanMessage(content=[
    {"type": "text", "text": "Tell me about this capital"},
    {"type": "image", "base64": img_b64, "mime_type": "image/png"}
])

response = agent.invoke({"messages": [multimodal_question]})
print(response['messages'][-1].content)
```

> ⚠️ `FileUpload` is Jupyter-specific. In production, read the file from disk with `open()` or from a web request body.

> ⚠️ **DeepSeek limitation:** `deepseek-chat` (DeepSeek V3) is text-only via the standard API. Image blocks will fail or be silently ignored. DeepSeek does have vision models (VL2 series) but they are not accessible via `langchain-deepseek`. Use a vision-capable model like `gpt-5-nano` instead.

### Audio input — microphone recording workflow

Audio input requires a dedicated audio-capable model (`gpt-4o-audio-preview`):

```python
import sounddevice as sd
from scipy.io.wavfile import write
import base64, io, time
from tqdm import tqdm

# Record 5 seconds of audio
duration = 5
sample_rate = 44100
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
for _ in tqdm(range(duration * 10)):
    time.sleep(0.1)
sd.wait()

# Write to in-memory WAV buffer
buf = io.BytesIO()
write(buf, sample_rate, audio)
aud_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

# Audio model
agent = create_agent(model='gpt-4o-audio-preview')

multimodal_question = HumanMessage(content=[
    {"type": "text", "text": "Tell me about this audio file"},
    {"type": "audio", "base64": aud_b64, "mime_type": "audio/wav"}
])

response = agent.invoke({"messages": [multimodal_question]})
print(response['messages'][-1].content)
```

### Content block format summary

| Type | Required keys | Example mime_type |
|---|---|---|
| `text` | `type`, `text` | — |
| `image` | `type`, `base64`, `mime_type` | `image/png`, `image/jpeg` |
| `audio` | `type`, `base64`, `mime_type` | `audio/wav`, `audio/mpeg` |

### Model capability matrix

| Model | Text | Image | Audio |
|---|---|---|---|
| `gpt-5-nano` | ✓ | ✓ | ✗ |
| `gpt-4o-audio-preview` | ✓ | ✗ | ✓ |
| `deepseek-chat` | ✓ | ✗ | ✗ |

## Open questions

- Does `gpt-5-nano` support audio input, or is `gpt-4o-audio-preview` always needed?
- Can a single agent handle both image and audio if the model supports both?
- What happens to image blocks when sent to a text-only model — silent ignore or error?

## Related sources

- [[lc-foundations-foundational-models]] — `create_agent`, `HumanMessage` basics
- [[ch06-multimodal]] — full pedagogical chapter
