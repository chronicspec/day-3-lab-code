# # app.py
# from flask import Flask, request, jsonify, render_template
# from chatbot_baseline import run_chatbot_baseline

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/ask-baseline', methods=['POST'])
# def ask_baseline():
#     data = request.json
#     user_input = data.get('input')
    
#     # Gọi hàm chatbot
#     response = run_chatbot_baseline(user_input)
    
#     return jsonify({"response": response})

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)


from flask import Flask, request, jsonify, render_template
from chatbot_baseline import run_chatbot_baseline
from tests.test_local import run_agent  # Import hàm run_agent đã sửa ở bước trước

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    user_input = request.json.get('input')
    
    # Chạy đồng thời 2 logic
    baseline_res = run_chatbot_baseline(user_input)
    agent_res = run_agent(user_input)
    
    return jsonify({
        "baseline": baseline_res,
        "agent": agent_res
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)