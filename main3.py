import os

try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    print("moviepy 라이브러리가 필요합니다.")
    print("터미널에서 'pip install moviepy==1.0.3'을 실행해주세요.")
    exit()

# ==========================================
# [1] 텍스트 파일 읽기 함수 (기존과 동일)
# ==========================================
def load_vocab_from_txt(filepath):
    vocab_list = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            current_item = {}
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line[0].isdigit() and '.' in line and ':' in line:
                    word_part, meaning_part = line.split('.', 1)[1].split(':', 1)
                    current_item = {
                        "word": word_part.strip(),
                        "meaning": meaning_part.strip()
                    }
                elif line.startswith('-') and current_item:
                    content = line[1:].strip()
                    if "sentence" not in current_item:
                        current_item["sentence"] = content
                    else:
                        current_item["translation"] = content
                        vocab_list.append(current_item)
                        current_item = {}
    except FileNotFoundError:
        print(f"오류: '{filepath}' 파일을 찾을 수 없습니다.")
        return []
    
    return vocab_list

# ==========================================
# [2] 동영상 생성 메인 로직
# ==========================================
def generate_video():
    vocab_data = load_vocab_from_txt('vocabulary.md')
    
    if not vocab_data:
        print("단어 데이터가 없거나 파일을 찾을 수 없어 프로그램을 종료합니다.")
        return

    IMAGE_DIR = "card_news_output"
    AUDIO_DIR = "audio_output"
    
    if not os.path.exists(IMAGE_DIR) or not os.path.exists(AUDIO_DIR):
        print(f"오류: '{IMAGE_DIR}' 또는 '{AUDIO_DIR}' 폴더를 찾을 수 없습니다.")
        print("먼저 카드뉴스와 음성 파일을 생성해주세요.")
        return

    print("동영상 렌더링을 시작합니다. (시간이 조금 걸릴 수 있습니다.)")
    video_clips = []

    for index, item in enumerate(vocab_data, start=1):
        # 특수문자 제거 로직 (기존 생성된 파일명과 맞춤)
        safe_word = item['word'].replace(" ", "_").replace("'", "").replace("+", "plus").replace("/", "_")
        
        # --- 파일 경로 설정 (카드뉴스 생성기의 파일명 규칙 기준) ---
        # 이미지 파일 (1~6번 조합)
        img_1 = os.path.join(IMAGE_DIR, f"{index:02d}_{safe_word}_1_word.png")
        img_2 = os.path.join(IMAGE_DIR, f"{index:02d}_{safe_word}_2_meaning.png")
        img_3 = os.path.join(IMAGE_DIR, f"{index:02d}_{safe_word}_3_word_meaning.png")
        img_4 = os.path.join(IMAGE_DIR, f"{index:02d}_{safe_word}_4_sentence.png")
        img_5 = os.path.join(IMAGE_DIR, f"{index:02d}_{safe_word}_5_translation.png")
        img_6 = os.path.join(IMAGE_DIR, f"{index:02d}_{safe_word}_6_sentence_translation.png")

        # 오디오 파일 (1~4번 조합)
        aud_1 = os.path.join(AUDIO_DIR, f"{index:02d}_{safe_word}_1_word.mp3")
        aud_2 = os.path.join(AUDIO_DIR, f"{index:02d}_{safe_word}_2_meaning.mp3")
        aud_3 = os.path.join(AUDIO_DIR, f"{index:02d}_{safe_word}_3_sentence.mp3")
        aud_4 = os.path.join(AUDIO_DIR, f"{index:02d}_{safe_word}_4_translation.mp3")

        try:
            # 1. 영단어 (이미지 + 오디오) -> 이미지+오디오 클립과 0.5초 무음 대기 클립으로 분리
            audio_clip_1 = AudioFileClip(aud_1)
            clip_1 = ImageClip(img_1).set_audio(audio_clip_1).set_duration(audio_clip_1.duration)
            clip_1_pause = ImageClip(img_1).set_duration(0.5)
            
            # 2. 한국어 뜻 (이미지 + 오디오)
            audio_clip_2 = AudioFileClip(aud_2)
            clip_2 = ImageClip(img_2).set_audio(audio_clip_2).set_duration(audio_clip_2.duration)
            clip_2_pause = ImageClip(img_2).set_duration(0.5)
            
            # 3. 영단어+뜻 확인 (이미지 전용, 1.5초 대기)
            clip_3 = ImageClip(img_3).set_duration(1.5)
            
            # 4. 영어 예문 (이미지 + 오디오)
            audio_clip_3 = AudioFileClip(aud_3)
            clip_4 = ImageClip(img_4).set_audio(audio_clip_3).set_duration(audio_clip_3.duration)
            clip_4_pause = ImageClip(img_4).set_duration(0.5)
            
            # 5. 한국어 해석 (이미지 + 오디오)
            audio_clip_4 = AudioFileClip(aud_4)
            clip_5 = ImageClip(img_5).set_audio(audio_clip_4).set_duration(audio_clip_4.duration)
            clip_5_pause = ImageClip(img_5).set_duration(0.5)
            
            # 6. 예문+해석 확인 (이미지 전용, 2초 대기)
            clip_6 = ImageClip(img_6).set_duration(2.0)

            # 단일 단어에 대한 모든 클립을 순서대로 배열에 추가
            video_clips.extend([
                clip_1, clip_1_pause, 
                clip_2, clip_2_pause, 
                clip_3, 
                clip_4, clip_4_pause, 
                clip_5, clip_5_pause, 
                clip_6
            ])
            print(f"[{index}/{len(vocab_data)}] '{item['word']}' 비디오 클립 준비 완료")
            
        except Exception as e:
            print(f"경고: '{item['word']}' 처리 중 오류 발생 (파일 누락 등). 이 단어는 건너뜁니다.")
            print(f"상세 오류: {e}")
            continue

    if not video_clips:
        print("연결할 비디오 클립이 없습니다.")
        return

    # 모든 클립을 하나로 병합
    print("\n최종 동영상 렌더링 중입니다. (화면 크기, 길이에 따라 수 분이 소요될 수 있습니다.)")
    final_video = concatenate_videoclips(video_clips, method="compose")
    
    # MP4 파일로 출력 (24fps)
    output_filename = "vocabulary_learning_video.mp4"
    final_video.write_videofile(
        output_filename, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        threads=4
    )
    
    print(f"\n완료! '{output_filename}' 파일이 성공적으로 생성되었습니다.")

if __name__ == "__main__":
    generate_video()