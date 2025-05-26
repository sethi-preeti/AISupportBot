from flask import Flask, request, jsonify
import rag 

app = Flask(__name__)
qa_chain = rag.setup_rag()

# API Endpoint
@app.route('/invoke', methods=['GET'])
def invoke_api():
    question = request.args.get('question', default="", type=str)
    answer = qa_chain.invoke(question)
    return jsonify({"output": answer})

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)