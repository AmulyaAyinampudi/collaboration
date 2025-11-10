def summarize_matches(matches):
    if not matches:
        return "No strong study group matches found yet."

    lines = []
    for m in matches:
        name = m.get("name", f"User {m['id']}")
        courses = ", ".join(m["shared_courses"])
        lines.append(f"{name} shares courses {courses} and prefers {m['time']} sessions.")
    return "\n".join(lines)
