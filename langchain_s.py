from flask import Flask, request, jsonify
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

app = Flask(__name__)

# LangChain을 사용한 레벨 재구성 로직
def process_playtime_with_langchain(playtime):
    print(f"[LangChain Server] Received playtime: {playtime}")  # 디버깅: 수신한 플레이 타임 출력

    template = """
    플레이어가 {playtime} 초 동안 게임을 플레이했습니다.
    
    다음 기준에 따라 오직 '어려움', '중간', '쉬움' 중 한 단어만 응답하세요:
    - 120초 이상: '어려움'
    - 60초~120초: '중간'
    - 60초 미만: '쉬움'
    
    다른 설명이나 부연 설명은 절대 하지 마세요.
    오직 '어려움', '중간', '쉬움' 중 한 단어만 응답하세요.
    """
    # 프롬프트 설정
    prompt = PromptTemplate(input_variables=["playtime"], template=template)

    # ChatOpenAI를 사용하여 gpt-4 모델로 프롬프트 응답 생성
    llm = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key="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")  # API 키 직접 전달

    try:
        # 프롬프트를 문자열로 포맷하여 전달
        formatted_prompt = prompt.format(playtime=playtime)
        response = llm.invoke(formatted_prompt)  # invoke 메서드 사용
        response_text = response.content.strip()  # .lower() 제거

        print(f"[LangChain Server] Raw response: {response_text}")  # 디버깅용

        # 응답 정규화 개선
        response_text = response_text.lower()  # 소문자로 변환
        if any(word in response_text for word in ["어려움", "상", "고급", "하드"]):
            response_text = "어려움"
        elif any(word in response_text for word in ["중간", "중", "중급", "미디엄"]):
            response_text = "중간"
        elif any(word in response_text for word in ["쉬움", "하", "초급", "이지"]):
            response_text = "쉬움"
        else:
            # 플레이타임 기준으로 기본값 설정
            if float(playtime) < 60:
                response_text = "쉬움"
            elif float(playtime) < 120:
                response_text = "중간"
            else:
                response_text = "어려움"

        print(f"[LangChain Server] Normalized difficulty: {response_text}")

        # 응답 매핑
        difficulty_mapping = {
            "어려움": {"difficulty": "hard", "enemy_count": 15, "playtime": f"{playtime}초"},
            "중간": {"difficulty": "medium", "enemy_count": 10, "playtime": f"{playtime}초"},
            "쉬움": {"difficulty": "easy", "enemy_count": 5, "playtime": f"{playtime}초"}
        }
        
        # 매핑 확인
        if response_text not in difficulty_mapping:
            print(f"[LangChain Server] Warning: Mapping failed for '{response_text}'")
            # 플레이타임 기준으로 기본값 반환
            if float(playtime) < 60:
                return {"difficulty": "easy", "enemy_count": 5, "playtime": f"{playtime}초"}
            elif float(playtime) < 120:
                return {"difficulty": "medium", "enemy_count": 10, "playtime": f"{playtime}초"}
            else:
                return {"difficulty": "hard", "enemy_count": 15, "playtime": f"{playtime}초"}

        return difficulty_mapping[response_text]
    except Exception as e:
        print(f"[LangChain Server] Error: {e}")
        # 에러 발생 시 playtime 기준으로 기본값 반환
        if float(playtime) < 60:
            return {"difficulty": "easy", "enemy_count": 5, "playtime": f"{playtime}초"}
        elif float(playtime) < 120:
            return {"difficulty": "medium", "enemy_count": 10, "playtime": f"{playtime}초"}
        else:
            return {"difficulty": "hard", "enemy_count": 15, "playtime": f"{playtime}초"}

def normalize_response(text):
    text = text.strip()
    # 추가적인 전처리 (필요한 경우)
    if "어려움" in text:
        return "어려움"
    elif "중간" in text:
        return "중간"
    elif "쉬움" in text:
        return "쉬움"
    return text

# LangChain이 데이터를 가공하는 엔드포인트
@app.route('/process', methods=['POST'])
def process_request():
    # Flask로부터 받은 데이터
    data = request.get_json()
    print(f"[LangChain Server] Received request data: {data}")  # 디버깅: 수신한 요청 데이터 출력
    playtime = data.get('playtime')

    # LangChain을 통해 플레이 타임에 따른 레벨 디자인 재구성
    new_level_design = process_playtime_with_langchain(playtime)
    print(f"[LangChain Server] Processed level design: {new_level_design}")  # 디버깅: 처리된 레벨 디자인 출력

    # 가공된 데이터를 Flask로 반환
    return jsonify(new_level_design)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # LangChain 서버는 5001번 포트에서 실행
