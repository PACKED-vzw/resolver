from resolver.database import db_session, init_db
from resolver.model import PersistentObject, Document

init_db()

objects = [(PersistentObject(id=3717, type='work'),
            [Document(3717, type='data', url='http://www.smak.be/collectie_kunstenaar.php?kunstwerk_id=361&l=a&kunstenaar_id=180'),
             Document(3717, type='representation', url='http://www.smak.be/collectie_afbeeldingen/berti01.jpg')]),
           (PersistentObject(id=63, type='work'),
            [Document(63, type='data', url='http://www.smak.be/collectie_kunstenaar.php?kunstwerk_id=375&l=b&kunstenaar_id=182'),
             Document(63, type='representation', url='http://www.smak.be/collectie_afbeeldingen/beullens_pierre.jpeg')]),
           (PersistentObject(id=3472, type='work'),
            [Document(3472, type='data', url='http://www.smak.be/collectie_kunstenaar.php?kunstwerk_id=1490&l=b&kunstenaar_id=1608'),
             Document(3472, type='representation', url='http://www.smak.be/collectie_afbeeldingen/billing.jpg')]),
           (PersistentObject(id=102, type='work'),
            [Document(102, type='data', url='http://www.smak.be/collectie_kunstenaar.php?kunstwerk_id=382&l=b&kunstenaar_id=186'),
             Document(102, type='representation', url='http://www.smak.be/collectie_afbeeldingen/birnbaum_tiananmensquare.jpg')]),
           (PersistentObject(id=3385, type='work'),
            [Document(3385, type='data', url='http://www.smak.be/collectie_kunstenaar.php?kunstwerk_id=1461&l=b&kunstenaar_id=41'),
             Document(3385, type='representation', url='http://www.smak.be/collectie_afbeeldingen/the%20journey%20(true%20colours).jpg')])]

for object, documents in objects:
    db_session.add(object)
    for document in documents:
        db_session.add(document)

db_session.commit()
