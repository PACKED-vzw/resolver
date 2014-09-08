import cPickle
from resolver.database import db
from resolver.model import KVPair

# TODO: Use new session only for KVStore?
# db.session.commit might cause problems with transactions outside the scope
def get(key):
    pair = KVPair.query.filter(KVPair.key == key).first()

    if pair:
        return cPickle.loads(str(pair.value))
    else:
        pair = KVPair(key, cPickle.dumps(None))
        db.session.add(pair)
        db.session.commit()
        return None

def set(key, value):
    pair = KVPair.query.filter(KVPair.key == key).first()

    if pair:
        pair.value = cPickle.dumps(value)
    else:
        pair = KVPair(key, cPickle.dumps(value))
        db.session.add(pair)

    db.session.commit()
