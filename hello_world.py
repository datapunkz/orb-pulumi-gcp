from flask import Flask

app = Flask(__name__)

def generate_html(message):
    version_number = '0001'
    html = """
        <html>
        <body>
            <div style='text-align:center;font-size:80px;'>
                <image width="800" height="333" src="https://storage.googleapis.com/gweb-cloudblog-publish/original_images/GC_NEXT-Blog-Header_V1.png">
                <br> {0}
                <p>Version Number: {1}</p>
            </div>
        </body>
        </html>""".format(message,version_number)
    return html

def greet():
    greeting = 'Welcome to Google Next 19!'
    return greeting

@app.route('/')

def hello_world():
    html = generate_html(greet())
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)