import pytest

# This "mark" tells pytest: "Hey, this test needs the database. Access it."
@pytest.mark.django_db
def test_create_user(django_user_model):
    # 1. Arrange (Setup)
    User = django_user_model
    
    # 2. Act (Do the thing)
    user = User.objects.create_user(email="pytest@test.com", password="password")
    count = User.objects.count()
    
    # 3. Assert (Check the result)
    assert count == 1
    assert user.email == "pytest@test.com"