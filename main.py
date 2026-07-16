import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

def load_vocab_from_txt(filepath):
    """
    주어진 텍스트 파일을 읽어 딕셔너리 리스트 형태로 변환하는 함수입니다.
    """
    vocab_list = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            current_item = {}
            for line in file:
                line = line.strip()
                # 빈 줄이거나 주석(#)으로 시작하는 줄은 건너뜀
                if not line or line.startswith('#'):
                    continue
                
                # "1. word: meaning" 형태 분석
                if line[0].isdigit() and '.' in line and ':' in line:
                    word_part, meaning_part = line.split('.', 1)[1].split(':', 1)
                    current_item = {
                        "word": word_part.strip(),
                        "meaning": meaning_part.strip()
                    }
                # "- 문장" 형태 분석 (영어 예문과 한글 해석 순서대로 저장)
                elif line.startswith('-') and current_item:
                    content = line[1:].strip()
                    if "sentence" not in current_item:
                        current_item["sentence"] = content
                    else:
                        current_item["translation"] = content
                        # 예문과 해석까지 모두 추출되면 리스트에 추가하고 초기화
                        vocab_list.append(current_item)
                        current_item = {}
    except FileNotFoundError:
        print(f"오류: '{filepath}' 파일을 찾을 수 없습니다.")
        return []
    
    return vocab_list

# 'vocabulary.txt' 파일에서 데이터를 읽어옵니다.
vocab_data = load_vocab_from_txt('vocabulary.md')

# 데이터를 제대로 불러오지 못한 경우 안전하게 종료
if not vocab_data:
    print("단어 데이터가 없거나 파일을 찾을 수 없어 프로그램을 종료합니다.")
    exit()

# 결과물을 저장할 폴더 생성
OUTPUT_DIR = "card_news_output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 이미지 기본 설정 (1080x1080 SNS 최적화 사이즈)
IMG_SIZE = 1080
BG_COLOR = "#F4F7F6"  # 부드러운 배경색
TEXT_COLOR = "#2C3E50" # 가독성 좋은 진한 회/남색

# macOS 기본 폰트 설정 (AppleSDGothicNeo)
# 맥 OS 환경에서 한글을 지원하는 기본 폰트 경로입니다.
font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

try:
    # 텍스트 길이에 따라 폰트 크기를 다르게 설정
    font_large = ImageFont.truetype(font_path, 110) # 단어용 큰 폰트
    font_medium = ImageFont.truetype(font_path, 70) # 예문용 중간 폰트
except IOError:
    print("기본 폰트를 찾을 수 없습니다. 기본 폰트로 대체합니다 (한글이 깨질 수 있습니다).")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()

def create_image(text, filename, is_long_text=False):
    """
    텍스트를 받아 1080x1080 사이즈의 이미지를 생성하고 저장하는 함수
    """
    # 새 이미지 캔버스 생성
    img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 텍스트가 길 경우 폰트 크기 조절 및 줄바꿈 처리
    if is_long_text:
        font = font_medium
        # 영어와 한글 혼용 시 줄바꿈 처리 (가로 약 30글자 기준)
        wrapped_text = "\n".join([textwrap.fill(line, width=30) for line in text.split("\n")])
    else:
        font = font_large
        wrapped_text = "\n".join([textwrap.fill(line, width=20) for line in text.split("\n")])

    # 텍스트가 이미지의 정중앙에 오도록 좌표 계산
    # Pillow 최신 버전에서는 textbbox를 사용하여 텍스트 영역의 크기를 구합니다.
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (IMG_SIZE - text_width) / 2
    y = (IMG_SIZE - text_height) / 2

    # 중앙 정렬하여 텍스트 그리기
    draw.multiline_text(
        (x, y), 
        wrapped_text, 
        font=font, 
        fill=TEXT_COLOR, 
        align="center",
        spacing=20 # 줄간격
    )
    
    # 이미지 저장
    save_path = os.path.join(OUTPUT_DIR, filename)
    img.save(save_path)
    print(f"생성 완료: {save_path}")

# 각 단어별로 6가지 조합의 카드뉴스 생성
print("카드뉴스 생성을 시작합니다...")

for index, item in enumerate(vocab_data, start=1):
    # 특수문자 제거(파일명에 사용하기 위함)
    safe_word = item['word'].replace(" ", "_").replace("'", "").replace("+", "plus").replace("/", "_")
    
    # 1. 영단어만
    create_image(
        text=item['word'], 
        filename=f"{index:02d}_{safe_word}_1_word.png", 
        is_long_text=False
    )
    
    # 2. 뜻만
    create_image(
        text=item['meaning'], 
        filename=f"{index:02d}_{safe_word}_2_meaning.png", 
        is_long_text=False
    )
    
    # 3. 영단어 + 뜻
    create_image(
        text=f"{item['word']}\n\n{item['meaning']}", 
        filename=f"{index:02d}_{safe_word}_3_word_meaning.png", 
        is_long_text=False
    )
    
    # 4. 예문만
    create_image(
        text=item['sentence'], 
        filename=f"{index:02d}_{safe_word}_4_sentence.png", 
        is_long_text=True
    )
    
    # 5. 해석만
    create_image(
        text=item['translation'], 
        filename=f"{index:02d}_{safe_word}_5_translation.png", 
        is_long_text=True
    )
    
    # 6. 예문 + 해석
    create_image(
        text=f"{item['sentence']}\n\n({item['translation']})", 
        filename=f"{index:02d}_{safe_word}_6_sentence_translation.png", 
        is_long_text=True
    )

print("\n모든 카드뉴스가 성공적으로 생성되었습니다!")
print(f"확인 경로: {os.path.abspath(OUTPUT_DIR)}")