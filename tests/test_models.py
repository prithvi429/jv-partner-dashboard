import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


def test_models_create():
    engine = create_engine('sqlite:///:memory:')
    models.Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    company = models.Company(name='Acme')
    product = models.Product(name='Referral')
    db.add(company)
    db.add(product)
    db.flush()

    deal = models.Deal(name='Test Deal', company=company, product=product, value=1234.5)
    db.add(deal)
    db.commit()

    assert deal.id is not None
    assert deal.company.name == 'Acme'
    assert deal.product.name == 'Referral'
