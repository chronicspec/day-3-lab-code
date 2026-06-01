from flask import Flask, request, jsonify, render_template
from tests.test_local import run_agent # Hàm đã có Timeout 40s

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask-agent', methods=['POST'])
def ask_agent():
    try:
        user_input = request.json.get('input', '')
        result_dict = run_agent(user_input) 
        return jsonify(result_dict)
    except Exception as e:
        return jsonify({"final_answer": "Lỗi hệ thống: " + str(e), "trace": [], "metrics": {"steps": 0, "latency_ms": 0}})

if __name__ == '__main__':
    app.run(debug=True, port=5000)