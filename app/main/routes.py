from flask import Blueprint, render_template, session, redirect, url_for
from ..models.models import User, QuizAttempt, UserProgress

# Membuat Blueprint 'main'
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

# app/main/routes.py

@main.route('/materi')
def materi():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(username=session['username']).first()
    
    # KEMBALIKAN KE LOGIKA INI: Ambil hanya modul yang sudah selesai
    completed_progress = UserProgress.query.filter_by(user_id=user.id, is_completed=True).all()
    completed_modules = {progress.module_name for progress in completed_progress}

    return render_template('materi.html', completed_modules=completed_modules)

@main.route('/pencapaian')
def pencapaian():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    
    # Ganti query dari QuizResult menjadi QuizAttempt
    quiz_attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.timestamp.desc()).all()

    # Kirim data 'quiz_attempts' ke template
    return render_template('pencapaian.html', quiz_history=quiz_attempts)

# --- [TAMBAHKAN BLOK KODE INI] ---
# Rute baru untuk menyajikan file HTML statis dari folder materi
@main.route('/templates/materi/<path:filename>')
def serve_materi_file(filename):
    return render_template(f'materi/{filename}')