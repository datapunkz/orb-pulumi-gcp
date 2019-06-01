from flask import Flask

app = Flask(__name__)

def generate_html(message):
    version_number = '0009'
    html = """
        <html>
        <body>
            <div style='text-align:center;font-size:80px;'>
                <image height="338" width="792" src="http://sessionize.com/image?f=3aa1ba56d3f57f411e0dbf7db1c94250,1140,400,False,True,7a-7e26-46f5-b92d-9f6cb59eb283.4a399ee8-9a74-4802-a12b-e344e161820a.png">
                <br> {0}
                <p>Version Number: {1}</p>
            </div>
        </body>
        </html>""".format(message,version_number)
    return html

def greet():
    greeting = 'Welcome to CI/CD!'
    return greeting

@app.route('/')

def hello_world():
    html = generate_html(greet())
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)