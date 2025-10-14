
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app --cov-report=html

# Ejecutar tests específicos
pytest tests/test_auth.py
pytest tests/test_auth.py::TestUserRegistration::test_register_user_success

# Ejecutar con verbose
pytest -v
