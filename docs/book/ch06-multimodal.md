# Chapter 6: Multimodal Messages — Sending Images and Audio to Agents

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 4)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `1.4_multimodal_messages.ipynb`
> **Version:** langchain 1.3.2 (May 2026)
> **Added:** 2026-05-30

---

## What you'll learn

- How `HumanMessage.content` works as a list of typed content blocks
- The base64 encoding workflow for images and audio
- Which models support which modalities — and what happens when they don't
- Why `deepseek-chat` can't handle images and which models to use instead

---

## The problem this solves

Text is only one channel. Real applications need to process images (receipts, screenshots, diagrams), audio (voice commands, call recordings), and documents. `HumanMessage.content` supports all of these through a uniform content block format — the same pattern works across text, images, and audio, and LangChain translates it to each provider's native API format.

---

## Core concept

`HumanMessage.content` accepts either a plain string or a **list of content blocks**. Each block is a dict with a `type` field and type-specific fields:

```python
# Plain string — works for text only
HumanMessage(content="Hello")

# Content block list — required for multimodal
HumanMessage(content=[
    {"type": "text",  "text": "Describe this image"},
    {"type": "image", "base64": "...", "mime_type": "image/png"},
])
```

Blocks can be freely mixed. A single message can contain multiple texts, multiple images, or any combination. OpenAI, Anthropic, and Google each have different native schemas for multimodal content, but LangChain translates the standard block format to whichever provider you're using — your message construction code stays the same regardless of which model you switch to.

**Model capability is a hard requirement.** Sending an image block to a text-only model will either error or silently produce a wrong answer. Always match modality to model.

---

## Code examples

### Example 1: Text as a content block

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

`content="..."` and `content=[{"type": "text", "text": "..."}]` are equivalent for text. The list form is required once you add any other block type.

### Example 2: Image input

Three steps — upload, encode, send:

```python
from ipywidgets import FileUpload
from IPython.display import display
import base64

# Step 1: Jupyter file picker (Jupyter-specific — see note below)
uploader = FileUpload(accept='.png', multiple=False)
display(uploader)

# Step 2: Extract bytes
# uploader.value[0]["content"] is a memoryview, not bytes — must convert
img_bytes = bytes(uploader.value[0]["content"])

# Step 3: Base64 encode to string
img_b64 = base64.b64encode(img_bytes).decode("utf-8")

# Step 4: Send with image block
multimodal_question = HumanMessage(content=[
    {"type": "text",  "text": "Tell me about this capital"},
    {"type": "image", "base64": img_b64, "mime_type": "image/png"},
])

response = agent.invoke({"messages": [multimodal_question]})
print(response['messages'][-1].content)
```

> **Note on `FileUpload`:** This is a Jupyter notebook widget. Outside of Jupyter, read the file from disk instead:
> ```python
> with open("image.png", "rb") as f:
>     img_b64 = base64.b64encode(f.read()).decode("utf-8")
> ```

### Example 3: Audio input

Audio requires a dedicated audio-capable model. `gpt-5-nano` does not process audio.

```python
import sounddevice as sd
from scipy.io.wavfile import write
import base64, io, time
from tqdm import tqdm

# Record 5 seconds from microphone
duration = 5
sample_rate = 44100
print("Recording...")
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
for _ in tqdm(range(duration * 10)):
    time.sleep(0.1)
sd.wait()
print("Done.")

# Write to in-memory WAV buffer and base64 encode
buf = io.BytesIO()
write(buf, sample_rate, audio)
aud_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

# Audio model — gpt-5-nano cannot process audio
agent = create_agent(model='gpt-4o-audio-preview')

multimodal_question = HumanMessage(content=[
    {"type": "text",  "text": "Tell me about this audio file"},
    {"type": "audio", "base64": aud_b64, "mime_type": "audio/wav"},
])

response = agent.invoke({"messages": [multimodal_question]})
print(response['messages'][-1].content)
```

---

## Content block format

| Type | Required keys | Common `mime_type` values |
|---|---|---|
| `text` | `type`, `text` | — |
| `image` | `type`, `base64`, `mime_type` | `image/png`, `image/jpeg`, `image/webp` |
| `audio` | `type`, `base64`, `mime_type` | `audio/wav`, `audio/mpeg`, `audio/mp4` |

---

## Model capability matrix

The notebook uses GPT throughout — not DeepSeek. This is not accidental.

| Model | Text | Image | Audio |
|---|---|---|---|
| `gpt-5-nano` | ✓ | ✓ | ✗ |
| `gpt-4o-audio-preview` | ✓ | ✗ | ✓ |
| `deepseek-chat` | ✓ | ✗ | ✗ |

**`deepseek-chat` (DeepSeek V3) is text-only** via the standard API that `langchain-deepseek` uses. DeepSeek does have vision models (the VL2 series), but they are not accessible through the `deepseek-chat` endpoint. Sending an image block to `deepseek-chat` will either error or be ignored — you won't get a useful response. Use `gpt-5-nano` or another vision-capable model for image tasks.

---

## Best practices

- **Match model to modality before running** — check the provider's docs to confirm vision/audio support. Errors from unsupported modalities are often opaque
- **Read files from disk in production** — `ipywidgets.FileUpload` is notebook-only. Use `open("file.png", "rb")` in scripts or API handlers
- **Keep base64 size in mind** — a 1 MB image becomes ~1.3 MB of base64 text in the prompt. Large images inflate token costs significantly; resize before encoding if possible
- **Use `mime_type` accurately** — sending `image/png` for a JPEG may cause model errors. Check the actual file format

---

## Common pitfalls

- **`memoryview` vs `bytes`** — `FileUpload.value[0]["content"]` is a `memoryview` object, not `bytes`. Calling `base64.b64encode()` on a `memoryview` directly may fail or produce wrong output. Always convert first: `bytes(uploaded_file["content"])`.

- **Wrong model for the modality** — sending an image to `deepseek-chat` or audio to `gpt-5-nano` won't raise a clear error upfront. The model either errors mid-call or ignores the non-text content and answers as if no image was sent.

- **Forgetting `load_dotenv()`** — `gpt-5-nano` and `gpt-4o-audio-preview` both need `OPENAI_API_KEY`. Without `load_dotenv()`, the agent raises an auth error before any message processing happens.

- **`multiple=False` on `FileUpload`** — if you forget this, `uploader.value` may contain multiple files and `uploader.value[0]` is still valid, but you might accidentally send the wrong file.

---

## Exercises

1. **Recall** — What is the difference between `HumanMessage(content="hello")` and `HumanMessage(content=[{"type": "text", "text": "hello"}])`? When must you use the list form?

2. **Apply** — Read a local image file from disk (skip the `FileUpload` widget), base64 encode it, and send it to `gpt-5-nano` with a question about its contents. Verify the model answers about the actual image.

3. **Extend** — Build a message with two images and a question that refers to both: "What is the difference between these two images?" What happens to token usage compared to a text-only message?

---

## Summary

- `HumanMessage.content` accepts a list of typed blocks: `text`, `image`, `audio`
- Image and audio blocks require `type`, `base64`, and `mime_type`
- `FileUpload` in Jupyter returns `memoryview` — convert to `bytes` before base64 encoding
- Model selection is critical: `gpt-5-nano` for images, `gpt-4o-audio-preview` for audio, `deepseek-chat` for text only
- The next chapter closes out Module 1 with the **Personal Chef** project — combining agents, tools, memory, and multimodal input into a single application
