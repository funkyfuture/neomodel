from neomodel.core import StructuredNode
from neomodel.exceptions import InflateConflict, DeflateConflict


class SemiStructuredNode(StructuredNode):
    """
    A base class allowing properties to be stored on a node that aren't
    specified in its definition. Conflicting properties are signaled with the
    :class:`DeflateConflict` exception::

        class Person(SemiStructuredNode):
            name = StringProperty()
            age = IntegerProperty()

            def hello(self):
                print("Hi my names " + self.name)

        tim = Person(name='Tim', age=8, weight=11).save()
        tim.hello = "Hi"
        tim.save() # DeflateConflict
    """
    __abstract_node__ = True

    @classmethod
    def inflate(cls, node):
        # support lazy loading
        if isinstance(node, int):
            snode = cls()
            snode.id = node
        else:
            props = {}
            for name, definition in cls.__property_definitions__.items():
                if name in node.properties:
                    props[name] = definition.inflate(node.properties[name], node)
                elif definition.has_default:
                    props[name] = definition.default_value()
                else:
                    props[name] = None
            # handle properties not defined on the class
            for free_key in (x for x in node.properties if x not in props):
                if hasattr(cls, free_key):
                    raise InflateConflict(cls, free_key,
                                          node.properties[free_key], node.id)
                props[free_key] = node.properties[free_key]

            snode = cls(**props)
            snode.id = node.id

        return snode

    @classmethod
    def deflate(cls, properties, obj=None, skip_empty=False):
        deflated = super().deflate(properties, obj, skip_empty=skip_empty)
        for key in (k for k in properties if k not in deflated):
            if hasattr(cls, key):
                raise DeflateConflict(cls, key, deflated[key], obj.id)
        properties.update(deflated)
        return properties

    def save(self):
        properties = {name: value for name, value in vars(self).items()
                      if not name.startswith('__')
                      and not callable(value)}
        properties.update(self.__properties__)
        return self._save(properties)
