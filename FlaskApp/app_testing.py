from flask import Flask
app = Flask(__name__)

@app.route('/')
def testing():
    return 'Application Testing!'

if __name__ == '__main__':
    app.run()
