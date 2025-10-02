from flask import Flask, request, jsonify
import os
import json
import requests
import signal
import sys
from werkzeug.serving import run_simple
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Simplified HTML Template with fixed popup and integrated chat
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professor Academy - UGC NET Coaching</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 { font-size: 2.5rem; margin-bottom: 10px; font-weight: 700; }
        .header p { font-size: 1.2rem; opacity: 0.9; }

        .content {
            padding: 40px;
            text-align: center;
        }

        .welcome-message {
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 30px;
            line-height: 1.6;
        }

        .cta-button {
            background: linear-gradient(135deg, #25D366, #128C7E);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(37, 211, 102, 0.3);
        }

        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37, 211, 102, 0.4);
        }

        .chatbot-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #25D366, #128C7E);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(37, 211, 102, 0.4);
            z-index: 1000;
            transition: all 0.3s ease;
            border: none;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 80%, 100% { transform: scale(0.9); opacity: 0.9; }
            40% { transform: scale(1); opacity: 1; }
        }

        .chatbot-widget {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 400px;
            height: 600px;
            background: #1e1e1e;
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
            z-index: 999;
            display: flex;
            flex-direction: column;
            border: 1px solid #3e3e42;
            overflow: hidden;
            transform: translateY(20px) scale(0.8);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            visibility: hidden;
        }

        .chatbot-widget.active {
            transform: translateY(0) scale(1);
            opacity: 1;
            visibility: visible;
        }

        .widget-header {
            background: linear-gradient(135deg, #25D366, #128C7E);
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-weight: 600;
        }

        .widget-header-left { display: flex; align-items: center; gap: 12px; }
        .widget-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }

        .widget-close {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 8px;
            border-radius: 50%;
            transition: background 0.2s;
        }

        .widget-close:hover { background: rgba(255, 255, 255, 0.1); }

        .widget-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #1a1a1a;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .message {
            display: flex;
            align-items: flex-end;
            animation: fadeIn 0.3s ease-in;
        }

        .message.bot { justify-content: flex-start; }
        .message.user { justify-content: flex-end; }
        .message.buttons { justify-content: flex-start; }

        .message.bot .message-content,
        .message.buttons .message-content {
            background: #2d2d30;
            color: #e4e6ea;
            border-radius: 16px 16px 16px 4px;
            font-size: 13px;
            padding: 12px 16px;
            max-width: 85%;
            line-height: 1.4;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            border: 1px solid #3e3e42;
        }

        .message.user .message-content {
            background: #25D366;
            color: white;
            border-radius: 16px 16px 4px 16px;
            font-size: 13px;
            padding: 12px 16px;
            max-width: 85%;
            line-height: 1.4;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        }

        /* Enhanced list styling for FAQ content */
        .message-content ul {
            margin: 8px 0;
            padding-left: 20px;
        }

        .message-content ol {
            margin: 8px 0;
            padding-left: 20px;
        }

        .message-content li {
            margin: 4px 0;
            line-height: 1.5;
        }

        .message-content ul li {
            list-style-type: disc;
            color: #e4e6ea;
        }

        .message-content ol li {
            list-style-type: decimal;
            color: #e4e6ea;
        }

        .message-content h3 {
            color: #25D366;
            margin: 10px 0 6px 0;
            font-size: 14px;
            font-weight: 600;
        }

        .message-content h4 {
            color: #25D366;
            margin: 8px 0 4px 0;
            font-size: 13px;
            font-weight: 500;
        }

        .message-content p {
            margin: 6px 0;
            line-height: 1.4;
        }

        .message-content strong {
            color: #25D366;
            font-weight: 600;
        }

        .message-content em {
            color: #ffd700;
            font-style: italic;
        }

        /* Button message styles */
        .buttons-container {
            background: #2d2d30;
            border-radius: 16px 16px 16px 4px;
            padding: 16px;
            max-width: 90%;
            border: 1px solid #3e3e42;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        }

        .buttons-title {
            color: #25D366;
            font-size: 12px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-align: center;
            font-weight: 600;
        }

        .action-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
        }

        .action-btn {
            padding: 8px 12px;
            border: 1px solid #25D366;
            background: transparent;
            color: #25D366;
            border-radius: 20px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.2s ease;
            white-space: nowrap;
        }

        .action-btn:hover {
            background: #25D366;
            color: white;
            transform: translateY(-1px);
        }

        .action-btn.primary {
            background: #25D366;
            color: white;
        }

        .action-btn.back {
            background: #444;
            border-color: #666;
            color: #ccc;
            width: auto;
            margin-top: 10px;
            padding: 4px 8px;
            font-size: 10px;
        }

        .widget-input-area {
            padding: 16px;
            border-top: 1px solid #3e3e42;
            background: #1e1e1e;
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .widget-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #3e3e42;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
            background: #2d2d30;
            color: #e4e6ea;
            transition: border-color 0.2s;
        }

        .widget-input:focus { border-color: #25D366; }
        .widget-input::placeholder { color: #8e8e93; }

        .widget-send-btn {
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 50%;
            background: #25D366;
            color: white;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .widget-send-btn:hover { background: #128C7E; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 768px) {
            .chatbot-widget {
                width: calc(100vw - 40px);
                height: calc(100vh - 120px);
                bottom: 90px;
                right: 20px;
                left: 20px;
            }
            .header h1 { font-size: 2rem; }
            .content { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="main-content">
        <div class="header">
            <h1>🎓 Professor Academy</h1>
            <p>UGC NET, CSIR NET, TRB Coaching Since 2016</p>
        </div>
        
        <div class="content">
            <div class="welcome-message">
                Quality & Affordable Coaching for UGC NET, CSIR NET, TRB, TN SET, and TN TET. 
                Specializing in Commerce, Computer Science, English, Economics, Education, Management, Mathematics, and Life Science.
            </div>
            <button class="cta-button" onclick="toggleWidget()">
                💬 Start Chat with AI Assistant
            </button>
        </div>
    </div>

    <button class="chatbot-toggle" id="chatbotToggle" onclick="toggleWidget()">🤖</button>
    
    <div class="chatbot-widget" id="chatbotWidget">
        <div class="widget-header">
            <div class="widget-header-left">
                <div class="widget-avatar">🎓</div>
                <div class="widget-info">
                    <h4>Professor Academy AI</h4>
                    <p>Ready to help</p>
                </div>
            </div>
            <button class="widget-close" onclick="closeWidget()">×</button>
        </div>
        
        <div class="widget-messages" id="widgetMessages">
            <div class="message bot">
                <div class="message-content">
                    👋 Hi! Welcome to Professor Academy! How can I assist you today?
                </div>
            </div>
        </div>
        
        <div class="widget-input-area">
            <input type="text" class="widget-input" id="widgetInput" placeholder="Type your message...">
            <button class="widget-send-btn" id="widgetSendBtn" onclick="sendMessage()">➤</button>
        </div>
    </div>

    <script>
        const chatbotWidget = document.getElementById('chatbotWidget');
        const widgetMessages = document.getElementById('widgetMessages');
        const widgetInput = document.getElementById('widgetInput');
        const chatbotToggle = document.getElementById('chatbotToggle');

        let currentFlow = 'welcome';
        let navigationHistory = [];
        let currentSubject = '';
        let currentExamType = '';
        let showFAQs = true;
        let manualSubjectInputMode = false;

        const ugcNetSubjects = [
            'Commerce', 'Computer Science', 'English', 'Economics', 'Education', 
            'Management', 'History', 'Geography', 'Law', 'Home Science',
            'Tamil', 'Paper 1', 'Others'
        ];

        const csirNetSubjects = [
            'Life Sciences', 'Chemical Sciences', 'Physical Sciences'
        ];

        const flows = {
            'welcome': {
                title: 'Choose an Option',
                buttons: [
                    { id: 'new-student', text: 'New Batch', type: 'primary' },
                    { id: 'current-batch', text: 'Current Batch', type: 'normal' },
                    { id: 'careers', text: 'Careers', type: 'normal' }
                ]
            },
            'new-student': {
                title: 'Which exam are you preparing for?',
                buttons: [
                    { id: 'ugc-net', text: 'UGC NET', type: 'primary' },
                    { id: 'csir', text: 'CSIR', type: 'normal' },
                    { id: 'tnset', text: 'TNSET', type: 'normal' },
                    { id: 'tntet', text: 'TNTET', type: 'normal' },
                    { id: 'college-trb', text: 'College TRB', type: 'normal' },
                    { id: 'poly-trb', text: 'Polytechnic TRB', type: 'normal' }
                ]
            },
            'ugc-net-subjects': {
                title: 'Select your UGC NET Subject',
                buttons: ugcNetSubjects.map(subject => ({
                    id: `subject-${subject.toLowerCase().replace(/\s+/g, '-')}`,
                    text: `${subject}`,
                    type: subject === 'Others' ? 'primary' : 'normal'
                }))
            },
            'csir-subjects': {
                title: 'Select your CSIR NET Subject',
                buttons: csirNetSubjects.map(subject => ({
                    id: `subject-${subject.toLowerCase().replace(/\s+/g, '-')}`,
                    text: `${subject}`,
                    type: 'normal'
                }))
            },
            'subject-options': {
                title: 'What would you like to know?',
                buttons: [
                    { id: 'exam-details', text: 'Exam Details', type: 'primary' },
                    { id: 'course-details', text: 'Course Details', type: 'primary' },
                    { id: 'fees', text: 'Fees Structure', type: 'normal' },
                    { id: 'books', text: 'Books', type: 'normal' },
                    { id: 'test-series', text: 'Test Series', type: 'normal' },
                    { id: 'free-materials', text: 'Free Materials', type: 'normal' },
                    { id: 'talk-expert', text: 'Talk to Expert', type: 'primary' }
                ]
            },
            'exam-details-sub': {
                title: 'Exam Details - Sub Options',
                buttons: [
                    { id: 'download-syllabus', text: 'Download Syllabus', type: 'normal' },
                    { id: 'previous-papers', text: 'Previous Year Papers', type: 'normal' },
                    { id: 'talk-expert-exam', text: 'Talk with Expert', type: 'primary' }
                ]
            },
            'course-details-sub': {
                title: 'Course Details - Sub Options',
                buttons: [
                    { id: 'view-syllabus', text: 'View Full Syllabus', type: 'normal' },
                    { id: 'download-brochure', text: 'Download Brochure', type: 'normal' },
                    { id: 'visit-course-page', text: 'Visit Course Page', type: 'normal' }
                ]
            },
            'fees-sub': {
                title: 'Fees Structure Options',
                buttons: [
                    { id: 'enroll-now', text: 'Enroll Now', type: 'primary' },
                    { id: 'need-help-joining', text: 'Need Help Before Joining?', type: 'normal' }
                ]
            },
            'books-sub': {
                title: 'Book Options',
                buttons: [
                    { id: 'view-sample', text: 'View Sample', type: 'normal' },
                    { id: 'buy-combo-books', text: 'Buy Combo Books', type: 'primary' },
                    { id: 'buy-paper1-books', text: 'Buy Paper 1 Books', type: 'normal' },
                    { id: 'buy-pyq-books', text: 'Buy PYQ Books', type: 'normal' }
                ]
            },
            'test-series-sub': {
                title: 'Test Series Options',
                buttons: [
                    { id: 'quizzes', text: 'Quizzes', type: 'normal' },
                    { id: 'current-affairs', text: 'Current Affairs', type: 'normal' },
                    { id: 'mock-tests', text: 'Mock Tests', type: 'normal' },
                    { id: 'pyq-papers', text: 'Previous Year Papers', type: 'normal' }
                ]
            },
            'free-materials-sub': {
                title: 'Free Materials',
                buttons: [
                    { id: 'download-free-pdf', text: 'Download Free PDF', type: 'primary' }
                ]
            },
            'talk-expert-sub': {
                title: 'Talk to Expert',
                buttons: [
                    { id: 'call-expert', text: 'Call Us Now: 7070701005', type: 'primary' },
                ]
            },
            'current-batch': {
                title: 'How can we help you?',
                buttons: [
                    { id: 'support-team', text: 'Support Team', type: 'primary' },
                    { id: 'exam-updates', text: 'Exam Updates', type: 'normal' },
                    { id: 'talk-expert', text: 'Talk to Expert', type: 'normal' }
                ]
            },
            'careers': {
                title: 'Career Opportunities',
                buttons: [
                    { id: 'faculty-jobs', text: 'Faculty Positions', type: 'primary' },
                    { id: 'admin-jobs', text: 'Admin Roles', type: 'normal' },
                    { id: 'tech-jobs', text: 'Tech Positions', type: 'normal' }
                ]
            },
            'csir': {
                title: 'CSIR NET Options',
                buttons: [
                    { id: 'csir-exam-details', text: 'Exam Details', type: 'primary' },
                    { id: 'csir-course-details', text: 'Course Details', type: 'primary' },
                    { id: 'csir-fees', text: 'Fees Structure', type: 'normal' },
                    { id: 'csir-books', text: 'Books', type: 'normal' },
                    { id: 'csir-test-series', text: 'Test Series', type: 'normal' },
                    { id: 'csir-free-materials', text: 'Free Materials', type: 'normal' },
                    { id: 'csir-talk-expert', text: 'Talk to Expert', type: 'primary' }
                ]
            },
            'tnset': {
                title: 'TNSET Options',
                buttons: [
                    { id: 'tnset-exam-details', text: 'Exam Details', type: 'primary' },
                    { id: 'tnset-course-details', text: 'Course Details', type: 'primary' },
                    { id: 'tnset-fees', text: 'Fees Structure', type: 'normal' },
                    { id: 'tnset-books', text: 'Books', type: 'normal' },
                    { id: 'tnset-test-series', text: 'Test Series', type: 'normal' },
                    { id: 'tnset-free-materials', text: 'Free Materials', type: 'normal' },
                    { id: 'tnset-talk-expert', text: 'Talk to Expert', type: 'primary' }
                ]
            },
            'tntet': {
                title: 'TNTET Options',
                buttons: [
                    { id: 'tntet-exam-details', text: 'Exam Details', type: 'primary' },
                    { id: 'tntet-course-details', text: 'Course Details', type: 'primary' },
                    { id: 'tntet-fees', text: 'Fees Structure', type: 'normal' },
                    { id: 'tntet-books', text: 'Books', type: 'normal' },
                    { id: 'tntet-test-series', text: 'Test Series', type: 'normal' },
                    { id: 'tntet-free-materials', text: 'Free Materials', type: 'normal' },
                    { id: 'tntet-talk-expert', text: 'Talk to Expert', type: 'primary' }
                ]
            },
            'college-trb': {
                title: 'College TRB Options',
                buttons: [
                    { id: 'college-trb-exam-details', text: 'Exam Details', type: 'primary' },
                    { id: 'college-trb-course-details', text: 'Course Details', type: 'primary' },
                    { id: 'college-trb-fees', text: 'Fees Structure', type: 'normal' },
                    { id: 'college-trb-books', text: 'Books', type: 'normal' },
                    { id: 'college-trb-test-series', text: 'Test Series', type: 'normal' },
                    { id: 'college-trb-free-materials', text: 'Free Materials', type: 'normal' },
                    { id: 'college-trb-talk-expert', text: 'Talk to Expert', type: 'primary' }
                ]
            },
            'poly-trb': {
                title: 'Polytechnic TRB Options',
                buttons: [
                    { id: 'poly-trb-exam-details', text: 'Exam Details', type: 'primary' },
                    { id: 'poly-trb-course-details', text: 'Course Details', type: 'primary' },
                    { id: 'poly-trb-fees', text: 'Fees Structure', type: 'normal' },
                    { id: 'poly-trb-books', text: 'Books', type: 'normal' },
                    { id: 'poly-trb-test-series', text: 'Test Series', type: 'normal' },
                    { id: 'poly-trb-free-materials', text: 'Free Materials', type: 'normal' },
                    { id: 'poly-trb-talk-expert', text: 'Talk to Expert', type: 'primary' }
                ]
            }
        };

        // Enhanced responses with proper HTML list formatting
        const responses = {
            'new-student': '<p>Great! Which exam/course are you preparing for?</p>',
            'current-batch': '<p>Welcome back! How can we assist you today?</p>',
            'careers': '<p>Explore career opportunities with Professor Academy!</p>',
            'ugc-net': '<p>Excellent choice! 🎯 Please select your UGC NET subject:</p>',
            'csir': `<h3>🔬 CSIR NET Coaching</h3>
<ul>
<li><strong>Available Subjects:</strong></li>
<li>Life Sciences</li>
<li>Chemical Sciences</li>
<li>Physical Sciences</li>
</ul>
<p>📞 <strong>Contact:</strong> 7070701005</p>`,
            'tnset': `<h3>📚 TN SET Preparation</h3>
<ul>
<li><strong>Features:</strong></li>
<li>Complete coaching for all subjects</li>
<li>Expert faculty guidance</li>
<li>Study materials included</li>
<li>Mock test series</li>
</ul>
<p>📞 <strong>Call:</strong> 7070701005</p>`,
            'tntet': `<h3>👨‍🏫 TN TET Coaching</h3>
<ol>
<li><strong>Paper Coverage:</strong></li>
<li>Paper 1 - Classes I-V</li>
<li>Paper 2 - Classes VI-VIII</li>
</ol>
<ul>
<li><strong>Additional Benefits:</strong></li>
<li>Child Development & Pedagogy</li>
<li>Subject-specific content</li>
<li>Practice tests</li>
</ul>
<p>📞 <strong>Contact:</strong> 7070701005</p>`,
            'college-trb': `<h3>🏫 College TRB Coaching</h3>
<ul>
<li><strong>Available for:</strong></li>
<li>All academic subjects</li>
<li>Expert faculty team</li>
<li>Comprehensive study materials</li>
<li>Regular assessments</li>
</ul>
<p>📞 <strong>Call:</strong> 7070701005</p>`,
            'poly-trb': `<h3>⚙️ Polytechnic TRB</h3>
<ul>
<li><strong>Engineering Subjects:</strong></li>
<li>Mechanical Engineering</li>
<li>Civil Engineering</li>
<li>Electrical Engineering</li>
<li>Electronics & Communication</li>
<li>Computer Science Engineering</li>
</ul>
<p>📞 <strong>Contact:</strong> 7070701005</p>`,
            'support-team': `<h3>👨‍💻 Support Team</h3>
<ul>
<li><strong>WhatsApp Support:</strong> +91 7070701005</li>
<li><strong>Email:</strong> support@professoracademy.com</li>
<li><strong>Available:</strong> Mon-Sat 9AM-8PM</li>
</ul>`,
            'exam-updates': `<h3>📢 Exam Updates</h3>
<ul>
<li><strong>Latest Notifications:</strong> professoracademy.com/notifications</li>
<li><strong>Exam Schedule:</strong> professoracademy.com/exam-schedule</li>
<li><strong>Important Dates:</strong> professoracademy.com/important-dates</li>
</ul>`,
            'faculty-jobs': `<h3>👨‍🏫 Faculty Positions</h3>
<ul>
<li><strong>Requirements:</strong></li>
<li>Master\'s degree with NET/SET</li>
<li>Teaching experience preferred</li>
<li>Subject expertise required</li>
</ul>
<p><strong>Apply:</strong> careers@professoracademy.com</p>
<p>📞 <strong>HR:</strong> 7070701005</p>`,
            'admin-jobs': `<h3>💼 Administrative Roles</h3>
<ul>
<li><strong>Available Positions:</strong></li>
<li>Academic Coordinator</li>
<li>Student Support Executive</li>
<li>Content Developer</li>
<li>Marketing Executive</li>
</ul>
<p>📞 <strong>Contact:</strong> 7070701005</p>`,
            'tech-jobs': `<h3>💻 Technology Positions</h3>
<ul>
<li><strong>Openings:</strong></li>
<li>Web Developer</li>
<li>Mobile App Developer</li>
<li>Digital Marketing Specialist</li>
<li>IT Support Engineer</li>
</ul>
<p>📞 <strong>Apply:</strong> 7070701005</p>`,
            'download-syllabus': `<h3>📥 Download Syllabus</h3>
<ul>
<li><strong>Available Resources:</strong></li>
<li>Complete syllabus PDF</li>
<li>Topic-wise breakdown</li>
<li>Weightage analysis</li>
</ul>
<p><strong>Access:</strong> professoracademy.com/syllabus</p>
<p>📞 <strong>Call:</strong> 7070701005</p>`,
            'previous-papers': `<h3>📚 Previous Year Papers</h3>
<ul>
<li><strong>Collection Includes:</strong></li>
<li>Last 10 years papers</li>
<li>Detailed solutions</li>
<li>Analysis & trends</li>
<li>Topic-wise questions</li>
</ul>
<p><strong>Available at:</strong> professoracademy.com/papers</p>
<p>📞 <strong>Call:</strong> 7070701005</p>`,
            'talk-expert-exam': '<p>📞 <strong>Expert Consultation</strong> Call Now: 7070701005 for exam guidance</p>',
            'view-syllabus': '<p>📋 <strong>Complete Syllabus</strong> Visit: professoracademy.com/full-syllabus 📞 Call: 7070701005</p>',
            'download-brochure': '<p>📥 <strong>Course Brochure</strong> Download: professoracademy.com/brochure 📞 Call: 7070701005</p>',
            'visit-course-page': '<p>🌐 <strong>Course Page</strong> Visit: professoracademy.com/courses 📞 Call: 7070701005</p>',
            'enroll-now': '<p>🔗 <strong>Enroll Now</strong> Visit: professoracademy.com/enroll 📞 Call: 7070701005</p>',
            'need-help-joining': '<p>🤝 <strong>Need Help?</strong> Visit: https://professoracademy.com/contact-us/ 📞 Call: 7070701005</p>',
            'quizzes': '<p>❓ <strong>Quizzes</strong> Available soon</p>',
            'current-affairs': '<p>📰 <strong>Current Affairs</strong> Available soon</p>',
            'mock-tests': '<p>📝 <strong>Mock Tests</strong> Available soon</p>',
            'pyq-papers': '<p>📚 <strong>Previous Year Papers</strong> Available soon</p>',
            'download-free-pdf': '<p>📥 <strong>Free PDFs</strong> Download at: professoracademy.com/free-materials 📞 Call: 7070701005</p>',
            'call-expert': '<p>📞 <strong>Call Expert</strong> 7070701005 - Available Mon-Sat 9AM-8PM</p>',
            'call-expert-alt': '<p>📞 <strong>Alternative Number</strong> 7070701009 - Available Mon-Sat 9AM-8PM</p>',
            // CSIR responses
            'csir-exam-details': `<h3>🔬 CSIR NET Exam Details</h3>
<ul>
<li><strong>Subjects:</strong> Life Sciences, Chemical Sciences, Physical Sciences</li>
<li><strong>Exam Pattern:</strong> Single paper with 200 marks</li>
<li><strong>Duration:</strong> 3 hours</li>
<li><strong>Frequency:</strong> Twice a year</li>
</ul>
<p>📞 <strong>For details call:</strong> 7070701005</p>`,
            'csir-course-details': `<h3>🔬 CSIR NET Course Details</h3>
<ul>
<li><strong>Features:</strong> Live classes, recorded lectures, study materials</li>
<li><strong>Duration:</strong> 4 months intensive program</li>
<li><strong>Faculty:</strong> Experienced subject experts</li>
<li><strong>Batch Starts:</strong> 16th June 2025</li>
</ul>
<p>📞 <strong>For enrollment call:</strong> 7070701005</p>`,
            'csir-fees': `<h3>💰 CSIR NET Fee Structure</h3>
<ul>
<li><strong>Course Fee:</strong> ₹12,000 - ₹15,000</li>
<li><strong>Inclusions:</strong> Study materials, mock tests, doubt sessions</li>
<li><strong>Payment Options:</strong> EMI available</li>
</ul>
<p>📞 <strong>For fee details call:</strong> 7070701005</p>`,
            'csir-books': `<h3>📖 CSIR NET Books</h3>
<ul>
<li><strong>Combo Books:</strong> ₹1,999 (includes shipping)</li>
<li><strong>Subject-wise Books:</strong> Available for all subjects</li>
<li><strong>Previous Year Papers:</strong> ₹499</li>
</ul>
<p>📞 <strong>To order books call:</strong> 7070701005</p>`,
            'csir-test-series': `<h3>📝 CSIR NET Test Series</h3>
<ul>
<li><strong>Includes:</strong> 10 full-length mock tests</li>
<li><strong>Features:</strong> Detailed analysis, rank comparison</li>
<li><strong>Price:</strong> ₹2,500</li>
</ul>
<p>📞 <strong>For test series call:</strong> 7070701005</p>`,
            'csir-free-materials': `<h3>🆓 CSIR NET Free Materials</h3>
<ul>
<li><strong>Includes:</strong> Syllabus PDFs, sample papers</li>
<li><strong>Access:</strong> professoracademy.com/free-materials</li>
</ul>
<p>📞 <strong>For support call:</strong> 7070701005</p>`,
            'csir-talk-expert': `<h3>📞 CSIR NET Expert Consultation</h3>
<ul>
<li><strong>Call:</strong> 7070701005</li>
<li><strong>Available:</strong> Mon-Sat 9AM-8PM</li>
</ul>`,
            // TNSET responses
            'tnset-exam-details': `<h3>📚 TN SET Exam Details</h3>
<ul>
<li><strong>Conducted by:</strong> Mother Teresa University</li>
<li><strong>Subjects:</strong> All major subjects</li>
<li><strong>Eligibility:</strong> Master\'s degree with 55% marks</li>
</ul>
<p>📞 <strong>For details call:</strong> 7070701005</p>`,
            'tnset-course-details': `<h3>📚 TN SET Course Details</h3>
<ul>
<li><strong>Features:</strong> Complete syllabus coverage</li>
<li><strong>Duration:</strong> 3 months intensive program</li>
<li><strong>Batch Starts:</strong> 16th June 2025</li>
</ul>
<p>📞 <strong>For enrollment call:</strong> 7070701005</p>`,
            'tnset-fees': `<h3>💰 TN SET Fee Structure</h3>
<ul>
<li><strong>Course Fee:</strong> ₹8,000 - ₹10,000</li>
<li><strong>Inclusions:</strong> Study materials, mock tests</li>
</ul>
<p>📞 <strong>For fee details call:</strong> 7070701005</p>`,
            'tnset-books': `<h3>📖 TN SET Books</h3>
<ul>
<li><strong>Combo Books:</strong> ₹1,500 (includes shipping)</li>
<li><strong>Subject-wise Books:</strong> Available for all subjects</li>
</ul>
<p>📞 <strong>To order books call:</strong> 7070701005</p>`,
            'tnset-test-series': `<h3>📝 TN SET Test Series</h3>
<ul>
<li><strong>Includes:</strong> 5 full-length mock tests</li>
<li><strong>Price:</strong> ₹1,500</li>
</ul>
<p>📞 <strong>For test series call:</strong> 7070701005</p>`,
            'tnset-free-materials': `<h3>🆓 TN SET Free Materials</h3>
<ul>
<li><strong>Includes:</strong> Syllabus PDFs, sample papers</li>
<li><strong>Access:</strong> professoracademy.com/free-materials</li>
</ul>
<p>📞 <strong>For support call:</strong> 7070701005</p>`,
            'tnset-talk-expert': `<h3>📞 TN SET Expert Consultation</h3>
<ul>
<li><strong>Call:</strong> 7070701005</li>
<li><strong>Available:</strong> Mon-Sat 9AM-8PM</li>
</ul>`,
            // TNTET responses
            'tntet-exam-details': `<h3>👨‍🏫 TN TET Exam Details</h3>
<ul>
<li><strong>Papers:</strong> Paper I (Classes I-V), Paper II (Classes VI-VIII)</li>
<li><strong>Subjects:</strong> Child Development, Language I & II, Mathematics, EVS/Science/Social Science</li>
</ul>
<p>📞 <strong>For details call:</strong> 7070701005</p>`,
            'tntet-course-details': `<h3>👨‍🏫 TN TET Course Details</h3>
<ul>
<li><strong>Features:</strong> Complete syllabus coverage</li>
<li><strong>Duration:</strong> 2 months intensive program</li>
<li><strong>Batch Starts:</strong> 16th June 2025</li>
</ul>
<p>📞 <strong>For enrollment call:</strong> 7070701005</p>`,
            'tntet-fees': `<h3>💰 TN TET Fee Structure</h3>
<ul>
<li><strong>Course Fee:</strong> ₹6,000 - ₹8,000</li>
<li><strong>Inclusions:</strong> Study materials, mock tests</li>
</ul>
<p>📞 <strong>For fee details call:</strong> 7070701005</p>`,
            'tntet-books': `<h3>📖 TN TET Books</h3>
<ul>
<li><strong>Combo Books:</strong> ₹1,200 (includes shipping)</li>
<li><strong>Paper-wise Books:</strong> Available separately</li>
</ul>
<p>📞 <strong>To order books call:</strong> 7070701005</p>`,
            'tntet-test-series': `<h3>📝 TN TET Test Series</h3>
<ul>
<li><strong>Includes:</strong> 5 full-length mock tests per paper</li>
<li><strong>Price:</strong> ₹1,200</li>
</ul>
<p>📞 <strong>For test series call:</strong> 7070701005</p>`,
            'tntet-free-materials': `<h3>🆓 TN TET Free Materials</h3>
<ul>
<li><strong>Includes:</strong> Syllabus PDFs, sample papers</li>
<li><strong>Access:</strong> professoracademy.com/free-materials</li>
</ul>
<p>📞 <strong>For support call:</strong> 7070701005</p>`,
            'tntet-talk-expert': `<h3>📞 TN TET Expert Consultation</h3>
<ul>
<li><strong>Call:</strong> 7070701005</li>
<li><strong>Available:</strong> Mon-Sat 9AM-8PM</li>
</ul>`,
            // College TRB responses
            'college-trb-exam-details': `<h3>🏫 College TRB Exam Details</h3>
<ul>
<li><strong>For:</strong> Assistant Professor positions in colleges</li>
<li><strong>Subjects:</strong> All academic subjects</li>
<li><strong>Pattern:</strong> Written exam followed by interview</li>
</ul>
<p>📞 <strong>For details call:</strong> 7070701005</p>`,
            'college-trb-course-details': `<h3>🏫 College TRB Course Details</h3>
<ul>
<li><strong>Features:</strong> Subject-specific coaching</li>
<li><strong>Duration:</strong> 3 months intensive program</li>
<li><strong>Batch Starts:</strong> 16th June 2025</li>
</ul>
<p>📞 <strong>For enrollment call:</strong> 7070701005</p>`,
            'college-trb-fees': `<h3>💰 College TRB Fee Structure</h3>
<ul>
<li><strong>Course Fee:</strong> ₹10,000 - ₹12,000</li>
<li><strong>Inclusions:</strong> Study materials, mock tests</li>
</ul>
<p>📞 <strong>For fee details call:</strong> 7070701005</p>`,
            'college-trb-books': `<h3>📖 College TRB Books</h3>
<ul>
<li><strong>Subject-wise Books:</strong> Available for all subjects</li>
<li><strong>Previous Year Papers:</strong> ₹600 per subject</li>
</ul>
<p>📞 <strong>To order books call:</strong> 7070701005</p>`,
            'college-trb-test-series': `<h3>📝 College TRB Test Series</h3>
<ul>
<li><strong>Includes:</strong> Subject-specific mock tests</li>
<li><strong>Price:</strong> ₹2,000 per subject</li>
</ul>
<p>📞 <strong>For test series call:</strong> 7070701005</p>`,
            'college-trb-free-materials': `<h3>🆓 College TRB Free Materials</h3>
<ul>
<li><strong>Includes:</strong> Syllabus PDFs, sample papers</li>
<li><strong>Access:</strong> professoracademy.com/free-materials</li>
</ul>
<p>📞 <strong>For support call:</strong> 7070701005</p>`,
            'college-trb-talk-expert': `<h3>📞 College TRB Expert Consultation</h3>
<ul>
<li><strong>Call:</strong> 7070701005</li>
<li><strong>Available:</strong> Mon-Sat 9AM-8PM</li>
</ul>`,
            // Polytechnic TRB responses
            'poly-trb-exam-details': `<h3>⚙️ Polytechnic TRB Exam Details</h3>
<ul>
<li><strong>For:</strong> Polytechnic Lecturer positions</li>
<li><strong>Subjects:</strong> Engineering disciplines</li>
<li><strong>Pattern:</strong> Written exam with technical questions</li>
</ul>
<p>📞 <strong>For details call:</strong> 7070701005</p>`,
            'poly-trb-course-details': `<h3>⚙️ Polytechnic TRB Course Details</h3>
<ul>
<li><strong>Features:</strong> Engineering subject coaching</li>
<li><strong>Duration:</strong> 3 months intensive program</li>
<li><strong>Batch Starts:</strong> 16th June 2025</li>
</ul>
<p>📞 <strong>For enrollment call:</strong> 7070701005</p>`,
            'poly-trb-fees': `<h3>💰 Polytechnic TRB Fee Structure</h3>
<ul>
<li><strong>Course Fee:</strong> ₹12,000 - ₹15,000</li>
<li><strong>Inclusions:</strong> Study materials, mock tests</li>
</ul>
<p>📞 <strong>For fee details call:</strong> 7070701005</p>`,
            'poly-trb-books': `<h3>📖 Polytechnic TRB Books</h3>
<ul>
<li><strong>Subject-wise Books:</strong> Available for all engineering subjects</li>
<li><strong>Previous Year Papers:</strong> ₹800 per subject</li>
</ul>
<p>📞 <strong>To order books call:</strong> 7070701005</p>`,
            'poly-trb-test-series': `<h3>📝 Polytechnic TRB Test Series</h3>
<ul>
<li><strong>Includes:</strong> Subject-specific mock tests</li>
<li><strong>Price:</strong> ₹2,500 per subject</li>
</ul>
<p>📞 <strong>For test series call:</strong> 7070701005</p>`,
            'poly-trb-free-materials': `<h3>🆓 Polytechnic TRB Free Materials</h3>
<ul>
<li><strong>Includes:</strong> Syllabus PDFs, sample papers</li>
<li><strong>Access:</strong> professoracademy.com/free-materials</li>
</ul>
<p>📞 <strong>For support call:</strong> 7070701005</p>`,
            'poly-trb-talk-expert': `<h3>📞 Polytechnic TRB Expert Consultation</h3>
<ul>
<li><strong>Call:</strong> 7070701005</li>
<li><strong>Available:</strong> Mon-Sat 9AM-8PM</li>
</ul>`
        };

        const feesTemplate = (examType, subject) => {
            let baseFee = 0;
            let feeRange = '';
            
            if (examType === 'ugc-net') {
                baseFee = 12000;
                feeRange = '₹12,000 - ₹16,200';
            } else if (examType === 'csir') {
                baseFee = 12000;
                feeRange = '₹12,000 - ₹15,000';
            } else if (examType === 'tnset') {
                baseFee = 8000;
                feeRange = '₹8,000 - ₹10,000';
            } else if (examType === 'tntet') {
                baseFee = 6000;
                feeRange = '₹6,000 - ₹8,000';
            } else if (examType === 'college-trb') {
                baseFee = 10000;
                feeRange = '₹10,000 - ₹12,000';
            } else if (examType === 'poly-trb') {
                baseFee = 12000;
                feeRange = '₹12,000 - ₹15,000';
            }
            
            return `<h3>💰 ${subject || examType.toUpperCase()} Fee Structure Details</h3>

<h4>Course Fees:</h4>
<ul>
<li>${feeRange} (varies by subject and package)</li>
<li>Complete Packages Available</li>
<li>Flexible Payment Options</li>
<li>Early Bird Discounts Available</li>
</ul>

<h4>What's Included:</h4>
<ul>
<li>Live Interactive Classes</li>
<li>Study Materials</li>
<li>Mock Test Series</li>
<li>Doubt Resolution Support</li>
<li>1 Year Course Access</li>
</ul>

<p>📞 <strong>For detailed fee structure call:</strong> 7070701005</p>`;
        };

        const booksTemplate = (examType) => {
            let bookPrice = 0;
            let bookName = '';
            
            if (examType === 'ugc-net') {
                bookPrice = 1999;
                bookName = 'UGC NET Paper 1 and PYQ Books';
            } else if (examType === 'csir') {
                bookPrice = 1999;
                bookName = 'CSIR NET Subject Books';
            } else if (examType === 'tnset') {
                bookPrice = 1500;
                bookName = 'TNSET Subject Books';
            } else if (examType === 'tntet') {
                bookPrice = 1200;
                bookName = 'TNTET Paper Books';
            } else if (examType === 'college-trb') {
                bookPrice = 1500;
                bookName = 'College TRB Subject Books';
            } else if (examType === 'poly-trb') {
                bookPrice = 1800;
                bookName = 'Polytechnic TRB Subject Books';
            }
            
            return `<h3>📖 Our Specially Curated Books</h3>

<h4>📚 Combo Books: ${bookName}</h4>
<ul>
<li>Price: ₹${bookPrice.toLocaleString('en-IN')}/-</li>
<li>Free shipping within Tamil Nadu</li>
<li>Other states: ₹300 courier charges</li>
</ul>

<h4>📖 Subject-wise Books</h4>
<ul>
<li>Available for all subjects</li>
<li>Detailed coverage of syllabus</li>
<li>Practice questions included</li>
</ul>

<p><strong>Refund Policy:</strong> Only for unused books within 7 days</p>`;
        };

        const testSeriesTemplate = (examType) => {
            let testCount = 0;
            
            if (examType === 'ugc-net') {
                testCount = 10;
            } else if (examType === 'csir') {
                testCount = 10;
            } else if (examType === 'tnset') {
                testCount = 5;
            } else if (examType === 'tntet') {
                testCount = 5;
            } else if (examType === 'college-trb') {
                testCount = 8;
            } else if (examType === 'poly-trb') {
                testCount = 8;
            }
            
            return `<h3>📝 Our ${examType.toUpperCase()} Test Series includes:</h3>

<h4>✅ Comprehensive Coverage:</h4>
<ul>
<li>Interactive Quizzes for quick revision</li>
<li>Current Affairs updates monthly</li>
<li>${testCount} Full-length Mock Tests with analysis</li>
<li>Previous Year Papers with solutions</li>
</ul>

<h4>Features:</h4>
<ul>
<li>Detailed performance analysis</li>
<li>Rank comparison with peers</li>
<li>Topic-wise assessment</li>
<li>Time management practice</li>
</ul>

<p>📞 <strong>For test series enrollment:</strong> 7070701005</p>`;
        };

        const freeMaterialsTemplate = () => {
            return `<h3>🆓 Download FREE Study Materials</h3>

<h4>Available Free Resources:</h4>
<ul>
<li>Previous Year Question Papers (PYQs)</li>
<li>Topic-wise Study Notes</li>
<li>Sample Question Banks</li>
<li>Current Affairs Updates</li>
<li>Quick Revision Notes</li>
</ul>

<h4>How to Access:</h4>
<ul>
<li>No registration required</li>
<li>Instant download available</li>
<li>Regular updates provided</li>
</ul>

<p>📞 <strong>For more free resources:</strong> 7070701005</p>`;
        };

        const talkExpertTemplate = () => {
            return `<h3>📞 Need Help Choosing the Right Plan?</h3>

<h4>Our Experts Can Help With:</h4>
<ul>
<li>Course selection guidance</li>
<li>Fee structure clarification</li>
<li>Study plan customization</li>
<li>Doubt resolution strategies</li>
<li>Career counseling</li>
</ul>

<h4>Contact Details:</h4>
<ul>
<li>Primary: 7070701005</li>
<li>Alternative: 7070701009</li>
<li>Available: Mon-Sat 9AM-8PM</li>
<li>WhatsApp support available</li>
</ul>

<p><strong>Or visit our contact page for more options</strong></p>`;
        };

        const examDetailsTemplate = (examType, subject) => {
            let examName = '';
            let paperStructure = '';
            
            if (examType === 'ugc-net') {
                examName = 'UGC NET';
                paperStructure = `<li>Paper 1: 50 questions | 100 marks | Teaching & Research Aptitude</li>
<li>Paper 2: 100 questions | 200 marks | Subject-specific content</li>
<li>Total Duration: 3 hours | Total Marks: 300</li>`;
            } else if (examType === 'csir') {
                examName = 'CSIR NET';
                paperStructure = `<li>Single paper with 200 marks</li>
<li>Duration: 3 hours</li>
<li>Objective type questions</li>`;
            } else if (examType === 'tnset') {
                examName = 'TNSET';
                paperStructure = `<li>Paper 1: General Paper</li>
<li>Paper 2: Subject-specific paper</li>
<li>Duration: 3 hours per paper</li>`;
            } else if (examType === 'tntet') {
                examName = 'TNTET';
                paperStructure = `<li>Paper 1: For Classes I-V</li>
<li>Paper 2: For Classes VI-VIII</li>
<li>Duration: 3 hours per paper</li>`;
            } else if (examType === 'college-trb') {
                examName = 'College TRB';
                paperStructure = `<li>Subject-specific written exam</li>
<li>Duration: 3 hours</li>
<li>Followed by interview</li>`;
            } else if (examType === 'poly-trb') {
                examName = 'Polytechnic TRB';
                paperStructure = `<li>Technical subject exam</li>
<li>Duration: 3 hours</li>
<li>Engineering-focused questions</li>`;
            }
            
            return `<h3>🎯 ${examName} ${subject ? subject : ''} - Complete Exam Information</h3>

<h4>📊 Exam Structure:</h4>
<ul>
${paperStructure}
</ul>

<h4>📅 Exam Schedule:</h4>
<ul>
<li>Frequency: ${examType === 'ugc-net' || examType === 'csir' ? 'Twice yearly (June & December)' : 'Annually'}</li>
<li>Latest Notification: June 2025</li>
<li>Application Period: As per official notification</li>
</ul>

<h4>🎯 Qualifying Criteria:</h4>
<ul>
<li>Minimum qualifying marks required</li>
<li>Subject expertise assessment</li>
<li>Combined score determines final ranking</li>
</ul>

<p>📞 <strong>For detailed information call:</strong> 7070701005</p>`;
        };

        const courseDetailsTemplate = (examType, subject) => {
            let courseName = '';
            let duration = '';
            
            if (examType === 'ugc-net') {
                courseName = 'UGC NET';
                duration = '4 Months';
            } else if (examType === 'csir') {
                courseName = 'CSIR NET';
                duration = '4 Months';
            } else if (examType === 'tnset') {
                courseName = 'TNSET';
                duration = '3 Months';
            } else if (examType === 'tntet') {
                courseName = 'TNTET';
                duration = '2 Months';
            } else if (examType === 'college-trb') {
                courseName = 'College TRB';
                duration = '3 Months';
            } else if (examType === 'poly-trb') {
                courseName = 'Polytechnic TRB';
                duration = '3 Months';
            }
            
            return `<h3>🚀 Transform Your ${courseName} ${subject ? subject : ''} Preparation Journey</h3>

<h4>✨ What Makes Our Course Special:</h4>
<ul>
<li>Live Interactive Classes with expert faculty</li>
<li>Comprehensive coverage of syllabus</li>
<li>Real-time doubt resolution sessions</li>
<li>Updated syllabus-based content delivery</li>
</ul>

<h4>⏰ Batch Information:</h4>
<ul>
<li>🆕 New Batch Starts: 16th June 2025</li>
<li>🌅 Morning Slot: 5:00 AM – 7:00 AM</li>
<li>🌙 Evening Slot: 8:00 PM – 9:30 PM</li>
<li>⏱️ Course Duration: ${duration}</li>
<li>🗓️ Access Validity: 1 Year</li>
</ul>

<h4>🎯 Learning Benefits:</h4>
<ul>
<li>Structured learning path</li>
<li>Regular performance tracking</li>
<li>Personalized guidance</li>
<li>Success-oriented approach</li>
</ul>

<p>📞 <strong>For enrollment call:</strong> 7070701005</p>`;
        };

        function openExternalLink(url) {
            window.open(url, '_blank');
        }

        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.innerHTML = content;
            
            messageDiv.appendChild(contentDiv);
            widgetMessages.appendChild(messageDiv);
            widgetMessages.scrollTop = widgetMessages.scrollHeight;
        }

        function addButtonMessage(flowId) {
            const flow = flows[flowId];
            if (!flow) return;

            const messageDiv = document.createElement('div');
            messageDiv.className = 'message buttons';
            
            const buttonsContainer = document.createElement('div');
            buttonsContainer.className = 'buttons-container';
            
            const titleDiv = document.createElement('div');
            titleDiv.className = 'buttons-title';
            titleDiv.textContent = flow.title;
            buttonsContainer.appendChild(titleDiv);
            
            const actionButtonsDiv = document.createElement('div');
            actionButtonsDiv.className = 'action-buttons';

            flow.buttons.forEach(button => {
                const btn = document.createElement('button');
                btn.className = `action-btn ${button.type === 'primary' ? 'primary' : ''}`;
                btn.textContent = button.text;
                btn.onclick = () => handleButtonClick(button.id);
                actionButtonsDiv.appendChild(btn);
            });

            if (flowId !== 'welcome') {
                const backBtn = document.createElement('button');
                backBtn.className = 'action-btn back';
                backBtn.textContent = '←';
                backBtn.onclick = goBack;
                actionButtonsDiv.appendChild(backBtn);
            }

            buttonsContainer.appendChild(actionButtonsDiv);
            messageDiv.appendChild(buttonsContainer);
            widgetMessages.appendChild(messageDiv);
            widgetMessages.scrollTop = widgetMessages.scrollHeight;
        }

        function handleButtonClick(buttonId) {
            if (manualSubjectInputMode) {
                return; // Ignore button clicks while in manual input mode
            }

            navigationHistory.push(currentFlow);

            // Handle subject selections
            if (buttonId.startsWith('subject-')) {
                const subjectName = buttonId.replace('subject-', '').replace(/-/g, ' ');
                const capitalizedSubject = subjectName.replace(/\b\w/g, l => l.toUpperCase());
                
                if (capitalizedSubject === 'Others') {
                    manualSubjectInputMode = true;
                    addMessage("Please type the subject you're interested in:");
                    return;
                }
                
                currentSubject = capitalizedSubject;
                currentFlow = 'subject-options';
                addButtonMessage('subject-options');
                return;
            }

            // Handle exam details with template
            if (buttonId === 'exam-details') {
                currentFlow = 'exam-details-sub';
                addMessage(examDetailsTemplate(currentExamType, currentSubject));
                addButtonMessage('exam-details-sub');
                return;
            }

            // Handle course details with template
            if (buttonId === 'course-details') {
                currentFlow = 'course-details-sub';
                addMessage(courseDetailsTemplate(currentExamType, currentSubject));
                addButtonMessage('course-details-sub');
                return;
            }

            // Handle fees with template
            if (buttonId === 'fees') {
                currentFlow = 'fees-sub';
                addMessage(feesTemplate(currentExamType, currentSubject));
                addButtonMessage('fees-sub');
                return;
            }

            // Handle books with template
            if (buttonId === 'books') {
                currentFlow = 'books-sub';
                addMessage(booksTemplate(currentExamType));
                addButtonMessage('books-sub');
                return;
            }

            // Handle test series with template
            if (buttonId === 'test-series') {
                currentFlow = 'test-series-sub';
                addMessage(testSeriesTemplate(currentExamType));
                addButtonMessage('test-series-sub');
                return;
            }

            // Handle free materials with template
            if (buttonId === 'free-materials') {
                currentFlow = 'free-materials-sub';
                addMessage(freeMaterialsTemplate());
                addButtonMessage('free-materials-sub');
                return;
            }

            // Handle talk to expert with template
            if (buttonId === 'talk-expert') {
                currentFlow = 'talk-expert-sub';
                addMessage(talkExpertTemplate());
                addButtonMessage('talk-expert-sub');
                return;
            }

            // Handle external links
            if (buttonId === 'view-sample') {
                openExternalLink('https://professoracademy.com/wp-content/uploads/2024/04/UGC-NET-JRF-TNSET-Paper-1-Sample-PDF.pdf');
                return;
            }
            if (buttonId === 'buy-combo-books') {
                openExternalLink('https://professoracademy.com/courses/ugc-net-paper-1-books-ugc-net-previous-year-question-book/');
                return;
            }
            if (buttonId === 'buy-paper1-books') {
                openExternalLink('https://professoracademy.com/courses/ugc-net-tnset-paper-1-books/');
                return;
            }
            if (buttonId === 'buy-pyq-books') {
                openExternalLink('https://professoracademy.com/courses/ugc-net-paper-1-previous-year-question-bank/');
                return;
            }
            if (buttonId === 'need-help-joining') {
                openExternalLink('https://professoracademy.com/contact-us/');
                return;
            }

            // Handle subject-specific links
            if (buttonId === 'download-syllabus') {
                switch(currentSubject.toLowerCase()) {
                    case 'tamil':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-TAMIL-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'education':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-EDUCATION-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'commerce':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-COMMERCE-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'home science':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-HOME-SCIENCE-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'history':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-HISTORY-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'geography':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-GEOGRAPHY-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'law':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-LAW-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'economics':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-ECONOMICS-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'english':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/04/NTA-UGC-NET-JRF-ENGLISH-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'computer science':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/04/NTA-UGC-NET-JRF-COMPUTER-SCIENCE-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'management':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-MANAGEMENT-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'paper 1':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-PAPER-1-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    default:
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-PAPER-1-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                }
                return;
            }

            if (buttonId === 'previous-papers') {
                openExternalLink('https://professoracademy.com/free-study-material/');
                return;
            }

            if (buttonId === 'view-syllabus') {
                switch(currentSubject.toLowerCase()) {
                    case 'tamil':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-TAMIL-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'education':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-EDUCATION-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'commerce':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-COMMERCE-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'home science':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-HOME-SCIENCE-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'history':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-HISTORY-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'geography':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-GEOGRAPHY-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'law':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-LAW-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'economics':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-ECONOMICS-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'english':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/04/NTA-UGC-NET-JRF-ENGLISH-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'computer science':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/04/NTA-UGC-NET-JRF-COMPUTER-SCIENCE-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'management':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2024/03/NTA-UGC-NET-JRF-MANAGEMENT-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    case 'paper 1':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-PAPER-1-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    default:
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-PAPER-1-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                }
                return;
            }

            if (buttonId === 'download-brochure') {
                switch(currentSubject.toLowerCase()) {
                    case 'tamil':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-Tamil.pdf');
                        break;
                    case 'education':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-Education.pdf');
                        break;
                    case 'commerce':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Commerce-2025-1.pdf');
                        break;
                    case 'home science':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-Home-Science.pdf');
                        break;
                    case 'history':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-History.pdf');
                        break;
                    case 'geography':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-Geography.pdf');
                        break;
                    case 'law':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-Law.pdf');
                        break;
                    case 'economics':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-Eco.pdf');
                        break;
                    case 'english':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-English.pdf');
                        break;
                    case 'computer science':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-CS.pdf');
                        break;
                    case 'management':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2025/04/UGC-NET-Brochure-2025-Management.pdf');
                        break;
                    case 'paper 1':
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-PAPER-1-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                        break;
                    default:
                        openExternalLink('https://professoracademy.com/wp-content/uploads/2023/12/NTA-UGC-NET-JRF-PAPER-1-SYLLABUS-PROFESSOR-ACADEMY.pdf');
                }
                return;
            }

            if (buttonId === 'visit-course-page') {
                switch(currentSubject.toLowerCase()) {
                    case 'tamil':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-tamil/');
                        break;
                    case 'education':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-jrf-education/');
                        break;
                    case 'commerce':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-jrf-commerce/');
                        break;
                    case 'home science':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-home-science/');
                        break;
                    case 'history':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-history/');
                        break;
                    case 'geography':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-geography/');
                        break;
                    case 'law':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-law/');
                        break;
                    case 'economics':
                        openExternalLink('https://professoracademy.com/courses/economics/');
                        break;
                    case 'english':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-english/');
                        break;
                    case 'computer science':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-cs/');
                        break;
                    case 'management':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-management/');
                        break;
                    case 'paper 1':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-paper-1/');
                        break;
                    default:
                        openExternalLink('https://professoracademy.com/courses/ugc-net-paper-1/');
                }
                return;
            }

            if (buttonId === 'enroll-now') {
                switch(currentSubject.toLowerCase()) {
                    case 'tamil':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-tamil/');
                        break;
                    case 'education':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-jrf-education/');
                        break;
                    case 'commerce':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-jrf-commerce/');
                        break;
                    case 'home science':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-home-science/');
                        break;
                    case 'history':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-history/');
                        break;
                    case 'geography':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-geography/');
                        break;
                    case 'law':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-law/');
                        break;
                    case 'economics':
                        openExternalLink('https://professoracademy.com/courses/economics/');
                        break;
                    case 'english':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-english/');
                        break;
                    case 'computer science':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-cs/');
                        break;
                    case 'management':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-management/');
                        break;
                    case 'paper 1':
                        openExternalLink('https://professoracademy.com/courses/ugc-net-paper-1/');
                        break;
                    default:
                        openExternalLink('https://professoracademy.com/courses/ugc-net-paper-1/');
                }
                return;
            }

            if (buttonId === 'download-free-pdf') {
                openExternalLink('https://professoracademy.com/free-study-material/');
                return;
            }

            if (buttonId === 'talk-expert-exam' || buttonId === 'call-expert' || buttonId === 'call-expert-alt') {
                window.location.href = 'tel:7070701005';
                return;
            }

            if (buttonId === 'need-help-joining') {
                window.location.href = 'tel:7070701005';
                return;
            }

            // Handle CSIR flows
            if (buttonId === 'csir') {
                currentExamType = 'csir';
                currentFlow = 'csir-subjects';
                addButtonMessage('csir-subjects');
                return;
            }

            // Handle TNSET flows
            if (buttonId === 'tnset') {
                currentExamType = 'tnset';
                currentFlow = 'tnset';
                addButtonMessage('tnset');
                return;
            }

            // Handle TNTET flows
            if (buttonId === 'tntet') {
                currentExamType = 'tntet';
                currentFlow = 'tntet';
                addButtonMessage('tntet');
                return;
            }

            // Handle College TRB flows
            if (buttonId === 'college-trb') {
                currentExamType = 'college-trb';
                currentFlow = 'college-trb';
                addButtonMessage('college-trb');
                return;
            }

            // Handle Polytechnic TRB flows
            if (buttonId === 'poly-trb') {
                currentExamType = 'poly-trb';
                currentFlow = 'poly-trb';
                addButtonMessage('poly-trb');
                return;
            }

            // Handle CSIR sub-flows
            if (buttonId.startsWith('csir-')) {
                const response = responses[buttonId];
                if (response) {
                    addMessage(response);
                }
                
                if (buttonId === 'csir-exam-details' || 
                    buttonId === 'csir-course-details' || 
                    buttonId === 'csir-fees' || 
                    buttonId === 'csir-books' || 
                    buttonId === 'csir-test-series' || 
                    buttonId === 'csir-free-materials' || 
                    buttonId === 'csir-talk-expert') {
                    return;
                }
            }

            // Handle TNSET sub-flows
            if (buttonId.startsWith('tnset-')) {
                const response = responses[buttonId];
                if (response) {
                    addMessage(response);
                }
                
                if (buttonId === 'tnset-exam-details' || 
                    buttonId === 'tnset-course-details' || 
                    buttonId === 'tnset-fees' || 
                    buttonId === 'tnset-books' || 
                    buttonId === 'tnset-test-series' || 
                    buttonId === 'tnset-free-materials' || 
                    buttonId === 'tnset-talk-expert') {
                    return;
                }
            }

            // Handle TNTET sub-flows
            if (buttonId.startsWith('tntet-')) {
                const response = responses[buttonId];
                if (response) {
                    addMessage(response);
                }
                
                if (buttonId === 'tntet-exam-details' || 
                    buttonId === 'tntet-course-details' || 
                    buttonId === 'tntet-fees' || 
                    buttonId === 'tntet-books' || 
                    buttonId === 'tntet-test-series' || 
                    buttonId === 'tntet-free-materials' || 
                    buttonId === 'tntet-talk-expert') {
                    return;
                }
            }

            // Handle College TRB sub-flows
            if (buttonId.startsWith('college-trb-')) {
                const response = responses[buttonId];
                if (response) {
                    addMessage(response);
                }
                
                if (buttonId === 'college-trb-exam-details' || 
                    buttonId === 'college-trb-course-details' || 
                    buttonId === 'college-trb-fees' || 
                    buttonId === 'college-trb-books' || 
                    buttonId === 'college-trb-test-series' || 
                    buttonId === 'college-trb-free-materials' || 
                    buttonId === 'college-trb-talk-expert') {
                    return;
                }
            }

            // Handle Polytechnic TRB sub-flows
            if (buttonId.startsWith('poly-trb-')) {
                const response = responses[buttonId];
                if (response) {
                    addMessage(response);
                }
                
                if (buttonId === 'poly-trb-exam-details' || 
                    buttonId === 'poly-trb-course-details' || 
                    buttonId === 'poly-trb-fees' || 
                    buttonId === 'poly-trb-books' || 
                    buttonId === 'poly-trb-test-series' || 
                    buttonId === 'poly-trb-free-materials' || 
                    buttonId === 'poly-trb-talk-expert') {
                    return;
                }
            }

            const response = responses[buttonId];
            if (response) {
                addMessage(response);
            }

            // Navigate to appropriate flow
            if (buttonId === 'ugc-net') {
                currentExamType = 'ugc-net';
                currentFlow = 'ugc-net-subjects';
                addButtonMessage('ugc-net-subjects');
            } else if (['new-student', 'current-batch', 'careers'].includes(buttonId)) {
                currentFlow = buttonId;
                addButtonMessage(buttonId);
            }
        }

        function goBack() {
            if (manualSubjectInputMode) {
                manualSubjectInputMode = false;
                currentFlow = 'ugc-net-subjects';
                addButtonMessage('ugc-net-subjects');
                return;
            }

            if (navigationHistory.length > 0) {
                currentFlow = navigationHistory.pop();
                addButtonMessage(currentFlow);
            }
        }

        function toggleWidget() {
            chatbotWidget.classList.toggle('active');
            chatbotToggle.innerHTML = chatbotWidget.classList.contains('active') ? '✖' : '🤖';
        }

        function closeWidget() {
            chatbotWidget.classList.remove('active');
            chatbotToggle.innerHTML = '🤖';
        }

        function sendMessage() {
            const message = widgetInput.value.trim();
            if (!message) return;

            addMessage(message, true);
            widgetInput.value = '';

            if (manualSubjectInputMode) {
                // Save the manual subject to Google Sheets
                saveSubjectToSheet(message);
                
                // Continue with the flow
                currentSubject = message;
                currentFlow = 'subject-options';
                addButtonMessage('subject-options');
                manualSubjectInputMode = false;
                return;
            }

            // Check for special commands
            if (message.toLowerCase() === 'do not show faqs') {
                showFAQs = false;
                addMessage("I'll only provide direct answers from now on. How can I help you?");
                return;
            }

            // Prepare the request to the backend
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    addMessage("Sorry, I encountered an error. Please try again later.");
                } else {
                    addMessage(data.response);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage("Sorry, I'm having trouble connecting. Please try again later.");
            });
        }

        function saveSubjectToSheet(subject) {
            fetch('/save_subject', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    subject: subject,
                    examType: currentExamType,
                    timestamp: new Date().toISOString()
                })
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Failed to save subject:', data.error);
                }
            })
            .catch(error => {
                console.error('Error saving subject:', error);
            });
        }

        widgetInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        // Initialize with welcome flow
        addButtonMessage('welcome');
    </script>
</body>
</html>
'''

class ProfessorAcademyChatbot:
    def __init__(self):
        # Gemini API configuration
        self.gemini_api_key = "AIzaSyAjdjYXpferSTiKGLsJazZ6XKPGBiPg7y4"
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        # Google Sheets configuration
        self.setup_google_sheets()
        
        # System prompt for the chatbot
        self.system_prompt = """You are a helpful AI assistant for Professor Academy, a Tamil Nadu-based coaching institute founded in 2016.

IMPORTANT INFORMATION ABOUT PROFESSOR ACADEMY:
- Founded in 2016 by experienced educators
- Specializes in UGC NET, CSIR NET, TRB, TN SET, and TN TET coaching
- Subjects offered: Commerce, Computer Science, English, Economics, Education, Management, Mathematics, and Life Science
- Provides both live and recorded online classes
- Offers study materials, mock tests, and personalized mentorship
- Contact: +91 7070701005
- Website: professoracademy.com

You can answer both Professor Academy specific questions and general knowledge questions. For Professor Academy queries, use the provided knowledge base and context. Keep responses concise and helpful.
"""

        # Load datasets
        self.load_all_datasets()
        print("✅ Gemini chatbot initialized successfully!")
        
    def setup_google_sheets(self):
        """Set up Google Sheets API connection"""
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # Path to your Google Sheets API credentials JSON file
            creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
            self.gc = gspread.authorize(creds)
            
            # Open the Google Sheet by name
            self.sheet = self.gc.open("Professor Academy Subjects").sheet1
            print("✅ Google Sheets connection established")
        except Exception as e:
            print(f"Error setting up Google Sheets: {e}")
            self.sheet = None
    
    def save_subject_to_sheet(self, subject_data):
        """Save subject data to Google Sheet"""
        try:
            if not self.sheet:
                return {'success': False, 'error': 'Google Sheets not initialized'}
                
            # Append the data to the sheet
            row = [
                subject_data.get('subject', ''),
                subject_data.get('examType', ''),
                subject_data.get('timestamp', '')
            ]
            self.sheet.append_row(row)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def load_all_datasets(self):
        """Load all available datasets"""
        self.datasets = {}
        
        # Try to load main dataset
        try:
            if os.path.exists('dataset.json'):
                with open('dataset.json', 'r', encoding='utf-8') as f:
                    self.datasets['main'] = json.load(f)
                print("✅ Main dataset loaded")
            else:
                self.datasets['main'] = {"qa_pairs": []}
                print("📝 Created new main dataset")
        except Exception as e:
            print(f"Error loading main dataset: {e}")
            self.datasets['main'] = {"qa_pairs": []}
            
        # Try to load knowledge base
        try:
            if os.path.exists('knowledge_base.json'):
                with open('knowledge_base.json', 'r', encoding='utf-8') as f:
                    self.datasets['knowledge_base'] = json.load(f)
                print("✅ Knowledge base loaded")
            else:
                self.datasets['knowledge_base'] = self.get_default_knowledge_base()
                print("📝 Created default knowledge base")
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            self.datasets['knowledge_base'] = self.get_default_knowledge_base()
    
    def get_default_knowledge_base(self):
        """Default knowledge base with Professor Academy information"""
        return {
            "courses": [
                {
                    "question": "What courses does Professor Academy offer?",
                    "answer": "Professor Academy offers comprehensive coaching for UGC NET, CSIR NET, TRB, TN SET, and TN TET exams. Our subjects include Commerce, Computer Science, English, Economics, Education, Management, Mathematics, and Life Science."
                },
                {
                    "question": "What is the fee structure?",
                    "answer": "Our course fees are very affordable starting from ₹4,000 with special offers. The fee includes live classes, recorded lectures, study materials, and mock tests. Contact +91 7070701005 for detailed fee structure."
                }
            ],
            "admission": [
                {
                    "question": "How to enroll in courses?",
                    "answer": "You can enroll by visiting professoracademy.com, selecting your subject, completing online registration, and making payment. You'll receive login credentials via email after successful payment."
                }
            ],
            "support": [
                {
                    "question": "How to get technical support?",
                    "answer": "For technical support, please call +91 7070701005 or visit our website professoracademy.com. We provide 24/7 support for all technical issues."
                }
            ]
        }
    
    def save_dataset(self, dataset_name, data):
        """Save dataset to file"""
        try:
            filename = f"{dataset_name}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.datasets[dataset_name] = data
            return True
        except Exception as e:
            print(f"Error saving {dataset_name}: {e}")
            return False
    
    def add_qa_pair(self, question, answer, dataset_name='main'):
        """Add a new Q&A pair to the specified dataset"""
        if dataset_name not in self.datasets:
            self.datasets[dataset_name] = {"qa_pairs": []}
        
        if "qa_pairs" not in self.datasets[dataset_name]:
            self.datasets[dataset_name]["qa_pairs"] = []
            
        self.datasets[dataset_name]["qa_pairs"].append({
            "question": question,
            "answer": answer
        })
        
        return self.save_dataset(dataset_name, self.datasets[dataset_name])
    
    def get_context_from_datasets(self):
        """Build context from all loaded datasets"""
        context_parts = []
        
        for dataset_name, dataset in self.datasets.items():
            if dataset_name == 'knowledge_base':
                for category, items in dataset.items():
                    for item in items:
                        context_parts.append(f"Q: {item.get('question', item.get('prompt', ''))}")
                        context_parts.append(f"A: {item.get('answer', item.get('response', ''))}")
            elif 'qa_pairs' in dataset:
                for qa in dataset['qa_pairs']:
                    context_parts.append(f"Q: {qa.get('question', qa.get('prompt', ''))}")
                    context_parts.append(f"A: {qa.get('answer', qa.get('response', ''))}")
        
        return "\n".join(context_parts)
    
    def generate_with_gemini(self, user_input):
        """Generate response using Gemini API"""
        try:
            context = self.get_context_from_datasets()
            
            full_prompt = f"""{self.system_prompt}

CONTEXT FROM KNOWLEDGE BASE:
{context}

User Question: {user_input}

Please provide a helpful response based on the context above. If it's about Professor Academy, use the knowledge base. For general questions, use your general knowledge."""

            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }
            
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0].get('content', {})
                    parts = content.get('parts', [])
                    if parts:
                        return parts[0].get('text', 'Sorry, I could not generate a response.')
            
            return "I'm sorry, I encountered an issue. Please try again or contact +91 7070701005 for support."
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "I'm sorry, I'm experiencing technical difficulties. Please contact +91 7070701005 for immediate assistance."
    
    def generate_response(self, user_input):
        """Main method to generate response"""
        return self.generate_with_gemini(user_input)

def create_app():
    app = Flask(__name__)
    chatbot = ProfessorAcademyChatbot()

    @app.route('/')
    def home():
        return HTML_TEMPLATE

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
        """Save subject data to Google Sheet"""
        try:
            subject_data = request.json
            if not subject_data or not subject_data.get('subject'):
                return jsonify({'success': False, 'error': 'Subject is required'})
            
            result = chatbot.save_subject_to_sheet(subject_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/add_qa', methods=['POST'])
    def add_qa():
        """Add new Q&A pair to dataset"""
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
        """Update entire dataset"""
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

    return app

def run_server():
    app = create_app()
    
    def shutdown_handler(signum, frame):
        print("\n🛑 Server shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    try:
        print("🚀 Starting Professor Academy Chatbot server...")
        print(f"🌐 Running on http://0.0.0.0:5000")
        
        # Production-ready server configuration
        run_simple(
            hostname='0.0.0.0',
            port=5000,
            application=app,
            threaded=True,
            processes=1,
            use_reloader=False,
            use_debugger=False
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_server()
