import googleapiclient.discovery
import time
import csv


def extract_channel_data(channel_id, max_results=50):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUR_API_KEY)

    video_data = []

    next_page_token = None
    for _ in range(max_results // 10):
        search_response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        items = search_response.get("items", [])

        if not items:
            break

        for item in items:
            video_id = item["id"]["videoId"]
            details_response = youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            ).execute()
            video_details = details_response.get("items", [{}])[0]

            title = video_details.get("snippet", {}).get("title", "")
            view_count = video_details.get("statistics", {}).get("viewCount", 0)
            published_at = video_details.get("snippet", {}).get("publishedAt", "")
            thumbnails = video_details.get("snippet", {}).get("thumbnails", {})

            comments = extract_video_comments(youtube, video_id)

            video_data.append({
                'title': title,
                'viewCount': view_count,
                'publishedAt': published_at,
                'thumbnails': thumbnails,
                'comments': comments
            })

        next_page_token = search_response.get("nextPageToken", None)
        time.sleep(1)

    return video_data


def extract_video_comments(youtube, video_id):
    comments = []

    comment_response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText"
    ).execute()

    for item in comment_response.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)

    return comments


def save_to_csv(video_data, filename='video_data.csv'):
    keys = ['title', 'viewCount', 'publishedAt', 'thumbnails', 'comments']
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        for video in video_data:
            # Serialize the thumbnails and comments fields as JSON strings
            video['thumbnails'] = str(video['thumbnails'])
            video['comments'] = '; '.join(video['comments'])
            writer.writerow(video)


def print_video_data(video_data):
    for video in video_data:
        print(f"Title: {video['title']}")
        print(f"View Count: {video['viewCount']}")
        print(f"Published At: {video['publishedAt']}")
        print(f"Thumbnails: {video['thumbnails']}")
        print(f"Comments: {video['comments']}")
        print("=" * 40)


YOUR_API_KEY = "AIzaSyBuHZ3yOAlDFlVK8mUBhKf1M3vMxOKtlTw"
channel_id = 'UCInZht3KI1alD8OEATNJ6vw'  # Muniba Mazari

data = extract_channel_data(channel_id)

print_video_data(data)
save_to_csv(data)
