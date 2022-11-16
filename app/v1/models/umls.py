import os
from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
                      UniqueIdProperty, RelationshipTo)
config.DATABASE_URL = os.environ["NEO4J_BOLT_URL"]
config.AUTO_INSTALL_LABELS = True


class Country(StructuredNode):
    code = StringProperty(unique_index=True, required=True)

class Person(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    age = IntegerProperty(index=True, default=0)
    # relation-ship 
    country = RelationshipTo(Country, 'IS_FROM')

