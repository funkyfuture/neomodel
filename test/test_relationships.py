from pytest import raises, mark

from neomodel import (
    One, IntegerProperty, StructuredNode, StringProperty, StructuredRel,
    Relationship, RelationshipFrom, RelationshipTo
)
from neomodel.exceptions import NodeIsDeletedError
from neomodel.relationship import RelationshipDefinition


class Person(StructuredNode):
    name = StringProperty(unique_index=True)
    age = IntegerProperty(index=True)
    is_from = RelationshipTo('Country', 'IS_FROM')
    knows = Relationship('Person', 'KNOWS')

    @property
    def special_name(self):
        return self.name

    def special_power(self):
        return "I have no powers"


class Country(StructuredNode):
    code = StringProperty(unique_index=True)
    inhabitant = RelationshipFrom(Person, 'IS_FROM')
    president = RelationshipTo(Person, 'PRESIDENT', cardinality=One)


class SuperHero(Person):
    power = StringProperty(index=True)

    def special_power(self):
        return "I have powers"


def test_actions_on_deleted_node():
    u = Person(name='Jim2', age=3).save()
    u.delete()
    with raises(NodeIsDeletedError):
        u.is_from.connect(None)

    with raises(NodeIsDeletedError):
        u.is_from.get()

    with raises(NodeIsDeletedError):
        u.save()


def test_bidirectional_relationships():
    u = Person(name='Jim', age=3).save()
    assert u

    de = Country(code='DE').save()
    assert de

    assert len(u.is_from) == 0
    assert not u.is_from

    assert u.is_from.__class__.__name__ == 'ZeroOrMore'
    u.is_from.connect(de)

    assert len(u.is_from) == 1
    assert u.is_from

    assert u.is_from.is_connected(de)

    b = u.is_from.all()[0]
    assert b.__class__.__name__ == 'Country'
    assert b.code == 'DE'

    s = b.inhabitant.all()[0]
    assert s.name == 'Jim'

    u.is_from.disconnect(b)
    assert not u.is_from.is_connected(b)


def test_either_direction_connect():
    rey = Person(name='Rey', age=3).save()
    sakis = Person(name='Sakis', age=3).save()

    rey.knows.connect(sakis)
    assert rey.knows.is_connected(sakis)
    assert sakis.knows.is_connected(rey)
    sakis.knows.connect(rey)

    result, meta = sakis.cypher("""MATCH (us), (them)
            WHERE id(us)={self} and id(them)={them}
            MATCH (us)-[r:KNOWS]-(them) RETURN COUNT(r)""",
            {'them': rey.id})
    assert int(result[0][0]) == 1

    rel = rey.knows.relationship(sakis)
    assert isinstance(rel, StructuredRel)

    rels = rey.knows.all_relationships(sakis)
    assert isinstance(rels[0], StructuredRel)


def test_search_and_filter_and_exclude():
    fred = Person(name='Fred', age=13).save()
    zz = Country(code='ZZ').save()
    zx = Country(code='ZX').save()
    zt = Country(code='ZY').save()
    fred.is_from.connect(zz)
    fred.is_from.connect(zx)
    fred.is_from.connect(zt)

    result = fred.is_from.filter(code='ZX')
    assert result[0].code == 'ZX'

    result = fred.is_from.exclude(code='ZZ').exclude(code='ZY')
    assert result[0].code == 'ZX' and len(result) == 1


def test_custom_methods():
    u = Person(name='Joe90', age=13).save()
    assert u.special_power() == "I have no powers"
    u = SuperHero(name='Joe91', age=13, power='xxx').save()
    assert u.special_power() == "I have powers"
    assert u.special_name == 'Joe91'


def test_valid_reconnection():
    p = Person(name='ElPresidente', age=93).save()
    assert p

    pp = Person(name='TheAdversary', age=33).save()
    assert pp

    c = Country(code='CU').save()
    assert c

    c.president.connect(p)
    assert c.president.is_connected(p)

    # the coup d'etat
    c.president.reconnect(p, pp)
    assert c.president.is_connected(pp)

    # reelection time
    c.president.reconnect(pp, pp)
    assert c.president.is_connected(pp)


def test_props_relationship():
    u = Person(name='Mar', age=20).save()
    assert u

    c = Country(code='AT').save()
    assert c

    c2 = Country(code='LA').save()
    assert c2

    with raises(NotImplementedError):
        c.inhabitant.connect(u, properties={'city': 'Thessaloniki'})


@mark.parametrize('node_class', (Person, SuperHero))
def test_introspective_properties(node_class):
    assert 'is_from' in node_class.__relationship_definitions__
    assert isinstance(node_class.__relationship_definitions__['is_from'],
                      RelationshipDefinition)
    assert 'knows' in node_class.__relationship_definitions__
    assert isinstance(node_class.__relationship_definitions__['knows'],
                      RelationshipDefinition)
