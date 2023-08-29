from routes import create_app
#change here for test
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    