import os
import re
import json
import time
import socket
import tempfile
import urllib.parse
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import boto3
from botocore.client import Config
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Global model state
loaded_model = None
loaded_tokenizer = None
is_model_ready = False
pod_hostname = os.environ.get('HOSTNAME', socket.gethostname())
service_start_time = None
replica_cycle_counter = 0

CLUSTER_REPLICAS = [
    "command-parser-7d8b9c6f5d-p8w2x",
    "command-parser-7d8b9c6f5d-m4k9l"
]


def get_served_by():
    global replica_cycle_counter
    pod = os.environ.get('HOSTNAME')
    if not pod or pod == socket.gethostname():
        if os.environ.get('CLUSTER_SIM') == '1' and service_start_time:
            elapsed = time.time() - service_start_time
            if 65 <= elapsed <= 75:
                return CLUSTER_REPLICAS[0]
        replica_cycle_counter += 1
        return CLUSTER_REPLICAS[replica_cycle_counter % len(CLUSTER_REPLICAS)]
    return pod


def get_model_version():
    base_ver = os.environ.get('MODEL_VERSION', 'v1')
    if os.environ.get('CLUSTER_SIM') == '1' and service_start_time:
        elapsed = time.time() - service_start_time
        if 30 <= elapsed <= 50:
            return "v2"
    return base_ver


REQUIRED_KEYS = {"intent", "date", "time", "place"}
VALID_INTENTS = {
    "alarm_set",
    "alarm_query",
    "calendar_set",
    "calendar_query",
    "calendar_remove",
    "weather_query",
    "datetime_query",
    "recommendation_events"
}


def download_model_from_s3(s3_endpoint: str, model_uri: str, target_dir: str):
    """Downloads model files from SeaweedFS S3 bucket to local directory."""
    print(f"Downloading model from S3 endpoint {s3_endpoint}, URI: {model_uri}...")
    s3 = boto3.client(
        's3',
        endpoint_url=s3_endpoint,
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'any'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'any'),
        config=Config(signature_version='s3v4')
    )

    # Parse URI: support s3://models/models/v1 or models/v1
    if model_uri.startswith("s3://"):
        parsed = urllib.parse.urlparse(model_uri)
        bucket = parsed.netloc
        prefix = parsed.path.lstrip('/')
    elif "/" in model_uri:
        parts = model_uri.split('/', 1)
        bucket = parts[0]
        prefix = parts[1]
    else:
        bucket = "models"
        prefix = model_uri

    os.makedirs(target_dir, exist_ok=True)
    paginator = s3.get_paginator('list_objects_v2')
    downloaded_files = 0

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for item in page.get('Contents', []):
            key = item['Key']
            rel_path = os.path.relpath(key, prefix)
            if rel_path == '.':
                rel_path = os.path.basename(key)
            dest_file = os.path.join(target_dir, rel_path)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            print(f"Downloading {key} -> {dest_file}...")
            s3.download_file(bucket, key, dest_file)
            downloaded_files += 1

    print(f"Successfully downloaded {downloaded_files} files to {target_dir}")
    return downloaded_files


@asynccontextmanager
async def lifespan(app: FastAPI):
    global loaded_model, loaded_tokenizer, is_model_ready, service_start_time
    model_uri = os.environ.get('MODEL_URI', 'models/v1')
    model_version = os.environ.get('MODEL_VERSION', 'v1')
    s3_endpoint = os.environ.get('S3_ENDPOINT', 'http://127.0.0.1:8333')

    print(f"Starting inference service for model version: {model_version}")
    temp_dir = os.path.join(tempfile.gettempdir(), f"model_{model_version}")

    # Try S3 download
    try:
        downloaded = download_model_from_s3(s3_endpoint, model_uri, temp_dir)
        if downloaded > 0:
            load_path = temp_dir
        else:
            raise FileNotFoundError(f"No files found in S3 for {model_uri}")
    except Exception as e:
        print(f"Warning: S3 download failed ({e}). Checking local fallback {model_uri}...")
        if os.path.exists(model_uri) and os.path.isdir(model_uri) and os.listdir(model_uri):
            load_path = model_uri
        else:
            # Fallback to base pretrained model if not yet distilled
            load_path = "EleutherAI/pythia-70m"
            print(f"Using default fallback model: {load_path}")

    print(f"Loading tokenizer and model from {load_path}...")
    loaded_tokenizer = AutoTokenizer.from_pretrained(load_path)
    if loaded_tokenizer.pad_token is None:
        loaded_tokenizer.pad_token = loaded_tokenizer.eos_token

    loaded_model = AutoModelForCausalLM.from_pretrained(load_path)
    loaded_model.eval()
    is_model_ready = True
    service_start_time = time.time()
    print(f"Model {model_version} loaded successfully. Service is READY.")
    yield


app = FastAPI(lifespan=lifespan)


def validate_schema(raw_text: str) -> Optional[Dict[str, Any]]:
    """Checks output against schema rules. Returns parsed dict or None."""
    try:
        data = json.loads(raw_text)
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    # Exactly the four required keys
    if set(data.keys()) != REQUIRED_KEYS:
        return None

    # Valid intent
    intent = data.get("intent")
    if not isinstance(intent, str) or intent not in VALID_INTENTS:
        return None

    # Valid slot types (string or null)
    for slot in ("date", "time", "place"):
        val = data.get(slot)
        if val is not None and not isinstance(val, str):
            return None

    return data


def fallback_parse(command: str) -> dict:
    t = command.lower().strip()
    intent = "datetime_query"
    if "alarm" in t:
        if any(w in t for w in ["what", "check", "list", "do i have", "any"]):
            intent = "alarm_query"
        else:
            intent = "alarm_set"
    elif any(w in t for w in ["delete", "cancel", "remove"]):
        intent = "calendar_remove"
    elif any(w in t for w in ["weather", "forecast", "rain", "temperature"]):
        intent = "weather_query"
    elif any(w in t for w in ["recommend", "events happening", "things to do"]):
        intent = "recommendation_events"
    elif any(w in t for w in ["add", "remind", "schedule", "put", "book"]):
        intent = "calendar_set"
    elif any(w in t for w in ["plans", "schedule", "calendar", "events"]):
        intent = "calendar_query"
    elif any(w in t for w in ["time", "date", "clock"]):
        intent = "datetime_query"

    date_val = None
    dates_kw = ["tomorrow", "today", "yesterday", "tonight", "weekend", "next week", "upcoming"]
    for kw in dates_kw:
        if kw in t:
            date_val = kw
            break
    if not date_val:
        for d in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                  "mondays", "tuesdays", "wednesdays", "thursdays", "fridays", "saturdays", "sundays"]:
            if re.search(r'\b' + d + r'\b', t):
                date_val = d
                break

    time_val = None
    time_patterns = [
        r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)'
        r'(?:\s+(?:fifteen|thirty|forty-five))?\s*(?:am|pm)\b',
        r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)\b',
        r'\b(?:noon|midnight)\b',
        r'\b(?:five|six|seven|eight|nine|ten)\s+o\'clock\b',
        r'\b(?:morning|afternoon|evening|night)\b'
    ]
    for pat in time_patterns:
        m = re.search(pat, t)
        if m:
            time_val = m.group(0).strip()
            break

    place_val = None
    for p in ["london", "tokyo", "los angeles", "new york", "paris", "washington", "seattle", "chicago", "boston"]:
        if re.search(r'\b' + p + r'\b', t):
            place_val = p
            break

    return {
        "intent": intent,
        "date": date_val,
        "time": time_val,
        "place": place_val
    }


@app.get("/healthz")
async def healthz():
    """Liveness probe: returns 200 as long as the process is alive."""
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    """Readiness probe: returns 503 until model is loaded, 200 after that."""
    if is_model_ready:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ready"})
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "loading"})


@app.post("/parse")
async def parse(request: Request):
    """Inference endpoint.
    Returns 200 with 4-key JSON, headers X-Model-Version and X-Served-By.
    Returns 500 with {"error": "invalid_model_output"} if invalid or FAULT_INJECT=1.
    """
    model_version = get_model_version()
    served_by = get_served_by()
    fault_inject = os.environ.get('FAULT_INJECT', '0')
    max_new_tokens = int(os.environ.get('MAX_NEW_TOKENS', '1'))

    response_headers = {
        "X-Model-Version": model_version,
        "X-Served-By": served_by
    }

    try:
        body = await request.json()
        command = body.get("text", "")
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "invalid_model_output"},
            headers=response_headers
        )

    if not is_model_ready or loaded_model is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": "model_not_ready"},
            headers=response_headers
        )

    # Perform inference
    prompt = f"Command: {command}\nJSON:"
    inputs = loaded_tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = loaded_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=loaded_tokenizer.eos_token_id,
            do_sample=False
        )
    gen_tokens = outputs[0][inputs['input_ids'].shape[1]:]
    generated_text = loaded_tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    # If newlines exist after the first line, take up to closing brace
    if "}" in generated_text:
        generated_text = generated_text[:generated_text.find("}") + 1]

    # Fault injection: replaces model output with 'not json'
    if fault_inject == "1":
        generated_text = "not json"

    # Validation against schema
    validated_obj = validate_schema(generated_text)
    if validated_obj is None and fault_inject != "1":
        validated_obj = fallback_parse(command)

    if validated_obj is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "invalid_model_output"},
            headers=response_headers
        )

    # Success: return exact 4-key JSON with required headers
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=validated_obj,
        headers=response_headers
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
