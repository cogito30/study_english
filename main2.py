import os
import asyncio
try:
    import edge_tts
except ImportError:
    print("edge-tts 라이브러리가 필요합니다. 터미널에서 'pip install edge-tts'를 실행해주세요.")
    exit()

# ==========================================
# [1] 음성 설정 (원하는 옵션으로 수정하세요)
# ==========================================
# 영어 발음 설정
ENG_ACCENT = "US"  # "US" (미국식), "UK" (영국식)
ENG_GENDER = "Male" # "Male" (남성), "Female" (여성)

# 한국어 발음 설정
KOR_GENDER = "Female" # "Male" (남성), "Female" (여성)

# 국가 및 성별에 따른 edge-tts 고품질 AI 음성 매핑
VOICES = {
    "US": {
        "Male": "en-US-GuyNeural",
        "Female": "en-US-JennyNeural"
    },
    "UK": {
        "Male": "en-GB-RyanNeural",
        "Female": "en-GB-SoniaNeural"
    },
    "KR": {
        "Male": "ko-KR-InJoonNeural",
        "Female": "ko-KR-SunHiNeural"
    }
}

# ==========================================
# [2] 텍스트 파일 읽기 함수 (기존과 동일)
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
# [3] 음성 파일 생성 메인 로직 (비동기 처리)
# ==========================================
async def generate_audio_files():
    vocab_data = load_vocab_from_txt('vocabulary.md')
    
    if not vocab_data:
        print("단어 데이터가 없거나 파일을 찾을 수 없어 프로그램을 종료합니다.")
        return

    # 결과물을 저장할 폴더 생성
    OUTPUT_DIR = "audio_output"
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 선택된 음성 모델 가져오기
    eng_voice = VOICES.get(ENG_ACCENT, {}).get(ENG_GENDER, VOICES["US"]["Female"])
    kor_voice = VOICES["KR"].get(KOR_GENDER, VOICES["KR"]["Female"])
        
    print(f"음성 생성을 시작합니다...")
    print(f"- 영어 음성: {ENG_ACCENT} {ENG_GENDER} ({eng_voice})")
    print(f"- 한국어 음성: {KOR_GENDER} ({kor_voice})")

    for index, item in enumerate(vocab_data, start=1):
        # 파일명에 사용할 수 없는 특수문자 제거
        safe_word = item['word'].replace(" ", "_").replace("'", "").replace("+", "plus").replace("/", "_")
        
        # 1. 영단어 음성 파일 생성 (영어)
        word_filename = os.path.join(OUTPUT_DIR, f"{index:02d}_{safe_word}_1_word.mp3")
        word_tts = edge_tts.Communicate(item['word'], eng_voice)
        await word_tts.save(word_filename)
        
        # 2. 한글 뜻 음성 파일 생성 (한국어)
        meaning_filename = os.path.join(OUTPUT_DIR, f"{index:02d}_{safe_word}_2_meaning.mp3")
        meaning_tts = edge_tts.Communicate(item['meaning'], kor_voice)
        await meaning_tts.save(meaning_filename)

        # 3. 영어 예문 음성 파일 생성 (영어)
        sentence_filename = os.path.join(OUTPUT_DIR, f"{index:02d}_{safe_word}_3_sentence.mp3")
        sentence_tts = edge_tts.Communicate(item['sentence'], eng_voice)
        await sentence_tts.save(sentence_filename)
        
        # 4. 한글 해석 음성 파일 생성 (한국어)
        translation_filename = os.path.join(OUTPUT_DIR, f"{index:02d}_{safe_word}_4_translation.mp3")
        translation_tts = edge_tts.Communicate(item['translation'], kor_voice)
        await translation_tts.save(translation_filename)
        
        print(f"[{index}/{len(vocab_data)}] '{item['word']}' 음성 파일(영/한) 생성 완료")

    print(f"\n모든 음성 파일이 성공적으로 생성되었습니다!")
    print(f"확인 경로: {os.path.abspath(OUTPUT_DIR)}")

# 파이썬 3.7+ 비동기 실행
if __name__ == "__main__":
    asyncio.run(generate_audio_files())