import json
import os
import io
from gtts import gTTS

class JapaneseLesson:
    def __init__(self, day_no, title, situation, conversation, vocabulary):
        self.day_no = day_no
        self.title = title
        self.situation = situation
        self.conversation = conversation
        self.vocabulary = vocabulary

    def generate_markdown(self):
        md = f"# 🇯🇵 오늘의 일본어 Day {self.day_no}: {self.title}\n\n"
        md += f"## 🎬 상황 설정\n{self.situation}\n\n"
        md += "## 🗣️ 오늘의 회화\n"
        for line in self.conversation:
            md += f"- **{line['speaker']}**: {line['jp']}\n"
            md += f"  - ({line['ko']})\n"
        
        md += "\n## 📚 핵심 단어장\n"
        for vocab in self.vocabulary:
            md += f"- **{vocab['word']}** [{vocab['pronunciation']}]: {vocab['meaning']}\n"
        
        return md
        
    def save_markdown_file(self):
        # day_{no}.md 형태로 파일명 지정
        filename = f"day_{self.day_no}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.generate_markdown())
        print(f"✅ '{filename}' 파일이 성공적으로 생성되었습니다!")

    def generate_audio_file(self):
        filename = f"day_{self.day_no}.mp3"
        
        try:
            # pydub는 이 메서드 실행 시점에 임포트하여, 설치 안 된 경우 예외 처리
            from pydub import AudioSegment
            
            # 1.5초(1500ms) 간격 무음 생성 (필요에 따라 시간 조절 가능)
            silence = AudioSegment.silent(duration=1500)
            combined_audio = AudioSegment.empty()
            
            print(f"🎧 '{filename}' 음성 파일 생성 중... (화자 간 1.5초 간격 추가)")
            
            for line in self.conversation:
                # 1. 각 문장(대사)별로 TTS 생성
                tts = gTTS(text=line['jp'], lang='ja')
                
                # 2. 파일로 저장하지 않고 메모리(버퍼)에 임시 저장하여 속도 향상
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                
                # 3. pydub를 이용해 mp3 데이터를 AudioSegment 객체로 변환
                segment = AudioSegment.from_file(fp, format="mp3")
                
                # 4. 전체 오디오에 현재 대사 + 무음(간격) 추가
                combined_audio += segment + silence
                
            # 5. 최종 완성된 오디오를 파일로 저장
            combined_audio.export(filename, format="mp3")
            print(f"✅ '{filename}' 음성 파일이 성공적으로 생성되었습니다!")
            
        except ImportError:
            print("❌ 라이브러리 오류: 'pydub' 라이브러리가 필요합니다.")
            print("👉 터미널에서 'pip install pydub'를 실행해주세요.")
        except FileNotFoundError:
            print("❌ FFmpeg 오류: 오디오 편집(간격 추가)을 위해 Mac에 'ffmpeg'가 필요합니다.")
            print("👉 터미널에서 'brew install ffmpeg'를 실행해주세요.")
        except Exception as e:
            print(f"❌ 음성 파일 생성 실패: {e}")
            print("💡 pydub와 ffmpeg가 정상적으로 설치되었는지 확인해주세요.")

    def export_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=2)

# ==========================================
# [테스트] 1일차 데이터: 카페에서 주문하기
# ==========================================
day1_data = {
    "day_no": 1,
    "title": "카페에서 주문하기",
    "situation": "일본 여행 중 카페에 방문하여 커피를 주문하고 사이즈를 선택하는 상황입니다.",
    "conversation": [
        {"speaker": "점원", "jp": "いらっしゃいませ。ご注文はお決まりですか？", "ko": "어서 오세요. 주문하시겠습니까?"},
        {"speaker": "나", "jp": "はい、ホットコーヒーを一つお願いします。", "ko": "네, 따뜻한 커피 하나 부탁합니다."},
        {"speaker": "점원", "jp": "サイズはどうなさいますか？", "ko": "사이즈는 어떻게 하시겠습니까?"},
        {"speaker": "나", "jp": "レギュラーサイズでお願いします。", "ko": "레귤러 사이즈로 부탁합니다."},
        {"speaker": "점원", "jp": "かしこまりました。", "ko": "알겠습니다."}
    ],
    "vocabulary": [
        {"word": "いらっしゃいませ", "pronunciation": "이랏샤이마세", "meaning": "어서 오세요"},
        {"word": "注文", "pronunciation": "츄-몬", "meaning": "주문"},
        {"word": "決まる", "pronunciation": "키마루", "meaning": "정해지다"},
        {"word": "一つ", "pronunciation": "히토츠", "meaning": "하나"},
        {"word": "お願い", "pronunciation": "오네가이", "meaning": "부탁"},
        {"word": "どうなさいますか", "pronunciation": "도-나사이마스카", "meaning": "어떻게 하시겠습니까? (어떻게 할까요의 정중어)"},
        {"word": "かしこまりました", "pronunciation": "카시코마리마시타", "meaning": "알겠습니다 (정중어)"}
    ]
}

# 객체 생성
lesson_day1 = JapaneseLesson(**day1_data)

# 파일 생성 실행
lesson_day1.save_markdown_file()
lesson_day1.generate_audio_file()

# JSON 출력 테스트가 필요하시면 아래 주석을 해제하세요.
# print("\n========== JSON 데이터 (DB 저장용) ==========")
# print(lesson_day1.export_json())