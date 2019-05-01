from flask import Flask

app = Flask(__name__)

def generate_html(message):
    version_number = '0007'
    html = """
        <html>
        <body>
            <div style='text-align:center;font-size:80px;'>
                <image height="625" width="2500" src="https://dal05.objectstorage.softlayer.net/v1/AUTH_d0619b05-07fc-49f0-8249-da585ea45ce5/docker/uploads/banner_v1_FDjns4W.png">
                <br> {0}
                <p>Version Number: {1}</p>
            </div>
        </body>
        </html>""".format(message,version_number)
    return html

def greet():
    greeting = 'Welcome to CI/CD'
    return greeting

@app.route('/')

def hello_world():
    html = generate_html(greet())
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)