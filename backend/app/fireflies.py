import requests

API_KEY = "f27ab6dd-ad78-4071-a179-5be139ad8af3"
GRAPHQL_URL = "https://api.fireflies.ai/graphql"

def upload_video(url):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    input_data = {
        "webhook": "https://webhook.site/7f7cb514-1424-4214-80b6-96117674eba6",
        "url": f'{url}',
        "title": "Meeting test",
        "attendees": [
            {
                "displayName": "Gaspard",
                "email": "inviteemail@gmail.com",
                "phoneNumber": "514 567 890",
            },
        ],
    }

    data = {
        "query": """
        mutation($input: AudioUploadInput) {
            uploadAudio(input: $input) {
                success
                title
                message
            }
        }
        """,
        "variables": {"input": input_data},
    }

    try:
        response = requests.post(GRAPHQL_URL, json=data, headers=headers)
        response_data = response.json()
        print("Upload Response:", response_data)

        if response_data.get("data") and response_data["data"].get("uploadAudio")["success"]:
            print("Video uploaded successfully!")
        else:
            print("Upload failed:", response_data)

    except requests.exceptions.RequestException as e:
        print("Upload Error:", e)

def get_transcript(transcript_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "query": """
        query Transcript($transcriptId: String!) {
            transcript(id: $transcriptId) {
                sentences {
                    index
                    speaker_name
                    speaker_id
                    text
                    raw_text
                    start_time
                    end_time
                    ai_filters {
                        task
                        pricing
                        metric
                        question
                        date_and_time
                        text_cleanup
                        sentiment
                    }
                }
                summary {
                    keywords
                    action_items
                    outline
                    shorthand_bullet
                    overview
                    bullet_gist
                    gist
                    short_summary
                }
            }
        }
        """,
        "variables": {"transcriptId": transcript_id},
    }

    try:
        response = requests.post(GRAPHQL_URL, json=data, headers=headers)
        response_data = response.json()
        titles=['keywords','action_items','outline','shorthand_bullet', 'overview','bullet_gist','gist','short_summary']
        meeting_transcript=[]
        
        # for data in titles:
        #     if data in response_data['data']['transcript']['summary']:  # Check if key exists in the response
        #         print(f'{data.capitalize()}: {response_data["data"]["transcript"]["summary"][data]}\n\n')

        meeting_summary=response_data['data']['transcript']['summary']['short_summary']
        sentences=response_data['data']['transcript']['sentences']

        # Print out sentences data
        # sentences_fields = ['index', 'speaker_id', 'text', 'raw_text', 'start_time', 'end_time']
        for sentence in sentences:
            # for field in sentences_fields:
            #     if field in sentence:  # Check if key exists in the sentence
            #         print(f'{field.capitalize()}: {sentence[field]}')
            speaker_sentence={
                'speaker':f'Speaker {sentence['speaker_id']}',
                'text':f'{sentence['text']}'
            }

            meeting_transcript.append(speaker_sentence)
            print()

        
        return meeting_summary,meeting_transcript


    except requests.exceptions.RequestException as e:
        print("Transcript Fetch Error:", e)


def get_admin_id():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "query": """
        query {
            users {
                user_id
                is_admin
                name
                integrations
                num_transcripts
                recent_meeting
            }
        }
        """,
    }

    try:
        response = requests.post(GRAPHQL_URL, json=data, headers=headers)
        response_data = response.json()
        
        if 'data' in response_data:
            users = response_data['data']['users']
            print("User Information:")
            for user in users:
                print(f"User Id : {user['user_id']}")
                print(f"Is admin?: {user['is_admin']}")
                print(f"Name: {user['name']}")
                print(f"Integrations: {user['integrations']}")
                print(f"Number of transcripts: {user['num_transcripts']}")
                print(f"Recent Meeting: {user['recent_meeting']}")

                if user['is_admin']==True:
                    return user['user_id']
                
            return None


        else:
            print("Error: No data returned from the API.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")


def get_transcripts(user_id,transcriptTitle):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    # Use the user_id dynamically in the variables
    data = {
        "query": """
        query Transcripts($userId: String) {
            transcripts(user_id: $userId) {
                title
                id
            }
        }
        """,
        "variables": {
            "userId": user_id
        }
    }


    try:
        response = requests.post(GRAPHQL_URL, headers=headers, json=data)
        response_data = response.json()
        
        if 'data' in response_data:
            transcripts = response_data['data']['transcripts']
            print("Transcripts Information:")
            for transcript in transcripts:
                print(f"Title: {transcript['title']}")
                print(f"id: {transcript['id']}")

                print(f'{transcriptTitle} vs {transcript['title']}')
                if transcript['title']==transcriptTitle:
                    return transcript['id']
                
            return None

        else:
            print("Error: No data returned from the API.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    url="https://drive.google.com/uc?export=download&id=1HeczGIhSUUu-moKfx522KXaRdE_DtrCk"
    # upload_video(url)

    # print("\nGetting the user id....")
    # admin_id=get_admin_id()

    # # if not admin_id:
    # #     return "eroor"

    # print("\nGetting the transcripts....")
    # transcript_id=get_transcripts(admin_id,"Meeting test")

    # print(transcript_id)

    print("\nGeting  a special transcript....")
    summary,full_transcript=get_transcript('01JN6G05VA8SVKPVC6NWBWK0RD')

    print('\nSummary',)
    print(summary)

    print('\n\nTranscripts\n')
    for sentence in full_transcript:
        print(f'-{sentence['speaker']}: {sentence['text']}')
