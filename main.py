from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS  
import sqlite3
import os

app = Flask(__name__, template_folder='.')
app.secret_key = "diu_secret_secure_key_2026" 
CORS(app)  

def init_db():
    conn = sqlite3.connect('campus.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            dept TEXT DEFAULT 'Computer Science & Engineering',
            campus TEXT DEFAULT 'Daffodil Smart City, Ashulia'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- DIU এর অল-ইন-ওয়ান এক্সপ্যান্ডেড ডাটাবেজ (লোকেশন + ইমেজ) ---
LANDMARKS_DATABASE = {
    # একাডেমিক ও প্রশাসনিক ভবন
    'main building': {
        'name': 'Main Academic Building', 'lat': 23.9184, 'lng': 90.2562, 
        'desc': 'Central structural hub for engineering and business faculties.',
        'img': 'https://images.unsplash.com/photo-1562774053-701939374585?w=500'
    },
    'innovation tower': {
        'name': 'DIU Innovation Tower', 'lat': 23.9175, 'lng': 90.2550, 
        'desc': 'IT Labs, Startup Cells, and high-tech CSE research centers.',
        'img': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=500'
    },
    'knowledge tower': {
        'name': 'Knowledge Tower', 'lat': 23.9180, 'lng': 90.2558, 
        'desc': 'Academic building mainly dedicated to Humanities, English, and Law departments.',
        'img': 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=500'
    },
    'admin': {
        'name': 'DIU Administrative Building', 'lat': 23.9170, 'lng': 90.2565, 
        'desc': 'The corporate heart of DIU housing admission offices, accounts, and registrar.',
        'img': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=500'
    },
    
    # লাইব্রেরি ও অডিটোরিয়াম
    'library': {
        'name': 'DIU Central Library', 'lat': 23.9190, 'lng': 90.2570, 
        'desc': 'Huge multi-story digital and physical archive for bookworms.',
        'img': 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=500'
    },
    'hall of fame': {
        'name': 'DIU Hall of Fame Auditorium', 'lat': 23.9168, 'lng': 90.2542, 
        'desc': 'The grand auditorium for hosting national/international tech fests and orientation.',
        'img': 'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=500'
    },

    # খেলার মাঠ ও আড্ডা জোন
    'playground': {
        'name': 'DIU Sports Green Playground', 'lat': 23.9201, 'lng': 90.2555, 
        'desc': 'Premium green turf football field and cricket ground.',
        'img': 'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=500'
    },
    'golf course': {
        'name': 'DIU Golf Course', 'lat': 23.9215, 'lng': 90.2540, 
        'desc': 'Beautiful lush green golf range inside the premium smart campus zone.',
        'img': 'https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=500'
    },
    'tong corner': {
        'name': 'DIU Tong Corner (Food Court)', 'lat': 23.9188, 'lng': 90.2548, 
        'desc': 'The official favorite hangout spot for tea, snacks, and student assignments.',
        'img': 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=500'
    },

    # রেসিডেন্সিয়াল হল (Hostels)
    'yunus khan hall': {
        'name': 'Professor Dr. Yunus Khan Male Hall', 'lat': 23.9220, 'lng': 90.2568, 
        'desc': 'Main residential hostel complex equipped with modern amenities for male students.',
        'img': 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500'
    },
    'rokeya hall': {
        'name': 'Begum Rokeya Female Hall', 'lat': 23.9225, 'lng': 90.2580, 
        'desc': 'Highly secure and premium residential facility for female students.',
        'img': 'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?w=500'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register_endpoint():
    try:
        data = request.get_json(force=True) or {}
        student_id = str(data.get('student_id', '')).strip()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = str(data.get('password', '')).strip()

        if not student_id or not name or not email or not password:
            return jsonify({'success': False, 'message': 'Please fill in all fields correctly!'})

        conn = sqlite3.connect('campus.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (student_id, name, email, password) VALUES (?, ?, ?, ?)', 
                       (student_id, name, email, password))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Registration successful!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Account already exists!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/login', methods=['POST'])
def login_endpoint():
    try:
        data = request.get_json(force=True) or {}
        student_id = str(data.get('student_id', '')).strip()
        password = str(data.get('password', '')).strip()

        conn = sqlite3.connect('campus.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE student_id = ? AND password = ?', (student_id, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_data = dict(user)
            del user_data['password'] 
            return jsonify({'success': True, 'user': user_data})
        else:
            return jsonify({'success': False, 'message': 'Invalid Credentials!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/profile/update', methods=['POST'])
def update_profile_endpoint():
    try:
        data = request.get_json(force=True) or {}
        student_id = str(data.get('student_id', '')).strip()
        name = data.get('name', '').strip()
        dept = data.get('dept', '').strip()
        campus = data.get('campus', '').strip()

        conn = sqlite3.connect('campus.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET name = ?, dept = ?, campus = ? WHERE student_id = ?', 
                       (name, dept, campus, student_id))
        conn.commit()
        
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE student_id = ?', (student_id,))
        user = cursor.fetchone()
        conn.close()

        return jsonify({'success': True, 'message': 'Profile updated!', 'user': dict(user)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/chatbot', methods=['POST'])
def chatbot_endpoint():
    data = request.get_json(force=True) or {}
    user_message = data.get('message', '').lower().strip()
    
    matched_key = None
    for key in LANDMARKS_DATABASE:
        if key in user_message:
            matched_key = key
            break

    if matched_key:
        landmark = LANDMARKS_DATABASE[matched_key]
        return jsonify({
            'reply': f"Sure! Plotting **{landmark['name']}** on the map. {landmark['desc']}",
            'location': {
                'name': landmark['name'], 
                'lat': landmark['lat'], 
                'lng': landmark['lng'],
                'img': landmark['img'] # ইমেজ ইউআরএল ফ্রন্টএন্ডে পাঠানো হচ্ছে
            }
        })
    else:
        return jsonify({
            'reply': "Sorry, I couldn't find that specific spot. Try searching for 'Main Building', 'Innovation Tower', 'Knowledge Tower', 'Library', 'Admin', 'Golf Course', 'Yunus Khan Hall', or 'Tong Corner'.",
            'location': None
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)