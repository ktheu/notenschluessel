import streamlit as st
import pandas as pd

# Notenschlüssel-Definitionen
PERCENTAGE_THRESHOLDS = [20, 27, 34, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
POINTS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
GRADES = ["6", "5-", "5", "5+", "4-", "4", "4+", "3-", "3", "3+", "2-", "2", "2+", "1-", "1", "1+"]

def calculate_grade(achieved_points, max_points):
    """Berechnet Note und Punkte basierend auf erreichter Punktzahl"""
    if max_points == 0:
        return 0, "6"
    
    percentage = (achieved_points / max_points) * 100
    
    # Finde die entsprechende Note
    for i in range(len(PERCENTAGE_THRESHOLDS)):
        if percentage < PERCENTAGE_THRESHOLDS[i]:
            return POINTS[i], GRADES[i]
    
    # Wenn >= 96%, dann 1+
    return POINTS[-1], GRADES[-1]

def create_txt(df, max_points):
    """Erstellt eine TXT-Datei mit der Notentabelle"""
    lines = []
    lines.append(f"Notenschluessel fuer maximal {max_points} Punkte")
    lines.append("="* 70)
    lines.append("")
    
    # Header
    header = f"{'Minimale Punkte':<20} {'Prozent':<15} {'Notenpunkte':<20} {'Note':<10}"
    lines.append(header)
    lines.append("-" * 70)
    
    # Daten
    for _, row in df.iterrows():
        line = f"{str(row['Minimale Punkte']):<20} {str(row['Prozent']):<15} {str(row['Notenpunkte']):<20} {str(row['Note']):<10}"
        lines.append(line)
    
    return "\n".join(lines)

def create_grade_table(max_points):
    """Erstellt eine Tabelle mit minimalen Punktzahlen für jede Note"""
    data = []
    seen_grades = set()
    
    for points in range(max_points + 1):
        grade_points, grade = calculate_grade(points, max_points)
        
        # Nur die erste (minimale) Punktzahl für jede Note hinzufügen
        if grade not in seen_grades:
            percentage = (points / max_points) * 100 if max_points > 0 else 0
            
            data.append({
                "Minimale Punkte": points,
                "Prozent": f"{percentage:.1f}%",
                "Notenpunkte": grade_points,
                "Note": grade
            })
            seen_grades.add(grade)
    
    return pd.DataFrame(data)

# Streamlit-Oberfläche
st.title("📊 Notenschlüssel-Rechner")
st.markdown("---")

# Eingabe der maximalen Punktzahl
max_points = st.number_input(
    "Maximale Punktzahl eingeben:",
    min_value=1,
    max_value=1000,
    value=100,
    step=1
)

# Zeige den Notenschlüssel als Information
with st.expander("ℹ️ Notenschlüssel-Information"):
    st.markdown("""
    **Prozentuale Grenzen:**
    - unter 20%: 0 Punkte (Note 6)
    - 20-27%: 1 Punkt (Note 5-)
    - 27-34%: 2 Punkte (Note 5)
    - 34-41%: 3 Punkte (Note 5+)
    - 41-46%: 4 Punkte (Note 4-)
    - 46-51%: 5 Punkte (Note 4)
    - 51-56%: 6 Punkte (Note 4+)
    - 56-61%: 7 Punkte (Note 3-)
    - 61-66%: 8 Punkte (Note 3)
    - 66-71%: 9 Punkte (Note 3+)
    - 71-76%: 10 Punkte (Note 2-)
    - 76-81%: 11 Punkte (Note 2)
    - 81-86%: 12 Punkte (Note 2+)
    - 86-91%: 13 Punkte (Note 1-)
    - 91-96%: 14 Punkte (Note 1)
    - ab 96%: 15 Punkte (Note 1+)
    """)

st.markdown("---")

# Erstelle und zeige die Tabelle
st.subheader(f"Notentabelle für maximal {max_points} Punkte")

df = create_grade_table(max_points)

# Zeige die Tabelle
st.dataframe(
    df,
    width='stretch',
    hide_index=True,
    height=400
)

# Download-Button für TXT
txt_content = create_txt(df, max_points)
st.download_button(
    label="🖨️ Tabelle zum Druck herunterladen",
    data=txt_content,
    file_name=f"notenschluessel_{max_points}_punkte.txt",
    mime="text/plain",
)

# Optionaler Einzelrechner
st.markdown("---")
st.subheader("🔍 Einzelne Note berechnen")

col1, col2, col3 = st.columns(3)

with col1:
    achieved = st.number_input(
        "Erreichte Punktzahl:",
        min_value=0,
        max_value=max_points,
        value=0,
        step=1
    )

with col2:
    grade_points, grade = calculate_grade(achieved, max_points)
    st.metric("Notenpunkte", grade_points)

with col3:
    percentage = (achieved / max_points) * 100 if max_points > 0 else 0
    st.metric("Note", grade, f"{percentage:.1f}%")


st.markdown("---")
st.subheader(f"Zwei Noten zusammenrechnen")

col1, col2, col3, col4 = st.columns(4)
# note1 = col1.text_input("Note 1 (z.B. 2+):", value="2+")
# note2 = col2.text_input("Note 2 (z.B. 3-):", value="3-")
note1 = col1.selectbox("Note 1:", GRADES, index=GRADES.index("2+"))
note2 = col2.selectbox("Note 2:", GRADES, index=GRADES.index("3-"))
gewicht1 = col3.number_input("Gewicht % Note 1:", min_value=0, max_value=100, value=50, step=5)
gewicht2 = 100 - gewicht1
col4.write(f"Note 2: {gewicht2}%")

if note1 in GRADES and note2 in GRADES:
    np1 = POINTS[GRADES.index(note1)]
    np2 = POINTS[GRADES.index(note2)]
    combined_np = (np1 * gewicht1 + np2 * gewicht2) / 100
    # Finde die Note für die kombinierte Notenpunkte
    for i in range(len(POINTS)):
        if combined_np <= POINTS[i]:
            combined_grade = GRADES[i]
            break
    else:
        combined_grade = GRADES[-1]
    
    st.success(f"Die kombinierte Note ist: {combined_grade} ({combined_np:.2f} Notenpunkte)")
