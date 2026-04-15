from flask import Flask, render_template, request, send_file
from database import get_db_connection
import matplotlib.pyplot as plt
import io
import base64
from matplotlib import rcParams
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
import datetime
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
# Configure matplotlib
plt.rcParams['font.family'] = 'DejaVu Sans'
#rcParams['font.family'] = 'Arial'
rcParams['font.size'] = 10

app = Flask(__name__)

def get_menu():
    """Returns the navigation menu HTML"""
    return '''
    <div class="menu">
        <a href="/">🏠 Home</a>
        <a href="/students">👨‍🎓 Students</a>
        <a href="/search">🔍 Search</a>
        <a href="/add_student">➕ Add Student</a>
        <a href="/enter_marks">📝 Enter Marks</a>
        <a href="/analysis">📊 Analysis</a>
    </div>
    '''

def get_instructions():
    """Returns instructions for each page"""
    return '''
    <div style="margin: 30px 0;">
        <h3 style="color: #333; margin-bottom: 20px; font-size: 22px;">📋 How to Use This System:</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.3s;">
                <h4 style="margin-bottom: 15px; font-size: 18px;">1️⃣ Add Students</h4>
                <p style="font-size: 14px; line-height: 1.6;">Start by registering all students using the "➕ Add Student" page. Enter their roll number, name, email, and phone.</p>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.3s;">
                <h4 style="margin-bottom: 15px; font-size: 18px;">2️⃣ Enter Marks</h4>
                <p style="font-size: 14px; line-height: 1.6;">Use the "📝 Enter Marks" page to add marks for each student in all 6 AIDS subjects (0-100).</p>
            </div>
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.3s;">
                <h4 style="margin-bottom: 15px; font-size: 18px;">3️⃣ View Results</h4>
                <p style="font-size: 14px; line-height: 1.6;">Check individual student results with grades, percentages, and detailed performance analytics.</p>
            </div>
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.3s;">
                <h4 style="margin-bottom: 15px; font-size: 18px;">4️⃣ Download PDF</h4>
                <p style="font-size: 14px; line-height: 1.6;">Export professional PDF result cards for any student with all marks and grades included.</p>
            </div>
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.3s;">
                <h4 style="margin-bottom: 15px; font-size: 18px;">5️⃣ Analyze Data</h4>
                <p style="font-size: 14px; line-height: 1.6;">Visit the "📊 Analysis" dashboard to see charts, statistics, and performance insights.</p>
            </div>
            <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333; padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.3s;">
                <h4 style="margin-bottom: 15px; font-size: 18px;">6️⃣ Search Students</h4>
                <p style="font-size: 14px; line-height: 1.6;">Use the "🔍 Search" feature to quickly find any student by name or roll number.</p>
            </div>
        </div>
        <div style="background: #e8f4f8; padding: 20px; border-radius: 12px; margin-top: 25px; border-left: 5px solid #2196F3; border-radius: 8px;">
            <p style="color: #333; margin: 0;"><strong>💡 Tip:</strong> All data is stored securely in MySQL database. You can enter and update marks anytime!</p>
        </div>
    </div>
    '''

def get_subjects_info():
    """Returns B.E AIDS subjects information"""
    return '''
    <div style="margin: 30px 0;">
        <h3 style="color: #333; margin-bottom: 20px; font-size: 22px;">📚 B.E (Artificial Intelligence & Data Science) 4th Semester - Subjects</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div style="background: white; border: 2px solid #667eea; padding: 25px; border-radius: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); transition: all 0.3s;">
                <h4 style="color: #667eea; margin-bottom: 10px; font-size: 16px;">🤖 AIDS2401</h4>
                <p style="color: #555; font-size: 14px; line-height: 1.6;">Machine Learning & Algorithms</p>
                <p style="color: #999; font-size: 12px; margin-top: 10px;">Core ML concepts and practical algorithms</p>
            </div>
            <div style="background: white; border: 2px solid #764ba2; padding: 25px; border-radius: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); transition: all 0.3s;">
                <h4 style="color: #764ba2; margin-bottom: 10px; font-size: 16px;">⚙️ AIDS2402</h4>
                <p style="color: #555; font-size: 14px; line-height: 1.6;">Data Engineering & ETL</p>
                <p style="color: #999; font-size: 12px; margin-top: 10px;">Pipeline design and data processing</p>
            </div>
            <div style="background: white; border: 2px solid #f093fb; padding: 25px; border-radius: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); transition: all 0.3s;">
                <h4 style="color: #f093fb; margin-bottom: 10px; font-size: 16px;">📊 AIDS2403</h4>
                <p style="color: #555; font-size: 14px; line-height: 1.6;">Advanced Statistics for AI</p>
                <p style="color: #999; font-size: 12px; margin-top: 10px;">Statistical methods and probability</p>
            </div>
            <div style="background: white; border: 2px solid #f5576c; padding: 25px; border-radius: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); transition: all 0.3s;">
                <h4 style="color: #f5576c; margin-bottom: 10px; font-size: 16px;">🧠 AIDS2404</h4>
                <p style="color: #555; font-size: 14px; line-height: 1.6;">Neural Networks & Deep Learning</p>
                <p style="color: #999; font-size: 12px; margin-top: 10px;">Deep learning architectures and frameworks</p>
            </div>
            <div style="background: white; border: 2px solid #4facfe; padding: 25px; border-radius: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); transition: all 0.3s;">
                <h4 style="color: #4facfe; margin-bottom: 10px; font-size: 16px;">🔍 AIDS2405</h4>
                <p style="color: #555; font-size: 14px; line-height: 1.6;">Data Mining & Knowledge Discovery</p>
                <p style="color: #999; font-size: 12px; margin-top: 10px;">Pattern discovery and knowledge extraction</p>
            </div>
            <div style="background: white; border: 2px solid #00f2fe; padding: 25px; border-radius: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); transition: all 0.3s;">
                <h4 style="color: #00f2fe; margin-bottom: 10px; font-size: 16px;">💬 AIDS2406</h4>
                <p style="color: #555; font-size: 14px; line-height: 1.6;">Natural Language Processing</p>
                <p style="color: #999; font-size: 12px; margin-top: 10px;">Text analysis and language understanding</p>
            </div>
        </div>
        <div style="background: linear-gradient(135deg, #fff5e1 0%, #ffe0b2 100%); padding: 25px; border-radius: 12px; margin-top: 25px; border-left: 5px solid #ff9800;">
            <h4 style="color: #333; margin-bottom: 10px;">ℹ️ Program Information</h4>
            <p style="color: #555; margin: 5px 0; font-size: 14px;"><strong>Semester:</strong> 4th Semester (B.E AIDS)</p>
            <p style="color: #555; margin: 5px 0; font-size: 14px;"><strong>Total Subjects:</strong> 6 | <strong>Max Marks per Subject:</strong> 100</p>
            <p style="color: #555; margin: 5px 0; font-size: 14px;"><strong>Passing Grade:</strong> 40% | <strong>Outstanding Grade:</strong> 90%</p>
        </div>
    </div>
    '''

def create_charts():
    """Generate charts for analysis page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Chart 1: Subject-wise Average Marks
    cursor.execute('''
        SELECT s.subject_name, AVG(m.marks) as avg_marks
        FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        GROUP BY s.id
        ORDER BY avg_marks DESC
    ''')
    subject_data = cursor.fetchall()
    
    subjects = [row[0][:15] + '...' if len(row[0]) > 15 else row[0] for row in subject_data]
    averages = [row[1] for row in subject_data]
    
    # Create bar chart
    plt.figure(figsize=(10, 5))
    bars = plt.bar(subjects, averages, color=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'])
    plt.title('📚 Subject-wise Average Marks', fontsize=14, fontweight='bold')
    plt.xlabel('Subjects')
    plt.ylabel('Average Marks')
    plt.xticks(rotation=15)
    plt.ylim(0, 100)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    # Save to base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    chart1_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    # Chart 2: Grade Distribution
    cursor.execute('''
        SELECT 
            CASE 
                WHEN marks >= 90 THEN 'O'
                WHEN marks >= 80 THEN 'A+'
                WHEN marks >= 70 THEN 'A'
                WHEN marks >= 60 THEN 'B+'
                WHEN marks >= 50 THEN 'B'
                WHEN marks >= 40 THEN 'P'
                ELSE 'F'
            END as grade,
            COUNT(*) as count
        FROM marks
        GROUP BY grade
        ORDER BY 
            CASE grade
                WHEN 'O' THEN 1
                WHEN 'A+' THEN 2
                WHEN 'A' THEN 3
                WHEN 'B+' THEN 4
                WHEN 'B' THEN 5
                WHEN 'P' THEN 6
                ELSE 7
            END
    ''')
    grade_data = cursor.fetchall()
    
    grades = [row[0] for row in grade_data]
    counts = [row[1] for row in grade_data]
    colors_list = ['#FFD700', '#4CAF50', '#2196F3', '#9C27B0', '#FF9800', '#795548', '#F44336']
    
    # Create pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(counts, labels=grades, colors=colors_list, autopct='%1.1f%%', startangle=90)
    plt.title('📊 Grade Distribution', fontsize=14, fontweight='bold')
    plt.axis('equal')
    
    # Save to base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    chart2_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    conn.close()
    
    return chart1_url, chart2_url

def generate_pdf(student_id):
    """Generate PDF result card for a student"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student data
    cursor.execute('SELECT roll_no, name, semester FROM students WHERE id=%s', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return None
    
    # Get marks data
    cursor.execute('''
        SELECT s.subject_code, s.subject_name, m.marks
        FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        WHERE m.student_id = %s
        ORDER BY s.subject_code
    ''', (student_id,))
    
    marks = cursor.fetchall()
    conn.close()
    
    if not marks:
        return None
    
    # Calculate total and percentage
    total_marks = sum([m[2] for m in marks])
    percentage = (total_marks / (len(marks) * 100)) * 100
    
    # Determine grade
    if percentage >= 90:
        grade = 'O (Outstanding)'
        grade_color = colors.gold
    elif percentage >= 80:
        grade = 'A+ (Excellent)'
        grade_color = colors.green
    elif percentage >= 70:
        grade = 'A (Very Good)'
        grade_color = colors.blue
    elif percentage >= 60:
        grade = 'B+ (Good)'
        grade_color = colors.purple
    elif percentage >= 50:
        grade = 'B (Above Average)'
        grade_color = colors.orange
    elif percentage >= 45:
        grade = 'C (Average)'
        grade_color = colors.brown
    elif percentage >= 40:
        grade = 'P (Pass)'
        grade_color = colors.grey
    else:
        grade = 'F (Fail)'
        grade_color = colors.red
    
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Build PDF content
    story = []
    
    # Title
    story.append(Paragraph("B.E (Artificial Intelligence & Data Science) 4th Semester - Result Card", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Student Information
    story.append(Paragraph(f"<b>Student Name:</b> {student[1]}", normal_style))
    story.append(Paragraph(f"<b>Roll Number:</b> {student[0]}", normal_style))
    story.append(Paragraph(f"<b>Semester:</b> {student[2]}", normal_style))
    story.append(Paragraph(f"<b>Date Generated:</b> {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Marks Table
    story.append(Paragraph("<b>Subject-wise Marks:</b>", header_style))
    
    # Table data
    table_data = [['Subject Code', 'Subject Name', 'Marks Obtained', 'Max Marks']]
    for subject_code, subject_name, mark in marks:
        table_data.append([subject_code, subject_name, str(mark), '100'])
    
    # Create table
    marks_table = Table(table_data, colWidths=[1.5*inch, 3*inch, 1.5*inch, 1.2*inch])
    marks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
    ]))
    
    story.append(marks_table)
    story.append(Spacer(1, 30))
    
    # Result Summary
    story.append(Paragraph("<b>Result Summary:</b>", header_style))
    
    summary_data = [
        ['Total Subjects', f'{len(marks)} out of 6'],
        ['Total Marks Obtained', f'{total_marks} / {len(marks) * 100}'],
        ['Percentage', f'{percentage:.2f}%'],
        ['Grade', grade],
        ['Status', 'PASS' if percentage >= 40 else 'FAIL']
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Footer
    story.append(Paragraph("<i>This is a computer-generated result card. No signature required.</i>", 
                          ParagraphStyle('Footer', parent=styles['Italic'], fontSize=9, textColor=colors.grey)))
    story.append(Paragraph("<i>©  B.E (Artificial Intelligence & Data Science) Department</i>", 
                          ParagraphStyle('Footer', parent=styles['Italic'], fontSize=9, textColor=colors.grey)))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch overall statistics
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT s.id) as total_students,
            COUNT(m.id) as total_marks_entries,
            AVG(m.marks) as avg_marks,
            MAX(m.marks) as highest_mark,
            MIN(m.marks) as lowest_mark,
            SUM(CASE WHEN m.marks >= 40 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(m.id), 0) as pass_percentage
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
    ''')
    overall_stats = cursor.fetchone()
    conn.close()
    
    total_students = overall_stats[0] or 0
    total_marks_entries = overall_stats[1] or 0
    avg_marks = overall_stats[2] or 0
    pass_percentage = overall_stats[5] or 0
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>B.E Result System</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 20px; 
                border-radius: 10px; 
                text-align: center;
            }}
            .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
            .header p {{ font-size: 16px; }}
            .menu {{ 
                margin: 20px 0; 
                display: flex; 
                flex-wrap: wrap; 
                gap: 10px;
                justify-content: center;
            }}
            .menu a {{ 
                padding: 12px 20px; 
                background: #4CAF50; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
                font-weight: bold;
                transition: all 0.3s;
            }}
            .menu a:hover {{ background: #45a049; transform: translateY(-2px); }}
            .container {{
                background: white; 
                padding: 25px; 
                border-radius: 10px; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                max-width: 1200px;
                margin: 0 auto;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 25px 0;
            }}
            .pdf-feature {{
                background: #ffeaa7;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 5px solid #e74c3c;
            }}
            h2 {{ 
                color: #333; 
                margin: 30px 0 20px 0;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }}
            @media (max-width: 768px) {{
                body {{ padding: 10px; }}
                .header {{ padding: 15px; }}
                .header h1 {{ font-size: 24px; }}
                .container {{ padding: 15px; }}
                .stats-grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎓 B.E Result Management System</h1>
            <p>Artificial Intelligence & Data Science 4th Semester</p>
        </div>
        
        {get_menu()}
        
        <div class="container">
            <div class="pdf-feature">
                <h3>📄 Features & Updates</h3>
                <p>Professional result management with PDF export, data analysis, and comprehensive statistics!</p>
            </div>
            
            <h2>📈 Overall Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>👨‍🎓 Total Students</h3>
                    <p style="font-size: 36px; margin: 10px 0;">{total_students}</p>
                </div>
                <div class="stat-card">
                    <h3>📝 Total Marks Entries</h3>
                    <p style="font-size: 36px; margin: 10px 0;">{total_marks_entries}</p>
                </div>
                <div class="stat-card">
                    <h3>📊 Average Marks</h3>
                    <p style="font-size: 36px; margin: 10px 0;">{avg_marks:.1f}</p>
                </div>
                <div class="stat-card">
                    <h3>🏆 Pass Percentage</h3>
                    <p style="font-size: 36px; margin: 10px 0;">{pass_percentage:.1f}%</p>
                </div>
            </div>
            
            {get_subjects_info()}
            
            {get_instructions()}
            
            <h2>🚀 Quick Links</h2>
            <div class="stats-grid">
                <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <h4>👨‍🎓 View Students</h4>
                    <p style="margin-top: 10px;"><a href="/students" style="color: white; text-decoration: none; font-weight: bold;">→ Go to Students</a></p>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <h4>📝 Enter Marks</h4>
                    <p style="margin-top: 10px;"><a href="/enter_marks" style="color: white; text-decoration: none; font-weight: bold;">→ Go to Marks</a></p>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                    <h4>🔍 Search Students</h4>
                    <p style="margin-top: 10px;"><a href="/search" style="color: white; text-decoration: none; font-weight: bold;">→ Go to Search</a></p>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                    <h4>📊 Data Analysis</h4>
                    <p style="margin-top: 10px;"><a href="/analysis" style="color: white; text-decoration: none; font-weight: bold;">→ Go to Analysis</a></p>
                </div>
            </div>
            
            <br><br>
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #666; font-size: 14px;">
            <hr>
            <p>B.E AIDS Result Management System • Artificial Intelligence & Data Science</p>
            <p>📊 Comprehensive Results Platform</p>
        </div>
    </body>
    </html>
    '''

@app.route('/students')
def view_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    
    student_rows = ""
    for student in students:
        student_rows += f"""
        <tr>
            <td>{student[0]}</td>
            <td>{student[1]}</td>
            <td>{student[2]}</td>
            <td>{student[3]}</td>
            <td>
                <a href='/view_result/{student[0]}' style='color: #2196F3; margin-right: 10px;'>👁️ View Result</a>
                <a href='/download_pdf/{student[0]}' style='color: #e74c3c;'>📄 Download PDF</a>
            </td>
        </tr>
        """
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Students List</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 20px; 
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ font-size: 16px; }}
        .menu {{
            margin: 15px 0; 
            display: flex; 
            flex-wrap: wrap; 
            gap: 10px;
            justify-content: center;
        }}
        .menu a {{
            padding: 10px 15px; 
            background: #4CAF50; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
            font-weight: bold;
            transition: all 0.3s;
            font-size: 14px;
        }}
        .menu a:hover {{ background: #45a049; transform: translateY(-2px); }}
        .container {{
            background: white; 
            padding: 25px; 
            border-radius: 10px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            max-width: 1000px;
            margin: 0 auto;
        }}
        table {{width: 100%; border-collapse: collapse; margin: 20px 0;}}
        th, td {{border: 1px solid #ddd; padding: 10px; text-align: left;}}
        th {{background: #4CAF50; color: white;}}
        .instructions {{background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50;}}
        .stats {{background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50;}}
        .pdf-btn {{background: #e74c3c; color: white; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-size: 14px; transition: all 0.3s;}}
        .pdf-btn:hover {{background: #c0392b; transform: translateY(-2px);}}
        h2, h3 {{ color: #333; margin: 20px 0 15px 0; }}
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .header {{ padding: 15px; }}
            .header h1 {{ font-size: 24px; }}
            .container {{ padding: 15px; }}
            table {{ font-size: 14px; }}
            th, td {{ padding: 8px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>👨‍🎓 Students List <span style="background: #e74c3c; color: white; padding: 5px 10px; border-radius: 15px; font-size: 14px;">PDF READY</span></h1>
        <p>B.E (Artificial Intelligence & Data Science) 4th Semester - All Registered Students (Click 📄 to download PDF)</p>
    </div>
    
    {get_menu()}
    
    <div class="container">
        <div class="stats">
            <h3>📊 Quick Stats</h3>
            <p><strong>Total Students:</strong> {len(students)}</p>
            <p><strong>New Feature:</strong> Download any student's result as PDF!</p>
            <p><strong>Need to find a specific student?</strong> Use the <a href="/search" style="color: #2196F3; font-weight: bold;">🔍 Search</a> feature!</p>
        </div>
        
        <h2>Registered Students</h2>
        
        <table>
            <tr>
                <th>ID</th>
                <th>Roll No</th>
                <th>Name</th>
                <th>Semester</th>
                <th>Actions</th>
            </tr>
            {student_rows}
        </table>
        
        <div style="background: #fff8e1; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h4>📄 PDF Export Instructions:</h4>
            <p>1. Click <strong>"📄 Download PDF"</strong> next to any student</p>
            <p>2. PDF will download automatically</p>
            <p>3. Print or save the professional result card</p>
            <p>4. PDF includes all subject marks, percentage, grade, and college branding</p>
        </div>
        
        {get_instructions()}
        {get_subjects_info()}
        
        <br>
        <a href="/" style="padding: 10px 20px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px;">← Back to Home</a>
    </div>
</body>
</html>'''
    
    return html_content

@app.route('/download_pdf/<int:student_id>')
def download_pdf(student_id):
    """Download student result as PDF"""
    pdf_buffer = generate_pdf(student_id)
    
    if pdf_buffer:
        # Get student name for filename
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM students WHERE id=%s', (student_id,))
        student_name = cursor.fetchone()[0]
        conn.close()
        
        # Clean filename
        filename = f"Result_{student_name.replace(' ', '_')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    else:
        return '''
        <div style="text-align: center; padding: 50px;">
            <h2>PDF Generation Failed</h2>
            <p>Student data not found or marks not available.</p>
            <p><a href="/students" style="color: #2196F3;">Back to Students</a> | <a href="/" style="color: #2196F3;">Home</a></p>
        </div>
        '''

@app.route('/search', methods=['GET', 'POST'])
def search_students():
    search_results = ""
    search_query = ""
    
    if request.method == 'POST':
        search_query = request.form['search_query']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search in name and roll number
        cursor.execute('''
            SELECT * FROM students 
            WHERE name LIKE %s OR roll_no LIKE %s
            ORDER BY name
        ''', (f'%{search_query}%', f'%{search_query}%'))
        
        students = cursor.fetchall()
        conn.close()
        
        if students:
            search_results = "<h3>🔍 Search Results:</h3>"
            search_results += f"<p>Found {len(students)} student(s) for '{search_query}'</p>"
            search_results += '<table><tr><th>ID</th><th>Roll No</th><th>Name</th><th>Semester</th><th>Actions</th></tr>'
            
            for student in students:
                search_results += f'''
                <tr>
                    <td>{student[0]}</td>
                    <td>{student[1]}</td>
                    <td>{student[2]}</td>
                    <td>{student[3]}</td>
                    <td>
                        <a href="/view_result/{student[0]}" style="color: #2196F3; margin-right: 10px;">👁️ View</a>
                        <a href="/download_pdf/{student[0]}" style="color: #e74c3c;">📄 PDF</a>
                    </td>
                </tr>
                '''
            
            search_results += '</table>'
        else:
            search_results = f'<div class="alert" style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">No students found for "{search_query}"</div>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Search Students</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
            .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
            .header p {{ font-size: 16px; }}
            .menu {{ margin: 20px 0; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }}
            .menu a {{ display: inline-block; padding: 12px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; transition: all 0.3s; }}
            .menu a:hover {{ background: #45a049; transform: translateY(-2px); }}
            .container {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); max-width: 900px; margin: 0 auto; }}
            .search-box {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            input[type="text"] {{ width: 70%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; }}
            input[type="submit"] {{ padding: 12px 30px; background: #2196F3; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; transition: all 0.3s; }}
            input[type="submit"]:hover {{ background: #0b7dda; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background: #4CAF50; color: white; }}
            h2, h3 {{ color: #333; margin: 20px 0 15px 0; }}
            .alert {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            @media (max-width: 768px) {{
                body {{ padding: 10px; }}
                .header {{ padding: 15px; }}
                .header h1 {{ font-size: 24px; }}
                .container {{ padding: 15px; }}
                input[type="text"] {{ width: 100%; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Search Students</h1>
            <p>B.E (Artificial Intelligence & Data Science) 4th Semester - Find Students by Name or Roll Number</p>
        </div>
        
        {get_menu()}
        
        <div class="container">
            <div class="search-box">
                <h3>Search Student Database</h3>
                <form method="POST">
                    <input type="text" name="search_query" value="{search_query}" placeholder="Enter student name or roll number..." required>
                    <input type="submit" value="Search">
                </form>
                <p style="color: #666; margin-top: 10px;">Search by: Name (e.g., "Aarav") or Roll No (e.g., "AIDS2024001")</p>
            </div>
            
            {search_results}
            
            {get_instructions()}
            {get_subjects_info()}
            
            <br>
            <a href="/students" style="padding: 10px 20px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px; display: inline-block; transition: all 0.3s;" onmouseover="this.style.background='#0b7dda';" onmouseout="this.style.background='#2196F3';">← Back to All Students</a>
        </div>
    </body>
    </html>
    '''

# [The rest of your routes remain EXACTLY THE SAME - add_student, enter_marks, view_result, analysis]
# Just copy all your existing routes from your current app.py (excluding home, students, search, download_pdf)


# Continue with your existing add_student route (copy from your current app.py)
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        roll_no = request.form['roll_no']
        name = request.form['name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO students (roll_no, name, semester, email, phone) VALUES (%s, %s, 4, %s, %s)', (roll_no, name, email, phone))
        conn.commit()
        conn.close()
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Success</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
                .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; text-align: center; }}
                .success-box h2 {{ color: #4CAF50; margin: 20px 0; }}
                .success-box p {{ margin: 10px 0; color: #333; }}
                .btn-group {{ margin: 30px 0; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }}
                .btn {{ padding: 12px 20px; color: white; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; transition: all 0.3s; }}
                .btn-primary {{ background: #4CAF50; }}
                .btn-primary:hover {{ background: #45a049; transform: translateY(-2px); }}
                .btn-secondary {{ background: #2196F3; }}
                .btn-secondary:hover {{ background: #0b7dda; transform: translateY(-2px); }}
                .btn-default {{ background: #666; }}
                .btn-default:hover {{ background: #555; transform: translateY(-2px); }}
                .info-box {{ background: #f0f8ff; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #4CAF50; text-align: left; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>✅ Success</h1>
            </div>
            
            <div class="container">
                <div class="success-box">
                    <h2>Student Added Successfully!</h2>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Roll No:</strong> {roll_no}</p>
                    <p><strong>Email:</strong> {email if email else 'Not provided'}</p>
                    <p><strong>Phone:</strong> {phone if phone else 'Not provided'}</p>
                    <p><strong>Semester:</strong> B.E AIDS 4th</p>
                    
                    <div class="btn-group">
                        <a href="/add_student" class="btn btn-primary">Add Another Student</a>
                        <a href="/enter_marks" class="btn btn-secondary">Enter Marks</a>
                        <a href="/" class="btn btn-default">Home</a>
                    </div>
                    
                    <div class="info-box">
                        <h4>Next Steps:</h4>
                        <p>1. Add more students if needed</p>
                        <p>2. Enter marks for this student in all 6 subjects</p>
                        <p>3. View the student's result</p>
                        <p>4. Download PDF result card</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Student</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
            .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
            .header p {{ font-size: 16px; }}
            .menu {{ margin: 20px 0; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }}
            .menu a {{ display: inline-block; padding: 12px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; transition: all 0.3s; }}
            .menu a:hover {{ background: #45a049; transform: translateY(-2px); }}
            .container {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }}
            h2 {{ color: #333; margin: 20px 0 15px 0; }}
            .form-group {{ margin: 15px 0; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #333; }}
            input[type="text"], input[type="email"], input[type="tel"] {{ width: 100%; padding: 12px; margin: 5px 0 10px 0; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; font-family: Arial; }}
            input[type="text"]:focus, input[type="email"]:focus, input[type="tel"]:focus {{ outline: none; border-color: #667eea; box-shadow: 0 0 5px rgba(102, 126, 234, 0.3); }}
            input[type="submit"] {{ width: 100%; background: #4CAF50; color: white; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px; }}
            input[type="submit"]:hover {{ background: #45a049; }}
            .instructions {{ background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
            .subjects-info {{ background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
            @media (max-width: 768px) {{
                body {{ padding: 10px; }}
                .header {{ padding: 15px; }}
                .header h1 {{ font-size: 24px; }}
                .container {{ padding: 15px; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>➕ Add New Student</h1>
            <p>B.E (Artificial Intelligence & Data Science) 4th Semester - Register New Student</p>
        </div>
        
        {get_menu()}
        
        <div class="container">
            <h2>Add Student Form</h2>
            
            <form method="POST">
                <div class="form-group">
                    <label for="roll_no">Roll Number:</label>
                    <input type="text" name="roll_no" id="roll_no" placeholder="e.g., AIDS2024001" required>
                </div>
                
                <div class="form-group">
                    <label for="name">Student Name:</label>
                    <input type="text" name="name" id="name" placeholder="e.g., Rahul Sharma" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email Address:</label>
                    <input type="email" name="email" id="email" placeholder="e.g., rahul@example.com">
                </div>
                
                <div class="form-group">
                    <label for="phone">Mobile Number:</label>
                    <input type="tel" name="phone" id="phone" placeholder="e.g., 9876543210">
                </div>
                
                <input type="submit" value="Add Student">
            </form>
            
            {get_instructions()}
            {get_subjects_info()}
            
            <br>
            <a href="/" style="color: #2196F3; text-decoration: none;">← Back to Home</a>
        </div>
    </body>
    </html>
    '''

# Continue with your existing enter_marks route (copy from your current app.py)
@app.route('/enter_marks', methods=['GET', 'POST'])
def enter_marks():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        subject_id = request.form['subject_id']
        marks = int(request.form['marks'])
        
        cursor.execute('SELECT id FROM marks WHERE student_id=%s AND subject_id=%s', (student_id, subject_id))
        
        if cursor.fetchone():
            cursor.execute('UPDATE marks SET marks=%s WHERE student_id=%s AND subject_id=%s', 
                          (marks, student_id, subject_id))
            message = "✅ Marks updated successfully!"
        else:
            cursor.execute('INSERT INTO marks (student_id, subject_id, marks) VALUES (%s, %s, %s)', 
                          (student_id, subject_id, marks))
            message = "✅ Marks entered successfully!"
        
        conn.commit()
        conn.close()
       
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Success</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
                .header h1 {{ font-size: 28px; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; text-align: center; }}
                .success-box h2 {{ color: #4CAF50; margin: 20px 0; }}
                .btn-group {{ margin: 30px 0; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }}
                .btn {{ padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 5px; display: inline-block; font-weight: bold; transition: all 0.3s; }}
                .btn:hover {{ background: #45a049; transform: translateY(-2px); }}
                .btn-alt {{ background: #2196F3; }}
                .btn-alt:hover {{ background: #0b7dda; }}
                .btn-default {{ background: #666; }}
                .btn-default:hover {{ background: #555; }}
                .info-box {{ background: #f0f8ff; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #4CAF50; text-align: left; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>✅ Success</h1>
            </div>
            
            <div class="container">
                <div class="success-box">
                    <h2>{message}</h2>
                    
                    <div class="btn-group">
                        <a href="/enter_marks" class="btn">Enter More Marks</a>
                        <a href="/students" class="btn btn-alt">View Students</a>
                        <a href="/" class="btn btn-default">Home</a>
                    </div>
                    
                    <div class="info-box">
                        <h4>Next Steps:</h4>
                        <p>1. Enter marks for other subjects</p>
                        <p>2. Check student's result</p>
                        <p>3. View data analysis for insights</p>
                        <p>4. Download PDF result card</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
    
    cursor.execute('SELECT id, roll_no, name FROM students ORDER BY name')
    students = cursor.fetchall()
    
    cursor.execute('SELECT id, subject_code, subject_name FROM subjects ORDER BY subject_code')
    subjects = cursor.fetchall()
    
    
    conn.close()
    
    student_options = ""
    for student in students:
        student_options += f'<option value="{student[0]}">{student[1]} - {student[2]}</option>'
    
    subject_options = ""
    for subject in subjects:
        subject_options += f'<option value="{subject[0]}">{subject[1]} - {subject[2]}</option>'
    
   
    menu_html = get_menu()
    instructions_html = get_instructions()
    subjects_info_html = get_subjects_info()

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enter Marks</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
            .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
            .header p {{ font-size: 16px; }}
            .menu {{ margin: 20px 0; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }}
            .menu a {{ display: inline-block; padding: 12px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; transition: all 0.3s; }}
            .menu a:hover {{ background: #45a049; transform: translateY(-2px); }}
            .container {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }}
            h2 {{ color: #333; margin: 20px 0 15px 0; }}
            form {{ margin-top: 20px; }}
            label {{ display: block; margin: 15px 0 5px 0; font-weight: bold; color: #333; }}
            select, input[type="number"] {{ width: 100%; padding: 10px; margin: 5px 0 20px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; font-size: 14px; }}
            input[type="submit"] {{ width: 100%; background: #4CAF50; color: white; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px; }}
            input[type="submit"]:hover {{ background: #45a049; }}
            .instructions {{ background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
            .subjects-info {{ background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
            @media (max-width: 768px) {{
                body {{ padding: 10px; }}
                .header {{ padding: 15px; }}
                .header h1 {{ font-size: 24px; }}
                .container {{ padding: 15px; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📝 Enter Student Marks</h1>
            <p>B.E (Artificial Intelligence & Data Science) 4th Semester - All 6 Subjects</p>
        </div>

        {menu_html}

        <div class="container">
            <h2>Enter Marks Form</h2>

            <form method="POST">
                <label for="student">Select Student:</label>
                <select name="student_id" id="student" required>
                    <option value="">-- Select Student --</option>
                    {student_options}
                </select>

                <label for="subject">Select Subject:</label>
                <select name="subject_id" id="subject" required>
                    <option value="">-- Select Subject --</option>
                    {subject_options}
                </select>

                <label for="marks">Enter Marks (0-100):</label>
                <input type="number" name="marks" id="marks" min="0" max="100" placeholder="Enter marks between 0-100" required>

                <input type="submit" value="Save Marks">
            </form>

            {instructions_html}
            {subjects_info_html}

            <br>
            <a href="/" style="color: #2196F3; text-decoration: none;">← Back to Home</a>
        </div>
    </body>
    </html>
    '''

# Continue with your existing view_result route (copy from your current app.py)
# BUT add PDF download button at the bottom

@app.route('/view_result/<int:student_id>')
def view_result(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT roll_no, name, semester FROM students WHERE id=%s', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return '''
        <div style="text-align: center; padding: 50px;">
            <h2>Student not found</h2>
            <p><a href="/students" style="color: #2196F3;">View Students</a> | <a href="/" style="color: #2196F3;">Home</a></p>
        </div>
        '''
    
    cursor.execute('''
        SELECT s.subject_code, s.subject_name, m.marks
        FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        WHERE m.student_id = %s
        ORDER BY s.subject_code
    ''', (student_id,))
    
    marks = cursor.fetchall()
    conn.close()
    
    if not marks:
        return f'''
        <div style="text-align: center; padding: 50px;">
            <h2>No marks found for {student[1]}</h2>
            <p>Please enter marks for this student first.</p>
            <p><a href="/enter_marks" style="color: #2196F3;">Enter Marks</a> | <a href="/" style="color: #2196F3;">Home</a></p>
        </div>
        '''
    
    total_marks = sum([m[2] for m in marks])
    percentage = (total_marks / (len(marks) * 100)) * 100
    
    if percentage >= 90:
        grade = 'O (Outstanding)'
        grade_color = '#FFD700'
    elif percentage >= 80:
        grade = 'A+ (Excellent)'
        grade_color = '#4CAF50'
    elif percentage >= 70:
        grade = 'A (Very Good)'
        grade_color = '#2196F3'
    elif percentage >= 60:
        grade = 'B+ (Good)'
        grade_color = '#9C27B0'
    elif percentage >= 50:
        grade = 'B (Above Average)'
        grade_color = '#FF9800'
    elif percentage >= 45:
        grade = 'C (Average)'
        grade_color = '#795548'
    elif percentage >= 40:
        grade = 'P (Pass)'
        grade_color = '#607D8B'
    else:
        grade = 'F (Fail)'
        grade_color = '#F44336'
    
    marks_table = ""
    for subject_code, subject_name, mark in marks:
        marks_table += f'<tr><td>{subject_code}<br><small>{subject_name}</small></td><td>{mark}</td><td>100</td></tr>'
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Student Result</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px 15px 0 0;
            text-align: center;
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ font-size: 16px; }}
        .menu {{
            margin: 15px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }}
        .menu a {{
            padding: 10px 15px;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: all 0.3s;
            font-size: 14px;
        }}
        .menu a:hover {{ background: #45a049; transform: translateY(-2px); }}
        .result-card {{
            background: white;
            padding: 30px;
            border-radius: 0 0 15px 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            max-width: 900px;
            margin: 0 auto;
        }}
        table {{width: 100%; border-collapse: collapse; margin: 25px 0;}}
        th, td {{border: 1px solid #ddd; padding: 12px; text-align: left;}}
        th {{background: #f8f9fa;}}
        .total-box {{background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 25px 0; border-left: 5px solid #4CAF50;}}
        .grade {{font-size: 28px; font-weight: bold; padding: 10px; border-radius: 8px; display: inline-block;}}
        .btn {{display: inline-block; padding: 12px 25px; background: #2196F3; color: white; text-decoration: none; border-radius: 8px; margin: 10px 5px; transition: all 0.3s;}}
        .btn:hover {{ background: #0b7dda; transform: translateY(-2px); }}
        .pdf-btn {{background: #e74c3c; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; display: inline-block; transition: all 0.3s;}}
        .pdf-btn:hover {{background: #c0392b; transform: translateY(-2px);}}
        h2 { color: #333; margin: 20px 0 15px 0; }
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .header {{ padding: 15px; }}
            .header h1 {{ font-size: 24px; }}
            .result-card {{ padding: 15px; }}
            table {{ font-size: 14px; }}
            th, td {{ padding: 8px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Student Result Card</h1>
        <p> B.E (Artificial Intelligence & Data Science) 4th Semester • All 6 Subjects</p>
    </div>
    
    {get_menu()}
    
    <div class="result-card">
        <h2>{student[1]} <span style="color: #666;">(Roll No: {student[0]})</span></h2>
        <p><strong>Semester:</strong> {student[2]}</p>
        
        <h3>📚 Subject-wise Marks:</h3>
        <table>
            <tr>
                <th>Subject (Code)</th>
                <th>Marks Obtained</th>
                <th>Maximum Marks</th>
            </tr>
            {marks_table}
        </table>
        
        <div class="total-box">
            <h3>📊 Result Summary</h3>
            <p><strong>Total Subjects:</strong> {len(marks)} out of 6</p>
            <p><strong>Total Marks Obtained:</strong> {total_marks} / {len(marks) * 100}</p>
            <p><strong>Percentage:</strong> <span style="font-size: 24px; font-weight: bold;">{percentage:.2f}%</span></p>
            <p><strong>Grade:</strong> <span class="grade" style="background-color: {grade_color}; color: white;">{grade}</span></p>
            <p><strong>Status:</strong> <span style="color: {'#4CAF50' if percentage >= 40 else '#F44336'}; font-weight: bold; font-size: 20px;">{'PASS' if percentage >= 40 else 'FAIL'}</span></p>
        </div>
        
        <div style="background: #e8f4f8; padding: 20px; border-radius: 10px; margin: 25px 0;">
            <h3>📄 Download Result Card</h3>
            <p>Click the button below to download a professional PDF version of this result card:</p>
            <a href="/download_pdf/{student_id}" class="pdf-btn">
                📄 Download PDF Result Card
            </a>
            <p style="color: #666; font-size: 14px; margin-top: 10px;">
                PDF includes: All subject marks, percentage, grade, college branding, and date stamp.
            </p>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/students" class="btn">← Back to Students</a>
            <a href="/" class="btn">🏠 Home</a>
            <a href="/enter_marks" class="btn">📝 Enter More Marks</a>
            <a href="/analysis" class="btn">📊 View Analysis</a>
        </div>
    </div>
</body>
</html>'''
    
    return html_content

# Continue with your existing analysis route (copy from your current app.py)
@app.route('/analysis')
def data_analysis():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT s.id) as total_students,
            COUNT(m.id) as total_marks_entries,
            AVG(m.marks) as avg_marks,
            MAX(m.marks) as highest_mark,
            MIN(m.marks) as lowest_mark,
            SUM(CASE WHEN m.marks >= 40 THEN 1 ELSE 0 END) * 100.0 / COUNT(m.id) as pass_percentage
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
    ''')
    overall_stats = cursor.fetchone()
    
    cursor.execute('''
        SELECT 
            sub.subject_code,
            sub.subject_name,
            COUNT(m.id) as total_students,
            AVG(m.marks) as avg_marks,
            MAX(m.marks) as highest,
            MIN(m.marks) as lowest,
            SUM(CASE WHEN m.marks >= 40 THEN 1 ELSE 0 END) as passed,
            COUNT(m.id) as total
        FROM subjects sub
        LEFT JOIN marks m ON sub.id = m.subject_id
        GROUP BY sub.id
        ORDER BY sub.subject_code
    ''')
    subject_stats = cursor.fetchall()
    
    cursor.execute('''
        SELECT 
            s.name,
            s.roll_no,
            AVG(m.marks) as avg_marks,
            SUM(m.marks) as total_marks
        FROM students s
        JOIN marks m ON s.id = m.student_id
        GROUP BY s.id
        ORDER BY avg_marks DESC
        LIMIT 5
    ''')
    top_students = cursor.fetchall()
    
    cursor.execute('''
        SELECT 
            CASE 
                WHEN marks >= 90 THEN 'O (90-100)'
                WHEN marks >= 80 THEN 'A+ (80-89)'
                WHEN marks >= 70 THEN 'A (70-79)'
                WHEN marks >= 60 THEN 'B+ (60-69)'
                WHEN marks >= 50 THEN 'B (50-59)'
                WHEN marks >= 45 THEN 'C (45-49)'
                WHEN marks >= 40 THEN 'P (40-44)'
                ELSE 'F (Below 40)'
            END as grade_range,
            COUNT(*) as count,
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM marks) as percentage
        FROM marks
        GROUP BY grade_range
        ORDER BY 
            CASE grade_range
                WHEN 'O (90-100)' THEN 1
                WHEN 'A+ (80-89)' THEN 2
                WHEN 'A (70-79)' THEN 3
                WHEN 'B+ (60-69)' THEN 4
                WHEN 'B (50-59)' THEN 5
                WHEN 'C (45-49)' THEN 6
                WHEN 'P (40-44)' THEN 7
                ELSE 8
            END
    ''')
    grade_distribution = cursor.fetchall()
    
    conn.close()
    
    # Generate charts
    chart1_url, chart2_url = create_charts()
    
    subject_table = ""
    for subject in subject_stats:
        total_students = subject[7] or 0
        passed_students = subject[6] or 0

        pass_rate = (passed_students / total_students * 100) if total_students > 0 else 0

        avg_marks = subject[3] if subject[3] is not None else 0

        subject_table += f'''
        <tr>
            <td>{subject[0]}<br><small>{subject[1]}</small></td>
            <td>{subject[2] or 0}</td>
            <td>{avg_marks:.1f}</td>
            <td>{subject[4] or 0}</td>
            <td>{subject[5] or 0}</td>
            <td>{pass_rate:.1f}%</td>
        </tr>
        '''
    
    top_students_table = ""
    for rank, student in enumerate(top_students, 1):
        top_students_table += f'''
        <tr>
            <td>{rank}</td>
            <td>{student[1]}</td>
            <td>{student[0]}</td>
            <td>{student[2]:.1f}</td>
            <td>{student[3]}</td>
        </tr>
        '''
    
    grade_table = ""
    for grade in grade_distribution:
        grade_table += f'''
        <tr>
            <td>{grade[0]}</td>
            <td>{grade[1]}</td>
            <td>{grade[2]:.1f}%</td>
        </tr>
        '''
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Data Analysis</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .header {{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;}}
        .menu {{margin: 20px 0;}}
        .menu a {{display: inline-block; margin: 10px; padding: 12px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;}}
        .container {{background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);}}
        .stats-grid {{display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 25px 0;}}
        .stat-card {{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;}}
        table {{width: 100%; border-collapse: collapse; margin: 20px 0;}}
        th, td {{border: 1px solid #ddd; padding: 10px; text-align: left;}}
        th {{background: #4CAF50; color: white;}}
        .instructions {{background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0;}}
        .chart-container {{display: flex; flex-wrap: wrap; gap: 20px; margin: 30px 0;}}
        .chart-box {{flex: 1; min-width: 300px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.1);}}
        .pdf-feature {{background: #ffeaa7; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #e74c3c;}}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Data Analysis Dashboard</h1>
        <p>Performance Statistics & Insights</p>
    </div>
    
    {get_menu()}
    
    <div class="container">
        <div class="pdf-feature">
            <h3>📄 NEW: PDF Export Feature!</h3>
            <p>Now you can download professional PDF result cards for any student!</p>
            <p>Visit <a href="/students" style="color: #2196F3; font-weight: bold;">Students Page</a> and click "📄 Download PDF" next to any student.</p>
        </div>
        
        <h2>📈 Overall Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>👨‍🎓 Total Students</h3>
                <p style="font-size: 36px; margin: 10px 0;">{overall_stats[0] or 0}</p>
            </div>
            <div class="stat-card">
                <h3>📝 Total Marks Entries</h3>
                <p style="font-size: 36px; margin: 10px 0;">{overall_stats[1] or 0}</p>
            </div>
            <div class="stat-card">
                <h3>📊 Average Marks</h3>
                <p style="font-size: 36px; margin: 10px 0;">{overall_stats[2] or 0:.1f}</p>
            </div>
            <div class="stat-card">
                <h3>🏆 Pass Percentage</h3>
                <p style="font-size: 36px; margin: 10px 0;">{overall_stats[5] or 0:.1f}%</p>
            </div>
        </div>
        
        <h2>📊 Visual Analysis</h2>
        <div class="chart-container">
            <div class="chart-box">
                <h3>📚 Subject Performance</h3>
                <img src="data:image/png;base64,{chart1_url}" style="width: 100%; border-radius: 5px;">
                <p style="text-align: center; color: #666; font-size: 12px; margin-top: 10px;">
                    Average marks across all 6 subjects
                </p>
            </div>
            
            <div class="chart-box">
                <h3>🎯 Grade Distribution</h3>
                <img src="data:image/png;base64,{chart2_url}" style="width: 100%; border-radius: 5px;">
                <p style="text-align: center; color: #666; font-size: 12px; margin-top: 10px;">
                    Overall grade distribution of all students
                </p>
            </div>
        </div>
        
        <h2>📚 Subject-wise Analysis</h2>
        <table>
            <tr>
                <th>Subject</th>
                <th>Students</th>
                <th>Average</th>
                <th>Highest</th>
                <th>Lowest</th>
                <th>Pass Rate</th>
            </tr>
            {subject_table}
        </table>
        
        <h2>🏆 Top 5 Students</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Roll No</th>
                <th>Name</th>
                <th>Average</th>
                <th>Total Marks</th>
            </tr>
            {top_students_table}
        </table>
        
        <h2>📊 Grade Distribution</h2>
        <table>
            <tr>
                <th>Grade Range</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
            {grade_table}
        </table>
        
        {get_instructions()}
        {get_subjects_info()}
        
        
        <br>
        <a href="/" style="padding: 10px 20px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px;">← Back to Home</a>
    </div>
</body>
</html>'''
    
    return html_content

if __name__ == '__main__':
    app.run(debug=True, port=5001)