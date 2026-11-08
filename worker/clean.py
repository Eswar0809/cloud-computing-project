import os
import sys
import json
import hashlib
import glob
from typing import Dict, Any, List
import boto3
from botocore.client import Config

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

REQUIRED_KEYS = {"intent", "date", "time", "place"}


def get_s3_client(endpoint_url: str):
    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'any'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'any'),
        config=Config(signature_version='s3v4')
    )


def load_shard_records(s3_client, bucket: str) -> List[Dict[str, Any]]:
    records = []
    # Try S3 first
    if s3_client:
        try:
            objs = s3_client.list_objects_v2(Bucket=bucket, Prefix="teacher/shard-")
            for item in objs.get('Contents', []):
                key = item['Key']
                if key.endswith('.jsonl'):
                    print(f"Reading shard from S3: {key}...")
                    body = s3_client.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
                    for line in body.splitlines():
                        if line.strip():
                            records.append(json.loads(line))
        except Exception as e:
            print(f"Note: S3 shard read encountered: {e}. Falling back to local files.")

    if not records:
        # Search local directories
        paths = glob.glob('data/teacher/shard-*.jsonl') + glob.glob('datasets/teacher/shard-*.jsonl')
        paths = sorted(list(set(paths)))
        for p in paths:
            print(f"Reading local shard: {p}...")
            with open(p, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
    return records


def clean_records(records: List[Dict[str, Any]]):
    # Sort strictly by ID
    records.sort(key=lambda x: x['id'])

    total_input = len(records)
    rej_a = 0  # not valid JSON
    rej_b = 0  # keys not exactly intent, date, time, place
    rej_c = 0  # intent not in 8
    rej_d = 0  # slot not null and not appearing in text
    rej_e = 0  # duplicate commands
    kept_records = []

    seen_command_texts = set()

    for r in records:
        raw = r.get('teacher_raw', '').strip()
        cmd_text = r.get('text', '')

        # (a) Check if valid JSON
        try:
            parsed = json.loads(raw)
        except Exception:
            rej_a += 1
            continue

        if not isinstance(parsed, dict):
            rej_a += 1
            continue

        # (b) Check keys are exactly intent, date, time, place
        if set(parsed.keys()) != REQUIRED_KEYS:
            rej_b += 1
            continue

        # (c) Check intent is one of the 8
        intent = parsed.get('intent')
        if not isinstance(intent, str) or intent not in VALID_INTENTS:
            rej_c += 1
            continue

        # (d) Check slot values: neither null nor text appearing in command
        cmd_text_norm = cmd_text.lower()
        bad_slot = False
        for slot in ('date', 'time', 'place'):
            val = parsed.get(slot)
            if val is not None:
                if not isinstance(val, str):
                    bad_slot = True
                    break
                val_norm = val.strip().lower()
                if not val_norm or val_norm not in cmd_text_norm:
                    bad_slot = True
                    break
        if bad_slot:
            rej_d += 1
            continue

        # (e) Duplicate command (keep the one with smallest id)
        norm_cmd = " ".join(cmd_text.strip().lower().split())
        if norm_cmd in seen_command_texts:
            rej_e += 1
            continue
        seen_command_texts.add(norm_cmd)

        # Passed all filters: keep record
        kept_records.append({
            "id": r['id'],
            "text": cmd_text,
            "intent": parsed['intent'],
            "date": parsed['date'],
            "time": parsed['time'],
            "place": parsed['place'],
            "teacher_raw": raw
        })

    counts = {
        "input_records": total_input,
        "rejected_a_invalid_json": rej_a,
        "rejected_b_bad_keys": rej_b,
        "rejected_c_bad_intent": rej_c,
        "rejected_d_bad_slot": rej_d,
        "rejected_e_duplicates": rej_e,
        "records_kept": len(kept_records),
        "checksum_formula_valid": total_input == (rej_a + rej_b + rej_c + rej_d + rej_e + len(kept_records))
    }

    return kept_records, counts


def main():
    s3_endpoint = os.environ.get('S3_ENDPOINT', 'http://127.0.0.1:8333')
    bucket_name = os.environ.get('DATASETS_BUCKET', 'datasets')

    s3 = None
    try:
        s3 = get_s3_client(s3_endpoint)
        s3.list_buckets()
    except Exception:
        s3 = None

    records = load_shard_records(s3, bucket_name)
    if not records:
        print("Error: No shard records found to clean!")
        sys.exit(1)

    print(f"Loaded {len(records)} raw teacher records.")
    kept, counts = clean_records(records)

    print("\n" + "=" * 50)
    print("           DATASET CLEANING SUMMARY TABLE         ")
    print("=" * 50)
    print(f"Total Input Records      : {counts['input_records']}")
    print(f"Rejected (a) Invalid JSON: {counts['rejected_a_invalid_json']}")
    print(f"Rejected (b) Bad Keys    : {counts['rejected_b_bad_keys']}")
    print(f"Rejected (c) Bad Intent  : {counts['rejected_c_bad_intent']}")
    print(f"Rejected (d) Bad Slot    : {counts['rejected_d_bad_slot']}")
    print(f"Rejected (e) Duplicates  : {counts['rejected_e_duplicates']}")
    print(f"Records Kept (Cleaned)   : {counts['records_kept']}")
    print(f"Sum matches Input?       : {counts['checksum_formula_valid']}")
    print("=" * 50 + "\n")

    # Write output to datasets/v1/train.jsonl
    out_dir = 'datasets/v1'
    os.makedirs(out_dir, exist_ok=True)
    out_jsonl = os.path.join(out_dir, 'train.jsonl')
    out_sha = os.path.join(out_dir, 'train.sha256')

    hasher = hashlib.sha256()
    with open(out_jsonl, 'w', encoding='utf-8') as f:
        for r in kept:
            line = json.dumps(r) + '\n'
            f.write(line)
            hasher.update(line.encode('utf-8'))

    sha256_hash = hasher.hexdigest()
    with open(out_sha, 'w', encoding='utf-8') as f:
        f.write(f"{sha256_hash}  train.jsonl\n")

    print(f"Saved cleaned dataset to {out_jsonl}")
    print(f"SHA-256 Checksum: {sha256_hash} written to {out_sha}")

    # Also save counts table to results/cleaning_counts.json for report
    os.makedirs('results', exist_ok=True)
    with open('results/cleaning_counts.json', 'w', encoding='utf-8') as f:
        json.dump(counts, f, indent=2)

    # Upload to S3
    if s3:
        try:
            print(f"Uploading cleaned dataset to s3://{bucket_name}/v1/train.jsonl...")
            s3.upload_file(out_jsonl, bucket_name, 'v1/train.jsonl')
            s3.upload_file(out_sha, bucket_name, 'v1/train.sha256')
            print("Upload to S3 complete!")
        except Exception as e:
            print(f"Warning: S3 upload failed: {e}")


if __name__ == '__main__':
    main()
