import os
import requests
import json
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen   # ✅ Needed for bot.listen()

@Client.on_message(filters.command(["rgvikramjeet"]))
async def rgvikramjeet(bot: Client, m: Message):
    try:
        # Step 1: Login
        await m.reply_text("Send **ID & Password** like this: `ID*Password`")
        input1: Message = await bot.listen(m.chat.id)
        raw_text = input1.text

        if "*" not in raw_text:
            return await m.reply_text("❌ Invalid format. Use: `ID*Password`")

        userid, password = raw_text.split("*", 1)

        login_url = "https://appapi.videocrypt.in/data_model/users/login_auth"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://rankersgurukul.com",
            "Referer": "https://rankersgurukul.com/",
            "Appid": "753",
            "Devicetype": "4",
            "Lang": "1"
        }
        payload = {"userid": userid, "password": password}

        response = requests.post(login_url, headers=headers, json=payload)
        data = response.json()

        if "access_token" not in data:
            return await m.reply_text("❌ Login failed. Please check your ID and password.")

        token = data["access_token"]
        user_id = data.get("user_id") or data.get("userid")
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Courses
        courses_url = f"https://appapi.videocrypt.in/data_model/courses?userId={user_id}"
        res_courses = requests.get(courses_url, headers=auth_headers).json()
        courses = res_courses.get("data", [])

        if not courses:
            return await m.reply_text("⚠️ No courses found.")

        message_text = "**📚 Your Courses:**\n\n"
        for course in courses:
            message_text += f"`{course.get('id')}` - **{course.get('course_name') or course.get('name')}**\n"
        await m.reply_text(message_text)

        await m.reply_text("Send the **Course ID** to continue:")
        selected_course = (await bot.listen(m.chat.id)).text.strip()

        # Step 3: Subjects
        subjects_url = f"https://appapi.videocrypt.in/data_model/courses/subjects?courseId={selected_course}"
        res_subjects = requests.get(subjects_url, headers=auth_headers).json()
        subjects = res_subjects.get("data", [])

        subj_text = "**📘 Subjects:**\n\n"
        for subj in subjects:
            subj_text += f"`{subj.get('id')}` - **{subj.get('subject_name')}**\n"
        await m.reply_text(subj_text)

        await m.reply_text("Send the **Subject ID**:")
        selected_subject = (await bot.listen(m.chat.id)).text.strip()

        # Step 4: Topics
        topics_url = f"https://appapi.videocrypt.in/data_model/courses/subjects/topics?subjectId={selected_subject}&courseId={selected_course}"
        res_topics = requests.get(topics_url, headers=auth_headers).json()
        topics = res_topics.get("data", [])

        topic_text = "**📝 Topics:**\n\n"
        for topic in topics:
            topic_text += f"`{topic.get('id')}` - **{topic.get('topic_name')}**\n"
        await m.reply_text(topic_text)

        await m.reply_text("Send one or more **Topic IDs** (separated by &):")
        topic_ids = (await bot.listen(m.chat.id)).text.strip().split("&")

        await m.reply_text("Now send the **Resolution** (or type 'any'):")
        resolution = (await bot.listen(m.chat.id)).text.strip()

        # Step 5: Videos
        download_links = []
        for topic_id in topic_ids:
            video_url = f"https://appapi.videocrypt.in/data_model/courses/videos?topicId={topic_id}&courseId={selected_course}"
            res_videos = requests.get(video_url, headers=auth_headers).json()
            videos = res_videos.get("data", [])

            for video in videos:
                title = video.get("Title") or "Untitled"
                enc_link = video.get("download_link") or video.get("pdf_link")
                if not enc_link:
                    continue

                try:
                    # ✅ Decrypt properly
                    key = b"638udh3829162018"   # must be correct
                    iv = b"fedcba9876543210"   # must be correct
                    ciphertext = b64decode(enc_link)
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
                    decrypted_link = plaintext.decode("utf-8")
                    download_links.append(f"{title}: {decrypted_link}")
                except Exception as e:
                    download_links.append(f"{title}: ❌ Failed to decrypt ({e})")

        # Step 6: Save & Send
        filename = f"Rgvikramjeet_{selected_course}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(download_links))

        await m.reply_document(filename, caption="✅ Download Links", quote=True)
        os.remove(filename)

    except Exception as e:
        import traceback
        await m.reply_text(f"❌ Error:\n{traceback.format_exc()}")
