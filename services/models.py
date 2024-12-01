import openai
import google.generativeai as genai
from utils.config import OPENAI_API_KEY, GEMINI_API_KEY
from typing import Optional, Dict, Any, List
from pydub import AudioSegment
openai.api_key = OPENAI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash-002')

def chatgpt_query(prompt, query):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"""You are an AI research assistant. Your task is to provide a clear, concise, and informative answer to the user's query based on the given search results. Follow these guidelines:

1. Directly address the user's question with a focused, relevant answer.
2. Synthesize information from multiple sources, presenting a coherent and balanced view.
3. Use objective, factual language. Avoid personal opinions or speculative statements.
4. Cite sources using [1], [2], etc., corresponding to the search result numbers.
5. If the search results don't contain enough information to fully answer the query, clearly state this limitation.
6. Present information in a logical, easy-to-follow structure. Use bullet points or numbered lists for clarity when appropriate.
7. Explain technical terms or concepts if they're crucial to understanding the answer.
8. If there are conflicting viewpoints in the sources, present them objectively without taking sides.
9. Provide context or background information only if it's directly relevant to answering the query.
10. Focus on accuracy and relevance over comprehensiveness. It's better to provide a shorter, correct answer than a longer, less focused one.

Remember to respond entirely in Korean, regardless of the language of the search results or user query.

User query: {query}
"""},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        print(f"Error in ChatGPT query: {e}")
        yield "ChatGPT 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."

def gemini_query(prompt, query):
    try:
        system_prompt = f"""You are an advanced AI assistant tasked with providing comprehensive and insightful answers based on search results. Analyze the given information, synthesize it, and present a well-structured response in Korean. Follow these guidelines:

1. Concisely summarize the key points from the search results.
2. Explain the significance of the information and provide additional context or background information.
3. Present conflicting viewpoints objectively, if any, and explain the pros and cons of each perspective.
4. Offer insights or potential implications related to the topic.
5. Suggest areas for further exploration or related topics, if applicable.
6. Ensure your response is informative, engaging, and directly relevant to the user's query.
7. Always cite your sources using [1], [2], etc., corresponding to the search result numbers.
8. Go beyond simple summarization to provide a deep understanding and analysis of the topic.
9. Support your answer with real-world examples, statistics, or case studies when possible.
10. Explain complex concepts in an easy-to-understand manner, using analogies or examples if necessary.
11. Structure your response clearly, using subheadings to separate information if needed.
12. At the end of your response, suggest 2-3 related questions the user might want to explore further.

Remember, your entire response must be in Korean, regardless of the language of the search results or the user's query.

User query: {query}

Based on the above guidelines, provide a comprehensive and insightful answer in Korean using the given search results."""

        full_prompt = f"{system_prompt}\n\nSearch results:\n{prompt}"
        response = gemini_model.generate_content(full_prompt,stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        print(f"Error in Gemini query: {e}")
        yield "Gemini 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."

def generate_script(query: str, search_results: str, 
                       duration_minutes: int = 5) -> str:
    system_prompt = """
    You are an expert podcast script writer. Create engaging scripts for two AI hosts:
    - Host A (지식): A knowledgeable and analytical character who focuses on facts and explanations
    - Host B (호기심): A curious and enthusiastic character who asks insightful questions and shares interesting perspectives
        
    Format the script with clear speaker labels and natural conversational flow. 
    Include appropriate reactions, interjections, and chemistry between the hosts.
    """

    user_prompt = f"""
    주제: '{query}'
        
    다음 검색 결과를 바탕으로 {duration_minutes}분 길이의 2인 진행 팟캐스트 대본을 작성해주세요.

    구성:
    1. 도입부 (30초):
        - 인사 및 주제 소개
        - 두 진행자의 자연스러운 호흡
        
    2. 본문 ({duration_minutes - 1}분):
        - 지식: 검색 결과의 핵심 내용 설명
        - 호기심: 적절한 질문과 청취자 관점 제시
        - 서로의 의견에 대한 자연스러운 리액션
        
    3. 마무리 (30초):
        - 핵심 내용 정리
        - 청취자 대상 마무리 멘트

    형식:
    지식: (대사)
    호기심: (대사)

    필수 요구사항:
    1. 모든 대화는 한글로 작성
    2. 자연스러운 대화체 사용
    3. 진행자별 특성이 잘 드러나도록 작성
    4. 서로 호흡이 맞는 대화 전개
    5. 청취자가 이해하기 쉽게 설명
    6. 적절한 예시와 비유 활용

    검색 결과:
    {search_results}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        console.print(f"[red]Error generating podcast script: {str(e)}[/red]")
        return None

def generate_audio(script: str) -> Optional[bytes]:
    try:
        if not script.strip():
            print("오류: 제공된 스크립트가 비어 있습니다.")
            return None

        segments = []
        current_speaker = None
        current_text = []

        for line in script.split('\n'):
            stripped_line = line.strip()
            print(f"처리 중인 라인: {stripped_line}")

            if stripped_line.startswith('지식:'):
                if current_speaker and current_text:
                    segments.append((current_speaker, ' '.join(current_text)))
                current_speaker = "onyx"  # 권위적인 음성
                current_text = [stripped_line[3:].strip()]  # "지식:" 제거
            elif stripped_line.startswith('호기심:'):
                if current_speaker and current_text:
                    segments.append((current_speaker, ' '.join(current_text)))
                current_speaker = "nova"  # 활기찬 음성
                current_text = [stripped_line[4:].strip()]  # "호기심:" 제거
            elif stripped_line:  # 공백이 아닌 줄은 현재 스피커의 텍스트에 추가
                if current_speaker:
                    current_text.append(stripped_line)
                else:
                    print(f"[warning]현재 스피커가 없어서 해당 라인 '{stripped_line}'을 건너뜁니다.")

            else:
                # 지식, 호기심이 없거나 공백인 경우 건너뜀
                print(f"건너뜬 라인: {stripped_line}")

        # 마지막으로 남은 텍스트 세그먼트 처리
        if current_speaker and current_text:
            segments.append((current_speaker, ' '.join(current_text)))

        if not segments:
            print("오류: 세그먼트가 생성되지 않았습니다.")
            return None

        print(f"생성된 세그먼트 수: {len(segments)}")
        for i, (speaker, text) in enumerate(segments, 1):
            print(f"Segment {i} - Speaker: {speaker}, Text: {text[:50]}...")

        all_audio = []
        for i, (voice, text) in enumerate(segments, 1):
            try:
                text_parts = []
                if len(text) > 1000:
                    print(f"[yellow]Segment {i} 텍스트가 너무 깁니다. 나눕니다.[/yellow]")
                    words = text.split()
                    part = []
                    for word in words:
                        if len(' '.join(part) + ' ' + word) <= 1000:
                            part.append(word)
                        else:
                            text_parts.append(' '.join(part))
                            part = [word]
                    if part:
                        text_parts.append(' '.join(part))
                else:
                    text_parts = [text]

                # 나뉜 텍스트 각각에 대해 음성 생성
                for part in text_parts:
                    response = openai.audio.speech.create(
                        model="tts-1",
                        voice=voice,
                        input=part,
                        speed=1.05
                    )
                    all_audio.append(response.content)
            except Exception as e:
                print(f"[red]Segment {i} 음성 생성 실패: {str(e)}[/red]")

        # 생성된 모든 오디오 조합
        if all_audio:
            print(f"[green]총 생성된 오디오 세그먼트 수: {len(all_audio)}[/green]")
            return b''.join(all_audio)
        else:
            print("[red]오디오 세그먼트 생성 실패: 생성된 데이터 없음[/red]")
            return None

    except Exception as e:
        print(f"[red]generate_audio 오류: {str(e)}[/red]")
        return None


    except Exception as e:
        print(f"[red]generate_audio 오류: {str(e)}[/red]")
        return None
def add_background_music(audio_file: str, music_file: str, output_file: str, volume_reduction: int = -20):
    try:
        voice = AudioSegment.from_file(audio_file)

        music = AudioSegment.from_file(music_file)

        music = music - abs(volume_reduction)

        if len(music) < len(voice):
            music = music * (len(voice) // len(music) + 1)
        music = music[:len(voice)]

        combined = voice.overlay(music)

        combined.export(output_file, format="mp3")
        return output_file
    except Exception as e:
        print(f"[red]배경음악 추가 중 오류 발생: {str(e)}[/red]")
        return None