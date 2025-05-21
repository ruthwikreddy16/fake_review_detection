# download_pdf.py
from flask import Blueprint, session, redirect, send_file
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

download_pdf_bp = Blueprint('download_pdf', __name__)

@download_pdf_bp.route('/download_pdf')
def download_pdf():
    if 'username' not in session:
        return redirect('/')  # redirect to login or home if not logged in

    username = session['username']

    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT h.review, h.prediction 
        FROM history h
        JOIN users u ON h.user_id = u.id
        WHERE u.username = ?
    """, (username,)).fetchall()
    conn.close()

    if not rows:
        return "No history found for user", 404

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica", 12)
    y = height - 40
    p.drawString(30, y, f"Prediction History for: {username}")
    y -= 30

    for i, row in enumerate(rows, 1):
        review = row['review'][:100] + "..." if len(row['review']) > 100 else row['review']
        text = f"{i}. Review: {review} | Prediction: {row['prediction']}"
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = height - 40
        p.drawString(30, y, text)
        y -= 20

    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name=f"{username}_review_history.pdf",
                     mimetype='application/pdf')
