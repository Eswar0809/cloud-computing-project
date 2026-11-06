import os
import json
import time
import urllib.request
from typing import List, Dict, Any
from contextlib import contextmanager
import boto3
from botocore.client import Config


@contextmanager
def worker_lock(lock_dir="data/ollama_lock", timeout=180):
    os.makedirs(os.path.dirname(lock_dir) or '.', exist_ok=True)
    start = time.time()
    while True:
        try:
            os.mkdir(lock_dir)
            break
        except FileExistsError:
            time.sleep(0.1)
            # Break stale lock after timeout
            if time.time() - start > timeout:
                try:
                    os.rmdir(lock_dir)
                except Exception:
                    pass
                start = time.time()
    try:
        yield
    finally:
        try:
            os.rmdir(lock_dir)
        except Exception:
            pass
        time.sleep(0.05)


def get_s3_client(endpoint_url: str):
    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'any'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'any'),
        config=Config(signature_version='s3v4')
    )


def load_commands(s3_client, bucket: str, key: str, local_fallback: str) -> List[Dict[str, Any]]:
    if s3_client:
        try:
            print(f"Loading commands from s3://{bucket}/{key}...")
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            lines = obj['Body'].read().decode('utf-8').splitlines()
            return [json.loads(line) for line in lines if line.strip()]
        except Exception as e:
            print(f"Could not load from S3 ({e}), falling back to local file {local_fallback}")

    if os.path.exists(local_fallback):
        print(f"Loading commands from local file {local_fallback}...")
        with open(local_fallback, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]

    raise FileNotFoundError(f"Could not find commands file in S3 ({bucket}/{key}) or local ({local_fallback})")


def query_teacher(ollama_host: str, prompt: str, retries: int = 3) -> str:
    url = f"{ollama_host.rstrip('/')}/api/generate"
    data = json.dumps({
        "model": "phi3.5",
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0,
            "seed": 42
        }
    }).encode('utf-8')

    with worker_lock():
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    res_json = json.loads(resp.read().decode('utf-8'))
                    return res_json.get('response', '').strip()
            except Exception as e:
                if attempt == retries - 1:
                    print(f"Failed after {retries} attempts: {e}")
                    return ""
                time.sleep(2 * (attempt + 1))


def main():
    shard_index = int(os.environ.get('SHARD_INDEX', '0'))
    shard_count = int(os.environ.get('SHARD_COUNT', '2'))
    s3_endpoint = os.environ.get('S3_ENDPOINT', 'http://127.0.0.1:8333')
    ollama_host = os.environ.get('OLLAMA_HOST', 'http://127.0.0.1:11434')
    prompt_file = os.environ.get('PROMPT_FILE', 'prompts/teacher_prompt.txt')
    bucket_name = os.environ.get('DATASETS_BUCKET', 'datasets')
    input_key = os.environ.get('INPUT_KEY', 'commands_pool.jsonl')
    local_input = os.environ.get('LOCAL_INPUT', 'data/commands_pool.jsonl')
    output_key = f"teacher/shard-{shard_index}.jsonl"
    local_output_dir = 'data/teacher'
    os.makedirs(local_output_dir, exist_ok=True)
    local_output = os.path.join(local_output_dir, f"shard-{shard_index}.jsonl")

    print(f"=== Starting Worker for Shard {shard_index} of {shard_count} ===")
    print(f"S3 Endpoint: {s3_endpoint} | Ollama Host: {ollama_host}")

    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    s3 = None
    try:
        s3 = get_s3_client(s3_endpoint)
        s3.list_buckets()
    except Exception as e:
        print(f"Warning: S3 client connection failed ({e}). Proceeding in local mode.")
        s3 = None

    all_commands = load_commands(s3, bucket_name, input_key, local_input)
    print(f"Total commands in pool: {len(all_commands)}")

    processed_ids = set()
    existing_records = []
    if os.path.exists(local_output):
        with open(local_output, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    processed_ids.add(rec['id'])
                    existing_records.append(rec)
        print(f"Resuming: found {len(processed_ids)} already processed records in {local_output}")

    shard_commands = [cmd for idx, cmd in enumerate(all_commands) if idx % shard_count == shard_index]
    print(f"Total commands assigned to shard {shard_index}: {len(shard_commands)}")

    t0 = time.time()
    count = len(existing_records)

    with open(local_output, 'a', encoding='utf-8') as out_f:
        for idx, cmd in enumerate(shard_commands, 1):
            cid = cmd['id']
            if cid in processed_ids:
                continue

            prompt = prompt_template.replace("{command}", cmd['text'])
            raw_reply = query_teacher(ollama_host, prompt)

            record = {
                "id": cid,
                "text": cmd['text'],
                "teacher_raw": raw_reply
            }
            out_f.write(json.dumps(record) + '\n')
            out_f.flush()
            existing_records.append(record)
            count += 1
            time.sleep(0.05)

            if count % 25 == 0 or count == len(shard_commands):
                elapsed = time.time() - t0
                avg_time = elapsed / max(count - len(processed_ids), 1)
                rem_time = (len(shard_commands) - count) * avg_time
                pct = (count / len(shard_commands)) * 100
                print(
                    f"[Shard {shard_index}] Completed {count}/{len(shard_commands)} "
                    f"records ({pct:.1f}%) | Est. remaining: {rem_time/60:.1f} min"
                )

    print(f"Shard {shard_index} processing finished! Total records: {len(existing_records)}")

    if s3:
        try:
            print(f"Uploading shard output to s3://{bucket_name}/{output_key}...")
            s3.upload_file(local_output, bucket_name, output_key)
            print(f"Upload of shard {shard_index} to S3 complete!")
        except Exception as e:
            print(f"Failed to upload to S3: {e}")


if __name__ == '__main__':
    main()
