from flask import Flask, render_template, request, jsonify, stream_with_context, Response, url_for
from dotenv import load_dotenv
import asyncio
import json
from services.search import fetch_all_search_results, fetch_and_process_content, semantic_search
from services.models import chatgpt_query, gemini_query, generate_script, generate_audio, add_background_music
from utils.text_processing import process_query
from pathlib import Path
from datetime import datetime
load_dotenv()

app = Flask(__name__)
output_dir = Path("static/generated_podcasts")  # static 폴더 안에 저장
output_dir.mkdir(parents=True, exist_ok=True)  # 부모 디렉토리도 생성

def save_outputs(script: str, audio: bytes, query: str) -> tuple:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"podcast_{timestamp}"

    script_filename = output_dir / f"{base_filename}.txt"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(f"주제: {query}\n\n")
        f.write(script)
        
    audio_filename = output_dir / f"{base_filename}.mp3"
    with open(audio_filename, "wb") as f:
        f.write(audio)
        
    return script_filename, audio_filename

latest_created_audio = None

@app.route('/podcast_url', methods=['GET'])
def get_podcast_url():
    global latest_created_audio
    if latest_created_audio:
        podcast_url = url_for('static', filename=f"generated_podcasts/{Path(latest_created_audio).name}", _external=True)
        return jsonify({'podcast_url': podcast_url})
    return jsonify({'podcast_url': None})

@app.route('/', methods=['GET', 'POST'])
def index():
    global latest_created_audio
    if request.method == 'POST':
        query = request.form['query']
        model_choice = request.form.get('model', 'ChatGPT')
        optimized_query = process_query(query)

        # 검색된 결과와 텍스트 처리
        text_results, image_results, video_results = asyncio.run(fetch_all_search_results(optimized_query))
        processed_text_results = asyncio.run(fetch_and_process_content(text_results))

        top_indices = semantic_search(optimized_query, processed_text_results)
        prompt = f"Search results:\n"
        for i, index in enumerate(top_indices, 1):
            result = processed_text_results[index]
            result_text = (
                f"{i}. Title: {result.get('title', 'No Title')}\n"
                f"Source: {result.get('source', 'Unknown')}\n"
                f"Content: {result.get('content', 'No Content')[:2000]}\n\n"
            )
            prompt += result_text

        # 팟캐스트 스크립트 생성
        script = generate_script(optimized_query, prompt, duration_minutes=3)
        # 팟캐스트 오디오 생성
        audio = generate_audio(script)
        if audio:
            script_file, audio_file = save_outputs(script, audio, optimized_query)
            music_file = "background.mp3"
            output_with_music = str(output_dir / f"podcast_with_bgm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
            result_file = add_background_music(audio_file, music_file, output_with_music)
            result_file_path = Path(result_file)
            podcast_url = url_for('static', filename=f"generated_podcasts/{result_file_path.name}")
            latest_created_audio = result_file

        display_results = []
        for i, index in enumerate(top_indices[:8], 1):
            result = processed_text_results[index]
            display_results.append({
                'title': result.get('title', 'No Title'),
                'snippet': result.get('snippet', 'No Snippet')[:200] + '...' if len(result.get('snippet', '')) > 200 else result.get('snippet', 'No Snippet'),
                'link': result.get('link', 'No Link'),
            })

        image_results_processed = [
            {
                "link": image.get('link'),
                "thumbnail": image.get('image'),
                "title": image.get('title')
            } for image in image_results
        ]

        video_results_processed = [
            {
                "link": video.get('link'),
                "thumbnail": video.get('thumbnail'),
                "title": video.get('title')
            } for video in video_results
        ]

        def generate():
            ai_response = ""
            if model_choice == 'ChatGPT':
                for chunk in chatgpt_query(prompt, optimized_query):
                    ai_response += chunk
                    yield chunk
            elif model_choice == 'Gemini':
                for chunk in gemini_query(prompt, optimized_query):
                    ai_response += chunk
                    yield chunk

            # AI 응답을 채팅에 추가
            final_response = {
                "image_results": image_results_processed,
                "video_results": video_results_processed,
                "search_results": display_results,
                "podcast_url": podcast_url,
                "ai_response": ai_response  # AI가 생성한 응답 추가
            }

            yield json.dumps(final_response)

        return Response(stream_with_context(generate()), content_type='application/json')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
