from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# 데이터 기록을 위한 전역 변수
log_data = []

# Unity에서 플레이 타임 데이터를 받는 엔드포인트
@app.route('/process_playtime', methods=['POST'])
def handle_playtime():
    data = request.get_json()
    playtime = data.get('playtime')
    print(f"[Flask Server] Received playtime from Unity: {playtime}")  # 디버깅: Unity에서 수신한 플레이 타임 출력
    
    # LangChain 서버로 데이터를 전송하여 처리 결과 받음
    new_level_design = send_to_langchain_for_processing(playtime)

    # 수신한 데이터를 기록
    log_entry = f"Received playtime: {playtime}, Processed Result: {new_level_design}"
    log_data.append(log_entry)
    print(f"[Flask Server] Log entry added: {log_entry}")  # 디버깅: 로그 항목 출력

    return jsonify(new_level_design)

# LangChain 서버로 데이터를 보내는 함수
def send_to_langchain_for_processing(playtime):
    url = "http://localhost:5001/process"
    payload = {"playtime": playtime}
    headers = {'Content-Type': 'application/json'}

    print(f"[Flask Server] Sending playtime to LangChain Server: {playtime}")  # 디버깅: LangChain 서버로 전송할 데이터 출력
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"[Flask Server] Received response from LangChain Server: {response.json()}")  # 디버깅: LangChain 서버로부터 받은 응답 출력
        return response.json()
    else:
        print("[Flask Server] Error: LangChain processing failed")  # 디버깅: 에러 발생 시 알림
        return {"error": "LangChain processing failed"}

# 웹사이트에서 데이터 기록 확인
@app.route('/logs')
def show_logs():
    return render_template('logs.html', logs=log_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Flask 서버는 5000번 포트에서 실행
