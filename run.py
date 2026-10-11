from app.main import app, init_db, migrate_old_data

if __name__ == '__main__':
    init_db()
    migrate_old_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
