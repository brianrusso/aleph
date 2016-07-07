import logging

from aleph.core import db
from aleph.model.common import DatedModel, IdModel


log = logging.getLogger(__name__)


class Reference(db.Model, IdModel, DatedModel):
    id = db.Column(db.Integer(), primary_key=True)
    document_id = db.Column(db.BigInteger, db.ForeignKey('document.id'))
    entity_id = db.Column(db.String(32), db.ForeignKey('entity.id'))
    origin = db.Column(db.String(128))
    weight = db.Column(db.Integer)

    entity = db.relationship('Entity', backref=db.backref('references', lazy='dynamic'))
    document = db.relationship('Document', backref=db.backref('references', lazy='dynamic'))

    @classmethod
    def index_references(cls, document_id):
        """Helper function to get reference data for indexing."""
        # cf. aleph.index.entities.generate_entities()
        from aleph.model.entity import Entity, collection_entity_table
        cet = collection_entity_table.alias()
        q = db.session.query(Reference.entity_id, cet.c.collection_id)
        q = q.filter(cet.c.entity_id == Reference.entity_id)
        q = q.filter(Reference.document_id == document_id)
        q = q.filter(Entity.id == Reference.entity_id)
        q = q.filter(Entity.state == Entity.STATE_ACTIVE)
        return q.all()

    def to_dict(self):
        return {
            'entity': {
                'id': self.entity.id,
                'name': self.entity.name,
                '$schema': self.entity.type
            },
            'weight': self.weight,
            'origin': self.origin
        }

    def __repr__(self):
        return '<Reference(%r, %r)>' % (self.document_id, self.entity_id)
