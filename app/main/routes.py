from flask import Blueprint, render_template, session, redirect, url_for, flash
from ..learning.routes import curriculum
from ..models.models import User, QuizAttempt, UserProgress

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/materi')
def materi():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(username=session['username']).first()
    
    completed_progress = UserProgress.query.filter_by(user_id=user.id, is_completed=True).all()
    completed_modules = {progress.module_name for progress in completed_progress}

    return render_template('materi.html', completed_modules=completed_modules)

@main.route('/pencapaian')
def pencapaian():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    
    quiz_attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.timestamp.desc()).all()

    return render_template('pencapaian.html', quiz_history=quiz_attempts)

@main.route('/templates/materi/<path:filename>')
def serve_materi_file(filename):
    return render_template(f'materi/{filename}')

@main.route('/sertifikat')
def sertifikat():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    
    # 1. Cek apakah semua modul sudah selesai
    completed_progress = UserProgress.query.filter_by(user_id=user.id, is_completed=True).count()
    total_modules = len(curriculum.keys()) # Hitung total modul yang ada

    if completed_progress < total_modules:
        # Jika belum selesai semua, kembalikan ke halaman materi
        flash("Anda harus menyelesaikan semua materi terlebih dahulu untuk melihat sertifikat.", "error")
        return redirect(url_for('main.materi'))

    # 2. Ambil semua skor kuis
    attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
    scores = {attempt.module_name: attempt.score for attempt in attempts}
    
    # 3. Ambil tanggal penyelesaian (dari kuis terakhir)
    last_attempt = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.timestamp.desc()).first()
    completion_date = last_attempt.timestamp

    return render_template('sertifikat.html', 
                             user_name=user.username, 
                             scores=scores, 
                             completion_date=completion_date)
