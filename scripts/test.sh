reset
#./scripts/uninstall.sh
#./scripts/install.sh
python examples/simple/manage.py test muses --traceback -v 3 --settings=settings.testing
#python examples/simple/manage.py test muses.tests.test_nested_proxy_field.TestNestedProxyFieldCreateAction.test_nested_proxy_field_model_serializer_depth --traceback -v 3 --settings=settings.testing
#python examples/simple/manage.py test muses.tests.test_nested_proxy_field.TestNestedProxyFieldUpdateAction.test_nested_proxy_field_model_serializer_depth --traceback -v 3 --settings=settings.testing
