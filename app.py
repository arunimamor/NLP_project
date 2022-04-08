from flask import Flask, render_template,request
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from nltk.tokenize import word_tokenize
import re
import nltk
from gtts import gTTS
from playsound import playsound
nltk.download('punkt')
language = 'en'
from transformers import pipeline
# summarization = pipeline('summarization')
app = Flask(__name__)

# def summary_generator(text):
#     summarized_text = summarization(text, min_length= 20, max_length = 200)
#     return summarized_text[0]['summary_text']

def summarise(text):
    model = AutoModelForSeq2SeqLM.from_pretrained("Linguist/t5-small-Linguists_summariser")
    tokenizer = AutoTokenizer.from_pretrained("Linguist/t5-small-Linguists_summariser")
    inputs = tokenizer("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs["input_ids"], max_length=150, min_length=20, length_penalty=2.0, num_beams=4)#, early_stopping=True)
    op_text = tokenizer.decode(outputs[0])
    result = re.sub(r'(^<pad>)|(</s>$)', '', op_text)
    print("inside summarise", result)
    print(type(result))
    return result
def combine(text):
    lst = word_tokenize(text)
    l = len(lst)
    mega = []
    chunks = (l//200)+1
    temp = ""
    t = []
    for i in range(chunks):
        t = lst[i:i+200]
        temp = " ".join(t)
        mega.append(summarise(temp))
    m_txt = " ".join(mega)
    print("inside combine ",m_txt)
    print(type(m_txt))
    return m_txt

def video_id(value):
    query = urllib.parse.urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urllib.parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None
def get_text_from_link(link_id):
   transcript = YouTubeTranscriptApi.get_transcript(link_id)
   script = ""
   for text in transcript:
      t = text["text"]
      if t != '[Music]':
         script += t + " "
   return script
@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        link = request.form.get("url") # getting the link
        video_id_from_link = video_id(link) # extracting the video_id
        Generated_text = get_text_from_link(video_id_from_link)
        #summary = summary_generator(Generated_text) # getting the summary of the text
        summary = combine(Generated_text)
        obj = gTTS(text=summary, lang=language, slow=False)
        obj.save("templates/audio/audio_output.mp3")
        return render_template('output.html', output = summary)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)




