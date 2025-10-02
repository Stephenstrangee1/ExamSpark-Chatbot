from flask import jsonify, request
from .chatbot import ProfessorAcademyChatbot
from config import Config

def init_routes(app):
    chatbot = ProfessorAcademyChatbot()

    @app.route('/')
    def home():
        with open('templates/index.html', 'r') as f:
            return f.read()

    @app.route('/chat', methods=['POST'])
    def chat():
        try:
            user_message = request.json.get('message', '').strip()
            if not user_message:
                return jsonify({'error': 'Please enter a message.'})
            response = chatbot.generate_response(user_message)
            return jsonify({'response': response})
        except Exception as e:
            return jsonify({'error': f'Error: {str(e)}'})

    @app.route('/save_subject', methods=['POST'])
    def save_subject():
        try:
            subject_data = request.json
            if not subject_data or not subject_data.get('subject'):
                return jsonify({'success': False, 'error': 'Subject is required'})
            result = chatbot.save_subject_to_sheet(subject_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # Add your other routes: /add_qa, /update_dataset
    @app.route('/add_qa', methods=['POST'])
    def add_qa():
        try:
            data = request.json
            question = data.get('question', '').strip()
            answer = data.get('answer', '').strip()
            dataset_name = data.get('dataset', 'main')
            if not question or not answer:
                return jsonify({'error': 'Question and answer are required'})
            if chatbot.add_qa_pair(question, answer, dataset_name):
                return jsonify({'success': True, 'message': 'Q&A pair added successfully'})
            else:
                return jsonify({'error': 'Failed to add Q&A pair'})
        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/update_dataset', methods=['POST'])
    def update_dataset():
        try:
            data = request.json
            dataset_name = data.get('dataset_name', 'main')
            dataset_content = data.get('content', {})
            if chatbot.save_dataset(dataset_name, dataset_content):
                return jsonify({'success': True, 'message': f'{dataset_name} updated successfully'})
            else:
                return jsonify({'error': 'Failed to update dataset'})
        except Exception as e:
            return jsonify({'error': str(e)})
