def build_cast_role_reply(movie, roles):
    if not roles:
        return f"Rất tiếc, mình chưa có thông tin diễn viên/vai diễn của phim **{movie.original_title}**."
    
    lines = [f"• **{r['role_name']}**: {r['actor_name']}" for r in roles[:10]]
    more = len(roles) > 10 and f" và còn {len(roles)-10} diễn viên khác..." or ""
    return (
        f"**{movie.original_title}** ({movie.release_date or 'N/A'})\n"
        f"Các vai diễn chính:\n" + "\n".join(lines) + more + 
        "\n\nBạn muốn mình tóm tắt nội dung phim này không?"
    )

def build_not_found_reply(intent: str, query: str):
    messages = {
        "cast_role": f"Không tìm thấy thông tin diễn viên/vai diễn cho phim gần giống \"{query}\". Bạn có thể ghi rõ tên phim hơn được không?",
        "actor": f"Chưa tìm thấy diễn viên nào khớp với \"{query}\". Có phải bạn muốn hỏi về ai khác?",
        "director": f"Chưa có thông tin đạo diễn \"{query}\" trong cơ sở dữ liệu.",
        "summary": f"Không tìm thấy phim nào tên gần giống \"{query}\". Bạn thử ghi lại tên phim giúp mình nhé!",
    }
    return messages.get(intent, "Mình chưa hiểu rõ câu hỏi. Bạn có thể nói cụ thể hơn không?")