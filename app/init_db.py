from app.database import engine
from app.models import Contact

def init_db():
    Contact.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
