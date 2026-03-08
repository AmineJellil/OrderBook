from cbin.gui.Window import app


def run_gui():
    app.run_server(debug=False, host='0.0.0.0', port=80)


if __name__ == '__main__':
    run_gui()
