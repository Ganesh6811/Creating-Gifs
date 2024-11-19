from flask import Flask, request, jsonify
import os
from whisper import load_model

app = Flask(__name__)

model = load_model("base")

@app.route("/process-video", methods=["POST"])
def process_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files["video"]
    
    if video_file.filename == "":
        return jsonify({"error": "No video file selected"}), 400

    video_path = os.path.join("uploads", video_file.filename)
    video_file.save(video_path)

    try:
        result = model.transcribe(video_path)

        filter_words = [
            "wow", "omg", "lol", "oops", "nope", "yes", "yay", "what", "ugh", "meh", "i love you",
            "woohoo", "seriously", "bruh", "congrats", "party time", "cheers", "let’s go", 
            "you did it", "fantastic", "amazing", "winning", "boom", "slay", "hi", "hello", 
            "hey", "what’s up", "howdy", "good morning", "good night", "bye", "see ya", "love", 
            "heartbroken", "sad", "angry", "happy", "excited", "nervous", "shocked", "bored", 
            "confused", "embarrassed", "chill", "you got this", "go for it", "keep going", "Happy",
            "don’t stop", "believe", "be strong", "stay positive", "keep calm", "good job", "well done", 
            "nice", "perfect", "awesome", "cool", "great", "genius", "love it", "thanks", "nailed it", 
            "i can’t even", "deal with it", "let’s do this", "i’m out", "mic drop", "game over", "savage", 
            "oh no", "wtf", "whoa", "bye felicia", "you’re kidding", "whatever", "facepalm", "same", 
            "lit", "mood"
        ]

        timestamps = []

        for segment in result["segments"]:
            text = segment["text"]
            matching_words = [word for word in filter_words if word.lower() in text.lower()]

            if matching_words:
                caption = ' '.join(matching_words)
                timestamps.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "caption": caption
                })

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

    return jsonify({"timestamps": timestamps})

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(port=5000)
