# Cloud-Architecture-Automated-Video-Highlight-Transcription-Generator

# YouTube Video Highlights Generator

**From long videos to key moments, delivered straight to your inbox.**

## Overview

Finding the important parts of a long YouTube video can take time. This project simplifies that process by extracting available captions, converting them into a readable transcript, and processing the transcript to generate timestamped highlights.

Built using Python and AWS services, the project automates the processing and delivery of video highlights through an event-driven workflow. Once the required files are uploaded to Amazon S3, an AWS Lambda function processes the input and sends an email containing the video's metadata and key highlights.

The current implementation uses `yt-dlp` to retrieve captions and Python scripts to convert them into a readable transcript. AWS Lambda handles the highlight-processing workflow, Amazon SNS delivers the results by email, and Amazon CloudWatch provides logs for monitoring and debugging.

## How It Works

1. **Extract captions:** `yt-dlp` retrieves available captions from a YouTube video in JSON format.
2. **Convert the transcript:** Python scripts process the caption file and convert it into a human-readable transcript.
3. **Prepare the metadata:** Video details, including the title, channel name, duration, and YouTube URL, are stored separately.
4. **Upload to Amazon S3:** The metadata and transcript are uploaded to their respective folders in the S3 bucket.
5. **Trigger AWS Lambda:** An S3 event invokes the configured Lambda function, `YouTube highlights`, to process the uploaded files and generate the highlights.
6. **Send the results:** Amazon SNS delivers an email containing the video details, YouTube link, and generated highlights.
7. **Monitor execution:** Amazon CloudWatch Logs are checked to verify execution and troubleshoot any errors.

## Architecture

```text
YouTube Video URL
       |
       v
     yt-dlp
       |
       v
  JSON Captions
       |
       v
Python Caption-to-Transcript Conversion
       |
       +----------------------+
       |                      |
       v                      v
 Human-Readable          Video Metadata
   Transcript          (Title, Channel,
       |                Duration, URL)
       |                      |
       v                      v
 Amazon S3:              Amazon S3:
 transcripts/             metadata/
       |                      |
       +----------+-----------+
                  |
                  v
          AWS Lambda Function
          "YouTube highlights"
                  |
                  v
       Highlight Generation
                  |
                  v
             Amazon SNS
                  |
                  v
          Email Notification
                  |
                  v
        Amazon CloudWatch Logs
          (Execution Monitoring)
```

*Note: CloudWatch is used to monitor execution and inspect logs. It is not a processing stage in the data pipeline.*

## AWS Services and Tools

| Service / Tool | Purpose |
|---|---|
| YouTube | Source of the video and its available captions |
| `yt-dlp` | Retrieves available YouTube captions |
| Python | Converts caption JSON into a readable transcript and prepares video metadata |
| Amazon S3 | Stores metadata and transcripts and initiates event-driven processing |
| AWS Lambda | Processes the uploaded files and generates video highlights |
| Amazon SNS | Sends the generated results to the subscribed email address |
| Amazon CloudWatch | Records Lambda execution logs for monitoring and debugging |
| AWS IAM | Controls permissions between the AWS resources |

## Project Structure

The local working directory contains the generated metadata, caption files, and converted transcript. The following illustrates the logical organization of the project; individual filenames may vary.

```text
project/
├── demo/
│   ├── demo-in/       # Video metadata
│   └── demo-out/      # Original and converted transcript files
├── captions_to_transcript.py
└── README.md
```

The AWS S3 bucket, `durga-highlights-12345`, contains the corresponding input folders:

```text
durga-highlights-12345/
├── metadata/
│   └── demo1.json
└── transcripts/
    └── demo1.json
```

The metadata file contains the video's title, channel name, duration, and URL. The transcript file contains the converted caption data, including timestamps where available.

## Technologies Used

- **Language:** Python
- **Caption Extraction:** `yt-dlp`
- **Cloud Storage:** Amazon S3
- **Serverless Processing:** AWS Lambda
- **Email Notifications:** Amazon SNS
- **Monitoring:** Amazon CloudWatch
- **Permissions:** AWS IAM

## Running the Demo

The following steps describe the current working workflow.

### 1. Select a YouTube video

Provide the URL of a video with available captions.

### 2. Download the captions

Use `yt-dlp` to retrieve the available captions in JSON format.

The caption file serves as the input for the transcript-conversion script.

### 3. Convert the captions

Run the Python caption-to-transcript conversion script to produce a readable transcript.

Save the resulting files in the appropriate local demo folders:

- `demo-in`: Video metadata, including title, channel, duration, and URL.
- `demo-out`: Original caption data and the converted transcript.

### 4. Upload the files to Amazon S3

Open the S3 bucket `durga-highlights-12345` and upload the files to their respective locations:

- Upload the metadata file to `metadata/`.
- Upload the converted transcript to `transcripts/`.

Ensure that the uploaded filenames and JSON structures match the expectations of the Lambda function.

### 5. Execute the highlight workflow

The configured S3 event notification invokes the `YouTube highlights` Lambda function when the relevant transcript object is uploaded.

The function processes the input and prepares the video details and highlights for email delivery.

### 6. Verify the email notification

Check the subscribed email inbox for the SNS notification. The email should contain the video title, YouTube link, channel name, and generated highlights.

### 7. Check CloudWatch Logs

Open the Lambda function's monitoring section and inspect its CloudWatch Logs to verify execution, review processing messages, and identify errors if the workflow fails.

## Current Implementation and Future Scope

The project currently uses locally retrieved YouTube captions rather than an AWS-managed audio transcription service. Highlight generation is handled by the existing Lambda implementation.

Potential enhancements include:

- **Automated audio transcription:** Integrate Amazon Transcribe to generate transcripts from audio stored in S3.
- **AI-powered summarization:** Integrate Amazon Bedrock to identify contextually important moments and produce more descriptive summaries.
- **Improved highlight ranking:** Refine the selection of key moments based on relevance, topic changes, and the importance of each segment.
- **Expanded input support:** Extend the workflow to process additional video sources and transcript formats.

Amazon Transcribe and Amazon Bedrock are not part of the current working demo. These integrations remain future enhancements and would require the necessary AWS service access, permissions, and configuration.

## Conclusion

This project demonstrates how Python and AWS services can work together to build a practical, event-driven video-processing pipeline. By combining caption extraction, transcript conversion, S3-triggered Lambda execution, and SNS email notifications, it provides a foundation for making long-form video content easier to navigate and review.

The architecture can be extended with automated transcription and AI-powered summarization as the project evolves.
