import argparse
from .app import get_app

def main(port):
    app = get_app()
    app.run(port=port)


def main_entrypoint():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store', help='Port',
                        default=5000, type=int, dest='port')
    parser.add_argument('--init-db', action='store_true', help='create db',
                        dest='init_db')
    args = parser.parse_args()

    if args.init_db:
        from .models import db
        db.create_all()

    main(port=args.port)
