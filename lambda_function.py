import json, os, re, boto3
from botocore.config import Config

s3 = boto3.client("s3")
sns = boto3.client("sns")
TOPIC = os.environ["TOPIC_ARN"]
MODEL_ID = os.environ.get("MODEL_ID", "").strip()
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")

def fmt(sec):
    sec = int(float(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"

def build_chunks(transcript, window=30):
    """Split Transcribe's word list into (start_seconds, text) chunks of ~30 s."""
    chunks, words, start = [], [], None
    for item in transcript["results"]["items"]:
        word = item["alternatives"][0]["content"]
        if item["type"] != "pronunciation":
            if words:
                words[-1] += word
            continue
        t = float(item["start_time"])
        if start is None:
            start = t
        if t - start >= window:
            chunks.append((start, " ".join(words)))
            words, start = [], t
        words.append(word)
    if words:
        chunks.append((start, " ".join(words)))
    return chunks

def bedrock_summary(title, chunks):
    text = "\n".join(f"[{fmt(s)}] {t}" for s, t in chunks)[:60000]
    client = boto3.client(
        "bedrock-runtime", region_name=BEDROCK_REGION,
        config=Config(retries={"max_attempts": 1}, connect_timeout=5, read_timeout=40))
    prompt = f"""Below is a timestamped transcript of the video "{title}".
Return:
1. A 3-sentence summary.
2. A list of the 5 most important highlights, each formatted as: [mm:ss] - one-sentence description.
Use only timestamps that appear in the transcript. Write in English.

TRANSCRIPT:
{text}"""
    resp = client.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 1000, "temperature": 0.3})
    return resp["output"]["message"]["content"][0]["text"]

def extractive_summary(chunks):
    """No-AI fallback: opening sentences + the 5 longest timestamped chunks."""
    if not chunks:
        return "No speech was detected in this video."
    sentences = re.split(r"(?<=[.!?]) +", chunks[0][1])
    summary = " ".join(sentences[:3])
    top = sorted(chunks, key=lambda c: len(c[1].split()), reverse=True)[:5]
    top.sort(key=lambda c: c[0])
    lines = [f"[{fmt(s)}] - {t[:220]}{'...' if len(t) > 220 else ''}" for s, t in top]
    return ("SUMMARY (opening of the video):\n" + summary +
            "\n\nKEY HIGHLIGHTS (most content-dense moments):\n" + "\n".join(lines))

def lambda_handler(event, context):
    rec = event["Records"][0]["s3"]
    bucket, key = rec["bucket"]["name"], rec["object"]["key"]
    job_id = key.split("/")[-1].rsplit(".", 1)[0]

    transcript = json.load(s3.get_object(Bucket=bucket, Key=key)["Body"])
    try:
        meta = json.load(s3.get_object(Bucket=bucket, Key=f"meta/{job_id}.json")["Body"])
    except Exception as e:
        print("No meta file:", e)
        meta = {"title": job_id, "channel": "Unknown", "url": ""}

    chunks = build_chunks(transcript)

    method = "Extractive summary (no AI model)"
    summary = None
    if MODEL_ID:
        try:
            summary = bedrock_summary(meta["title"], chunks)
            method = f"Amazon Bedrock ({MODEL_ID})"
        except Exception as e:
            print("Bedrock failed, using fallback:", e)
    if summary is None:
        summary = extractive_summary(chunks)

    body = (f"Video: {meta['title']}\nChannel: {meta['channel']}\n{meta['url']}\n"
            f"Method: {method}\n\n{summary}")
    sns.publish(TopicArn=TOPIC, Subject=f"Highlights: {meta['title']}"[:100], Message=body)
    return {"status": "sent", "method": method}