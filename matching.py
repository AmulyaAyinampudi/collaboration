from database import get_connection
import ast

def fetch_all_students():
    conn = get_connection()
    cur = conn.cursor()
    # fetch students + names
    cur.execute("""
        SELECT s.user_id, u.name, s.courses, s.grades, s.preferred_times
        FROM students s
        JOIN users u ON s.user_id = u.id
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def compute_matches(current_user_id):
    data = fetch_all_students()
    if not data:
        return []

    def to_list(s):
        try: return ast.literal_eval(s)
        except: return []
    def to_dict(s):
        try: return ast.literal_eval(s)
        except: return {}

    users = []
    for uid, name, c, g, t in data:
        users.append({
            "id": uid,
            "name": name,
            "courses": to_list(c),
            "grades": to_dict(g),
            "time": t
        })

    current_user = next((u for u in users if u["id"] == current_user_id), None)
    if not current_user: return []

    matches = []
    for u in users:
        if u["id"] == current_user_id:
            continue
        shared = set(u["courses"]) & set(current_user["courses"])
        if shared and u["time"] == current_user["time"]:
            matches.append({
                "id": u["id"],
                "name": u["name"],
                "shared_courses": list(shared),
                "time": u["time"]
            })

    return matches
