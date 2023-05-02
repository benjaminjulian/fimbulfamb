from flask import Flask, render_template, redirect, url_for, request
import zipfile
import io
import openai
import os
from datetime import datetime
from creds import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

def translate(text, language):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            { "role": "user", "content": "Translate this Icelandic text to English. Be concise and clear and use easily understandable language. Observe the following jargon throughout: félag=union, þing ASÍ=ASÍ congress, alþýða=people.\n\nÞað eru erfiðir tímar, það er atvinnuþref." },
            { "role": "assistant", "content": "There are difficult times and labour disputes." },
            { "role": "user", "content": "Translate all the Icelandic in the <w:t> tags into {language}, but keep the XML otherwise intact:\n\n" + text }
        ],
    )
    print(response)
    return response.choices[0].message.content

def translate_file(filename, language):
    # unpack the zipfile
    docx = zipfile.ZipFile(filename)
    xml = docx.read("word/document.xml")
    xml = xml.decode("utf-8")
    xml_to_translate = xml[xml.find("<w:body>"):xml.find("</w:body>")+len("</w:body>")]
    print(xml_to_translate)
    xml_translated = translate(xml_to_translate, language)
    print(xml_translated)
    xml = xml.replace(xml_to_translate, xml_translated)
    docx.close()

    # create a temp filename
    filename_output = filename + "_" + language + ".docx"
    file_to_replace = "word/document.xml"

    # Open the original zipfile and create a new zipfile to store the modified contents
    with zipfile.ZipFile(filename, 'r') as zin, zipfile.ZipFile(filename_output, 'w') as zout:
        for item in zin.infolist():
            if item.filename == file_to_replace:
                # Create a new ZipInfo object with the same metadata as the original file
                new_zipinfo = zipfile.ZipInfo(item.filename, item.date_time)
                new_zipinfo.external_attr = item.external_attr
                new_zipinfo.compress_type = zipfile.ZIP_DEFLATED

                # Add the new content to the modified zipfile
                zout.writestr(new_zipinfo, xml)
            else:
                # Copy the original file to the modified zipfile
                with zin.open(item.filename) as infile, io.BytesIO() as buf:
                    buf.write(infile.read())
                    buf.seek(0)
                    zout.writestr(item, buf.getvalue())
    return filename_output

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def handle_translate_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    lang = request.form['lang']

    if file.filename == '':
        return redirect(request.url)

    if file and lang:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        translated_file_path = translate_file(file_path, lang)

        # return the translated file to the user
        return redirect(url_for('static', filename=translated_file_path))

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
